from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any

class ForecastRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "months": 12
            }
        }
    )
    
    months: int

class ForecastResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "forecast_data": [
                    {
                        "mean": 100.5,
                        "mean_ci_lower": 95.2,
                        "mean_ci_upper": 105.8
                    }
                ]
            }
        }
    )
    
    forecast_data: List[Dict[str, Any]]
