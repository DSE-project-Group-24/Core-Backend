from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List, Optional
from datetime import date, datetime

class AccidentCharacteristics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    hourly_distribution: Dict[int, int]
    collision_types: Dict[str, int]
    travel_modes: Dict[str, int]
    road_categories: Dict[str, int]

class Demographics(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    age_groups: Dict[str, int]
    gender_dist: Dict[str, int]
    ethnicity_dist: Dict[str, int]
    education_dist: Dict[str, int]
    occupation_dist: Dict[str, int]

class MedicalFactors(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    outcomes_dist: Dict[str, int]
    wash_room_access: Dict[str, int]
    toilet_modification: Dict[str, int]
    avg_hospital_expenditure: float

class FinancialImpact(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    income_comparison: Dict[str, int]
    avg_income_change: float
    family_status_dist: Dict[str, int]
    insurance_claim_dist: Dict[str, int]
    avg_bystander_exp: float
    avg_travel_exp: float

class TemporalTrends(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    monthly_trends: Dict[int, int]
    daily_trends: Dict[int, int]

class DataQuality(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    quality_dist: Dict[str, int]
    total_records: int
    completion_rate: float

class AccidentAnalyticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    accident_characteristics: AccidentCharacteristics
    demographics: Demographics
    medical_factors: MedicalFactors
    financial_impact: FinancialImpact
    temporal_trends: TemporalTrends
    data_quality: DataQuality
    
    # Summary statistics
    total_records: int
    peak_accident_hour: int
    most_common_collision: str
    avg_income_impact: float
    
    # Timestamps
    generated_at: datetime
    data_period: Optional[Dict[str, Any]] = None

class AccidentAnalyticsFilters(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gender: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    ethnicity: Optional[str] = None
    collision_type: Optional[str] = None
    road_category: Optional[str] = None
    discharge_outcome: Optional[str] = None
    hospital_id: Optional[str] = None