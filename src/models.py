from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    deliveries = relationship("Delivery", back_populates="owner")


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    target_lat = Column(Float)
    target_lon = Column(Float)
    prey_type = Column(String)  # Тип цілі (напр. "Brain", "Meat")
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="deliveries")
