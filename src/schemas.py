from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class DeliveryCreate(BaseModel):
    target_lat: float
    target_lon: float
    prey_type: str


class DeliveryResponse(DeliveryCreate):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
