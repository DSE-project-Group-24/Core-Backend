# app/models/patient.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

class PatientBase(BaseModel):
    # Required
    full_name: str = Field(..., alias="Full Name")
    gender: str = Field(..., alias="Gender")

    # Optional
    contact_number: Optional[str] = Field(None, alias="Contact Number")
    date_of_birth: Optional[date] = Field(None, alias="Date of Birth")
    ethnicity: Optional[str] = Field(None, alias="Ethnicity")              # <-- fixed
    nic: Optional[str] = Field(None, alias="NIC")
    address_street: Optional[str] = Field(None, alias="Address Street")
    life_style: Optional[str] = Field(None, alias="Life Style")
    education_qualification: Optional[str] = Field(None, alias="Education Qualification")
    occupation: Optional[str] = Field(None, alias="Occupation")
    family_monthly_income: Optional[str] = Field(None, alias="Family Monthly Income")
    blood_group: Optional[str] = Field(None, alias="Blood Group")
    registered_date: Optional[date] = Field(None, alias="Registered Date")  # <-- added

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, alias="Full Name")
    gender: Optional[str] = Field(None, alias="Gender")
    contact_number: Optional[str] = Field(None, alias="Contact Number")
    date_of_birth: Optional[date] = Field(None, alias="Date of Birth")
    ethnicity: Optional[str] = Field(None, alias="Ethnicity")
    nic: Optional[str] = Field(None, alias="NIC")
    address_street: Optional[str] = Field(None, alias="Address Street")
    life_style: Optional[str] = Field(None, alias="Life Style")
    education_qualification: Optional[str] = Field(None, alias="Education Qualification")
    occupation: Optional[str] = Field(None, alias="Occupation")
    family_monthly_income: Optional[str] = Field(None, alias="Family Monthly Income")
    blood_group: Optional[str] = Field(None, alias="Blood Group")
    registered_date: Optional[date] = Field(None, alias="Registered Date")

class PatientOut(PatientBase):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)
    patient_id: str
    hospital_id: str = Field(..., alias="Hospital ID")