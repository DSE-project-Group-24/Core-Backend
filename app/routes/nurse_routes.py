from fastapi import APIRouter, Depends, HTTPException, Path
from app.models.user import UserOut
from app.services.nurse_service import (
    get_all_nurses_service,
    get_nurse_by_id_service,
    get_nurse_by_name_service,
    get_nurse_by_nic_service
)

from app.auth.dependencies import get_current_user, hospital_admin_required

router = APIRouter()

@router.get("/", dependencies=[Depends(hospital_admin_required)])
def get_all_nurses():
    return get_all_nurses_service()

@router.get("/id/{nurse_id}", dependencies=[Depends(get_current_user)])
def get_nurse_by_id(nurse_id: str = Path(..., description="Nurse UUID")):
    return get_nurse_by_id_service(nurse_id)

@router.get("/name/{name}", dependencies=[Depends(get_current_user)])
def get_nurse_by_name(name: str = Path(..., description="Nurse name")):
    return get_nurse_by_name_service(name)


@router.get("/nic/{nic}", dependencies=[Depends(get_current_user)])
def get_nurse_by_nic(nic: str = Path(..., description="Nurse NIC")):
    return get_nurse_by_nic_service(nic)
