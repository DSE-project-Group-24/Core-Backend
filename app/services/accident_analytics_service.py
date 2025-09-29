from typing import Dict, Any, List, Optional
from datetime import datetime
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

def get_comprehensive_analytics_service(filters: AccidentAnalyticsFilters) -> AccidentAnalyticsResponse:
    """Get comprehensive accident analytics - follows existing service pattern"""
    supabase = get_supabase()
    
    # Get filtered accident data
    accident_data = _get_filtered_accident_data(supabase, filters)
    
    # Generate all analytics
    accident_chars = _get_accident_characteristics(accident_data)
    demographics = _get_demographics(accident_data)
    medical_factors = _get_medical_factors(accident_data)
    financial_impact = _get_financial_impact(accident_data)
    temporal_trends = _get_temporal_trends(accident_data)
    data_quality = _get_data_quality(accident_data)
    summary_stats = _get_summary_statistics(accident_data)
    
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
        data_period=_get_data_period(accident_data)
    )

def get_accident_summary_service() -> Dict[str, Any]:
    """Get accident summary statistics - follows existing service pattern"""
    supabase = get_supabase()
    
    # Get all accident data (no filters)
    response = supabase.table("Accident Record").select("*").execute()
    accident_data = response.data or []
    
    summary_stats = _get_summary_statistics(accident_data)
    
    return {
        "total_accidents": summary_stats['total_records'],
        "peak_accident_hour": summary_stats['peak_hour'],
        "most_common_collision": summary_stats['common_collision'],
        "avg_income_impact": summary_stats['avg_income_change'],
        "generated_at": datetime.now().isoformat()
    }

def get_filter_options_service() -> Dict[str, Any]:
    """Get available filter options - follows existing service pattern"""
    supabase = get_supabase()
    
    # Get all accident data with patient info to extract unique values
    response = supabase.table("Accident Record").select("""
        *,
        Patient:patient_id (
            Date of Birth,
            Ethnicity,
            Gender
        )
    """).execute()
    accident_data = response.data or []
    
    # Extract unique values for each filter field
    genders = set()
    ethnicities = set()
    collision_types = set()
    road_categories = set()
    discharge_outcomes = set()
    ages = []
    dates = []
    
    for record in accident_data:
        patient_data = record.get('Patient')
        if patient_data:
            # Gender
            gender = patient_data.get('Gender')
            if gender:
                genders.add(gender)
            
            # Ethnicity
            ethnicity = patient_data.get('Ethnicity')
            if ethnicity:
                ethnicities.add(ethnicity)
            
            # Calculate age
            dob = patient_data.get('Date of Birth')
            if dob:
                try:
                    from datetime import datetime, date
                    if isinstance(dob, str):
                        birth_date = datetime.fromisoformat(dob.replace('Z', '+00:00')).date()
                    else:
                        birth_date = dob
                    
                    today = date.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    ages.append(age)
                except (ValueError, TypeError, AttributeError):
                    pass
        
        # Collision types
        collision = record.get('Collision with')
        if collision and collision != 'Victim not willing to share/ Unable to respond/  Early Discharge':
            collision_types.add(collision)
        
        # Road categories
        road_category = record.get('Category of Road')
        if road_category and road_category != 'Victim not willing to share/ Unable to respond/  Early Discharge':
            road_categories.add(road_category)
        
        # Discharge outcomes
        discharge_outcome = record.get('Discharge Outcome')
        if discharge_outcome:
            discharge_outcomes.add(discharge_outcome)
        
        # Dates
        incident_date = record.get('incident at date')
        if incident_date:
            dates.append(incident_date)
    
    age_range = {
        "min": min(ages) if ages else 0,
        "max": max(ages) if ages else 100
    }
    
    date_range = {
        "min": min(dates) if dates else None,
        "max": max(dates) if dates else None
    }
    
    return {
        "genders": sorted(list(genders)),
        "ethnicities": sorted(list(ethnicities)),
        "collision_types": sorted(list(collision_types)),
        "road_categories": sorted(list(road_categories)),
        "discharge_outcomes": sorted(list(discharge_outcomes)),
        "age_range": age_range,
        "date_range": date_range
    }

from typing import List, Dict, Any

