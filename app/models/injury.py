
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID

#Side = Literal["Front","Back","Left","Right","N/A","Unknown"]
Severity = Literal["severe","moderate","unknown"]

class InjuryBase(BaseModel):
    site_of_injury: str = Field(..., min_length=1)
    type_of_injury: str = Field(..., min_length=1)
    side: Optional[str] = Field(None, alias="side")  #Side
    investigation_done: Optional[str] = Field(None, alias="investigation_done")

class InjuryIn(InjuryBase):
    # if not provided, backend will assign the next injury_no
    injury_no: Optional[int] = None

class InjuryUpdate(BaseModel):
    site_of_injury:   Optional[str] = None
    type_of_injury: Optional[str] = None
    side: Optional[str] = Field(None, alias="side")  #Side
    investigation_done: Optional[str] = Field(None, alias="investigation_done")

class InjuryOut(InjuryBase):
    accident_id: UUID
    injury_no: int
    severity: Severity

    class Config:
        populate_by_name = True

class BulkInjuries(BaseModel):
    items: List[InjuryIn]