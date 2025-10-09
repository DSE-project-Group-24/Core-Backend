# app/schemas/transfer.py
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

TransferStatus = Literal["pending", "approved", "rejected", "cancelled"]

class TransferBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)
    accident_id: str
    to_hospital: str
    note: Optional[str] = None

class TransferCreate(TransferBase):
    pass

class TransferOut(BaseModel):
    transfer_id: str
    accident_id: str
    from_hospital: str
    to_hospital: str
    requested_by: str
    approved_by: Optional[str] = None
    transfer_time_to_second_hospital: Optional[str] = None
    status: TransferStatus = "pending"
    created_at: Optional[str] = None
    decided_at: Optional[str] = None

class TransferApprove(BaseModel):
    new_managed_by: str  # nurse user_id in the destination hospital
    transfer_time_to_second_hospital: str  # categorical

class TransferReject(BaseModel):
    reason: Optional[str] = None  # optional, if you want to store

class TransferCreateIn(BaseModel):
    accident_id: str = Field(..., description="Accident being transferred")
    to_hospital_id: str = Field(..., description="Destination hospital")


class TransferApproveIn(BaseModel):
    new_nurse_user_id: str = Field(..., description="Nurse (user_id) who will manage the record after approval")
    transfer_time_category: str = Field(
        ...,
        description="Categorical text (e.g., '<15 min', '15–30 min', '30–60 min', etc.)"
    )