from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.db import get_supabase
from app.models.accident import AccidentRecordCreate, AccidentRecordUpdate

TABLE = "Accident Record"  # exact table name with spaces

def _strip_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}

def _empty_strings_to_unknown(d: dict) -> dict:
    """
    Convert empty strings to None so the DB stores NULL instead of "".
    Works for both insert and update payloads.
    """
    out = {}
    for k, v in d.items():
        if isinstance(v, str) and v.strip() == "":
            out[k] = "Unknown"
        else:
            out[k] = v
    return out


def create_accident_record_service(accident: AccidentRecordCreate, user):
    supabase = get_supabase()

    payload = jsonable_encoder(accident, by_alias=True)
    print("Payload:", payload)
    payload = _strip_none(payload)

    # Force manager = current user; ignore client value for security
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid user")
    payload["managed_by"] = user_id

    payload = _empty_strings_to_unknown(payload)

    # Let DB defaults set Severity='U', Completed=false, created_on
    resp = supabase.table(TABLE).insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create accident record.")
    return resp.data[0]

def edit_accident_record_service(accident_id: str, accident: AccidentRecordUpdate, user):
    supabase = get_supabase()

    # Fetch record and check permissions
    existing = supabase.table(TABLE).select("*").eq("accident_id", accident_id).single().execute()
    rec = existing.data
    if not rec:
        raise HTTPException(status_code=404, detail="Accident record not found.")

    user_id = (user.get("sub") or user.get("user_id") or user.get("id"))
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid user")

    if rec.get("Completed"):
        raise HTTPException(status_code=403, detail="Completed records cannot be edited.")
    if str(rec.get("managed_by")) != str(user_id):
        raise HTTPException(status_code=403, detail="You are not allowed to edit this record.")

    # Build payload with JSON-safe values and DB aliases (spaces)
    # Either use model_dump(..., mode="json") OR jsonable_encoder(...)
    payload = accident.model_dump(mode="json", by_alias=True, exclude_unset=True)
    # If you prefer the encoder:
    # payload = jsonable_encoder(accident, by_alias=True, exclude_unset=True)

    # Prevent changing ownership/patient
    for forbidden in ("patient_id", "managed_by"):
        payload.pop(forbidden, None)

    # Normalize empty strings -> unknown
    payload = _empty_strings_to_unknown(payload)

    if not payload:
        return rec

    resp = supabase.table(TABLE).update(payload).eq("accident_id", accident_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Accident record not updated.")
    return resp.data[0]

def get_all_accident_records_service():
    supabase = get_supabase()
    resp = supabase.table(TABLE).select("*").execute()
    return resp.data or []

def get_accident_record_by_id_service(accident_id: str):
    supabase = get_supabase()
    resp = supabase.table(TABLE).select("*").eq("accident_id", accident_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Accident record not found.")
    return resp.data

def get_accident_records_by_patient_service(patient_id: str):
    supabase = get_supabase()
    resp = supabase.table(TABLE).select("*").eq("patient_id", patient_id).order("created_on", desc=True).execute()
    return resp.data or []