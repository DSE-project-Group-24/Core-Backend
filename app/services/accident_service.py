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

def _get_value(obj, *keys, default=None):
    """Small helper to safely get a value from dict or object by several keys/attrs."""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj[k] is not None:
                return obj[k]
    else:
        for k in keys:
            v = getattr(obj, k, None)
            if v is not None:
                return v
    return default

def get_accident_records_by_patient_service(patient_id: str, user):
    supabase = get_supabase()

    # 1) Identify current user and role
    current_user_id = user.get("sub")
    if not current_user_id:
        # If your auth guarantees this, you can raise 403 instead.
        current_user_id = None

    current_user_row = None
    current_role = None
    current_nurse_hospital_id = None

    if current_user_id:
        user_resp = supabase.table("User") \
            .select("user_id, role") \
            .eq("user_id", current_user_id) \
            .single() \
            .execute()
        current_user_row = user_resp.data
        current_role = (current_user_row or {}).get("role")

        # If current user is a nurse, fetch their hospital_id from Nurse table
        if current_role == "nurse":
            nurse_resp = supabase.table("Nurse") \
                .select("user_id, hospital_id") \
                .eq("user_id", current_user_id) \
                .single() \
                .execute()
            if nurse_resp.data:
                current_nurse_hospital_id = nurse_resp.data.get("hospital_id")

    # 2) Get records for patient
    resp = supabase.table(TABLE) \
        .select("*") \
        .eq("patient_id", patient_id) \
        .order("created_on", desc=True) \
        .execute()
    records = resp.data or []
    if not records:
        return []

    # 3) Collect all distinct manager user_ids
    managed_ids = list({rec.get("managed_by") for rec in records if rec.get("managed_by")})
    for rec in records:
        print("Managed by:", rec.get("managed_by"))
    if not managed_ids:
        # Nothing to enrich
        return records

    # 4) Fetch managers' user records (user_id -> name)
    users_resp = supabase.table("User") \
        .select("user_id, name") \
        .in_("user_id", managed_ids) \
        .execute()
    users = {u["user_id"]: u.get("name") for u in (users_resp.data or [])}

    # 5) Fetch managers' nurse records (user_id -> hospital_id)
    nurses_resp = supabase.table("Nurse") \
        .select("user_id, hospital_id") \
        .in_("user_id", managed_ids) \
        .execute()
    manager_user_to_hospital = {n["user_id"]: n.get("hospital_id") for n in (nurses_resp.data or [])}

    # 6) Fetch hospitals for all manager hospital_ids (hospital_id -> name)
    manager_hospital_ids = list({hid for hid in manager_user_to_hospital.values() if hid})
    hospitals = {}
    if manager_hospital_ids:
        hospitals_resp = supabase.table("Hospital") \
            .select("hospital_id, name") \
            .in_("hospital_id", manager_hospital_ids) \
            .execute()
        hospitals = {h["hospital_id"]: h.get("name") for h in (hospitals_resp.data or [])}

    # 7) Attach managed_by_name based on rule:
    #    If current user is nurse AND manager's hospital_id != current nurse's hospital_id:
    #        managed_by_name = that manager's Hospital.name
    #    Else:
    #        managed_by_name = manager's User.name
    for rec in records:
        manager_id = rec.get("managed_by")
        manager_name = users.get(manager_id)
        manager_hospital_id = manager_user_to_hospital.get(manager_id)

        if current_role == "nurse" and current_nurse_hospital_id and manager_hospital_id:
            if str(manager_hospital_id) != str(current_nurse_hospital_id):
                # cross-hospital → show hospital name
                rec["managed_by_name"] = hospitals.get(manager_hospital_id) or manager_name
            else:
                # same hospital → show user (manager) name
                rec["managed_by_name"] = manager_name
        else:
            # if not a nurse (or unknown hospital), keep original behavior
            rec["managed_by_name"] = manager_name
    for rec in records:
        print("Managed by 2:", rec.get("managed_by"))
    return records