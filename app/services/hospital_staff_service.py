from fastapi import HTTPException
from app.db import get_supabase
from app.models.hospital_staff import AssignStaffToHospital

def get_doctors_count_service(hospital_id: str):
    """
    Get count of all doctors in a specific hospital
    """
    supabase = get_supabase()
    try:
        resp = supabase.table("Doctor").select("*", count="exact").eq("hospital_id", hospital_id).execute()
        count = resp.count if hasattr(resp, 'count') else len(resp.data)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting doctors count: {str(e)}")

def get_nurses_count_service(hospital_id: str):
    """
    Get count of all nurses in a specific hospital
    """
    supabase = get_supabase()
    try:
        resp = supabase.table("Nurse").select("*", count="exact").eq("hospital_id", hospital_id).execute()
        count = resp.count if hasattr(resp, 'count') else len(resp.data)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting nurses count: {str(e)}")


def get_patients_count_service(hospital_id: str):
    """
    Get count of all patients in a specific hospital
    """
    supabase = get_supabase()
    try:
        resp = supabase.table("Hospital_Patient").select("*", count="exact").eq("hospital_id", hospital_id).execute()
        count = resp.count if hasattr(resp, 'count') else len(resp.data)
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patients count: {str(e)}")



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
