from fastapi import APIRouter, Depends, HTTPException, Path
from app.models.hospital import HospitalCreate, HospitalUpdate
from app.models.hospital_staff import AssignStaffToHospital
from app.services.hospital_staff_service import add_doctor_to_hospital_service, add_nurse_to_hospital_service
from app.services.hospital_service import (
    create_hospital_service,
    get_all_hospitals_service,
    get_hospital_by_id_service,
    get_hospital_by_name_service,
    edit_hospital_service
)
from app.auth.dependencies import get_current_user, hospital_admin_required

router = APIRouter()

@router.post("/", dependencies=[Depends(hospital_admin_required)])
def create_hospital(hospital: HospitalCreate):
    return create_hospital_service(hospital)

@router.get("/", dependencies=[Depends(get_current_user)])
def get_all_hospitals():
    return get_all_hospitals_service()

@router.get("/id/{hospital_id}", dependencies=[Depends(get_current_user)])
def get_hospital_by_id(hospital_id: str = Path(..., description="Hospital UUID")):
    return get_hospital_by_id_service(hospital_id)

@router.get("/name/{name}", dependencies=[Depends(get_current_user)])
def get_hospital_by_name(name: str = Path(..., description="Hospital name")):
    return get_hospital_by_name_service(name)

@router.patch("/{hospital_id}", dependencies=[Depends(hospital_admin_required)])
def edit_hospital(hospital_id: str, hospital: HospitalUpdate):
    return edit_hospital_service(hospital_id, hospital)


# Assign doctor to hospital (hospital admin only)
@router.post("/assign-doctor", dependencies=[Depends(hospital_admin_required)])
def assign_doctor(data: AssignStaffToHospital):
    return add_doctor_to_hospital_service(data)

# Assign nurse to hospital (hospital admin only)
@router.post("/assign-nurse", dependencies=[Depends(hospital_admin_required)])
def assign_nurse(data: AssignStaffToHospital):
    return add_nurse_to_hospital_service(data)