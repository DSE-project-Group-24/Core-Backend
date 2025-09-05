from pydantic import BaseModel
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
    address: Optional[str] = None
    city: Optional[str] = None
    contact_number: Optional[str] = None
    Region: Optional[str] = None

    class Config:
        # This allows using the model for partial updates
        extra = "forbid"  # Prevent extra fields from being accepted