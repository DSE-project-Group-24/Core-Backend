from pydantic import BaseModel, ConfigDict , Field
from typing import Dict, Any, List, Optional
from datetime import date, datetime


class AccidentAnalyticsFilters1(BaseModel):
    start_date: date = Field(..., description="Start date for filtering")
    end_date: date = Field(..., description="End date for filtering")
    severity: str = Field(..., description="Severity level (S or M)")


class AccidentAnalyticsResponse1(BaseModel):
    results: Dict[str, Dict[str, int]]  # {column_name: {category: count}}