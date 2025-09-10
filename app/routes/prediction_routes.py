from fastapi import APIRouter, Depends
from app.models.prediction import ForecastRequest, ForecastResponse
from app.services.prediction_service import get_forecast_service
from app.auth.dependencies import government_personnel_required

router = APIRouter()

@router.post("/forecast", response_model=ForecastResponse, dependencies=[Depends(government_personnel_required)])
async def forecast(req: ForecastRequest):
    """Generate forecast for given number of months"""
    forecast_data = get_forecast_service(req.months)
    return ForecastResponse(forecast_data=forecast_data)


