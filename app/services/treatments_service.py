# app/services/treatments_service.py
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.db import get_supabase

TABLE = "Treatment"  # exact table name

# --------- helpers ---------
def _db_or_500(resp, msg="Database error"):
    # Supabase client sometimes lacks `.error` attr in certain versions
    if resp is None or getattr(resp, "data", None) is None:
        err = getattr(resp, "error", None)
        detail = getattr(err, "message", None) if err else None
        raise HTTPException(status_code=500, detail=detail or msg)
    return resp.data

def _get_current_nurse_hospital_id(user) -> str:
    supabase = get_supabase()
    user_id = (user.get("sub") or user.get("user_id") or user.get("id"))
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid user")

    nurse = (
        supabase.table("Nurse")
        .select("hospital_id")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    data = _db_or_500(nurse, "Failed to read nurse record")
    hid = data.get("hospital_id")
    if not hid:
        raise HTTPException(status_code=400, detail="Nurse has no hospital_id")
    return str(hid)

def _next_treatment_no(accident_id: str) -> int:
    supabase = get_supabase()
    r = (
        supabase.table(TABLE)
        .select("treatment_no")
        .eq("accident_id", accident_id)
        .order("treatment_no", desc=True)
        .limit(1)
        .execute()
    )
    # If no rows yet, return 1
    if r and r.data is not None and len(r.data) > 0:
        try:
            return int(r.data[0]["treatment_no"]) + 1
        except Exception:
            return 1
    return 1

# --------- CRUD ---------
def list_treatments(accident_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    r = (
        supabase.table(TABLE)
        .select("*")
        .eq("accident_id", accident_id)
        .order("treatment_no")
        .execute()
    )
    return _db_or_500(r, "Failed to list treatments")

def create_treatment(accident_id: str, payload: Dict[str, Any], user) -> Dict[str, Any]:
    supabase = get_supabase()
    # Server-side set hospital_id
    hospital_id = _get_current_nurse_hospital_id(user)

    no = payload.get("treatment_no") or _next_treatment_no(accident_id)
    row = {
        "accident_id": accident_id,
        "treatment_no": int(no),
        "treatment_type": payload.get("treatment_type"),
        "description": payload.get("description"),
        "hospital_id": hospital_id,  # FORCE current nurse hospital
        "ward_number": payload.get("ward_number"),
        "number_of_days_stay": payload.get("number_of_days_stay"),
        "reason": payload.get("reason"),
    }
    r = supabase.table(TABLE).insert(row).execute()
    data = _db_or_500(r, "Failed to create treatment")
    if not data:
        raise HTTPException(status_code=500, detail="Create returned no data")
    return data[0]

def update_treatment(accident_id: str, treatment_no: int, payload: Dict[str, Any], user) -> Dict[str, Any]:
    supabase = get_supabase()
    # Read existing to enforce hospital guard and to preserve hospital_id
    cur = (
        supabase.table(TABLE)
        .select("*")
        .eq("accident_id", accident_id)
        .eq("treatment_no", treatment_no)
        .single()
        .execute()
    )
    current = _db_or_500(cur, "Treatment not found")
    if not current:
        raise HTTPException(status_code=404, detail="Treatment not found")

    # Optional: enforce same-hospital rule for edits (backend safety)
    my_hid = _get_current_nurse_hospital_id(user)
    if str(current.get("hospital_id")) != str(my_hid):
        raise HTTPException(status_code=403, detail="Cannot edit treatment from another hospital")

    # Never overwrite hospital_id on update
    updates = {
        "treatment_type": payload.get("treatment_type", current.get("treatment_type")),
        "description": payload.get("description", current.get("description")),
        "ward_number": payload.get("ward_number", current.get("ward_number")),
        "number_of_days_stay": payload.get("number_of_days_stay", current.get("number_of_days_stay")),
        "reason": payload.get("reason", current.get("reason")),
    }

    r = (
        supabase.table(TABLE)
        .update(updates)
        .eq("accident_id", accident_id)
        .eq("treatment_no", treatment_no)
        .execute()
    )
    data = _db_or_500(r, "Failed to update treatment")
    return data[0]

def delete_treatment(accident_id: str, treatment_no: int, user) -> None:
    supabase = get_supabase()
    # read row to enforce hospital rule
    cur = (
        supabase.table(TABLE)
        .select("hospital_id")
        .eq("accident_id", accident_id)
        .eq("treatment_no", treatment_no)
        .single()
        .execute()
    )
    current = _db_or_500(cur, "Treatment not found")
    my_hid = _get_current_nurse_hospital_id(user)
    if str(current.get("hospital_id")) != str(my_hid):
        raise HTTPException(status_code=403, detail="Cannot delete treatment from another hospital")

    r = (
        supabase.table(TABLE)
        .delete()
        .eq("accident_id", accident_id)
        .eq("treatment_no", treatment_no)
        .execute()
    )
    _db_or_500(r, "Failed to delete treatment")

# --------- bulk upsert (used by accident create/edit) ---------
def bulk_upsert(accident_id: str, items: List[Dict[str, Any]], user) -> List[Dict[str, Any]]:
    """
    Upsert treatments by composite key (accident_id, treatment_no).
    - New rows: assign treatment_no if missing and FORCE hospital_id = current nurse hospital.
    - Existing rows: keep original hospital_id (do not overwrite), and block update
      if the row belongs to a different hospital.
    """
    supabase = get_supabase()
    my_hid = _get_current_nurse_hospital_id(user)

    # Fetch existing rows for accident
    existing_resp = (
        supabase.table(TABLE)
        .select("treatment_no,hospital_id")
        .eq("accident_id", accident_id)
        .execute()
    )
    existing_rows = _db_or_500(existing_resp, "Failed to read existing treatments")
    existing_index = {int(row["treatment_no"]): str(row.get("hospital_id")) for row in existing_rows}

    next_no = _next_treatment_no(accident_id)

    rows = []
    for it in items or []:
        no = it.get("treatment_no")
        if not no:
            no = next_no
            next_no += 1
        print("days stay:", it.get("number_of_days_stay"))
        no = int(no)
        if no in existing_index:
            # Editing existing: keep original hospital_id and enforce same hospital
            original_hid = existing_index[no]
            
            rows.append({
                "accident_id": accident_id,
                "treatment_no": no,
                "treatment_type": it.get("treatment_type"),
                "description": it.get("description"),
                "ward_number": it.get("ward_number"),
                "number_of_days_stay": it.get("number_of_days_stay"),
                "reason": it.get("reason"),
                "hospital_id": original_hid,  # preserve original
            })
        else:
            # New: set hospital_id = current nurse hospital
            rows.append({
                "accident_id": accident_id,
                "treatment_no": no,
                "treatment_type": it.get("treatment_type"),
                "description": it.get("description"),
                "hospital_id": my_hid,  # enforce
                "ward_number": it.get("ward_number"),
                "number_of_days_stay": it.get("number_of_days_stay"),
                "reason": it.get("reason"),
            })

    if not rows:
        return []

    # Upsert on composite key
    r = supabase.table(TABLE).upsert(rows, on_conflict="accident_id,treatment_no").execute()
    return _db_or_500(r, "Failed to upsert treatments")