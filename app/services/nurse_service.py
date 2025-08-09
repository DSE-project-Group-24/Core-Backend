from sqlalchemy.orm import Session
from uuid import UUID
from ..models.patient import Patient, PatientCreate, PatientUpdate, SeverityLevel
from fastapi import HTTPException, status

def get_pending_patients(db: Session, hospital_id: UUID):
    return (
        db.query(Patient)
        .filter(Patient.hospital_id == hospital_id, Patient.severity == SeverityLevel.unknown)
        .all()
    )

def add_pending_patient(db: Session, patient_in: PatientCreate, creator_id: UUID):
    patient = Patient(
        name=patient_in.name,
        ward=patient_in.ward,
        bed_number=patient_in.bed_number,
        hospital_id=patient_in.hospital_id,
        severity=SeverityLevel.unknown,
        created_by=creator_id,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def complete_patient_details(
    db: Session,
    patient_id: UUID,
    patient_update: PatientUpdate,
    hospital_id: UUID,
):
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.hospital_id == hospital_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    for field, value in patient_update.dict(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient
