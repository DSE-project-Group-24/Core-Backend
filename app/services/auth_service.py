from sqlalchemy.orm import Session
from uuid import UUID
from passlib.context import CryptContext
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import jwt

from ..models.user import User, UserCreate, UserUpdate, UserRole
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token creation
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# Create user
def create_user(db: Session, user: UserCreate) -> User:
    hashed_pw = hash_password(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_pw,
        role=user.role,
        hospital_id=user.hospital_id,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# List users by hospital (exclude admins and govt)
def list_users_by_hospital(db: Session, hospital_id: UUID):
    return (
        db.query(User)
        .filter(
            User.hospital_id == hospital_id,
            User.role.in_([UserRole.nurse, UserRole.doctor])
        )
        .all()
    )

# Update user
def update_user(db: Session, user_id: UUID, user_update: UserUpdate, hospital_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id, User.hospital_id == hospital_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# Delete user
def delete_user(db: Session, user_id: UUID, hospital_id: UUID):
    user = db.query(User).filter(User.id == user_id, User.hospital_id == hospital_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()

# Dependency to get current user from JWT (used in utils/role_check.py)
def get_current_user(db: Session, token: str) -> User:
    from fastapi import HTTPException, Security
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import jwt

    security = HTTPBearer()
    credentials: HTTPAuthorizationCredentials = Security(security)
    if not credentials:
        raise HTTPException(status_code=401, detail="Invalid authorization")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user
