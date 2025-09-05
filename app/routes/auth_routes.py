from typing import List
from fastapi import APIRouter, Query
from app.models.user import UserOut, UserIn, UserLogin
from app.services.auth_service import (
    register_nurse_service, 
    register_doctor_service, 
    register_hospital_administrator_service, 
    register_government_service,  
    list_users_service, 
    login_user_service
)

router = APIRouter()

@router.get("/", response_model=List[UserOut])
def list_users(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return list_users_service(limit, offset)



@router.post("/login")
def login_user(credentials: UserLogin):
    return login_user_service(credentials)



# ===== Role-specific registration endpoints =====
@router.post("/register/nurse", response_model=UserOut)
def register_nurse(user: UserIn):
    return register_nurse_service(user)


@router.post("/register/doctor", response_model=UserOut)
def register_doctor(user: UserIn):
    return register_doctor_service(user)


@router.post("/register/hospital-administrator", response_model=UserOut)
def register_hospital_administrator(user: UserIn):
    return register_hospital_administrator_service(user)


@router.post("/register/government", response_model=UserOut)
def register_government(user: UserIn):
    return register_government_service(user)