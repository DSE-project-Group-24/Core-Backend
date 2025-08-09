from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import uuid
import enum
from datetime import datetime

from ..database import engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# --- Severity Enum ---
class SeverityLevel(str, enum.Enum):
    serious = "Serious"
    mild_moderate = "Mild/Moderate"
    unknown = "Unknown"

# --- SQLAlchemy ORM Model ---
class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    ward = Column(String, nullable=False)
    bed_number = Column(String, nullable=False)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False)
    admitted_at = Column(DateTime, default=datetime.utcnow)
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.unknown)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    hospital = relationship("Hospital", back_populates="patients")
    creator = relationship("User")

# --- Pydantic Schemas ---
class PatientBase(BaseModel):
    name: str
    ward: str
    bed_number: str
    hospital_id: uuid.UUID
    severity: SeverityLevel = SeverityLevel.unknown

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: str | None = None
    ward: str | None = None
    bed_number: str | None = None
    severity: SeverityLevel | None = None

class PatientOut(PatientBase):
    id: uuid.UUID
    admitted_at: datetime
    created_by: uuid.UUID

    class Config:
        orm_mode = True
