from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.db import get_supabase
from app.models.accident import AccidentRecordCreate, AccidentRecordUpdate
from .injuries_service import bulk_upsert as injuries_bulk_upsert, list_injuries as injuries_list

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
    #print("Payload:", payload)
    payload = _strip_none(payload)

    # Force manager = current user; ignore client value for security
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid user")
    payload["managed_by"] = user_id

    payload = _empty_strings_to_unknown(payload)

    injuries = payload.pop("injuries", None)
    print("Injuries:", injuries)
    # Let DB defaults set Severity='U', Completed=false, created_on
    resp = supabase.table(TABLE).insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create accident record.")
    print("Resp:", resp.data[0])
    accident_id = resp.data[0].get("accident_id")

    if injuries:
        try:
            injuries_bulk_upsert(accident_id, [i | {"accident_id": accident_id} for i in injuries])
        except Exception as e:
            #Rollback by deleting the accident record we just created
            supabase.table("Accident Record").delete().eq("accident_id", accident_id).execute()
            raise
        resp.data[0]["injuries"] = injuries_list(accident_id)
    return resp.data[0]

# app/services/accidents_service.py (or wherever this lives)
from fastapi import HTTPException
from typing import Dict, Any, List, Set
from app.db import get_supabase
from app.services.injuries_service import (
    bulk_upsert as injuries_bulk_upsert,
    list_injuries as injuries_list,
    delete_injury as injuries_delete,
)
# ... import your models and _empty_strings_to_unknown as you already do ...

TABLE = "Accident Record"  # your existing constant

def edit_accident_record_service(accident_id: str, accident: AccidentRecordUpdate, user):
    supabase = get_supabase()

    # 1) Fetch existing + permission checks (unchanged)
    existing = (
        supabase.table(TABLE)
        .select("*")
        .eq("accident_id", accident_id)
        .single()
        .execute()
    )
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

    # 2) Build payload from model, split out injuries
    payload: Dict[str, Any] = accident.model_dump(
        mode="json", by_alias=True, exclude_unset=True
    )

    incoming_injuries = payload.pop("injuries", None)  # <-- take injuries out
    for forbidden in ("patient_id", "managed_by"):
        payload.pop(forbidden, None)

    payload = _empty_strings_to_unknown(payload)

    # 3) Update the accident record if there is anything to update
    if payload:
        resp = (
            supabase.table(TABLE)
            .update(payload)
            .eq("accident_id", accident_id)
            .execute()
        )
        if not resp.data:
            raise HTTPException(status_code=404, detail="Accident record not updated.")
        rec = resp.data[0]  # updated base record

    # 4) If injuries were provided, sync the Injury table to match
    if incoming_injuries is not None:
        # Normalize incoming items -> keys expected by injuries_bulk_upsert
        norm_items: List[Dict[str, Any]] = []
        incoming_numbers: Set[int] = set()

        for it in incoming_injuries or []:
            item = {
                "injury_no": it.get("injury_no"),  # may be None; bulk_upsert assigns
                "site_of_injury": (it.get("site_of_injury") or "").strip(),
                "type_of_injury": (it.get("type_of_injury") or "").strip(),
                "side": (it.get("side") or "").strip(),
                "investigation_done": (it.get("investigation_done") or "").strip(),
                # severity is auto inside bulk_upsert via infer_severity
            }
            # Keep numbers you were given, used for deletion-diff below
            if item["injury_no"]:
                try:
                    incoming_numbers.add(int(item["injury_no"]))
                except Exception:
                    pass
            norm_items.append(item)

        # Upsert all provided injuries (create/update + compute severity)
        upserted = injuries_bulk_upsert(accident_id, norm_items)

        # Delete injuries that exist in DB but are NOT in the incoming set of numbers
        # (only if client is doing "full replacement"). Since you sent `injuries`
        # explicitly, we treat it as the source of truth.
        existing_rows = injuries_list(accident_id)
        existing_numbers = {int(r.get("injury_no")) for r in existing_rows if r.get("injury_no") is not None}

        # If client didn't provide any injury_no (all None), we can't diff safely.
        # But your frontend sends sequential injury_no, so this path is fine:
        if len(incoming_numbers) > 0:
            to_delete = existing_numbers - incoming_numbers
            for no in sorted(to_delete):
                injuries_delete(accident_id, int(no))

        # Attach normalized injuries to result (so caller gets fresh list)
        rec["injuries"] = injuries_list(accident_id)

    else:
        # If not provided, keep existing injuries as-is (optional: attach them)
        # rec["injuries"] = injuries_list(accident_id)  # uncomment if you want to always return injuries
        pass

    return rec

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
    INJURIES_TABLE = "Injury"  # exact table name with spaces

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
    
    # ---- NEW: prefill empty injuries list so the shape is consistent
    for rec in records:
        rec["injuries"] = []

    # ---- NEW: fetch all injuries for those accidents in a single call
    accident_ids = [r.get("accident_id") for r in records if r.get("accident_id")]
    if accident_ids:
        inj_resp = (
            supabase.table(INJURIES_TABLE)
            .select("accident_id, injury_no, site_of_injury, type_of_injury, side, investigation_done, severity")
            .in_("accident_id", accident_ids)
            .order("injury_no", desc=False)
            .execute()
        )
        injuries = inj_resp.data or []

        # group by accident_id
        by_acc = {}
        for row in injuries:
            aid = row.get("accident_id")
            by_acc.setdefault(aid, []).append(row)

        # attach to matching records
        for rec in records:
            aid = rec.get("accident_id")
            if aid in by_acc:
                rec["injuries"] = by_acc[aid]

    # 3) Collect all distinct manager user_ids
    managed_ids = list({rec.get("managed_by") for rec in records if rec.get("managed_by")})
    #for rec in records:
        #print("Managed by:", rec.get("managed_by"))
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
    # for rec in records:
    #     print("Managed by 2:", rec.get("managed_by"))
    # print("Records with injuries:")
    # for rec in records:
    #     print(rec.get("injuries"))
    # print("records:")
    # print(records)
    return records