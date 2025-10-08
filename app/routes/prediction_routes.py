from fastapi import APIRouter, Depends
from typing import Dict
from app.models.prediction import ForecastRequest, ForecastResponse
from pydantic import BaseModel
from app.auth.dependencies import government_personnel_required
from app.services.prediction_service import get_forecast_service, get_daily_forecast
router = APIRouter()

# Import get_forecast_service after app initialization to avoid circular imports
from app.services.prediction_service import get_forecast_service

@router.post("/forecast", response_model=ForecastResponse)
async def forecast_endpoint(request: ForecastRequest):
    """Endpoint to generate forecast for both models"""
    forecasts = get_forecast_service(request.months)
    return ForecastResponse(forecast_M=forecasts["forecast_M"], forecast_S=forecasts["forecast_S"])


class DailyForecastRequest(BaseModel):
    days: int = 7  # default to next 7 days

@router.post("/daily-forecast")
async def daily_forecast_endpoint(request: DailyForecastRequest) -> Dict[str, float]:
    """
    Endpoint to forecast next N days of daily accidents using SARIMA.
    Returns a dictionary: {date: predicted_mean}.
    """
    forecast_series = get_daily_forecast(request.days)
    # Convert index to string for JSON serialization
    forecast_dict = {str(idx.date()): float(val) for idx, val in forecast_series.items()}
    return forecast_dict