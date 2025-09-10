from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError, jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Only allow hospital administrators
def hospital_admin_required(user: dict = Depends(get_current_user)):
    if user.get("role") != "hospital_administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hospital administrators can perform this action."
        )
    return user


# Only allow nurses
def nurse_required(user: dict = Depends(get_current_user)):
    if user.get("role") != "nurse":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only nurses can perform this action."
        )
    return user

# Only allow government personnel
def government_personnel_required(user: dict = Depends(get_current_user)):
    if user.get("role") != "government_personnel":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only government personnel can perform this action."
        )
    return user