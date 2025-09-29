from typing import Dict, Any, List, Optional
from datetime import datetime, date
import logging
from collections import defaultdict
from app.models.analytics import (
    AccidentAnalyticsResponse,
    AccidentCharacteristics,
    Demographics,
    MedicalFactors,
    FinancialImpact,
    TemporalTrends,
    DataQuality,
    AccidentAnalyticsFilters
)
from app.db import get_supabase

logger = logging.getLogger(__name__)

class AccidentAnalyticsService:
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    def get_comprehensive_analytics(self, filters: AccidentAnalyticsFilters = None) -> AccidentAnalyticsResponse:
        """
        Get comprehensive accident analytics data for dashboard
        
        Args:
            filters: Optional filters to apply to the data
        
        Returns:
            AccidentAnalyticsResponse: Complete analytics data
        """
        try:
            logger.info("Starting comprehensive accident analytics generation")
            
            # Get all accident data with filters applied
            accident_data = self._get_filtered_accident_data(filters)
            
            # Get all analytics components
            accident_chars = self._get_accident_characteristics(accident_data)
            demographics = self._get_demographics(accident_data)
            medical_factors = self._get_medical_factors(accident_data)
            financial_impact = self._get_financial_impact(accident_data)
            temporal_trends = self._get_temporal_trends(accident_data)
            data_quality = self._get_data_quality(accident_data)
            
            # Calculate summary statistics
            summary_stats = self._get_summary_statistics(accident_data)
            
            logger.info("Accident analytics generation completed successfully")
            
            return AccidentAnalyticsResponse(
                accident_characteristics=accident_chars,
                demographics=demographics,
                medical_factors=medical_factors,
                financial_impact=financial_impact,
                temporal_trends=temporal_trends,
                data_quality=data_quality,
                total_records=summary_stats['total_records'],
                peak_accident_hour=summary_stats['peak_hour'],
                most_common_collision=summary_stats['common_collision'],
                avg_income_impact=summary_stats['avg_income_change'],
                generated_at=datetime.now(),
                data_period=self._get_data_period(accident_data)
            )
            
        except Exception as e:
            logger.error(f"Error generating accident analytics: {str(e)}")
            raise
    
    def _get_filtered_accident_data(self, filters: AccidentAnalyticsFilters) -> List[Dict[str, Any]]:
        """Get accident data from Supabase with filters applied"""
        try:
            # Start with base query
            query = self.supabase.table("Accident Record").select("*")
            
            # Apply filters if provided
            if filters:
                if filters.start_date:
                    query = query.gte("incident_date", filters.start_date.isoformat())
                
                if filters.end_date:
                    query = query.lte("incident_date", filters.end_date.isoformat())
                
                if filters.gender:
                    query = query.eq("gender", filters.gender)
                
                if filters.age_min:
                    query = query.gte("age", filters.age_min)
                
                if filters.age_max:
                    query = query.lte("age", filters.age_max)
                
                if filters.ethnicity:
                    query = query.eq("ethnicity", filters.ethnicity)
                
                if filters.collision_type:
                    query = query.eq("collision_with", filters.collision_type)
                
                if filters.road_category:
                    query = query.eq("road_category", filters.road_category)
                
                if filters.discharge_outcome:
                    query = query.eq("discharge_outcome", filters.discharge_outcome)
                
                if filters.hospital_id:
                    query = query.eq("current_hospital_id", filters.hospital_id)
            
            # Execute query
            response = query.execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching accident data: {str(e)}")
            raise
    
    def _get_accident_characteristics(self, accident_data: List[Dict[str, Any]]) -> AccidentCharacteristics:
        """Get accident characteristics analysis from data array"""
        
        # Initialize counters
        hourly_distribution = defaultdict(int)
        collision_types = defaultdict(int)
        travel_modes = defaultdict(int)
        road_categories = defaultdict(int)
        
        # Process each accident record
        for record in accident_data:
            # Hourly distribution
            if record.get('time_of_collision') is not None:
                hourly_distribution[int(record['time_of_collision'])] += 1
            
            # Collision types
            if record.get('collision_with'):
                collision_types[record['collision_with']] += 1
            
            # Travel modes
            if record.get('mode_of_travel'):
                travel_modes[record['mode_of_travel']] += 1
            
            # Road categories
            if record.get('road_category'):
                road_categories[record['road_category']] += 1
        
        return AccidentCharacteristics(
            hourly_distribution=dict(hourly_distribution),
            collision_types=dict(collision_types),
            travel_modes=dict(travel_modes),
            road_categories=dict(road_categories)
        )
    
    def _get_demographics(self, accident_data: List[Dict[str, Any]]) -> Demographics:
        """Get demographic analysis from data array"""
        
        # Initialize counters
        age_groups = defaultdict(int)
        gender_dist = defaultdict(int)
        ethnicity_dist = defaultdict(int)
        education_dist = defaultdict(int)
        occupation_dist = defaultdict(int)
        
        # Process each accident record
        for record in accident_data:
            # Age groups
            age = record.get('age')
            if age is not None:
                if 18 <= age <= 25:
                    age_groups['18-25'] += 1
                elif 26 <= age <= 35:
                    age_groups['26-35'] += 1
                elif 36 <= age <= 45:
                    age_groups['36-45'] += 1
                elif 46 <= age <= 55:
                    age_groups['46-55'] += 1
                else:
                    age_groups['56+'] += 1
            
            # Gender distribution
            if record.get('gender'):
                gender_dist[record['gender']] += 1
            
            # Ethnicity distribution
            if record.get('ethnicity'):
                ethnicity_dist[record['ethnicity']] += 1
            
            # Education distribution
            if record.get('education_level'):
                education_dist[record['education_level']] += 1
            
            # Occupation distribution
            if record.get('occupation'):
                occupation_dist[record['occupation']] += 1
        
        return Demographics(
            age_groups=dict(age_groups),
            gender_dist=dict(gender_dist),
            ethnicity_dist=dict(ethnicity_dist),
            education_dist=dict(education_dist),
            occupation_dist=dict(occupation_dist)
        )
    
    def _get_medical_factors(self, conditions: str) -> MedicalFactors:
        """Get medical factors analysis"""
        
        # Discharge outcomes
        outcome_query = f"""
            SELECT discharge_outcome, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY discharge_outcome
            ORDER BY count DESC
        """
        outcome_result = self.db.execute(text(outcome_query)).fetchall()
        outcomes_dist = {row.discharge_outcome: row.count for row in outcome_result}
        
        # Washroom access
        washroom_query = f"""
            SELECT access_to_wash_room, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY access_to_wash_room
        """
        washroom_result = self.db.execute(text(washroom_query)).fetchall()
        wash_room_access = {str(row.access_to_wash_room): row.count for row in washroom_result}
        
        # Toilet modification
        toilet_query = f"""
            SELECT type_of_toilet_modification, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY type_of_toilet_modification
            ORDER BY count DESC
        """
        toilet_result = self.db.execute(text(toilet_query)).fetchall()
        toilet_modification = {row.type_of_toilet_modification: row.count for row in toilet_result}
        
        # Average hospital expenditure
        expenditure_query = f"""
            SELECT AVG(CAST(additional_hospital_expenditure AS FLOAT)) as avg_expenditure
            FROM accidents 
            WHERE {conditions} AND additional_hospital_expenditure IS NOT NULL
        """
        expenditure_result = self.db.execute(text(expenditure_query)).fetchone()
        avg_hospital_expenditure = float(expenditure_result.avg_expenditure or 0)
        
        return MedicalFactors(
            outcomes_dist=outcomes_dist,
            wash_room_access=wash_room_access,
            toilet_modification=toilet_modification,
            avg_hospital_expenditure=avg_hospital_expenditure
        )
    
    def _get_financial_impact(self, conditions: str) -> FinancialImpact:
        """Get financial impact analysis"""
        
        # Income comparison
        income_query = f"""
            SELECT 
                CASE 
                    WHEN family_monthly_income_after_accident > family_monthly_income_before_accident THEN 'improved'
                    WHEN family_monthly_income_after_accident = family_monthly_income_before_accident THEN 'same'
                    ELSE 'decreased'
                END as income_change,
                COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            AND family_monthly_income_before_accident IS NOT NULL
            AND family_monthly_income_after_accident IS NOT NULL
            GROUP BY income_change
        """
        income_result = self.db.execute(text(income_query)).fetchall()
        income_comparison = {row.income_change: row.count for row in income_result}
        
        # Average income change
        avg_change_query = f"""
            SELECT AVG(CAST(family_monthly_income_after_accident AS FLOAT) - CAST(family_monthly_income_before_accident AS FLOAT)) as avg_change
            FROM accidents 
            WHERE {conditions}
            AND family_monthly_income_before_accident IS NOT NULL
            AND family_monthly_income_after_accident IS NOT NULL
        """
        avg_change_result = self.db.execute(text(avg_change_query)).fetchone()
        avg_income_change = float(avg_change_result.avg_change or 0)
        
        # Family status distribution
        family_query = f"""
            SELECT family_current_status, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY family_current_status
            ORDER BY count DESC
        """
        family_result = self.db.execute(text(family_query)).fetchall()
        family_status_dist = {row.family_current_status: row.count for row in family_result}
        
        # Insurance claim distribution
        insurance_query = f"""
            SELECT vehicle_insurance_type, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY vehicle_insurance_type
            ORDER BY count DESC
        """
        insurance_result = self.db.execute(text(insurance_query)).fetchall()
        insurance_claim_dist = {row.vehicle_insurance_type: row.count for row in insurance_result}
        
        # Average expenses
        bystander_query = f"""
            SELECT AVG(CAST(bystander_expenditure_per_day AS FLOAT)) as avg_bystander
            FROM accidents 
            WHERE {conditions} AND bystander_expenditure_per_day IS NOT NULL
        """
        bystander_result = self.db.execute(text(bystander_query)).fetchone()
        avg_bystander_exp = float(bystander_result.avg_bystander or 0)
        
        travel_query = f"""
            SELECT AVG(CAST(traveling_expenditure_per_day AS FLOAT)) as avg_travel
            FROM accidents 
            WHERE {conditions} AND traveling_expenditure_per_day IS NOT NULL
        """
        travel_result = self.db.execute(text(travel_query)).fetchone()
        avg_travel_exp = float(travel_result.avg_travel or 0)
        
        return FinancialImpact(
            income_comparison=income_comparison,
            avg_income_change=avg_income_change,
            family_status_dist=family_status_dist,
            insurance_claim_dist=insurance_claim_dist,
            avg_bystander_exp=avg_bystander_exp,
            avg_travel_exp=avg_travel_exp
        )
    
    def _get_temporal_trends(self, conditions: str) -> TemporalTrends:
        """Get temporal trends analysis"""
        
        # Monthly trends
        monthly_query = f"""
            SELECT EXTRACT(MONTH FROM incident_date) as month, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY EXTRACT(MONTH FROM incident_date)
            ORDER BY month
        """
        monthly_result = self.db.execute(text(monthly_query)).fetchall()
        monthly_trends = {int(row.month): row.count for row in monthly_result}
        
        # Daily trends (day of week)
        daily_query = f"""
            SELECT EXTRACT(DOW FROM incident_date) as day_of_week, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY EXTRACT(DOW FROM incident_date)
            ORDER BY day_of_week
        """
        daily_result = self.db.execute(text(daily_query)).fetchall()
        daily_trends = {int(row.day_of_week): row.count for row in daily_result}
        
        return TemporalTrends(
            monthly_trends=monthly_trends,
            daily_trends=daily_trends
        )
    
    def _get_data_quality(self, conditions: str) -> DataQuality:
        """Get data quality metrics"""
        
        # Total records
        total_query = f"""
            SELECT COUNT(*) as total
            FROM accidents 
            WHERE {conditions}
        """
        total_result = self.db.execute(text(total_query)).fetchone()
        total_records = total_result.total
        
        # Quality distribution (assuming you have a data_quality column)
        quality_query = f"""
            SELECT 
                CASE 
                    WHEN (incident_date IS NOT NULL AND age IS NOT NULL AND gender IS NOT NULL) THEN 'Complete'
                    ELSE 'Missing/Incomplete'
                END as quality,
                COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY quality
        """
        quality_result = self.db.execute(text(quality_query)).fetchall()
        quality_dist = {row.quality: row.count for row in quality_result}
        
        # Calculate completion rate
        complete_records = quality_dist.get('Complete', 0)
        completion_rate = (complete_records / total_records * 100) if total_records > 0 else 0
        
        return DataQuality(
            quality_dist=quality_dist,
            total_records=total_records,
            completion_rate=completion_rate
        )
    
    def _get_summary_statistics(self, conditions: str) -> Dict[str, Any]:
        """Get summary statistics for the response"""
        
        # Peak accident hour
        peak_hour_query = f"""
            SELECT time_of_collision, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY time_of_collision
            ORDER BY count DESC
            LIMIT 1
        """
        peak_hour_result = self.db.execute(text(peak_hour_query)).fetchone()
        peak_hour = peak_hour_result.time_of_collision if peak_hour_result else 0
        
        # Most common collision type
        collision_query = f"""
            SELECT collision_with, COUNT(*) as count
            FROM accidents 
            WHERE {conditions}
            GROUP BY collision_with
            ORDER BY count DESC
            LIMIT 1
        """
        collision_result = self.db.execute(text(collision_query)).fetchone()
        common_collision = collision_result.collision_with if collision_result else "Unknown"
        
        # Average income change
        income_query = f"""
            SELECT AVG(CAST(family_monthly_income_after_accident AS FLOAT) - CAST(family_monthly_income_before_accident AS FLOAT)) as avg_change
            FROM accidents 
            WHERE {conditions}
            AND family_monthly_income_before_accident IS NOT NULL
            AND family_monthly_income_after_accident IS NOT NULL
        """
        income_result = self.db.execute(text(income_query)).fetchone()
        avg_income_change = float(income_result.avg_change or 0)
        
        # Total records
        total_query = f"""
            SELECT COUNT(*) as total
            FROM accidents 
            WHERE {conditions}
        """
        total_result = self.db.execute(text(total_query)).fetchone()
        total_records = total_result.total
        
        return {
            'peak_hour': peak_hour,
            'common_collision': common_collision,
            'avg_income_change': avg_income_change,
            'total_records': total_records
        }
    
    def _get_data_period(self, conditions: str) -> Dict[str, Any]:
        """Get the data period information"""
        
        period_query = f"""
            SELECT 
                MIN(incident_date) as start_date,
                MAX(incident_date) as end_date,
                COUNT(*) as total_records
            FROM accidents 
            WHERE {conditions}
        """
        period_result = self.db.execute(text(period_query)).fetchone()
        
        if period_result:
            return {
                'start_date': period_result.start_date.isoformat() if period_result.start_date else None,
                'end_date': period_result.end_date.isoformat() if period_result.end_date else None,
                'total_records': period_result.total_records
            }
        
        return None


