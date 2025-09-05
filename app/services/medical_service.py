from fastapi import HTTPException
from app.db import get_supabase
from app.models.medical import (
    TreatmentCreate, TreatmentUpdate,
    TransferCreate, TransferUpdate,
    InjuryCreate, InjuryUpdate,
    ManagementCreate, ManagementUpdate
)
from app.utils.serializers import serialize_payload

# Treatment Services
def create_treatment_service(treatment: TreatmentCreate, hospital_id: str):
    supabase = get_supabase()
    payload = treatment.dict(by_alias=True)
    payload["hospital_id"] = hospital_id
    
    # Verify the hospital exists
    hospital_resp = supabase.table("Hospital").select("hospital_id").eq("hospital_id", hospital_id).single().execute()
    if not hospital_resp.data:
        raise HTTPException(status_code=404, detail="Hospital not found.")
        
    resp = supabase.table("Treatment").insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create treatment.")
    
    treatment_data = resp.data[0]
    # Make sure treatment_id is explicitly included in the response
    treatment_id = treatment_data.get("treatment_id")
    if treatment_id:
        treatment_data["message"] = f"Treatment created successfully with ID: {treatment_id}"
    
    return treatment_data

def edit_treatment_service(treatment_id: str, treatment: TreatmentUpdate):
    supabase = get_supabase()
    payload = treatment.dict(exclude_unset=True, by_alias=True)
    resp = supabase.table("Treatment").update(payload).eq("treatment_id", treatment_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Treatment not found or not updated.")
    return resp.data[0]

def get_all_treatments_service():
    supabase = get_supabase()
    resp = supabase.table("Treatment").select("*").execute()
    return resp.data or []

def get_treatment_by_id_service(treatment_id: str):
    supabase = get_supabase()
    resp = supabase.table("Treatment").select("*").eq("treatment_id", treatment_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Treatment not found.")
    return resp.data

def get_treatments_by_accident_service(accident_id: str):
    supabase = get_supabase()
    resp = supabase.table("Treatment").select("*").eq("accident_id", accident_id).execute()
    return resp.data or []



# Transfer Services
def create_transfer_service(transfer: TransferCreate):
    supabase = get_supabase()
    
    # Use serialize_payload to handle Decimal values
    payload = serialize_payload(transfer)
    
    resp = supabase.table("Transfer").insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create transfer.")
    
    transfer_data = resp.data[0]
    transfer_id = transfer_data.get("transfer_id")
    if transfer_id:
        transfer_data["message"] = f"Transfer created successfully with ID: {transfer_id}"
    
    return transfer_data

def edit_transfer_service(transfer_id: str, transfer: TransferUpdate):
    supabase = get_supabase()
    
    # Use serialize_payload to handle Decimal values
    payload = serialize_payload(transfer)
    
    resp = supabase.table("Transfer").update(payload).eq("transfer_id", transfer_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Transfer not found or not updated.")
    return resp.data[0]

def get_all_transfers_service():
    supabase = get_supabase()
    resp = supabase.table("Transfer").select("*").execute()
    return resp.data or []

def get_transfer_by_id_service(transfer_id: str):
    supabase = get_supabase()
    resp = supabase.table("Transfer").select("*").eq("transfer_id", transfer_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Transfer not found.")
    return resp.data

def get_transfers_by_accident_service(accident_id: str):
    supabase = get_supabase()
    resp = supabase.table("Transfer").select("*").eq("accident_id", accident_id).execute()
    return resp.data or []



# Injury Services
def create_injury_service(injury: InjuryCreate):
    supabase = get_supabase()
    payload = injury.dict(by_alias=True)
    resp = supabase.table("Injury").insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create injury record.")
    return resp.data[0]

def edit_injury_service(injury_no: str, injury: InjuryUpdate):
    supabase = get_supabase()
    payload = injury.dict(exclude_unset=True, by_alias=True)
    resp = supabase.table("Injury").update(payload).eq("injury_no", injury_no).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Injury record not found or not updated.")
    return resp.data[0]

def get_all_injuries_service():
    supabase = get_supabase()
    resp = supabase.table("Injury").select("*").execute()
    return resp.data or []

def get_injury_by_id_service(injury_no: str):
    supabase = get_supabase()
    resp = supabase.table("Injury").select("*").eq("injury_no", injury_no).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Injury record not found.")
    return resp.data

def get_injuries_by_accident_service(accident_id: str):
    supabase = get_supabase()
    resp = supabase.table("Injury").select("*").eq("accident_id", accident_id).execute()
    return resp.data or []





# Management Services
def create_management_service(management: ManagementCreate):
    supabase = get_supabase()
    payload = management.dict(by_alias=True)
    resp = supabase.table("managemeny").insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create management record.")
    return resp.data[0]

def edit_management_service(management_id: str, management: ManagementUpdate):
    supabase = get_supabase()
    payload = management.dict(exclude_unset=True, by_alias=True)
    resp = supabase.table("managemeny").update(payload).eq("management_id", management_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Management record not found or not updated.")
    return resp.data[0]

def get_all_managements_service():
    supabase = get_supabase()
    resp = supabase.table("managemeny").select("*").execute()
    return resp.data or []

def get_management_by_id_service(management_id: str):
    supabase = get_supabase()
    resp = supabase.table("managemeny").select("*").eq("management_id", management_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Management record not found.")
    return resp.data

def get_managements_by_accident_service(accident_id: str):
    supabase = get_supabase()
    resp = supabase.table("managemeny").select("*").eq("accident_id", accident_id).execute()
    return resp.data or []
