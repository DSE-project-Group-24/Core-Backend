from fastapi import APIRouter, Depends
from app.models.prediction import ForecastRequest, ForecastResponse
from app.services.prediction_service import get_forecast_service
from app.auth.dependencies import government_personnel_required

router = APIRouter()

# @router.post("/forecast", response_model=ForecastResponse, dependencies=[Depends(government_personnel_required)])
# async def forecast(req: ForecastRequest):
#     """Generate forecast for given number of months"""
#     forecast_data = get_forecast_service(req.months)
#     return ForecastResponse(forecast_data=forecast_data)

# Import get_forecast_service after app initialization to avoid circular imports
from app.services.prediction_service import get_forecast_service

@router.post("/forecast", response_model=ForecastResponse)
async def forecast_endpoint(request: ForecastRequest):
    """Endpoint to generate forecast for both models"""
    forecasts = get_forecast_service(request.months)
    return ForecastResponse(forecast_M=forecasts["forecast_M"], forecast_S=forecasts["forecast_S"])


