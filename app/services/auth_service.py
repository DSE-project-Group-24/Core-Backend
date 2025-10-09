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
    
    flag = False
    # Check role-specific tables for hosputal information
    try:
        if user["role"] not in ["government_personnel"]:
            STAFF_TABLE = ""
            flag = True
            if user["role"] in ["nurse"]:
                STAFF_TABLE = "Nurse"
            elif user["role"] in ["doctor"]:
                STAFF_TABLE = "Doctor"
            elif user["role"] in ["hospital_administrator"]:
                STAFF_TABLE = "Hospital_Administrator"
            resp = (
                supabase.table(STAFF_TABLE)
                .select("hospital_id, Hospital(name)")   # join to Hospital via FK
                .eq("user_id", user["user_id"])
                .single()
                .execute()
            )
            data = handle_response(resp)
            if not data:
                raise HTTPException(status_code=401, detail="You are not assigned to any hospital. Please contact an Administrator.")
    except APIError as e:
        raise HTTPException(status_code=401, detail="You are not assigned to any hospital. Please contact an Administrator.")
    # Create tokens
    token_data = {"sub": str(user["user_id"]), "email": user["email"], "role": user["role"], "name": user["name"]   }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    if flag:
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user["user_id"],
            "name": user["name"],
            "role": user["role"],
            "hospital_id": data.get("hospital_id"),
            "hospital_name":(data.get("Hospital") or {}).get("name")
        }
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user["user_id"],
        "name": user["name"],
        "role": user["role"]
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



