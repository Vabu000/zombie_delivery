from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class UserRole:
    ADMIN = "admin"
    COURIER = "courier"
    USER = "user"


class DeliveryStatus:
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER, nullable=False)
    is_admin = Column(Boolean, default=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    deliveries = relationship(
        "Delivery",
        back_populates="owner",
        foreign_keys="Delivery.owner_id",
        cascade="all, delete-orphan",
    )
    assigned_deliveries = relationship(
        "Delivery",
        back_populates="courier",
        foreign_keys="Delivery.courier_id",
    )


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Нічна доставка провізії", nullable=False)
    prey_type = Column(String, nullable=False)  # "Brain", "Meat", "Plasma", "Supplies"
    target_lat = Column(Float, nullable=False)
    target_lon = Column(Float, nullable=False)
    danger_level = Column(String, default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, NIGHTMARE
    status = Column(String, default=DeliveryStatus.PENDING, nullable=False)
    reward_brains = Column(Integer, default=15, nullable=False)
    notes = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="deliveries", foreign_keys=[owner_id])
    courier = relationship("User", back_populates="assigned_deliveries", foreign_keys=[courier_id])
