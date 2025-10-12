from fastapi import APIRouter, Depends, Query , HTTPException
from typing import Optional,Dict, Any
from datetime import date
from fastapi.responses import JSONResponse
from app.models.gov_dash import AccidentAnalyticsResponse1,AccidentAnalyticsFilters1
from app.services.govDash_service import (
    get_accident_trends_service,
    get_comprehensive_analytics_service1,
    # get_accident_stats
)
from app.auth.dependencies import government_personnel_required


router = APIRouter()

@router.post("/comprehensive", response_model=AccidentAnalyticsResponse1)
def get_comprehensive_analytics1(filters: AccidentAnalyticsFilters1):
    """
    Get accident analytics filtered by date range and severity.
    """
    try:
        return get_comprehensive_analytics_service1(filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/trendsAll", summary="Get accident trends by month, year, and day-of-week")
def get_accident_trends():
    """
    Returns accident statistics grouped by:
    - Month (YYYY-MM)
    - Year
    - Day of the week

    Each group contains:
    - total accidents
    - serious accidents (Severity = 'S')
    """
    try:
        data = get_accident_trends_service()
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    
