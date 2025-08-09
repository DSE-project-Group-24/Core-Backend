from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import uuid
import enum
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# --- Injury Type Enum ---
class InjuryType(str, enum.Enum):
    head = "Head Injury"
    limb = "Limb Injury"
    torso = "Torso Injury"
    multiple = "Multiple Injuries"
    other = "Other"

# --- Injury Site Enum ---
class InjurySite(str, enum.Enum):
    road = "Road Accident"
    workplace = "Workplace Accident"
    home = "Home Accident"
    other = "Other"

# --- SQLAlchemy ORM Model ---
class Accident(Base):
    __tablename__ = "accidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    injury_type = Column(Enum(InjuryType), nullable=False)
    injury_site = Column(Enum(InjurySite), nullable=False)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="accident")
    creator = relationship("User")

# --- Pydantic Schemas ---
class AccidentBase(BaseModel):
    patient_id: uuid.UUID
    injury_type: InjuryType
    injury_site: InjurySite

class AccidentCreate(AccidentBase):
    pass

class AccidentUpdate(BaseModel):
    injury_type: InjuryType | None = None
    injury_site: InjurySite | None = None

class AccidentOut(AccidentBase):
    id: uuid.UUID
    occurred_at: datetime
    created_by: uuid.UUID

    class Config:
        orm_mode = True
