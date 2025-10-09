from pydantic import BaseModel, ConfigDict
from typing import Optional

class HospitalCreate(BaseModel):
    name: str
    Type: str
    address: str
    city: str
    contact_number: str
    Region: str

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    Type: Optional[str] = None
    model_config = ConfigDict(
        # This allows using the model for partial updates
        extra="forbid"  # Prevent extra fields from being accepted
    )
    
    address: Optional[str] = None
    city: Optional[str] = None
    contact_number: Optional[str] = None
    Region: Optional[str] = None


class Hospital(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    hospital_id: str
    name: str
    Type: str
    address: Optional[str] = None
    city: Optional[str] = None
    contact_number: Optional[str] = None
    Region: Optional[str] = None