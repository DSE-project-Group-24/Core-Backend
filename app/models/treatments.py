# app/schemas/treatments.py
from typing import Optional, List
from pydantic import BaseModel, Field

class TreatmentBase(BaseModel):
    treatment_no: Optional[int] = Field(None, description="Sequential number within accident")
    treatment_type: Optional[str] = None
    description: Optional[str] = None
    ward_number: Optional[str] = None
    number_of_days_stay: Optional[int] = None
    reason: Optional[str] = None
    # hospital_id is server-controlled; exclude from create/update payloads

class TreatmentCreate(TreatmentBase):
    pass

TreatmentIn = TreatmentCreate
class TreatmentUpdate(TreatmentBase):
    pass

class TreatmentOut(TreatmentBase):
    accident_id: str
    hospital_id: Optional[str] = None
    hospital_name: Optional[str] = None

class TreatmentBulk(BaseModel):
    items: List[TreatmentBase]