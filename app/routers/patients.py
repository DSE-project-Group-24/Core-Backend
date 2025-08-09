from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..models.patient import PatientCreate, PatientOut, PatientUpdate
from ..models.user import User, UserRole
from ..services import patient_service
from ..database import get_db
from ..utils.role_check import get_current_active_user

router = APIRouter()

def doctor_or_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role not in {UserRole.doctor, UserRole.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return current_user

@router.get("/", response_model=List[PatientOut])
def list_patients(
    current_user: User = Depends(doctor_or_admin_user),
    db: Session = Depends(get_db),
):
    return patient_service.list_patients(db, current_user)

@router.post("/", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_in: PatientCreate,
    current_user: User = Depends(doctor_or_admin_user),
    db: Session = Depends(get_db),
):
    # Admins can create patients; doctors can too, restricted to their hospital
    if patient_in.hospital_id != current_user.hospital_id:
        raise HTTPException(status_code=400, detail="Hospital mismatch")
    return patient_service.create_patient(db, patient_in, current_user.id)

@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: uuid.UUID,
    patient_update: PatientUpdate,
    current_user: User = Depends(doctor_or_admin_user),
    db: Session = Depends(get_db),
):
    return patient_service.update_patient(db, patient_id, patient_update, current_user)

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(doctor_or_admin_user),
    db: Session = Depends(get_db),
):
    patient_service.delete_patient(db, patient_id, current_user)
    return
