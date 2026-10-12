from typing import Optional

from pydantic import BaseModel, ConfigDict

from src.models import DangerLevel, DeliveryStatus, UserRole


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None


class UserAdminCreate(BaseModel):
    username: str
    password: str
    admin_secret: str
    full_name: Optional[str] = "Overlord Admin"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    role: str = UserRole.USER.value
    is_admin: bool = False
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class DeliveryCreate(BaseModel):
    title: Optional[str] = "Нічна доставка провізії"
    target_lat: float
    target_lon: float
    prey_type: str  # Наприклад: "Brain", "Meat", "Plasma", "Supplies"
    danger_level: Optional[str] = DangerLevel.MEDIUM.value
    notes: Optional[str] = None


class DeliveryUpdate(BaseModel):
    title: Optional[str] = None
    target_lat: Optional[float] = None
    target_lon: Optional[float] = None
    prey_type: Optional[str] = None
    danger_level: Optional[str] = None
    notes: Optional[str] = None


class DeliveryStatusUpdate(BaseModel):
    status: str


class DeliveryResponse(BaseModel):
    id: int
    title: str
    target_lat: float
    target_lon: float
    prey_type: str
    danger_level: str
    status: str = DeliveryStatus.PENDING.value
    reward_brains: int
    notes: Optional[str] = None
    owner_id: int
    courier_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