# Service functions that follow the existing pattern
def get_comprehensive_analytics_service(filters: AccidentAnalyticsFilters) -> AccidentAnalyticsResponse:
    """Get comprehensive accident analytics - follows existing service pattern"""
    db = get_supabase()
    analytics_service = AccidentAnalyticsService(db)
    return analytics_service.get_comprehensive_analytics(filters)


def get_accident_summary_service() -> Dict[str, Any]:
    """Get accident summary statistics - follows existing service pattern"""
    db = get_supabase()
    analytics_service = AccidentAnalyticsService(db)
    summary_stats = analytics_service._get_summary_statistics("1=1")  # No filters
    
    return {
        "total_accidents": summary_stats['total_records'],
        "peak_accident_hour": summary_stats['peak_hour'],
        "most_common_collision": summary_stats['common_collision'],
        "avg_income_impact": summary_stats['avg_income_change'],
        "generated_at": datetime.now().isoformat()
    }


def get_filter_options_service() -> Dict[str, Any]:
    """Get available filter options - follows existing service pattern"""
    db = get_supabase()
    
    # Get distinct values for each filter field
    # Gender options
    gender_query = "SELECT DISTINCT gender FROM accidents WHERE gender IS NOT NULL ORDER BY gender"
    gender_result = db.execute(text(gender_query)).fetchall()
    genders = [row.gender for row in gender_result]
    
    # Ethnicity options
    ethnicity_query = "SELECT DISTINCT ethnicity FROM accidents WHERE ethnicity IS NOT NULL ORDER BY ethnicity"
    ethnicity_result = db.execute(text(ethnicity_query)).fetchall()
    ethnicities = [row.ethnicity for row in ethnicity_result]
    
    # Collision type options
    collision_query = "SELECT DISTINCT collision_with FROM accidents WHERE collision_with IS NOT NULL ORDER BY collision_with"
    collision_result = db.execute(text(collision_query)).fetchall()
    collision_types = [row.collision_with for row in collision_result]
    
    # Road category options
    road_query = "SELECT DISTINCT road_category FROM accidents WHERE road_category IS NOT NULL ORDER BY road_category"
    road_result = db.execute(text(road_query)).fetchall()
    road_categories = [row.road_category for row in road_result]
    
    # Discharge outcome options
    outcome_query = "SELECT DISTINCT discharge_outcome FROM accidents WHERE discharge_outcome IS NOT NULL ORDER BY discharge_outcome"
    outcome_result = db.execute(text(outcome_query)).fetchall()
    discharge_outcomes = [row.discharge_outcome for row in outcome_result]
    
    # Age range
    age_query = "SELECT MIN(age) as min_age, MAX(age) as max_age FROM accidents WHERE age IS NOT NULL"
    age_result = db.execute(text(age_query)).fetchone()
    age_range = {
        "min": age_result.min_age if age_result else 0,
        "max": age_result.max_age if age_result else 100
    }
    
    # Date range
    date_query = "SELECT MIN(incident_date) as min_date, MAX(incident_date) as max_date FROM accidents WHERE incident_date IS NOT NULL"
    date_result = db.execute(text(date_query)).fetchone()
    date_range = {
        "min": date_result.min_date.isoformat() if date_result and date_result.min_date else None,
        "max": date_result.max_date.isoformat() if date_result and date_result.max_date else None
    }
    
    return {
        "genders": genders,
        "ethnicities": ethnicities,
        "collision_types": collision_types,
        "road_categories": road_categories,
        "discharge_outcomes": discharge_outcomes,
        "age_range": age_range,
        "date_range": date_range
    }