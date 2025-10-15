from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.db import get_supabase
from app.models.accident import AccidentRecordCreate, AccidentRecordUpdate
from typing import Dict, Any, List, Set
from app.services.injuries_service import (
    bulk_upsert as injuries_bulk_upsert,
    list_injuries as injuries_list,
    delete_injury as injuries_delete,
)
from app.services.treatments_service import (
    bulk_upsert as treatments_bulk_upsert,
    delete_treatment as treatments_delete,
    list_treatments as treatments_list,
)
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
    print("before payload")
    payload = jsonable_encoder(accident, by_alias=True)
    print("after payload")
    payload = _strip_none(payload)
    print("after strip none")
    # Force manager = current user; ignore client value for security
    user_id = user.get("sub")
    print(user.get("sub"))
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid user")
    payload["managed_by"] = user_id

    payload = _empty_strings_to_unknown(payload)

    # Pull out child collections (optional)
    injuries = payload.pop("injuries", None)
    treatments = payload.pop("treatments", None)

    # Create the base accident record (let DB defaults fill Created_on/Completed/Severity)
    resp = supabase.table(TABLE).insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create accident record.")
    rec = resp.data[0]
    accident_id = rec.get("accident_id")

    try:
        # Upsert injuries if provided
        if injuries:
            print("got here")
            injuries_bulk_upsert(
                accident_id,
                [i | {"accident_id": accident_id} for i in injuries]
            )
            rec["injuries"] = injuries_list(accident_id)
        else:
            rec["injuries"] = []
        #print("Treatments:")
        #print(treatments)
        # Upsert treatments if provided (hospital_id forced in service using current user)
        if treatments:
            treatments_bulk_upsert(
                accident_id,
                [t | {"accident_id": accident_id} for t in treatments],
                user,
            )
            rec["treatments"] = treatments_list(accident_id)
        else:
            rec["treatments"] = []

        return rec

    except Exception as e:
        # BEST-EFFORT rollback (no transactions in JS client): delete child rows then accident
        try:
            supabase.table("Injury").delete().eq("accident_id", accident_id).execute()
        except Exception:
            pass
        try:
            supabase.table("Treatment").delete().eq("accident_id", accident_id).execute()
        except Exception:
            pass
        supabase.table("Accident Record").delete().eq("accident_id", accident_id).execute()
        raise



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

    # 2) Build payload; split out injuries & treatments
    payload: Dict[str, Any] = accident.model_dump(
        mode="json", by_alias=True, exclude_unset=True
    )

    incoming_injuries = payload.pop("injuries", None)
    incoming_treatments = payload.pop("treatments", None)

    for forbidden in ("patient_id", "managed_by"):
        payload.pop(forbidden, None)

    payload = _empty_strings_to_unknown(payload)

    # 3) Update the accident record if needed
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

    # 4) Injuries (full replacement if provided)
    #print("Incoming injuries:")
    #print(incoming_injuries)
    if incoming_injuries != []:
        #print("huh")
        norm_items: List[Dict[str, Any]] = []
        incoming_numbers: Set[int] = set()

        for it in (incoming_injuries or []):
            item = {
                "injury_no": it.get("injury_no"),
                "site_of_injury": (it.get("site_of_injury") or "").strip(),
                "type_of_injury": (it.get("type_of_injury") or "").strip(),
                "side": (it.get("side") or "").strip(),
                "investigation_done": (it.get("investigation_done") or "").strip(),
            }
            if item["injury_no"]:
                try:
                    incoming_numbers.add(int(item["injury_no"]))
                except Exception:
                    pass
            norm_items.append(item)

        injuries_bulk_upsert(accident_id, norm_items)

        existing_rows = injuries_list(accident_id)
        existing_numbers = {int(r.get("injury_no")) for r in existing_rows if r.get("injury_no") is not None}

        if len(incoming_numbers) > 0:
            to_delete = existing_numbers - incoming_numbers
            for no in sorted(to_delete):
                injuries_delete(accident_id, int(no))

        rec["injuries"] = injuries_list(accident_id)

    #print("Incoming treatments:")
    #print(incoming_treatments)
    # 5) Treatments (full replacement if provided)
    if incoming_treatments != []:
        # Normalize payload; DO NOT include/allow hospital_id from client
        norm_items: List[Dict[str, Any]] = []
        incoming_numbers: Set[int] = set()

        for it in (incoming_treatments or []):
            item = {
                "treatment_no": it.get("treatment_no"),
                "treatment_type": (it.get("treatment_type") or "").strip(),
                "description": (it.get("description") or "").strip(),
                "ward_number": it.get("ward_number"),
                "number_of_days_stay": it.get("number_of_days_stay"),
                "reason": (it.get("reason") or "").strip(),
                # hospital_id is enforced server-side on create and preserved on update
            }
            if item["treatment_no"]:
                try:
                    incoming_numbers.add(int(item["treatment_no"]))
                except Exception:
                    pass
            norm_items.append(item)
        #print("before upsert:")
        #print(norm_items)
        # Upsert using backend rule (create -> force current hospital; update -> preserve/guard)
        treatments_bulk_upsert(accident_id, norm_items, user)
        #print("after upsert")
        # Diff-delete (mirror injuries logic)
        existing_rows = treatments_list(accident_id)
        existing_numbers = {int(r.get("treatment_no")) for r in existing_rows if r.get("treatment_no") is not None}

        if len(incoming_numbers) > 0:
            to_delete = existing_numbers - incoming_numbers
            for no in sorted(to_delete):
                # Will raise 403 in service if other-hospital; that’s desired
                treatments_delete(accident_id, int(no), user)

        rec["treatments"] = treatments_list(accident_id)

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
    INJURIES_TABLE = "Injury"
    TREATMENTS_TABLE = "Treatment"

    # ---- existing user/role/hospital lookup (unchanged) ----
    current_user_id = user.get("sub")
    if not current_user_id:
        current_user_id = None

    current_user_row = None
    current_role = None
    current_nurse_hospital_id = None

    if current_user_id:
        user_resp = (
            supabase.table("User")
            .select("user_id, role")
            .eq("user_id", current_user_id)
            .single()
            .execute()
        )
        current_user_row = user_resp.data
        current_role = (current_user_row or {}).get("role")

        if current_role == "nurse":
            nurse_resp = (
                supabase.table("Nurse")
                .select("user_id, hospital_id")
                .eq("user_id", current_user_id)
                .single()
                .execute()
            )
            if nurse_resp.data:
                current_nurse_hospital_id = nurse_resp.data.get("hospital_id")

    # ---- fetch accident records ----
    resp = (
        supabase.table(TABLE)
        .select("*")
        .eq("patient_id", patient_id)
        .order("created_on", desc=True)
        .execute()
    )
    records = resp.data or []
    if not records:
        return []

    # prefill children arrays
    for rec in records:
        rec["injuries"] = []
        rec["treatments"] = []

    # ---- fetch all injuries in one call ----
    accident_ids = [r.get("accident_id") for r in records if r.get("accident_id")]
    if accident_ids:
        inj_resp = (
            supabase.table(INJURIES_TABLE)
            .select("accident_id, injury_no, site_of_injury, type_of_injury, side, investigation_done, severity, investigation_done")
            .in_("accident_id", accident_ids)
            .order("injury_no", desc=False)
            .execute()
        )
        injuries = inj_resp.data or []

        by_acc_inj = {}
        for row in injuries:
            aid = row.get("accident_id")
            by_acc_inj.setdefault(aid, []).append(row)

        for rec in records:
            aid = rec.get("accident_id")
            if aid in by_acc_inj:
                rec["injuries"] = by_acc_inj[aid]

    # ---- fetch all treatments in one call ----
    if accident_ids:
        tr_resp = (
            supabase.table(TREATMENTS_TABLE)
            .select(
                """
                accident_id,
                treatment_no,
                treatment_type,
                description,
                hospital_id,
                ward_number,
                number_of_days_stay,
                reason,
                Hospital(name)         -- 👈 pull related hospital name
                """
            )
            .in_("accident_id", accident_ids)
            .order("treatment_no", desc=False)
            .execute()
        )
        treatments = tr_resp.data or []

        # Flatten Hospital(name) → hospital_name for the frontend
        for row in treatments:
            row["hospital_name"] = (row.get("Hospital") or {}).get("name")
            row.pop("Hospital", None)

        by_acc_tr = {}
        for row in treatments:
            aid = row.get("accident_id")
            by_acc_tr.setdefault(aid, []).append(row)

        for rec in records:
            aid = rec.get("accident_id")
            if aid in by_acc_tr:
                rec["treatments"] = by_acc_tr[aid]

    # ---- existing managed_by_name enrichment (unchanged) ----
    managed_ids = list({rec.get("managed_by") for rec in records if rec.get("managed_by")})
    if not managed_ids:
        return records

    users_resp = (
        supabase.table("User")
        .select("user_id, name")
        .in_("user_id", managed_ids)
        .execute()
    )
    users = {u["user_id"]: u.get("name") for u in (users_resp.data or [])}

    nurses_resp = (
        supabase.table("Nurse")
        .select("user_id, hospital_id")
        .in_("user_id", managed_ids)
        .execute()
    )
    manager_user_to_hospital = {n["user_id"]: n.get("hospital_id") for n in (nurses_resp.data or [])}

    manager_hospital_ids = list({hid for hid in manager_user_to_hospital.values() if hid})
    hospitals = {}
    if manager_hospital_ids:
        hospitals_resp = (
            supabase.table("Hospital")
            .select("hospital_id, name")
            .in_("hospital_id", manager_hospital_ids)
            .execute()
        )
        hospitals = {h["hospital_id"]: h.get("name") for h in (hospitals_resp.data or [])}

    for rec in records:
        manager_id = rec.get("managed_by")
        manager_name = users.get(manager_id)
        manager_hospital_id = manager_user_to_hospital.get(manager_id)

        if current_role == "nurse" and current_nurse_hospital_id and manager_hospital_id:
            if str(manager_hospital_id) != str(current_nurse_hospital_id):
                rec["managed_by_name"] = hospitals.get(manager_hospital_id) or manager_name
            else:
                rec["managed_by_name"] = manager_name
        else:
            rec["managed_by_name"] = manager_name

    return records