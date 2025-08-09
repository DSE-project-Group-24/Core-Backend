from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
import uuid
import enum

from ..database import engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# --- Role Enum ---
# class UserRole(str, enum.Enum):
#     nurse = "nurse"
#     doctor = "doctor"
#     admin = "admin"
#     government = "government"

# --- SQLAlchemy ORM Model ---
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    #role = Column(Enum(UserRole), nullable=False)
    # hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationship (example: if hospital table exists)
    # hospital = relationship("Hospital", back_populates="users")

# --- Pydantic Schemas ---
# class UserBase(BaseModel):
#     email: EmailStr
#     full_name: str
#     role: UserRole
#     hospital_id: uuid.UUID | None = None
#     is_active: bool = True

# class UserCreate(UserBase):
#     password: str

# class UserUpdate(BaseModel):
#     full_name: str | None = None
#     password: str | None = None
#     is_active: bool | None = None

# class UserOut(UserBase):
#     id: uuid.UUID

#     class Config:
#         orm_mode = True

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True