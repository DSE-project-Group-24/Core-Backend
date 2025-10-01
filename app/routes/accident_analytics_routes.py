from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from app.models.analytics import AccidentAnalyticsResponse, AccidentAnalyticsFilters
from app.services.accident_analytics_service import (
    get_comprehensive_analytics_service,
    get_accident_summary_service,
    get_filter_options_service
)
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.get("", response_model=AccidentAnalyticsResponse, dependencies=[Depends(get_current_user)])
def get_accident_analytics(
    start_date: Optional[date] = Query(None, description="Filter accidents from this date"),
    end_date: Optional[date] = Query(None, description="Filter accidents to this date"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    age_min: Optional[int] = Query(None, ge=0, le=120, description="Minimum age filter"),
    age_max: Optional[int] = Query(None, ge=0, le=120, description="Maximum age filter"),
    ethnicity: Optional[str] = Query(None, description="Filter by ethnicity"),
    collision_type: Optional[str] = Query(None, description="Filter by collision type"),
    road_category: Optional[str] = Query(None, description="Filter by road category"),
    discharge_outcome: Optional[str] = Query(None, description="Filter by discharge outcome"),
    hospital_id: Optional[int] = Query(None, description="Filter by hospital ID")
):
    # Create filters object
    filters = AccidentAnalyticsFilters(
        start_date=start_date,
        end_date=end_date,
        gender=gender,
        age_min=age_min,
        age_max=age_max,
        ethnicity=ethnicity,
        collision_type=collision_type,
        road_category=road_category,
        discharge_outcome=discharge_outcome,
        hospital_id=hospital_id
    )
    
    return get_comprehensive_analytics_service(filters)

@router.get("/summary", dependencies=[Depends(get_current_user)])
def get_accident_summary():
    return get_accident_summary_service()

@router.get("/filters/options", dependencies=[Depends(get_current_user)])
def get_filter_options():
    return get_filter_options_service()

@router.get("/health")
def analytics_health_check():
    return {
        "status": "healthy",
        "service": "accident_analytics",
        "version": "1.0.0"
    }