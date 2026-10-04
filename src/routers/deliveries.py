from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import DeliveryCreate, DeliveryResponse
from src.models import Delivery, User
from src.auth import get_current_user

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.post("/", response_model=DeliveryResponse)
def create_delivery(
    delivery: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_del = Delivery(**delivery.model_dump(), owner_id=current_user.id)
    db.add(new_del)
    db.commit()
    db.refresh(new_del)
    return new_del


@router.put("/{delivery_id}", response_model=DeliveryResponse)
def update_delivery(
    delivery_id: int,
    delivery: DeliveryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_del = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not db_del:
        raise HTTPException(status_code=404, detail="Доставка не знайдена")

    # IDOR Vulnerability Prevention (Горизонтальне розмежування прав)
    if db_del.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Ви не можете редагувати чужі маршрути"
        )

    db_del.target_lat = delivery.target_lat
    db_del.target_lon = delivery.target_lon
    db_del.prey_type = delivery.prey_type
    db.commit()
    db.refresh(db_del)
    return db_del
