# from pydantic import BaseModel, ConfigDict
# from typing import List, Dict, Any

# class ForecastRequest(BaseModel):
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "months": 12
#             }
#         }
#     )
    
#     months: int

# class ForecastResponse(BaseModel):
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "forecast_data": [
#                     {
#                         "mean": 100.5,
#                         "mean_ci_lower": 95.2,
#                         "mean_ci_upper": 105.8
#                     }
#                 ]
#             }
#         }
#     )
    
#     forecast_data: List[Dict[str, Any]]

from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI(title="SARIMA Forecast API")

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
                "forecast_M": [
                    {
                        "mean": 100.5,
                        "mean_ci_lower": 95.2,
                        "mean_ci_upper": 105.8
                    }
                ],
                "forecast_S": [
                    {
                        "mean": 90.3,
                        "mean_ci_lower": 85.1,
                        "mean_ci_upper": 95.5
                    }
                ]
            }
        }
    )
    
    forecast_M: List[Dict[str, Any]]
    forecast_S: List[Dict[str, Any]]

# # Import get_forecast_service after app initialization to avoid circular imports
# from app.services.prediction_service import get_forecast_service

# @app.post("/predictions/forecast", response_model=ForecastResponse)
# async def forecast_endpoint(request: ForecastRequest):
#     """Endpoint to generate forecast for both models"""
#     forecasts = get_forecast_service(request.months)
#     return ForecastResponse(forecast_M=forecasts["forecast_M"], forecast_S=forecasts["forecast_S"])

from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any

class Forecast_WeeklyRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"days": 7}
        }
    )
    days: int

class Forecast_WeeklyResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "forecast": [
                    {"mean": 100.5, "mean_ci_lower": 95.2, "mean_ci_upper": 105.8}
                ]
            }
        }
    )
    forecast: List[Dict[str, Any]]
