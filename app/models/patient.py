from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

class PatientBase(BaseModel):
    full_name: str = Field(..., alias="Full Name")
    contact_number: Optional[str] = Field(None, alias="Contact Number")
    date_of_birth: Optional[date] = Field(None, alias="Date of Birth")
    ethinicity: Optional[str] = Field(None, alias="Ethnicity")
    gender: str = Field(..., alias="Gender")
    nic: Optional[str] = Field(None, alias="NIC")
    address_street: Optional[str] = Field(None, alias="Address Street")
    life_style: Optional[str] = Field(None, alias="Life Style")
    education_qualification: Optional[str] = Field(None, alias="Education Qualification")
    occupation: Optional[str] = Field(None, alias="Occupation")
    employment_type_name: Optional[str] = Field(None, alias="Employment Type Name")
    family_monthly_income: Optional[str] = Field(None, alias="Family Monthly Income")
    blood_group: Optional[str] = Field(None, alias="Blood Group")

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, alias="Full Name")
    contact_number: Optional[str] = Field(None, alias="Contact Number")
    date_of_birth: Optional[date] = Field(None, alias="Date of Birth")
    ethinicity: Optional[str] = Field(None, alias="Ethnicity")
    gender: Optional[str] = Field(None, alias="Gender")
    address_street: Optional[str] = Field(None, alias="Address Street")
    life_style: Optional[str] = Field(None, alias="Life Style")
    education_qualification: Optional[str] = Field(None, alias="Education Qualification")
    occupation: Optional[str] = Field(None, alias="Occupation")
    employment_type_name: Optional[str] = Field(None, alias="Employment Type Name")
    family_monthly_income: Optional[str] = Field(None, alias="Family Monthly Income")
    blood_group: Optional[str] = Field(None, alias="Blood Group")

class PatientOut(PatientBase):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True
    )
    
    patient_id: str
    hospital_id: str = Field(..., alias="Hospital ID")
