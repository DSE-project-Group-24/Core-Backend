from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

# Treatment Model
class TreatmentBase(BaseModel):
    accident_id: str
    treatment_type: Optional[str] = None
    description: Optional[str] = None
    ward_number: Optional[int] = None
    number_of_days_stay: Optional[int] = None
    reason: Optional[str] = None
    hospital_distance: Optional[int] = Field(None, alias="hospital distance from home")

class TreatmentCreate(TreatmentBase):
    pass

class TreatmentUpdate(TreatmentBase):
    accident_id: Optional[str] = None

class TreatmentOut(TreatmentBase):
    treatment_id: str
    hospital_id: str
    
    class Config:
        from_attributes = True
        validate_by_name = True

# Transfer Model
class TransferBase(BaseModel):
    accident_id: str
    from_hospital: str
    to_hospital: str
    transfer_time: Optional[Decimal] = Field(None, alias="transfer time to second hospital")
    first_aid_given: Optional[bool] = Field(None, alias="First Aid given At Seen")

class TransferCreate(TransferBase):
    pass

class TransferUpdate(TransferBase):
    accident_id: Optional[str] = None
    from_hospital: Optional[str] = None
    to_hospital: Optional[str] = None

class TransferOut(TransferBase):
    transfer_id: str
    
    class Config:
        from_attributes = True
        validate_by_name = True

# Injury Model
class InjuryBase(BaseModel):
    accident_id: str
    site_of_injury: Optional[str] = None
    type_of_injury: Optional[str] = None
    side: Optional[str] = None
    investigation_done: Optional[str] = Field(None, alias="Investigation Done")

class InjuryCreate(InjuryBase):
    pass

class InjuryUpdate(InjuryBase):
    accident_id: Optional[str] = None

class InjuryOut(InjuryBase):
    injury_no: str
    
    class Config:
        from_attributes = True
        validate_by_name = True

# Management Model (using "managemeny" as in schema)
class ManagementBase(BaseModel):
    accident_id: str
    type: Optional[str] = None

class ManagementCreate(ManagementBase):
    pass

class ManagementUpdate(ManagementBase):
    accident_id: Optional[str] = None

class ManagementOut(ManagementBase):
    management_id: str
    
    class Config:
        from_attributes = True
        validate_by_name = True
