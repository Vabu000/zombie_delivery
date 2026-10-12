from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class UserRole(str, Enum):
    """Ролі користувачів системи."""

    ADMIN = "admin"
    COURIER = "courier"
    USER = "user"


class DeliveryStatus(str, Enum):
    """Статуси життєвого циклу доставки."""

    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class DangerLevel(str, Enum):
    """Рівні небезпеки зон доставки."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    NIGHTMARE = "NIGHTMARE"


class PreyType(str, Enum):
    """Типи провізії та здобичі."""

    BRAIN = "Brain"
    MEAT = "Meat"
    PLASMA = "Plasma"
    ANTIDOTE = "Antidote"
    SUPPLIES = "Supplies"


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    role: str = Column(String, default=UserRole.USER.value, nullable=False)
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    full_name: Optional[str] = Column(String, nullable=True)
    created_at: datetime = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    deliveries = relationship(
        "Delivery",
        back_populates="owner",
        foreign_keys="[Delivery.owner_id]",
        cascade="all, delete-orphan",
    )
    assigned_deliveries = relationship(
        "Delivery",
        back_populates="courier",
        foreign_keys="[Delivery.courier_id]",
    )

    def __init__(self, **kwargs):
        # Автоматична синхронізація ролі admin та прапорця is_admin
        if kwargs.get("role") == UserRole.ADMIN or kwargs.get("role") == "admin":
            kwargs.setdefault("is_admin", True)
        elif kwargs.get("is_admin") is True:
            kwargs.setdefault("role", UserRole.ADMIN.value)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Delivery(Base):
    __tablename__ = "deliveries"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String, default="Нічна доставка провізії", nullable=False)
    prey_type: str = Column(String, nullable=False)  # "Brain", "Meat", "Plasma", "Supplies"
    target_lat: float = Column(Float, nullable=False)
    target_lon: float = Column(Float, nullable=False)
    danger_level: str = Column(String, default=DangerLevel.MEDIUM.value, nullable=False)
    status: str = Column(String, default=DeliveryStatus.PENDING.value, nullable=False)
    reward_brains: int = Column(Integer, default=15, nullable=False)
    notes: Optional[str] = Column(String, nullable=True)

    owner_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    courier_id: Optional[int] = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: datetime = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    owner = relationship("User", back_populates="deliveries", foreign_keys=[owner_id])
    courier = relationship("User", back_populates="assigned_deliveries", foreign_keys=[courier_id])

    def __repr__(self) -> str:
        return f"<Delivery(id={self.id}, title='{self.title}', status='{self.status}')>"
