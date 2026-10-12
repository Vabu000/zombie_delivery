from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth import get_current_user, require_courier_or_admin
from src.database import get_db
from src.models import Delivery, DeliveryStatus, User, UserRole
from src.schemas import (
    DeliveryCreate,
    DeliveryResponse,
    DeliveryStatusUpdate,
    DeliveryUpdate,
)

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


def calculate_reward(danger_level: str, prey_type: str) -> int:
    base = 10
    danger_mult = {
        "LOW": 1.0,
        "MEDIUM": 1.5,
        "HIGH": 2.0,
        "NIGHTMARE": 3.0,
    }.get(danger_level.upper(), 1.0)
    prey_mult = {
        "BRAIN": 2.0,
        "PLASMA": 1.8,
        "MEAT": 1.5,
        "ANTIDOTE": 2.2,
        "SUPPLIES": 1.2,
    }.get(prey_type.upper(), 1.0)
    return int(base * danger_mult * prey_mult)


@router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reward = calculate_reward(delivery.danger_level or "MEDIUM", delivery.prey_type)
    new_del = Delivery(
        title=delivery.title or "Нічна доставка провізії",
        target_lat=delivery.target_lat,
        target_lon=delivery.target_lon,
        prey_type=delivery.prey_type,
        danger_level=(delivery.danger_level or "MEDIUM").upper(),
        status=DeliveryStatus.PENDING,
        reward_brains=reward,
        notes=delivery.notes,
        owner_id=current_user.id,
    )
    db.add(new_del)
    db.commit()
    db.refresh(new_del)
    return new_del


@router.get("/", response_model=List[DeliveryResponse])
def get_deliveries(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Delivery)

    if current_user.is_admin or current_user.role == UserRole.ADMIN:
        # Адміністратор бачить усі доставки
        if status_filter:
            query = query.filter(Delivery.status == status_filter.upper())
    elif current_user.role == UserRole.COURIER:
        # Кур'єр бачить доступні для взяття (PENDING) або закріплені за ним
        query = query.filter(
            (Delivery.status == DeliveryStatus.PENDING) | (Delivery.courier_id == current_user.id)
        )
        if status_filter:
            query = query.filter(Delivery.status == status_filter.upper())
    else:
        # Звичайний клієнт бачить ТІЛЬКИ власні замовлення
        query = query.filter(Delivery.owner_id == current_user.id)
        if status_filter:
            query = query.filter(Delivery.status == status_filter.upper())

    return query.all()


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery_by_id(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_del = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не знайдена",
        )

    # Захист від IDOR: доступ лише власнику, призначеному кур'єру або адміністратору
    is_owner = db_del.owner_id == current_user.id
    is_assigned_courier = db_del.courier_id == current_user.id
    is_admin = current_user.is_admin or current_user.role == UserRole.ADMIN

    if not (is_owner or is_assigned_courier or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено: несанкціонований перегляд чужої доставки (IDOR захист)",
        )

    return db_del


@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: int,
    delivery: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_del = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не знайдена",
        )

    # IDOR Vulnerability Prevention (Горизонтальне розмежування прав)
    if db_del.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не можете редагувати чужі маршрути",
        )

    # Бізнес-правило: не можна змінювати замовлення, які вже доставлені або скасовані
    if db_del.status in [DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неможливо редагувати доставку у завершеному чи скасованому статусі",
        )

    if delivery.title is not None:
        db_del.title = delivery.title
    if delivery.target_lat is not None:
        db_del.target_lat = delivery.target_lat
    if delivery.target_lon is not None:
        db_del.target_lon = delivery.target_lon
    if delivery.prey_type is not None:
        db_del.prey_type = delivery.prey_type
    if delivery.danger_level is not None:
        db_del.danger_level = delivery.danger_level.upper()
    if delivery.notes is not None:
        db_del.notes = delivery.notes

    # Перерахунок винагороди при зміні параметрів
    db_del.reward_brains = calculate_reward(db_del.danger_level, db_del.prey_type)

    db.commit()
    db.refresh(db_del)
    return db_del


@router.post("/{delivery_id}/claim", response_model=DeliveryResponse)
def claim_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_courier_or_admin),
):
    db_del = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не знайдена",
        )
    if db_del.status != DeliveryStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Замовлення вже прийняте в доставку або завершене",
        )

    db_del.courier_id = current_user.id
    db_del.status = DeliveryStatus.IN_TRANSIT
    db.commit()
    db.refresh(db_del)
    return db_del


@router.post("/{delivery_id}/complete", response_model=DeliveryResponse)
def complete_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_del = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не знайдена",
        )

    # Тільки призначений кур'єр або адміністратор
    is_courier = db_del.courier_id == current_user.id
    is_admin = current_user.is_admin or current_user.role == UserRole.ADMIN

    if not (is_courier or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Лише призначений кур'єр або адміністратор може завершити доставку",
        )

    db_del.status = DeliveryStatus.DELIVERED
    db.commit()
    db.refresh(db_del)
    return db_del


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def change_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_del = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не знайдена",
        )

    is_admin = current_user.is_admin or current_user.role == UserRole.ADMIN
    is_courier = db_del.courier_id == current_user.id

    if not (is_admin or is_courier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостатньо прав для зміни статусу доставки",
        )

    new_status = status_update.status.upper()
    if new_status not in [
        DeliveryStatus.PENDING,
        DeliveryStatus.IN_TRANSIT,
        DeliveryStatus.DELIVERED,
        DeliveryStatus.CANCELLED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неприпустимий статус доставки",
        )

    db_del.status = new_status
    db.commit()
    db.refresh(db_del)
    return db_del


@router.delete("/{delivery_id}")
def cancel_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_del = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_del:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Доставка не знайдена",
        )

    # IDOR Vulnerability Prevention: лише власник або адміністратор
    if db_del.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ви не можете скасувати чужу доставку",
        )

    db_del.status = DeliveryStatus.CANCELLED
    db.commit()
    return {"message": "Доставку успішно скасовано", "delivery_id": delivery_id}
