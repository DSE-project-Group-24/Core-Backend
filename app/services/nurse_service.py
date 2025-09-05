from fastapi import HTTPException
from app.db import get_supabase

# Service: Get all nurses
def get_all_nurses_service():
    supabase = get_supabase()
    resp = supabase.table("User").select("user_id, role, nic, name, email").eq("role", "nurse").execute()
    return resp.data or []


# Service: Get nurse by id
def get_nurse_by_id_service(nurse_id: str):
    supabase = get_supabase()
    try:
        resp = supabase.table("User").select("user_id, role, nic, name, email").eq("id", nurse_id).single().execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Nurse not found.")
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid nurse ID: {str(e)}")
    

# Service: Get nurse by name
def get_nurse_by_name_service(name: str):
    supabase = get_supabase()
    resp = supabase.table("User").select("user_id, role, nic, name, email").eq("name", name).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Nurse not found.")
    return resp.data


# Service: Get nurse by nic
def get_nurse_by_nic_service(nic: str):
    supabase = get_supabase()
    resp = supabase.table("User").select("user_id, role, nic, name, email").eq("nic", nic).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Nurse not found.")
    return resp.data