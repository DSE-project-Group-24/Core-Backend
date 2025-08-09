from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from ..models.patient import Patient, PatientCreate, PatientUpdate
from ..models.user import User, UserRole

def list_patients(db: Session, user: User):
    # Doctors and Admins see patients only from their hospital
    return db.query(Patient).filter(Patient.hospital_id == user.hospital_id).all()

def create_patient(db: Session, patient_in: PatientCreate, creator_id: UUID):
    patient = Patient(
        name=patient_in.name,
        ward=patient_in.ward,
        bed_number=patient_in.bed_number,
        hospital_id=patient_in.hospital_id,
        severity=patient_in.severity,
        created_by=creator_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def update_patient(db: Session, patient_id: UUID, patient_update: PatientUpdate, user: User):
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.hospital_id == user.hospital_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Optionally enforce: only admins or doctors from same hospital can update
    for field, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient_id: UUID, user: User):
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.hospital_id == user.hospital_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    db.delete(patient)
    db.commit()