def _get_filtered_accident_data(supabase, filters: AccidentAnalyticsFilters) -> List[Dict[str, Any]]:
    """Get accident data from Supabase with filters applied (joins Patient via patient_id)."""
    try:
        # embed Patient by the foreign-key column 'patient_id'
        # NOTE: column names that contain spaces must be wrapped in double quotes
        select_str = (
            '*, "Patient":patient_id('
            '"Full Name","Date of Birth","Ethnicity","Gender",'
            '"Education Qualification","Occupation","Family Monthly Income"'
            ')'
        )

        query = supabase.table("Accident Record").select(select_str)

        # Apply filters if provided
        if filters:
            if filters.start_date:
                query = query.gte("incident at date", filters.start_date.isoformat())
            if filters.end_date:
                query = query.lte("incident at date", filters.end_date.isoformat())
            if filters.collision_type:
                query = query.eq("Collision with", filters.collision_type)
            if filters.road_category:
                query = query.eq("Category of Road", filters.road_category)
            if filters.discharge_outcome:
                query = query.eq("Discharge Outcome", filters.discharge_outcome)

        # Execute query
        response = query.execute()

        # helpful debugging if something goes wrong
        if getattr(response, "error", None):
            raise Exception(f"Supabase error: {response.error}")

        return response.data or []

    except Exception as e:
        raise Exception(f"Error fetching accident data: {str(e)}")

def _get_accident_characteristics(accident_data: List[Dict[str, Any]]) -> AccidentCharacteristics:
    """Get accident characteristics analysis from data array"""
    
    # Initialize counters
    hourly_distribution = defaultdict(int)
    collision_types = defaultdict(int)
    travel_modes = defaultdict(int)
    road_categories = defaultdict(int)
    
    # Process each accident record
    for record in accident_data:
        # Hourly distribution - extract hour from "time of collision"
        time_str = record.get('time of collision')
        if time_str and time_str != 'Victim Unable to recall the Time or Early Discharge':
            try:
                # Try to extract hour from time string (assuming format like "14:30" or "2:30 PM")
                if ':' in time_str:
                    hour = int(time_str.split(':')[0])
                    if 'PM' in time_str.upper() and hour != 12:
                        hour += 12
                    elif 'AM' in time_str.upper() and hour == 12:
                        hour = 0
                    hourly_distribution[hour] += 1
            except (ValueError, IndexError):
                pass
        
        # Collision types
        collision = record.get('Collision with')
        if collision and collision != 'Victim not willing to share/ Unable to respond/  Early Discharge':
            collision_types[collision] += 1
        
        # Travel modes
        travel_mode = record.get('Mode of traveling during accident')
        if travel_mode and travel_mode not in [None, '']:
            travel_modes[travel_mode] += 1
        
        # Road categories
        road_category = record.get('Category of Road')
        if road_category and road_category != 'Victim not willing to share/ Unable to respond/  Early Discharge':
            road_categories[road_category] += 1
    
    return AccidentCharacteristics(
        hourly_distribution=dict(hourly_distribution),
        collision_types=dict(collision_types),
        travel_modes=dict(travel_modes),
        road_categories=dict(road_categories)
    )

def _get_demographics(accident_data: List[Dict[str, Any]]) -> Demographics:
    """Get demographic analysis from data array"""
    
    # Initialize counters
    age_groups = defaultdict(int)
    gender_dist = defaultdict(int)
    ethnicity_dist = defaultdict(int)
    education_dist = defaultdict(int)
    occupation_dist = defaultdict(int)
    
    # Process each accident record
    for record in accident_data:
        patient_data = record.get('Patient')
        if patient_data:
            # Calculate age from Date of Birth
            dob = patient_data.get('Date of Birth')
            if dob:
                try:
                    from datetime import datetime, date
                    if isinstance(dob, str):
                        birth_date = datetime.fromisoformat(dob.replace('Z', '+00:00')).date()
                    else:
                        birth_date = dob
                    
                    today = date.today()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    
                    # Age groups
                    if 18 <= age <= 25:
                        age_groups['18-25'] += 1
                    elif 26 <= age <= 35:
                        age_groups['26-35'] += 1
                    elif 36 <= age <= 45:
                        age_groups['36-45'] += 1
                    elif 46 <= age <= 55:
                        age_groups['46-55'] += 1
                    elif age > 55:
                        age_groups['56+'] += 1
                    else:
                        age_groups['Under 18'] += 1
                        
                except (ValueError, TypeError, AttributeError):
                    pass
            
            # Gender distribution
            gender = patient_data.get('Gender')
            if gender:
                gender_dist[gender] += 1
            
            # Ethnicity distribution
            ethnicity = patient_data.get('Ethnicity')
            if ethnicity:
                ethnicity_dist[ethnicity] += 1
            
            # Education distribution
            education = patient_data.get('Education Qualification')
            if education:
                education_dist[education] += 1
            
            # Occupation distribution
            occupation = patient_data.get('Occupation')
            if occupation:
                occupation_dist[occupation] += 1
    
    return Demographics(
        age_groups=dict(age_groups),
        gender_dist=dict(gender_dist),
        ethnicity_dist=dict(ethnicity_dist),
        education_dist=dict(education_dist),
        occupation_dist=dict(occupation_dist)
    )

