from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    require_admin,
    verify_password,
)
from src.config import settings
from src.database import get_db
from src.models import Delivery, DeliveryStatus, User, UserRole
from src.schemas import (
    TokenResponse,
    UserAdminCreate,
    UserCreate,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач вже існує",
        )
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=UserRole.USER.value,
        is_admin=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/register-admin", response_model=UserResponse)
def register_admin(user: UserAdminCreate, db: Session = Depends(get_db)):
    if user.admin_secret != settings.ADMIN_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Невірний секретний ключ для реєстрації адміністратора",
        )
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з таким логіном вже існує",
        )
    admin_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name or "Hive Overlord Admin",
        role=UserRole.ADMIN.value,
        is_admin=True,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user


@router.post("/register-courier", response_model=UserResponse)
def register_courier(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач вже існує",
        )
    courier_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name or "Zombie Night Hunter",
        role=UserRole.COURIER.value,
        is_admin=False,
    )
    db.add(courier_user)
    db.commit()
    db.refresh(courier_user)
    return courier_user


@router.post("/login", response_model=TokenResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль",
        )
    token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role, "id": db_user.id}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": db_user.role,
        "username": db_user.username,
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено",
        )

    # Горизонтальне розмежування прав (IDOR): звичайний юзер не може міняти чужий профіль
    if target_user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено: спроба несанкціонованої модифікації чужого профілю (IDOR)",
        )

    if user_update.full_name is not None:
        target_user.full_name = user_update.full_name
    if user_update.password is not None:
        target_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(target_user)
    return target_user


@router.get("/admin-panel")
def admin_panel(current_user: User = Depends(require_admin)):
    return {
        "message": "Вітаємо в адмін-панелі для вищого керівництва зомбі.",
        "admin_username": current_user.username,
        "role": current_user.role,
        "system_status": "All sectors operational under Hive Mind control",
    }


@router.get("/dashboard")
def user_dashboard_stub(current_user: User = Depends(get_current_user)):
    return {
        "title": "Домашня сторінка користувача-виживалого",
        "username": current_user.username,
        "role": current_user.role,
        "status": "Alive and Ordering",
        "message": "Ласкаво просимо до кабінету замовлень Zombie Delivery!",
    }


@router.get("/courier-panel")
def courier_panel_stub(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (current_user.is_admin or current_user.role in [UserRole.COURIER, UserRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ лише для кур'єрів зомбі",
        )
    active_count = (
        db.query(Delivery)
        .filter(
            Delivery.courier_id == current_user.id,
            Delivery.status == DeliveryStatus.IN_TRANSIT.value,
        )
        .count()
    )
    return {
        "title": "Панель нічного кур'єра-мисливця",
        "username": current_user.username,
        "role": current_user.role,
        "active_hunts": active_count,
        "status": "Ready for night shift hunt",
    }
