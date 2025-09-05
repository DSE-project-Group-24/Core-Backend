from pydantic import BaseModel

class AssignStaffToHospital(BaseModel):
    user_id: str  # UUID of the user (doctor or nurse)
    hospital_id: str  # UUID of the hospital
