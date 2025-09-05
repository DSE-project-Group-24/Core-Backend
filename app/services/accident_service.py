from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.db import get_supabase
from app.models.accident import AccidentRecordCreate, AccidentRecordUpdate

def create_accident_record_service(accident: AccidentRecordCreate):
    supabase = get_supabase()
    payload = jsonable_encoder(accident, by_alias=True)

    # Remove keys with None so DB defaults apply
    payload = {k: v for k, v in payload.items() if v is not None}

    resp = supabase.table("Accident Record").insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create accident record.")
    return jsonable_encoder(resp.data[0])

def edit_accident_record_service(accident_id: str, accident: AccidentRecordUpdate):
    supabase = get_supabase()
    payload = accident.dict(exclude_unset=True, by_alias=True)
    resp = supabase.table("Accident Record").update(payload).eq("accident_id", accident_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Accident record not found or not updated.")
    return resp.data[0]

def get_all_accident_records_service():
    supabase = get_supabase()
    resp = supabase.table("Accident Record").select("*").execute()
    return resp.data or []

def get_accident_record_by_id_service(accident_id: str):
    supabase = get_supabase()
    resp = supabase.table("Accident Record").select("*").eq("accident_id", accident_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Accident record not found.")
    return resp.data

def get_accident_records_by_patient_service(patient_id: str):
    supabase = get_supabase()
    resp = supabase.table("Accident Record").select("*").eq("patient_id", patient_id).execute()
    return resp.data or []
