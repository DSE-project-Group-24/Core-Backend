# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# import uuid

# from ..models.user import UserCreate, UserOut, UserUpdate, UserRole, User
# from ..services import auth_service
# from ..database import get_db
# from ..utils.role_check import get_current_active_user

# router = APIRouter()

# def admin_user(current_user: User = Depends(get_current_active_user)):
#     if current_user.role != UserRole.admin:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized as admin")
#     return current_user

# @router.get("/users", response_model=List[UserOut])
# def list_users(
#     current_user: User = Depends(admin_user),
#     db: Session = Depends(get_db),
# ):
#     # Admin can list only users within their hospital except other admins
#     return auth_service.list_users_by_hospital(db, current_user.hospital_id)

# @router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
# def create_user(
#     user_in: UserCreate,
#     current_user: User = Depends(admin_user),
#     db: Session = Depends(get_db),
# ):
#     # Ensure created user belongs to admin's hospital and role is nurse or doctor only
#     if user_in.hospital_id != current_user.hospital_id:
#         raise HTTPException(status_code=400, detail="Hospital mismatch")
#     if user_in.role not in {UserRole.nurse, UserRole.doctor}:
#         raise HTTPException(status_code=400, detail="Can only create nurse or doctor accounts")
#     return auth_service.create_user(db, user_in)

# @router.put("/users/{user_id}", response_model=UserOut)
# def update_user(
#     user_id: uuid.UUID,
#     user_update: UserUpdate,
#     current_user: User = Depends(admin_user),
#     db: Session = Depends(get_db),
# ):
#     return auth_service.update_user(db, user_id, user_update, current_user.hospital_id)

# @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_user(
#     user_id: uuid.UUID,
#     current_user: User = Depends(admin_user),
#     db: Session = Depends(get_db),
# ):
#     auth_service.delete_user(db, user_id, current_user.hospital_id)
#     return


# routers/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserOut  # Adjust import to your structure

router = APIRouter()

@router.get("/all-users", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()
