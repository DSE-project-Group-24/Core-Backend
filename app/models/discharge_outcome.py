from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, Union
from datetime import date

class DischargeOutcomePredictionRequest(BaseModel):
    """Request model for discharge outcome prediction"""
    current_hospital_name: Optional[str] = Field(None, description="Current Hospital Name")
    family_current_status: Optional[str] = Field(None, description="Family Current Status")
    type_of_injury_no_1: Optional[str] = Field(None, description="Type of injury No 1")
    traveling_expenditure_per_day: Optional[str] = Field(None, description="Traveling Expenditure per day")
    first_hospital_name: Optional[str] = Field(None, description="First Hospital Name")
    date_of_birth: Optional[str] = Field(None, description="Date Of Birth (YYYY-MM-DD format)")
    site_of_injury_no1: Optional[str] = Field(None, description="Site of Injury No1")
    approximate_speed: Optional[str] = Field(None, description="Approximate Speed")
    incident_at_time_and_date: Optional[str] = Field(None, description="Incident At Time and Date (YYYY-MM-DD format)")
    hospital_distance_from_home: Optional[str] = Field(None, description="Hospital Distance From Home")
    mode_of_transport_to_the_hospital: Optional[str] = Field(None, description="Mode of Transport to the Hospital")
    educational_qualification: Optional[str] = Field(None, description="Educational Qualification")
    time_taken_to_reach_hospital: Optional[str] = Field(None, description="Time Taken To Reach Hospital")
    any_other_hospital_admission_expenditure: Optional[str] = Field(None, description="Any Other Hospital Admission Expenditure")
    site_of_injury_no_2: Optional[str] = Field(None, description="Site of injury No 2")
    occupation: Optional[str] = Field(None, description="Occupation")
    family_monthly_income_before_accident: Optional[str] = Field(None, description="Family Monthly Income Before Accident")
    collision_with: Optional[str] = Field(None, description="Collision With")
    life_style: Optional[str] = Field(None, description="Life Style")
    collision_force_from: Optional[str] = Field(None, description="Collision Force From")
    road_type: Optional[str] = Field(None, description="Road Type")
    type_of_injury_no_2: Optional[str] = Field(None, description="Type of Injury No 2")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_hospital_name": "DGH – Kilinochchi",
                "family_current_status": "Moderately Affected",
                "type_of_injury_no_1": "fracture",
                "traveling_expenditure_per_day": "100-200",
                "first_hospital_name": "DGH – Kilinochchi",
                "date_of_birth": "1990-05-15",
                "site_of_injury_no1": "head injury",
                "approximate_speed": "40 - 80 km/h",
                "incident_at_time_and_date": "2023-10-15",
                "hospital_distance_from_home": "5-10 Km",
                "mode_of_transport_to_the_hospital": "Ambulance",
                "educational_qualification": "O/L or A/L",
                "time_taken_to_reach_hospital": "Less Than 15 Minutes",
                "any_other_hospital_admission_expenditure": "No Other Expenses",
                "site_of_injury_no_2": "no secondary injury found",
                "occupation": "Student",
                "family_monthly_income_before_accident": "30000-45000",
                "collision_with": "Motorbike",
                "life_style": "Living with care givers",
                "collision_force_from": "Front",
                "road_type": "Straight",
                "type_of_injury_no_2": "abrasion"
            }
        }
    )

class DischargeOutcomePredictionResponse(BaseModel):
    """Response model for discharge outcome prediction"""
    prediction: str = Field(..., description="Predicted discharge outcome")
    prediction_probabilities: Dict[str, float] = Field(..., description="Probability scores for each class")
    preprocessed_features: Dict[str, Any] = Field(..., description="Features after preprocessing (mixed types)")
    model_info: Dict[str, Any] = Field(..., description="Information about the model used")

    model_config = ConfigDict(from_attributes=True)

class DischargeOutcomeModelInfo(BaseModel):
    """Model information response"""
    features: list[str] = Field(..., description="List of features used by the model")
    total_features: int = Field(..., description="Total number of features")
    classes: list[str] = Field(..., description="Possible prediction classes")
    model_type: str = Field(..., description="Type of model used")
    description: str = Field(..., description="Model description")

    model_config = ConfigDict(from_attributes=True)