def _get_medical_factors(accident_data: List[Dict[str, Any]]) -> MedicalFactors:
    """Get medical factors analysis from data array"""
    
    # Initialize counters
    outcomes_dist = defaultdict(int)
    wash_room_access = defaultdict(int)
    toilet_modification = defaultdict(int)
    expenditures = []
    
    # Process each accident record
    for record in accident_data:
        # Discharge outcomes
        discharge_outcome = record.get('Discharge Outcome')
        if discharge_outcome:
            outcomes_dist[discharge_outcome] += 1
        
        # Note: These fields don't exist in your schema, but keeping structure for future use
        # You might need to add these fields or get this data from related tables
        
        # For now, using bystander expenditure as hospital expenditure proxy
        bystander_exp = record.get('Bystander expenditure per day')
        if bystander_exp and bystander_exp != '0':
            try:
                expenditures.append(float(bystander_exp))
            except (ValueError, TypeError):
                pass
    
    avg_hospital_expenditure = sum(expenditures) / len(expenditures) if expenditures else 0.0
    
    return MedicalFactors(
        outcomes_dist=dict(outcomes_dist),
        wash_room_access=dict(wash_room_access),
        toilet_modification=dict(toilet_modification),
        avg_hospital_expenditure=avg_hospital_expenditure
    )

def _get_financial_impact(accident_data: List[Dict[str, Any]]) -> FinancialImpact:
    """Get financial impact analysis from data array"""
    
    # Initialize counters
    income_comparison = defaultdict(int)
    family_status_dist = defaultdict(int)
    insurance_claim_dist = defaultdict(int)
    bystander_expenses = []
    travel_expenses = []
    income_changes = []
    
    # Process each accident record
    for record in accident_data:
        # Income comparison
        income_before = record.get('Family monthly income before accident')
        income_after = record.get('Family monthly income after accident')
        
        if (income_before and income_before != 'Victim not willing to share/ Unable to respond/  Early Discharge' and
            income_after and income_after != 'Victim not willing to share/ Unable to respond/  Early Discharge'):
            try:
                # Handle string values like "10000-15000" or "Above 50000"
                before_val = _parse_income_range(income_before)
                after_val = _parse_income_range(income_after)
                
                if before_val is not None and after_val is not None:
                    change = after_val - before_val
                    income_changes.append(change)
                    
                    if change > 0:
                        income_comparison['improved'] += 1
                    elif change == 0:
                        income_comparison['same'] += 1
                    else:
                        income_comparison['decreased'] += 1
            except (ValueError, TypeError):
                pass
        
        # Family status
        family_status = record.get('Family current status')
        if family_status and family_status != 'Victim not willing to share/ Unable to respond/  Early Discharge':
            family_status_dist[family_status] += 1
        
        # Insurance
        vehicle_insured = record.get('vehicle insured')
        insurance_type = record.get('vehicle insured type')
        if vehicle_insured and vehicle_insured != 'Victim not willing to share/ Unable to respond/  Early Discharge':
            if insurance_type and insurance_type != 'Victim not willing to share/ Unable to respond/  Early Discharge':
                insurance_claim_dist[f"{vehicle_insured} - {insurance_type}"] += 1
            else:
                insurance_claim_dist[vehicle_insured] += 1
        
        # Bystander expenditure
        bystander_exp = record.get('Bystander expenditure per day')
        if bystander_exp and bystander_exp != '0':
            try:
                bystander_expenses.append(float(bystander_exp))
            except (ValueError, TypeError):
                pass
    
    avg_income_change = sum(income_changes) / len(income_changes) if income_changes else 0.0
    avg_bystander_exp = sum(bystander_expenses) / len(bystander_expenses) if bystander_expenses else 0.0
    avg_travel_exp = 0.0  # No travel expense field in schema
    
    return FinancialImpact(
        income_comparison=dict(income_comparison),
        avg_income_change=avg_income_change,
        family_status_dist=dict(family_status_dist),
        insurance_claim_dist=dict(insurance_claim_dist),
        avg_bystander_exp=avg_bystander_exp,
        avg_travel_exp=avg_travel_exp
    )

def _parse_income_range(income_str: str) -> Optional[float]:
    """Parse income range strings like '10000-15000' or 'Above 50000' to average values"""
    if not income_str or income_str == 'Victim not willing to share/ Unable to respond/  Early Discharge':
        return None
    
    income_str = income_str.strip().lower()
    
    # Handle ranges like "10000-15000"
    if '-' in income_str:
        try:
            parts = income_str.split('-')
            min_val = float(parts[0].strip())
            max_val = float(parts[1].strip())
            return (min_val + max_val) / 2
        except (ValueError, IndexError):
            pass
    
    # Handle "above X" or "over X"
    if 'above' in income_str or 'over' in income_str:
        try:
            # Extract number
            import re
            numbers = re.findall(r'\d+', income_str)
            if numbers:
                return float(numbers[0]) * 1.5  # Assume 50% above the threshold
        except ValueError:
            pass
    
    # Handle "below X" or "under X"
    if 'below' in income_str or 'under' in income_str:
        try:
            import re
            numbers = re.findall(r'\d+', income_str)
            if numbers:
                return float(numbers[0]) * 0.75  # Assume 25% below the threshold
        except ValueError:
            pass
    
    # Try to parse as direct number
    try:
        return float(income_str)
    except ValueError:
        return None

