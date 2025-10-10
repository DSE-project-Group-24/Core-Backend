"""
Example integration: Combining Accident Records with Discharge Outcome Prediction

This example shows how you could potentially integrate the discharge outcome prediction
with your existing accident record system.
"""

from typing import Optional
from app.models.accident import AccidentRecordOut
from app.models.discharge_outcome import DischargeOutcomePredictionRequest
from app.services.discharge_outcome_service import predict_discharge_outcome_service

def create_discharge_prediction_from_accident_record(
    accident_record: AccidentRecordOut,
    patient_data: dict = None  # Additional patient data if needed
) -> Optional[dict]:
    """
    Create a discharge outcome prediction request from an accident record.
    
    This function maps accident record fields to the prediction model fields.
    Some fields might need additional patient data that's not in the accident record.
    """
    
    try:
        # Map accident record fields to prediction request fields
        prediction_request_data = {
            # Direct mappings from accident record
            "approximate_speed": getattr(accident_record, 'approximate_speed', None),
            "mode_of_transport_to_the_hospital": getattr(accident_record, 'mode_of_transport', None),
            "time_taken_to_reach_hospital": getattr(accident_record, 'time_to_hospital', None),
            "hospital_distance_from_home": getattr(accident_record, 'hospital_distance_from_home', None),
            "traveling_expenditure_per_day": getattr(accident_record, 'traveling_expenditure_per_day', None),
            "any_other_hospital_admission_expenditure": getattr(accident_record, 'any_other_hospital_admission_expenditure', None),
            "family_monthly_income_before_accident": getattr(accident_record, 'income_before_accident', None),
            "collision_with": getattr(accident_record, 'collision_with', None),
            "life_style": getattr(accident_record, 'life_style', None) if hasattr(accident_record, 'life_style') else None,
            "collision_force_from": getattr(accident_record, 'collision_force_from', None),
            "road_type": getattr(accident_record, 'road_type', None),
            "family_current_status": getattr(accident_record, 'family_status', None),
            
            # Date fields - these would need to be extracted from accident record dates
            "incident_at_time_and_date": getattr(accident_record, 'incident_at_date', None),
            
            # These fields would typically come from patient data
            "current_hospital_name": patient_data.get('current_hospital_name') if patient_data else None,
            "first_hospital_name": patient_data.get('first_hospital_name') if patient_data else None,
            "date_of_birth": patient_data.get('date_of_birth') if patient_data else None,
            "educational_qualification": patient_data.get('educational_qualification') if patient_data else None,
            "occupation": patient_data.get('occupation') if patient_data else None,
            
            # These would need medical record data (not typically in accident records)
            "type_of_injury_no_1": None,  # Would come from medical records
            "site_of_injury_no1": None,   # Would come from medical records
            "site_of_injury_no_2": None,  # Would come from medical records
            "type_of_injury_no_2": None,  # Would come from medical records
        }
        
        # Create the prediction request
        prediction_request = DischargeOutcomePredictionRequest(**prediction_request_data)
        
        # Make the prediction
        prediction_result = predict_discharge_outcome_service(prediction_request)
        
        return {
            "accident_id": getattr(accident_record, 'accident_id', None),
            "patient_id": getattr(accident_record, 'patient_id', None),
            "discharge_prediction": prediction_result,
            "data_completeness": _calculate_data_completeness(prediction_request_data)
        }
        
    except Exception as e:
        print(f"Error creating discharge prediction: {str(e)}")
        return None

def _calculate_data_completeness(data: dict) -> dict:
    """Calculate how complete the data is for prediction"""
    total_fields = len(data)
    filled_fields = sum(1 for value in data.values() if value is not None and value != "")
    
    return {
        "total_fields": total_fields,
        "filled_fields": filled_fields,
        "completeness_percentage": (filled_fields / total_fields) * 100 if total_fields > 0 else 0,
        "missing_fields": [key for key, value in data.items() if value is None or value == ""]
    }

# Example usage function
def example_usage():
    """
    Example of how this integration might be used in a real scenario
    """
    
    # This would typically come from your accident service
    # accident_record = get_accident_record_by_id_service("some-accident-id")
    
    # This would typically come from your patient service  
    # patient_data = get_patient_by_id_service("some-patient-id")
    
    # For example purposes, let's create mock data
    class MockAccidentRecord:
        def __init__(self):
            self.accident_id = "acc-123"
            self.patient_id = "pat-456"
            self.approximate_speed = "40 - 80 km/h"
            self.mode_of_transport = "Ambulance"
            self.time_to_hospital = "Less Than 15 Minutes"
            self.hospital_distance_from_home = "5-10 Km"
            self.traveling_expenditure_per_day = "100-200"
            self.any_other_hospital_admission_expenditure = "No Other Expenses"
            self.income_before_accident = "30000-45000"
            self.collision_with = "Motorbike"
            self.collision_force_from = "Front"
            self.road_type = "Straight"
            self.family_status = "Moderately Affected"
            self.incident_at_date = "2023-10-15"
    
    mock_accident = MockAccidentRecord()
    
    mock_patient_data = {
        "current_hospital_name": "DGH – Kilinochchi",
        "first_hospital_name": "DGH – Kilinochchi", 
        "date_of_birth": "1990-05-15",
        "educational_qualification": "O/L or A/L",
        "occupation": "Student"
    }
    
    # Create discharge prediction
    result = create_discharge_prediction_from_accident_record(
        mock_accident, 
        mock_patient_data
    )
    
    if result:
        print("✅ Discharge prediction created successfully!")
        print(f"🎯 Predicted outcome: {result['discharge_prediction']['prediction']}")
        print(f"📊 Data completeness: {result['data_completeness']['completeness_percentage']:.1f}%")
        print(f"🔍 Missing fields: {len(result['data_completeness']['missing_fields'])}")
    else:
        print("❌ Failed to create discharge prediction")

if __name__ == "__main__":
    print("📋 Example: Integrating Accident Records with Discharge Prediction")
    print("=" * 70)
    example_usage()