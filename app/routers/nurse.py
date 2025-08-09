from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models.user import UserOut
from ..models.patient import PatientCreate, PatientOut, PatientUpdate, SeverityLevel
from ..models.user import UserRole, User
from ..services import nurse_service
from ..database import get_db
from ..utils.role_check import get_current_active_user, role_required

router = APIRouter()

# Nurse role only dependency
def nurse_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.nurse:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as nurse")
    return current_user

@router.get("/pending-patients", response_model=List[PatientOut])
def get_pending_patients(
    current_user: User = Depends(nurse_user),
    db: Session = Depends(get_db),
):
    # Fetch patients with severity = unknown in nurse's hospital
    return nurse_service.get_pending_patients(db, current_user.hospital_id)

@router.post("/add-patient", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def add_pending_patient(
    patient_in: PatientCreate,
    current_user: User = Depends(nurse_user),
    db: Session = Depends(get_db),
):
    # Hospital ID must match nurse's hospital for data integrity
    if patient_in.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=400, detail="Hospital mismatch")

    return nurse_service.add_pending_patient(db, patient_in, current_user.id)

@router.put("/complete-patient/{patient_id}", response_model=PatientOut)
def complete_patient_details(
    patient_id: uuid.UUID,
    patient_update: PatientUpdate,
    current_user: User = Depends(nurse_user),
    db: Session = Depends(get_db),
):
    # Nurse can update patient only in their hospital
    return nurse_service.complete_patient_details(db, patient_id, patient_update, current_user.hospital_id)


@router.get("/all-nurses", response_model=List[UserOut])
def get_all_nurses(db: Session = Depends(get_db)):
    nurses = db.query(User).filter(User.role == UserRole.nurse).all()
    return nurses