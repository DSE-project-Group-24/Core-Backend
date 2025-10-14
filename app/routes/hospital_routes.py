from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List
from app.models.hospital import Hospital

from app.models.hospital import HospitalCreate, HospitalUpdate
from app.models.hospital_staff import AssignStaffToHospital
from app.services.hospital_staff_service import (
    add_doctor_to_hospital_service,
    add_nurse_to_hospital_service,
    get_doctors_count_service,
    get_nurses_count_service, get_patients_count_service

)
from app.services.hospital_service import (
    create_hospital_service,
    get_all_hospitals_service,
    get_hospital_by_id_service,
    get_hospital_by_name_service,
    edit_hospital_service,
    get_all_hospitals,
    search_hospitals_by_name,
    list_hospitals


)
from app.auth.dependencies import get_current_user, hospital_admin_required,government_personnel_required
from app.auth.hospital_dependency import get_user_hospital_id

router = APIRouter()

@router.post("/", dependencies=[Depends(hospital_admin_required)])
def create_hospital(hospital: HospitalCreate):
    return create_hospital_service(hospital)

@router.get("/", dependencies=[Depends(get_current_user)])
def get_all_hospitals():
    return get_all_hospitals_service()

@router.get("/hospital_list", dependencies=[Depends(get_current_user)])
def get_hospital_list():
    return list_hospitals()

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
async def assign_doctor(data: dict, hospital_id: str = Depends(get_user_hospital_id)):
    staff_data = AssignStaffToHospital(user_id=data["user_id"], hospital_id=hospital_id)
    return add_doctor_to_hospital_service(staff_data)

# Assign nurse to hospital (hospital admin only)
@router.post("/assign-nurse", dependencies=[Depends(hospital_admin_required)])
async def assign_nurse(data: dict, hospital_id: str = Depends(get_user_hospital_id)):
    staff_data = AssignStaffToHospital(user_id=data["user_id"], hospital_id=hospital_id)
    return add_nurse_to_hospital_service(staff_data)

# Get count of doctors in hospital (hospital admin only)
@router.get("/doctors-count", dependencies=[Depends(hospital_admin_required)])
async def get_doctors_count(hospital_id: str = Depends(get_user_hospital_id)):
    """Get the count of all doctors in the logged-in hospital administrator's hospital"""
    return get_doctors_count_service(hospital_id)

# Get count of nurses in hospital (hospital admin only)
@router.get("/nurses-count", dependencies=[Depends(hospital_admin_required)])
async def get_nurses_count(hospital_id: str = Depends(get_user_hospital_id)):
    """Get the count of all nurses in the logged-in hospital administrator's hospital"""
    return get_nurses_count_service(hospital_id)

# Get count of patients in hospital (hospital admin only)
@router.get("/patients-count", dependencies=[Depends(hospital_admin_required)])
async def get_patients_count(hospital_id: str = Depends(get_user_hospital_id)):
    """Get the count of all patients in the logged-in hospital administrator's hospital"""
    return get_patients_count_service(hospital_id)

# Routes for access hospitals to goverment persons



# @router.get("/all", dependencies=[Depends(government_personnel_required)])
# def get_all_hospitals():
#     return get_all_hospitals_service()

@router.get("/all")
def get_all_hospitals():
    return get_all_hospitals_service()