def _get_temporal_trends(accident_data: List[Dict[str, Any]]) -> TemporalTrends:
    """Get temporal trends analysis from data array"""
    
    # Initialize counters
    monthly_trends = defaultdict(int)
    daily_trends = defaultdict(int)
    
    # Process each accident record
    for record in accident_data:
        incident_date = record.get('incident at date')
        if incident_date:
            try:
                # Parse date - handle different formats
                if isinstance(incident_date, str):
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(incident_date.replace('Z', '+00:00'))
                else:
                    date_obj = incident_date
                
                # Monthly trends (1-12)
                monthly_trends[date_obj.month] += 1
                
                # Daily trends (0=Monday, 6=Sunday)
                daily_trends[date_obj.weekday()] += 1
                
            except (ValueError, TypeError, AttributeError):
                pass
    
    return TemporalTrends(
        monthly_trends=dict(monthly_trends),
        daily_trends=dict(daily_trends)
    )

def _get_data_quality(accident_data: List[Dict[str, Any]]) -> DataQuality:
    """Get data quality metrics from data array"""
    
    total_records = len(accident_data)
    complete_records = 0
    
    # Check completeness of key fields
    for record in accident_data:
        patient_data = record.get('Patient')
        
        # Check if key fields exist and are not default values
        has_date = record.get('incident at date') is not None
        has_patient = patient_data is not None
        has_gender = patient_data and patient_data.get('Gender') is not None if patient_data else False
        
        # Count as complete if we have basic required data
        if has_date and has_patient and has_gender:
            complete_records += 1
    
    completion_rate = (complete_records / total_records * 100) if total_records > 0 else 0
    
    quality_dist = {
        'Complete': complete_records,
        'Missing/Incomplete': total_records - complete_records
    }
    
    return DataQuality(
        quality_dist=quality_dist,
        total_records=total_records,
        completion_rate=completion_rate
    )

def _get_summary_statistics(accident_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get summary statistics from data array"""
    
    total_records = len(accident_data)
    
    # Peak accident hour
    hourly_counts = defaultdict(int)
    for record in accident_data:
        time_str = record.get('time of collision')
        if time_str and time_str != 'Victim Unable to recall the Time or Early Discharge':
            try:
                if ':' in time_str:
                    hour = int(time_str.split(':')[0])
                    if 'PM' in time_str.upper() and hour != 12:
                        hour += 12
                    elif 'AM' in time_str.upper() and hour == 12:
                        hour = 0
                    hourly_counts[hour] += 1
            except (ValueError, IndexError):
                pass
    
    peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else 0
    
    # Most common collision type
    collision_counts = defaultdict(int)
    for record in accident_data:
        collision = record.get('Collision with')
        if collision and collision != 'Victim not willing to share/ Unable to respond/  Early Discharge':
            collision_counts[collision] += 1
    
    common_collision = max(collision_counts.items(), key=lambda x: x[1])[0] if collision_counts else "Unknown"
    
    # Average income change
    income_changes = []
    for record in accident_data:
        income_before = record.get('Family monthly income before accident')
        income_after = record.get('Family monthly income after accident')
        
        if (income_before and income_before != 'Victim not willing to share/ Unable to respond/  Early Discharge' and
            income_after and income_after != 'Victim not willing to share/ Unable to respond/  Early Discharge'):
            try:
                before_val = _parse_income_range(income_before)
                after_val = _parse_income_range(income_after)
                
                if before_val is not None and after_val is not None:
                    change = after_val - before_val
                    income_changes.append(change)
            except (ValueError, TypeError):
                pass
    
    avg_income_change = sum(income_changes) / len(income_changes) if income_changes else 0.0
    
    return {
        'peak_hour': peak_hour,
        'common_collision': common_collision,
        'avg_income_change': avg_income_change,
        'total_records': total_records
    }

def _get_data_period(accident_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get the data period information from data array"""
    
    dates = []
    for record in accident_data:
        incident_date = record.get('incident at date')
        if incident_date:
            dates.append(incident_date)
    
    if dates:
        return {
            'start_date': min(dates),
            'end_date': max(dates),
            'total_records': len(accident_data)
        }
    
    return None