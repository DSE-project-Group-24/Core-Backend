from fastapi import HTTPException
from app.db import get_supabase
from app.models.hospital_staff import AssignStaffToHospital

def add_doctor_to_hospital_service(data: AssignStaffToHospital):
    supabase = get_supabase()
    # Check if already assigned
    exists = supabase.table("Doctor").select("*").eq("user_id", data.user_id).eq("hospital_id", data.hospital_id).execute()
    if exists.data:
        raise HTTPException(status_code=400, detail="Doctor already assigned to this hospital.")
    resp = supabase.table("Doctor").insert({
        "user_id": data.user_id,
        "hospital_id": data.hospital_id
    }).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to assign doctor.")
    return {"message": "Doctor assigned successfully."}

def add_nurse_to_hospital_service(data: AssignStaffToHospital):
    supabase = get_supabase()
    # Check if already assigned
    exists = supabase.table("Nurse").select("*").eq("user_id", data.user_id).eq("hospital_id", data.hospital_id).execute()
    if exists.data:
        raise HTTPException(status_code=400, detail="Nurse already assigned to this hospital.")
    resp = supabase.table("Nurse").insert({
        "user_id": data.user_id,
        "hospital_id": data.hospital_id
    }).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to assign nurse.")
    return {"message": "Nurse assigned successfully."}
