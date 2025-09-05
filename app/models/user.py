from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    nic: str
    role: str = "user"  # default role


class UserOut(BaseModel):
    user_id: UUID
    role: str
    nic: str
    name: str
    email: EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str