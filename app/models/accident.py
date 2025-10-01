from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, time
from decimal import Decimal

# Accident Record Model
class AccidentRecordBase(BaseModel):
    patient_id: str
    managed_by: Optional[str] = Field(None, alias="managed by")
    incident_at_date: Optional[date] = Field(None, alias="incident at date")
    incident_at_time: Optional[time] = Field(None, alias="incident at time")
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
    vehicle_type: Optional[str] = Field(None, alias="Vehicle type")
    helmet_worn: Optional[str] = Field(None, alias="Helmet Worn")
    engine_capacity: Optional[str] = Field(None, alias="Engine Capacity")
    mode_of_transport: Optional[str] = Field(None, alias="Mode of transport to hospital")
    time_to_hospital: Optional[str] = Field(None, alias="Time taken to reach hospital")
    bystander_expenditure: Optional[str] = Field(None, alias="Bystander expenditure per day")
    income_before_accident: Optional[str] = Field(None, alias="Family monthly income before accident")
    income_after_accident: Optional[str] = Field(None, alias="Family monthly income after accident")
    family_status: Optional[str] = Field(None, alias="Family current status")
    insurance_claim_type: Optional[str] = Field(None, alias="Any insurance claim type")
    dress_name: Optional[str] = Field(None, alias="Dress name")
    vehicle_insured: Optional[str] = Field(None, alias="vehicle insured")
    vehicle_insured_type: Optional[str] = Field(None, alias="vehicle insured type")
    passenger_type: Optional[str] = Field(None, alias="Passenger type")
    first_aid_given: Optional[bool] = Field(None, alias="First aid given at seen")
    completed: Optional[bool] = Field(None, alias="Completed")

class AccidentRecordCreate(AccidentRecordBase):
    pass

class AccidentRecordUpdate(AccidentRecordBase):
    patient_id: Optional[str] = None
    managed_by: Optional[str] = None

class AccidentRecordOut(AccidentRecordBase):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True
    )
    
    accident_id: str
