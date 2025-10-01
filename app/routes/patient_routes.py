from fastapi import APIRouter, Depends, Path, Query
from app.models.patient import PatientCreate, PatientUpdate, PatientOut, PatientOutPatch
from app.services.patient_service import (
    create_patient_service,
    edit_patient_service,
    get_patient_by_id_service,
    get_hospital_patients_service
)
from app.auth.dependencies import get_current_user, nurse_required
from app.auth.hospital_dependency import get_user_hospital_id

router = APIRouter()

@router.post("/", response_model=PatientOut, dependencies=[Depends(nurse_required)])
async def create_patient(
    patient: PatientCreate,
    hospital_id: str = Depends(get_user_hospital_id)
):
    return create_patient_service(patient, hospital_id)

@router.patch("/{patient_id}", response_model=PatientOutPatch, dependencies=[Depends(get_current_user)])
def edit_patient(patient_id: str, patient: PatientUpdate):
    return edit_patient_service(patient_id, patient)

@router.get("/", response_model=list[PatientOut])
async def get_hospital_patients(hospital_id: str = Depends(get_user_hospital_id)):
    """Get patients associated with the current user's hospital"""
    return get_hospital_patients_service(hospital_id)

@router.get("/{patient_id}", response_model=PatientOut, dependencies=[Depends(get_current_user)])
def get_patient_by_id(patient_id: str = Path(..., description="Patient UUID")):
    return get_patient_by_id_service(patient_id)

# @router.get("")
# def search_patients(search: str = Query("", description="name or NIC or hospital id"),
#                     limit: int = Query(12, ge=1, le=50),
#                     user=Depends(get_current_user)):
#     supabase = get_supabase()

#     # Adjust table/columns to yours; example assumes a table Patient with columns id, name, nic, hospital_id
#     q = supabase.table("Patient").select("id,name,nic,hospital_id")

#     if search:
#         # simple OR filter using ilike on name/nic/hospital_id
#         # Supabase Python SDK: use filter chaining
#         # Workaround: use rpc or multiple queries if needed. Here, a naive approach:
#         name = supabase.table("Patient").select("id,name,nic,hospital_id").ilike("name", f"%{search}%").limit(limit).execute().data or []
#         nic  = supabase.table("Patient").select("id,name,nic,hospital_id").ilike("nic", f"%{search}%").limit(limit).execute().data or []
#         hid  = supabase.table("Patient").select("id,name,nic,hospital_id").ilike("hospital_id", f"%{search}%").limit(limit).execute().data or []
#         # merge unique by id preserving order
#         seen, merged = set(), []
#         for arr in (name, nic, hid):
#             for r in arr:
#                 if r["id"] not in seen:
#                     merged.append(r); seen.add(r["id"])
#         return merged[:limit]

#     return q.limit(limit).execute().data or []