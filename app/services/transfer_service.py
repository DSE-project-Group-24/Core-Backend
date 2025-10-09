from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException
from app.db import get_supabase

ACCIDENT_TABLE = "Accident Record"      # exact name with space
TRANSFER_TABLE = "Transfer"             # exact name
HOSPITAL_PATIENT_TABLE = "Hospital_Patient"
USER_TABLE = "User"
NURSE_TABLE = "Nurse"
ADMIN_TABLE = "Admin"


# ---------------------------
# Helpers
# ---------------------------

def _require_user(user: Dict[str, Any]) -> str:
    uid = user.get("sub") or user.get("user_id") or user.get("id")
    if not uid:
        raise HTTPException(status_code=403, detail="Invalid user.")
    return str(uid)


def _get_user_role_and_hospital(user_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (role, hospital_id) for the given user_id.
    Looks up Admin first (strict), then falls back to Nurse.
    Role is the value in the User table if present; otherwise inferred.
    """
    supabase = get_supabase()

    # Try Admin table
    admin_r = (
        supabase.table(ADMIN_TABLE)
        .select("user_id, hospital_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if admin_r.data and len(admin_r.data) > 0:
        # Role from User table if you keep it, else just 'admin'
        role_r = (
            supabase.table(USER_TABLE)
            .select("role")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        role = (role_r.data or {}).get("role") or "admin"
        return role, str(admin_r.data[0]["hospital_id"])

    # Fallback Nurse table
    nurse_r = (
        supabase.table(NURSE_TABLE)
        .select("user_id, hospital_id")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if nurse_r.data and len(nurse_r.data) > 0:
        role_r = (
            supabase.table(USER_TABLE)
            .select("role")
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        role = (role_r.data or {}).get("role") or "nurse"
        return role, str(nurse_r.data[0]["hospital_id"])

    # Not found in either
    role_r = (
        supabase.table(USER_TABLE)
        .select("role")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    role = (role_r.data or {}).get("role")
    return role, None


def _assert_accident_managed_by_user(accident_id: str, user_id: str) -> Dict[str, Any]:
    """
    Fetches the accident row and ensures it's currently managed by user_id.
    """
    supabase = get_supabase()
    r = (
        supabase.table(ACCIDENT_TABLE)
        .select("accident_id, managed_by")
        .eq("accident_id", accident_id)
        .single()
        .execute()
    )
    row = r.data
    if not row:
        raise HTTPException(status_code=404, detail="Accident record not found.")
    if str(row.get("managed_by")) != str(user_id):
        raise HTTPException(status_code=403, detail="You can only transfer records you manage.")
    return row


def _ensure_same_hospital(user_hospital_id: Optional[str], hospital_id: Optional[str], message: str) -> None:
    if not user_hospital_id or not hospital_id or str(user_hospital_id) != str(hospital_id):
        raise HTTPException(status_code=403, detail=message)


# ---------------------------
# Nurse: Create transfer request
# ---------------------------

def create_transfer_request_service(
    *,
    accident_id: str,
    to_hospital_id: str,
    user: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Nurse requests a transfer:
    - Must currently manage the accident
    - from_hospital is nurse's hospital
    - approved_by and "transfer time to second hospital" are NOT set here
    """
    supabase = get_supabase()
    user_id = _require_user(user)
    role, nurse_hospital_id = _get_user_role_and_hospital(user_id)

    if role != "nurse":
        raise HTTPException(status_code=403, detail="Only nurses can request transfers.")

    # Ensure the nurse manages the record being transferred
    _assert_accident_managed_by_user(accident_id, user_id)

    if not nurse_hospital_id:
        raise HTTPException(status_code=403, detail="Nurse hospital not found.")

    if str(to_hospital_id) == str(nurse_hospital_id):
        raise HTTPException(status_code=400, detail="Destination hospital must be different.")

    payload = {
        "accident_id": accident_id,
        "from_hospital": nurse_hospital_id,
        "to_hospital": to_hospital_id,
        # Do NOT set "approved_by"
        # Do NOT set "transfer time to second hospital"
        # You may add created_on if your table has it as a default
    }

    resp = supabase.table(TRANSFER_TABLE).insert(payload).execute()
    if not resp.data:
        # surface db error message if available
        msg = getattr(resp, "error", None)
        msg = getattr(msg, "message", None) if msg else "Failed to create transfer request."
        raise HTTPException(status_code=500, detail=msg)

    return resp.data[0]


# ---------------------------
# Lists
# ---------------------------

def list_my_outgoing_transfers_service(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    For a nurse: list transfers created from their hospital (outgoing).
    """
    supabase = get_supabase()
    user_id = _require_user(user)
    role, nurse_hospital_id = _get_user_role_and_hospital(user_id)

    if role != "nurse" or not nurse_hospital_id:
        return []

    r = (
        supabase.table(TRANSFER_TABLE)
        .select("*")
        .eq("from_hospital", nurse_hospital_id)
        .order("transfer_id", desc=True)
        .execute()
    )
    return r.data or []


def list_incoming_transfers_for_admin_service(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    For an admin: list pending transfers where to_hospital = admin's hospital and approved_by is NULL.
    """
    supabase = get_supabase()
    user_id = _require_user(user)
    role, admin_hospital_id = _get_user_role_and_hospital(user_id)

    if role != "admin" or not admin_hospital_id:
        return []

    r = (
        supabase.table(TRANSFER_TABLE)
        .select("*")
        .eq("to_hospital", admin_hospital_id)
        .is_("approved_by", None)
        .order("transfer_id", desc=True)
        .execute()
    )
    return r.data or []


# ---------------------------
# Admin: Approve / Reject (atomic via RPC)
# ---------------------------

def approve_transfer_service(
    *,
    transfer_id: str,
    new_nurse_user_id: str,
    transfer_time_category: str,
    user: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Admin approves a transfer atomically by calling the Postgres function:
      approve_transfer(p_transfer_id uuid, p_admin_id uuid, p_new_nurse_id uuid, p_transfer_time text)

    That function:
      1) Validates admin belongs to the destination hospital of the transfer
      2) Updates Accident Record.managed_by to the new nurse
      3) Writes approved_by and "transfer time to second hospital"
      4) Inserts row into Hospital_Patient (patient ↔ new hospital)

    Returns the updated Transfer row (optionally include expanded info in the SQL function).
    """
    supabase = get_supabase()
    admin_id = _require_user(user)
    role, admin_hospital_id = _get_user_role_and_hospital(admin_id)

    if role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve transfers.")

    # Optional: verify transfer belongs to this admin's hospital before RPC
    t = (
        supabase.table(TRANSFER_TABLE)
        .select("transfer_id, to_hospital, approved_by")
        .eq("transfer_id", transfer_id)
        .single()
        .execute()
    )
    tr = t.data
    if not tr:
        raise HTTPException(status_code=404, detail="Transfer not found.")
    if tr.get("approved_by") is not None:
        raise HTTPException(status_code=400, detail="Transfer already approved.")
    _ensure_same_hospital(admin_hospital_id, tr.get("to_hospital"), "You can only approve transfers to your hospital.")

    # --- Atomic call to Postgres function
    params = {
        "p_transfer_id": transfer_id,
        "p_admin_id": admin_id,
        "p_new_nurse_id": new_nurse_user_id,
        "p_transfer_time": transfer_time_category,
    }
    rpc = supabase.rpc("approve_transfer", params).execute()
    if getattr(rpc, "error", None):
        # supabase-py v2 gives error on the object; v1 sometimes only returns data=None
        detail = getattr(rpc.error, "message", "Approval failed.")
        raise HTTPException(status_code=500, detail=detail)

    if not rpc.data:
        # Some PostgREST setups return nothing from RPCs by default
        # Fall back to reloading the Transfer row
        refreshed = (
            supabase.table(TRANSFER_TABLE)
            .select("*")
            .eq("transfer_id", transfer_id)
            .single()
            .execute()
        )
        if not refreshed.data:
            raise HTTPException(status_code=500, detail="Approval succeeded but failed to load transfer.")
        return refreshed.data

    # If your SQL returns the updated transfer row, just return it
    return rpc.data


def reject_transfer_service(
    *,
    transfer_id: str,
    user: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Admin rejects a transfer:
      - Must belong to the destination hospital
      - Only allowed if still pending
      - Deletes the Transfer row (does NOT touch Accident Record or Hospital_Patient)
    """
    supabase = get_supabase()
    admin_id = _require_user(user)
    role, admin_hospital_id = _get_user_role_and_hospital(admin_id)

    if role != "admin" or not admin_hospital_id:
        raise HTTPException(status_code=403, detail="Only admins can reject transfers.")

    # Verify pending & belongs to admin hospital
    t = (
        supabase.table(TRANSFER_TABLE)
        .select("transfer_id, to_hospital, approved_by")
        .eq("transfer_id", transfer_id)
        .single()
        .execute()
    )
    tr = t.data
    if not tr:
        raise HTTPException(status_code=404, detail="Transfer not found.")
    if tr.get("approved_by") is not None:
        raise HTTPException(status_code=400, detail="Transfer already approved; cannot reject.")
    _ensure_same_hospital(admin_hospital_id, tr.get("to_hospital"), "You can only reject transfers to your hospital.")

    # Delete
    d = (
        supabase.table(TRANSFER_TABLE)
        .delete()
        .eq("transfer_id", transfer_id)
        .execute()
    )
    if getattr(d, "error", None):
        msg = getattr(d.error, "message", "Failed to reject (delete) transfer.")
        raise HTTPException(status_code=500, detail=msg)

    return {"ok": True, "transfer_id": transfer_id, "status": "rejected"}