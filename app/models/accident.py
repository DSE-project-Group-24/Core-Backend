from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

# Pydantic v2 models

class AccidentRecordBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, validate_by_name=True)
    patient_id: str

    # DB column is managed_by (no space). You renamed to "managed_by" in DB – good.
    created_by: Optional[str] = Field(None, alias="managed_by")

    incident_at_date: Optional[date] = Field(None, alias="incident at date")
    time_of_collision: Optional[str] = Field(None, alias="time of collision")
    mode_of_traveling: Optional[str] = Field(None, alias="Mode of traveling during accident")
    visibility: Optional[str] = Field(None, alias="Visibility")
    collision_force_from: Optional[str] = Field(None, alias="Collision force from")
    collision_with: Optional[str] = Field(None, alias="Collision with")
    road_condition: Optional[str] = Field(None, alias="Road Condition")
    road_type: Optional[str] = Field(None, alias="Road Type")
    category_of_road: Optional[str] = Field(None, alias="Category of Road")
    road_signals_exist: Optional[str] = Field(None, alias="Road signals exist")
    approximate_speed: Optional[str] = Field(None, alias="Approximate speed")
    alcohol_consumption: Optional[str] = Field(None, alias="Alcohol Consumption")
    time_between_alcohol: Optional[str] = Field(None, alias="Time between alcohol consumption and accident")
    illicit_drugs: Optional[str] = Field(None, alias="Illicit Drugs")
    helmet_worn: Optional[str] = Field(None, alias="Helmet Worn")
    engine_capacity: Optional[str] = Field(None, alias="Engine Capacity")
    mode_of_transport: Optional[str] = Field(None, alias="Mode of transport to hospital")
    time_to_hospital: Optional[str] = Field(None, alias="Time taken to reach hospital")
    bystander_expenditure: Optional[str] = Field(None, alias="Bystander expenditure per day")
    income_before_accident: Optional[str] = Field(None, alias="Family monthly income before accident")
    income_after_accident: Optional[str] = Field(None, alias="Family monthly income after accident")
    family_status: Optional[str] = Field(None, alias="Family current status")
    vehicle_insured: Optional[str] = Field(None, alias="vehicle insured")
    passenger_type: Optional[str] = Field(None, alias="Passenger type")
    discharge_outcome: Optional[str] = Field(None, alias="Discharge Outcome")

    # categorical; use str (Yes/No/Unknown)
    first_aid_given: Optional[str] = Field(None, alias="First aid given at seen")

    # Completed is controlled by the form checkbox
    completed: Optional[bool] = Field(None, alias="Completed")

class AccidentRecordCreate(AccidentRecordBase):
    pass

class AccidentRecordUpdate(AccidentRecordBase):
    patient_id: Optional[str] = None
    created_by: Optional[str] = None

class AccidentRecordOut(AccidentRecordBase):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)
    accident_id: str
    created_on: date
    managed_by_name: Optional[str] = Field(None, alias="managed_by_name")
    # Note: createf on and managed by name were added by SHakthi for the record viewing readability.
    # created_on, severity etc. can be present in raw DB data, but not required here.