from fastapi import APIRouter, Depends, Path
from app.models.patient import PatientCreate, PatientUpdate, PatientOut
from app.services.patient_service import (
    create_patient_service,
    edit_patient_service,
    get_patient_by_id_service,
    get_hospital_patients_service
)
from app.auth.dependencies import get_current_user, nurse_required
from app.auth.hospital_dependency import get_user_hospital_id

router = APIRouter()

@router.post("/", response_model=PatientOut, dependencies=[Depends(nurse_required)])
async def create_patient(
    patient: PatientCreate,
    hospital_id: str = Depends(get_user_hospital_id)
):
    return create_patient_service(patient, hospital_id)

@router.patch("/{patient_id}", response_model=PatientOut, dependencies=[Depends(get_current_user)])
def edit_patient(patient_id: str, patient: PatientUpdate):
    return edit_patient_service(patient_id, patient)

@router.get("/", response_model=list[PatientOut])
async def get_hospital_patients(hospital_id: str = Depends(get_user_hospital_id)):
    """Get patients associated with the current user's hospital"""
    return get_hospital_patients_service(hospital_id)

@router.get("/{patient_id}", response_model=PatientOut, dependencies=[Depends(get_current_user)])
def get_patient_by_id(patient_id: str = Path(..., description="Patient UUID")):
    return get_patient_by_id_service(patient_id)
