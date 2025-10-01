from fastapi import APIRouter, Depends, Path
from app.models.accident import AccidentRecordCreate, AccidentRecordUpdate, AccidentRecordOut
from app.services.accident_service import (
    create_accident_record_service,
    edit_accident_record_service,
    get_all_accident_records_service,
    get_accident_record_by_id_service,
    get_accident_records_by_patient_service
)
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=AccidentRecordOut)
def create_accident_record(accident: AccidentRecordCreate, user=Depends(get_current_user)):
    return create_accident_record_service(accident, user)

@router.patch("/{accident_id}", response_model=AccidentRecordOut)
def edit_accident_record(accident_id: str, accident: AccidentRecordUpdate, user=Depends(get_current_user)):
    return edit_accident_record_service(accident_id, accident, user)

@router.get("/", response_model=list[AccidentRecordOut])
def get_all_accident_records(user=Depends(get_current_user)):
    return get_all_accident_records_service()

@router.get("/{accident_id}", response_model=AccidentRecordOut)
def get_accident_record_by_id(accident_id: str = Path(..., description="Accident Record UUID"), user=Depends(get_current_user)):
    return get_accident_record_by_id_service(accident_id)

@router.get("/patient/{patient_id}", response_model=list[AccidentRecordOut])
def get_accident_records_by_patient(patient_id: str = Path(..., description="Patient UUID"), user=Depends(get_current_user)):
    return get_accident_records_by_patient_service(patient_id, user)