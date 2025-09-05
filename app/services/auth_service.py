from fastapi import HTTPException
from app.db import get_supabase
from postgrest.exceptions import APIError
from app.models.user import UserIn, UserLogin
from app.utils.auth import hash_password, verify_password, create_access_token, create_refresh_token




# Role-specific registration functions
def register_nurse_service(user: UserIn):
    return register_user_service(user, "nurse")

def register_doctor_service(user: UserIn):
    return register_user_service(user, "doctor")

def register_hospital_administrator_service(user: UserIn):
    return register_user_service(user, "hospital_administrator")

def register_government_service(user: UserIn):
    return register_user_service(user, "government_personnel")


# Login function
def login_user_service(credentials: UserLogin):
    supabase = get_supabase()
    resp = supabase.table("User").select("*").eq("email", credentials.email).execute()
    data = handle_response(resp)

    if not data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = data[0]

    # Check hashed password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create tokens
    token_data = {"sub": str(user["user_id"]), "email": user["email"], "role": user["role"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }





def handle_response(resp):
    """Standardize error handling for supabase-py responses."""
    if getattr(resp, "error", None):
        raise HTTPException(status_code=400, detail=str(resp.error))
    return resp.data

def list_users_service(limit: int, offset: int):
    supabase = get_supabase()
    start = offset
    end = offset + limit - 1
    resp = supabase.table("User").select("*").range(start, end).execute()
    data = handle_response(resp)
    return data or []

def register_user_service(user: UserIn, role: str | None = None):
    supabase = get_supabase()
    hashed_pw = hash_password(user.password)

    user_role = role if role else user.role

    try:
        resp = supabase.table("User").insert({
            "email": user.email,
            "password": hashed_pw,
            "name": user.name,
            "nic": user.nic,
            "role": user_role
        }).execute()
    except APIError as e:
        if getattr(e, "code", None) == "23505":
            raise HTTPException(status_code=400, detail="Email already registered")
        raise HTTPException(status_code=400, detail=str(e))

    data = handle_response(resp)
    if not data:
        raise HTTPException(status_code=400, detail="Failed to register user")
    return data[0]



