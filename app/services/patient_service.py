from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.db import get_supabase
from app.models.patient import PatientCreate, PatientUpdate

def create_patient_service(patient: PatientCreate, hospital_id: str):
    supabase = get_supabase()

    if not hospital_id:
        raise HTTPException(status_code=400, detail="Hospital ID is required to create a patient.")

    # Create patient
    payload = jsonable_encoder(patient, by_alias=True)
    resp = supabase.table("Patient").insert(payload).execute()

    if not resp.data:
        raise HTTPException(status_code=500, detail="Failed to create patient.")

    patient_id = resp.data[0]["patient_id"]

    try:
        # Check if hospital exists
        hospital_resp = (
            supabase.table("Hospital")
            .select("hospital_id")
            .eq("hospital_id", hospital_id)
            .single()
            .execute()
        )
        if not hospital_resp.data:
            # rollback patient
            supabase.table("Patient").delete().eq("patient_id", patient_id).execute()
            raise HTTPException(status_code=404, detail="Hospital not found.")

        # Add patient to hospital
        hp_resp = (
            supabase.table("Hospital_Patient")
            .insert({"patient_id": patient_id, "hospital_id": hospital_id})
            .execute()
        )

        if not hp_resp.data:
            # rollback patient
            supabase.table("Patient").delete().eq("patient_id", patient_id).execute()
            raise HTTPException(status_code=500, detail="Failed to associate patient with hospital.")

    except Exception as e:
        # rollback patient
        supabase.table("Patient").delete().eq("patient_id", patient_id).execute()
        raise HTTPException(status_code=500, detail=f"Failed to associate patient with hospital: {str(e)}")

    patient_data = resp.data[0]
    patient_data["Hospital ID"] = hospital_id
    return patient_data


def edit_patient_service(patient_id: str, patient: PatientUpdate):
    supabase = get_supabase()
    payload = jsonable_encoder(patient, by_alias=True, exclude_unset=True)
    print(patient_id)
    update_resp = supabase.table("Patient").update(payload).eq("patient_id", patient_id).execute()
    if not update_resp.data:
        raise HTTPException(status_code=404, detail="Patient not found or not updated.")

    # Fetch full patient
    resp = supabase.table("Patient").select("*").eq("patient_id", patient_id).single().execute()
    patient_row = resp.data
    if not patient_row:
        raise HTTPException(status_code=404, detail="Patient not found.")

    return patient_row

# def get_all_patients_service():
#     supabase = get_supabase()
#     resp = supabase.table("Patient").select("*").execute()
#     return resp.data or []

def get_hospital_patients_service(hospital_id: str):
    supabase = get_supabase()

    # Query Hospital_Patient table to get patient IDs associated with the hospital
    resp = (
        supabase.table("Hospital_Patient")
        .select("patient_id")
        .eq("hospital_id", hospital_id)
        .execute()
    )

    if not resp.data:
        return []

    # Extract patient IDs
    patient_ids = [item["patient_id"] for item in resp.data]

    # Get patient details for these IDs
    patients_resp = (
        supabase.table("Patient")
        .select("*")
        .in_("patient_id", patient_ids)
        .execute()
    )

    patients = patients_resp.data or []

    # 🔥 Add hospital_id to every patient dict
    for p in patients:
        p["Hospital ID"] = hospital_id

    return patients


def get_patient_by_id_service(patient_id: str):
    supabase = get_supabase()
    resp = supabase.table("Patient").select("*").eq("patient_id", patient_id).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Patient not found.")
    return resp.data


def get_patient_by_nic_service(nic: str):
    supabase = get_supabase()
    resp = supabase.table("Patient").select("*").eq("nic", nic).single().execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Patient not found.")
    return resp.data