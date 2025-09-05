from fastapi import APIRouter, Depends, Path
from app.models.medical import (
    TreatmentCreate, TreatmentUpdate, TreatmentOut,
    TransferCreate, TransferUpdate, TransferOut,
    InjuryCreate, InjuryUpdate, InjuryOut,
    ManagementCreate, ManagementUpdate, ManagementOut
)
from app.services.medical_service import (
    # Treatment services
    create_treatment_service, edit_treatment_service, 
    get_all_treatments_service, get_treatment_by_id_service, get_treatments_by_accident_service,
    # Transfer services
    create_transfer_service, edit_transfer_service,
    get_all_transfers_service, get_transfer_by_id_service, get_transfers_by_accident_service,
    # Injury services
    create_injury_service, edit_injury_service,
    get_all_injuries_service, get_injury_by_id_service, get_injuries_by_accident_service,
    # Management services
    create_management_service, edit_management_service,
    get_all_managements_service, get_management_by_id_service, get_managements_by_accident_service
)
from app.auth.dependencies import get_current_user
from app.auth.hospital_dependency import get_user_hospital_id

router = APIRouter()

# Treatment routes
@router.post("/treatments", response_model=TreatmentOut)
async def create_treatment(
    treatment: TreatmentCreate, 
    hospital_id: str = Depends(get_user_hospital_id)
):
    return create_treatment_service(treatment, hospital_id)

@router.patch("/treatments/{treatment_id}", response_model=TreatmentOut, dependencies=[Depends(get_current_user)])
def edit_treatment(treatment_id: str, treatment: TreatmentUpdate):
    return edit_treatment_service(treatment_id, treatment)


# Get all treatments for a specific accident
@router.get("/treatments/accident/{accident_id}", response_model=list[TreatmentOut], dependencies=[Depends(get_current_user)])
def get_treatments_by_accident(accident_id: str = Path(..., description="Accident Record UUID")):
    return get_treatments_by_accident_service(accident_id)

@router.get("/treatments/{treatment_id}", response_model=TreatmentOut, dependencies=[Depends(get_current_user)])
def get_treatment_by_id(treatment_id: str = Path(..., description="Treatment UUID")):
    return get_treatment_by_id_service(treatment_id)




# Transfer routes
@router.post("/transfers", response_model=TransferOut, dependencies=[Depends(get_current_user)])
def create_transfer(transfer: TransferCreate):
    return create_transfer_service(transfer)


@router.patch("/transfers/{transfer_id}", response_model=TransferOut, dependencies=[Depends(get_current_user)])
def edit_transfer(transfer_id: str, transfer: TransferUpdate):
    return edit_transfer_service(transfer_id, transfer)

@router.get("/transfers", response_model=list[TransferOut], dependencies=[Depends(get_current_user)])
def get_all_transfers():
    return get_all_transfers_service()

@router.get("/transfers/{transfer_id}", response_model=TransferOut, dependencies=[Depends(get_current_user)])
def get_transfer_by_id(transfer_id: str = Path(..., description="Transfer UUID")):
    return get_transfer_by_id_service(transfer_id)

@router.get("/transfers/accident/{accident_id}", response_model=list[TransferOut], dependencies=[Depends(get_current_user)])
def get_transfers_by_accident(accident_id: str = Path(..., description="Accident Record UUID")):
    return get_transfers_by_accident_service(accident_id)



# Injury routes
@router.post("/injuries", response_model=InjuryOut, dependencies=[Depends(get_current_user)])
def create_injury(injury: InjuryCreate):
    return create_injury_service(injury)

@router.patch("/injuries/{injury_no}", response_model=InjuryOut, dependencies=[Depends(get_current_user)])
def edit_injury(injury_no: str, injury: InjuryUpdate):
    return edit_injury_service(injury_no, injury)

@router.get("/injuries", response_model=list[InjuryOut], dependencies=[Depends(get_current_user)])
def get_all_injuries():
    return get_all_injuries_service()

@router.get("/injuries/{injury_no}", response_model=InjuryOut, dependencies=[Depends(get_current_user)])
def get_injury_by_id(injury_no: str = Path(..., description="Injury UUID")):
    return get_injury_by_id_service(injury_no)

@router.get("/injuries/accident/{accident_id}", response_model=list[InjuryOut], dependencies=[Depends(get_current_user)])
def get_injuries_by_accident(accident_id: str = Path(..., description="Accident Record UUID")):
    return get_injuries_by_accident_service(accident_id)

# Management routes
@router.post("/managements", response_model=ManagementOut, dependencies=[Depends(get_current_user)])
def create_management(management: ManagementCreate):
    return create_management_service(management)

@router.patch("/managements/{management_id}", response_model=ManagementOut, dependencies=[Depends(get_current_user)])
def edit_management(management_id: str, management: ManagementUpdate):
    return edit_management_service(management_id, management)

@router.get("/managements", response_model=list[ManagementOut], dependencies=[Depends(get_current_user)])
def get_all_managements():
    return get_all_managements_service()

@router.get("/managements/{management_id}", response_model=ManagementOut, dependencies=[Depends(get_current_user)])
def get_management_by_id(management_id: str = Path(..., description="Management UUID")):
    return get_management_by_id_service(management_id)

@router.get("/managements/accident/{accident_id}", response_model=list[ManagementOut], dependencies=[Depends(get_current_user)])
def get_managements_by_accident(accident_id: str = Path(..., description="Accident Record UUID")):
    return get_managements_by_accident_service(accident_id)
