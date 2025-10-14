from app.models.hospital import HospitalCreate, HospitalUpdate
from fastapi import HTTPException
from app.db import get_supabase
from app.models.hospital import Hospital
from typing import List, Optional

# Service: Create hospital
def create_hospital_service(hospital: HospitalCreate):
    supabase = get_supabase()
    resp = supabase.table("Hospital").select("*").eq("name", hospital.name).eq("city", hospital.city).execute()
    if resp.data:
        raise HTTPException(status_code=400, detail="Hospital already exists in this city.")
    insert_resp = supabase.table("Hospital").insert({
        "name": hospital.name,
        "Type": hospital.Type,
        "address": hospital.address,
        "city": hospital.city,
        "contact_number": hospital.contact_number,
        "Region": hospital.Region
    }).execute()
    if not insert_resp.data:
        raise HTTPException(status_code=500, detail="Failed to create hospital.")
    return {"message": "Hospital created successfully.", "hospital_id": insert_resp.data[0]["hospital_id"]}

# Service: Get all hospitals
def get_all_hospitals_service():
    supabase = get_supabase()
    resp = supabase.table("Hospital").select("*").execute()
    return resp.data or []

def list_hospitals ():
    supabase = get_supabase()
    resp = supabase.table("Hospital").select("hospital_id, name").execute()
    return resp.data or []

# Service: Get hospital by id
def get_hospital_by_id_service(hospital_id: str):
    supabase = get_supabase()
    try:
        # Ensure proper UUID handling
        resp = supabase.table("Hospital").select("*").eq("hospital_id", hospital_id).single().execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Hospital not found.")
        return resp.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid hospital ID: {str(e)}")
# Service: Get hospital by name
def get_hospital_by_name_service(name: str):
    supabase = get_supabase()
    resp = supabase.table("Hospital").select("*").eq("name", name).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Hospital not found.")
    return resp.data

# Service: Edit hospital
def edit_hospital_service(hospital_id: str, hospital: HospitalUpdate):
    supabase = get_supabase()
    
    # Convert Pydantic model to dict, excluding unset (None) values
    update_data = hospital.dict(exclude_unset=True)
    
    # Check if there's anything to update
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update.")
    
    # First check if hospital exists
    check_resp = supabase.table("Hospital").select("hospital_id").eq("hospital_id", hospital_id).execute()
    if not check_resp.data:
        raise HTTPException(status_code=404, detail="Hospital not found.")
    
    # Then update
    resp = supabase.table("Hospital").update(update_data).eq("hospital_id", hospital_id).execute()
    
    if not resp.data:
        raise HTTPException(status_code=400, detail="No fields were updated.")
        
    return {"message": "Hospital updated successfully.", "hospital_id": hospital_id}

def get_all_hospitals() -> List[Hospital]:
    supabase = get_supabase()
    result = supabase.table('Hospital').select('*').execute()
    return [Hospital.model_validate(h) for h in result.data]

def search_hospitals_by_name(name: str) -> List[Hospital]:
    supabase = get_supabase()
    result = supabase.table('Hospital').select('*').ilike('name', f'%{name}%').execute()
    return [Hospital.model_validate(h) for h in result.data]