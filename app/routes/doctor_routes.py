from fastapi import APIRouter, Depends, HTTPException, Path
from app.services.doctor_service import (
    get_all_doctors_service,
    get_doctor_by_id_service,
    get_doctor_by_name_service,
    get_doctor_by_nic_service
)

from app.auth.dependencies import get_current_user, hospital_admin_required

router = APIRouter()

@router.get("/", dependencies=[Depends(hospital_admin_required)])
def get_all_doctors():
    return get_all_doctors_service()

@router.get("/id/{doctor_id}", dependencies=[Depends(get_current_user)])
def get_doctor_by_id(doctor_id: str = Path(..., description="Doctor UUID")):
    return get_doctor_by_id_service(doctor_id)

@router.get("/name/{name}", dependencies=[Depends(get_current_user)])
def get_doctor_by_name(name: str = Path(..., description="Doctor name")):
    return get_doctor_by_name_service(name)


@router.get("/nic/{nic}", dependencies=[Depends(get_current_user)])
def get_doctor_by_nic(nic: str = Path(..., description="Doctor NIC")):
    return get_doctor_by_nic_service(nic)
