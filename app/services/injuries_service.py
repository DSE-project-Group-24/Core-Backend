# app/services/injuries_service.py
from fastapi import HTTPException
from typing import List, Dict, Any, Literal
from app.db import get_supabase
import joblib
import os
import pandas as pd


try:
    # supabase-py -> postgrest exceptions live here
    from postgrest.exceptions import APIError as PostgrestAPIError
except Exception:  # fallback if import path differs
    PostgrestAPIError = Exception

Severity = Literal["severe", "moderate", "unknown"]

# Make sure this matches your actual table *exactly*.
# You previously said "Injuries". If the real table is Injuries, set TABLE = "Injuries".
TABLE = "Injury"

# Column with a space must be quoted in selects/updates
INVESTIGATION_COL = '"investigation_done"'

_model_cache = None

def _load_model():
    """Load and cache the severity prediction model."""
    global _model_cache
    if _model_cache is None:
        model_path = os.path.join(
            os.path.dirname(__file__),  # directory of this service file
            "..",  "..",                     # go up 2 levels
            "trained_models",
            "injury_severity_simple_model-7.pkl",
        )
        model_path = os.path.abspath(model_path)
        try:
            _model_cache = joblib.load(model_path)
            print(f"✅ Loaded severity model from: {model_path}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model load failed: {e}")
    return _model_cache
_load_model()

def infer_severity(site_of_injury: str, type_of_injury: str) -> Severity:
    """
    Predict severity using the trained sklearn model that expects:
        DataFrame with columns ["Site of Injury No1", "Type of injury No 1"]
    Returns 'severe', 'moderate', or 'unknown'.
    """
    try:
        model = _load_model()

        # Build DataFrame exactly as used during training
        X = pd.DataFrame([{
            "Site of Injury No1": site_of_injury,
            "Type of injury No 1": type_of_injury,
        }])

        # Predict (model outputs ndarray)
        y_pred = model.predict(X)
        if y_pred is not None and len(y_pred) > 0:
            pred = y_pred[0]
            if pred == "S":
                return "severe"
            elif pred == "M":
                return "moderate"
            else:
                return "unknown"

    except Exception as e:
        print(f"[infer_severity] ML inference failed, falling back. err={e}")

    return "unknown"

def _next_injury_no(accident_id: str) -> int:
    supabase = get_supabase()
    try:
        r = (
            supabase.table(TABLE)
            .select("injury_no")
            .eq("accident_id", accident_id)
            .order("injury_no", desc=True)
            .limit(1)
            .execute()
        )
    except PostgrestAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))

    rows = r.data or []
    if not rows:
        return 1
    return int(rows[0]["injury_no"]) + 1

def list_injuries(accident_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    try:
        r = (
            supabase.table(TABLE)
            .select(f'accident_id, injury_no, site_of_injury, type_of_injury, side, {INVESTIGATION_COL}, severity')
            .eq("accident_id", accident_id)
            .order("injury_no")
            .execute()
        )
    except PostgrestAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))

    rows = r.data or []
    # normalize alias for frontend convenience
    for row in rows:
        row["investigation_done"] = row.get("investigation_done") or row.get("investigation_done")
    return rows

def create_injury(accident_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    supabase = get_supabase()
    try:
        injury_no = payload.get("injury_no") or _next_injury_no(accident_id)
        sev = infer_severity(payload["site_of_injury"], payload["type_of_injury"])

        # Build row. Use dict with quoted key for the spaced column.
        row = {
            "accident_id": accident_id,
            "injury_no": injury_no,
            "site_of_injury": payload["site_of_injury"],
            "type_of_injury": payload["type_of_injury"],
            "side": payload["side"],
            # supabase-py accepts { '"investigation_done"': value } for spaced cols
            "severity": sev,
        }
        if payload.get("investigation_done") is not None:
            row["investigation_done"] = payload.get("investigation_done")

        r = supabase.table(TABLE).insert(row).execute()
        data = r.data or []
        if not data:
            # If the lib raised no exception but returned empty, treat as server error.
            raise HTTPException(status_code=500, detail="Insert failed (no data returned).")
        return data[0]
    except PostgrestAPIError as e:
        # Unique violation, etc. will land here
        msg = str(e)
        # Best-effort duplicate detection
        if "duplicate" in msg.lower() or "unique" in msg.lower():
            raise HTTPException(status_code=409, detail="Injury number already exists for this accident.")
        raise HTTPException(status_code=500, detail=msg)

def update_injury(accident_id: str, injury_no: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    supabase = get_supabase()
    try:
        cur = (
            supabase.table(TABLE)
            .select(f'accident_id, injury_no, site_of_injury, type_of_injury, side, {INVESTIGATION_COL}, severity')
            .eq("accident_id", accident_id)
            .eq("injury_no", injury_no)
            .single()
            .execute()
        )
        if not cur.data:
            raise HTTPException(status_code=404, detail="Injury not found.")

        new_site = payload.get("site_of_injury", cur.data["site_of_injury"])
        new_type = payload.get("type_of_injury", cur.data["type_of_injury"])
        severity = cur.data.get("severity")

        if ("site_of_injury" in payload) or ("type_of_injury" in payload):
            severity = infer_severity(new_site, new_type)

        updates: Dict[str, Any] = {
            "site_of_injury": new_site,
            "type_of_injury": new_type,
            "side": payload.get("side", cur.data["side"]),
            "severity": severity,
        }
        # Only include investigation_done if provided; otherwise keep as-is
        if "investigation_done" in payload:
            updates["investigation_done"] = payload.get("investigation_done")

        r = (
            supabase.table(TABLE)
            .update(updates)
            .eq("accident_id", accident_id)
            .eq("injury_no", injury_no)
            .execute()
        )
        data = r.data or []
        if not data:
            raise HTTPException(status_code=500, detail="Update failed (no data returned).")
        return data[0]
    except PostgrestAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))

def delete_injury(accident_id: str, injury_no: int) -> None:
    supabase = get_supabase()  # <- fixed
    try:
        r = (
            supabase.table(TABLE)
            .delete()
            .eq("accident_id", accident_id)
            .eq("injury_no", injury_no)
            .execute()
        )
        # Some Supabase setups return [] on successful delete; treat as OK.
        # If you want to ensure something was deleted, you can check r.count with return= 'representation'
        # but default delete doesn’t return count.
        return
    except PostgrestAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))

def bulk_upsert(accident_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    supabase = get_supabase()
    try:
        rows = []
        current_next = _next_injury_no(accident_id)
        for it in items or []:
            no = it.get("injury_no")
            if not no:
                no = current_next
                current_next += 1
            sev = infer_severity(it["site_of_injury"], it["type_of_injury"])
            row = {
                "accident_id": accident_id,
                "injury_no": no,
                "site_of_injury": it["site_of_injury"],
                "type_of_injury": it["type_of_injury"],
                "side": it["side"],
                "severity": sev,
            }
            if it.get("investigation_done") is not None:
                row["investigation_done"] = it.get("investigation_done")
            rows.append(row)

        # upsert on composite key
        r = (
            supabase.table(TABLE)
            .upsert(rows, on_conflict="accident_id,injury_no")
            .execute()
        )
        data = r.data or []
        return data
    except PostgrestAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))