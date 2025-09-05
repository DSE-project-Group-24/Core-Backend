from fastapi import HTTPException
from app.db import get_supabase

# Service: Get all doctors
def get_all_doctors_service():
    supabase = get_supabase()
    resp = supabase.table("User").select("user_id, role, nic, name, email").eq("role", "doctor").execute()
    return resp.data or []


# Service: Get doctor by id
def get_doctor_by_id_service(doctor_id: str):
    supabase = get_supabase()
    try:
        resp = supabase.table("User").select("user_id, role, nic, name, email").eq("id", doctor_id).single().execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Doctor not found.")
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid doctor ID: {str(e)}")

# Service: Get doctor by name
def get_doctor_by_name_service(name: str):
    supabase = get_supabase()
    resp = supabase.table("User").select("user_id, role, nic, name, email").eq("name", name).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    return resp.data


# Service: Get doctor by nic
def get_doctor_by_nic_service(nic: str):
    supabase = get_supabase()
    resp = supabase.table("User").select("user_id, role, nic, name, email").eq("nic", nic).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    return resp.data