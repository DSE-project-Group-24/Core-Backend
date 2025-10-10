"""
Test script for the Discharge Outcome Prediction API integration
"""
import requests
import json

# API base URL
API_BASE_URL = "http://localhost:8000"

# Sample test data based on your model requirements
SAMPLE_TEST_DATA = {
    "current_hospital_name": "DGH – Kilinochchi",
    "family_current_status": "Moderately Affected",
    "type_of_injury_no_1": "fracture",
    "traveling_expenditure_per_day": "100-200",
    "first_hospital_name": "DGH – Kilinochchi",
    "date_of_birth": "1990-05-15",
    "site_of_injury_no1": "head injury",
    "approximate_speed": "40 - 80 km/h",
    "incident_at_time_and_date": "2023-10-15",
    "hospital_distance_from_home": "5-10 Km",
    "mode_of_transport_to_the_hospital": "Ambulance",
    "educational_qualification": "O/L or A/L",
    "time_taken_to_reach_hospital": "Less Than 15 Minutes",
    "any_other_hospital_admission_expenditure": "No Other Expenses",
    "site_of_injury_no_2": "no secondary injury found",
    "occupation": "Student",
    "family_monthly_income_before_accident": "30000-45000",
    "collision_with": "Motorbike",
    "life_style": "Living with care givers",
    "collision_force_from": "Front",
    "road_type": "Straight",
    "type_of_injury_no_2": "abrasion"
}

def test_discharge_outcome_api():
    """Test the discharge outcome prediction API endpoints"""
    
    print("🧪 Testing Discharge Outcome Prediction API Integration")
    print("=" * 60)
    
    try:
        # You'll need to get an authentication token first
        # For testing purposes, let's assume you have a way to get the token
        # You might need to modify this part based on your auth system
        
        headers = {
            "Content-Type": "application/json",
            # "Authorization": "Bearer YOUR_TOKEN_HERE"  # Add authentication if needed
        }
        
        # Test 1: Health check
        print("\n1️⃣ Testing model health check...")
        try:
            health_response = requests.get(
                f"{API_BASE_URL}/predictions/discharge-outcome/health",
                headers=headers
            )
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Health Status: {health_data.get('status', 'unknown')}")
                print(f"📊 Model Loaded: {health_data.get('model_loaded', False)}")
                print(f"🔢 Features Count: {health_data.get('features_count', 0)}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed. Make sure the server is running.")
            return
        
        # Test 2: Model info
        print("\n2️⃣ Testing model info endpoint...")
        try:
            info_response = requests.get(
                f"{API_BASE_URL}/predictions/discharge-outcome/model-info",
                headers=headers
            )
            if info_response.status_code == 200:
                info_data = info_response.json()
                print(f"✅ Model Type: {info_data.get('model_type', 'unknown')}")
                print(f"🎯 Classes: {info_data.get('classes', [])}")
                print(f"📈 Total Features: {info_data.get('total_features', 0)}")
            else:
                print(f"❌ Model info failed: {info_response.status_code}")
        except Exception as e:
            print(f"❌ Model info error: {str(e)}")
        
        # Test 3: Features list
        print("\n3️⃣ Testing features endpoint...")
        try:
            features_response = requests.get(
                f"{API_BASE_URL}/predictions/discharge-outcome/features",
                headers=headers
            )
            if features_response.status_code == 200:
                features_data = features_response.json()
                print(f"✅ Features loaded: {len(features_data.get('features', []))}")
                print("📋 First 5 features:")
                for i, feature in enumerate(features_data.get('features', [])[:5]):
                    print(f"   {i+1}. {feature}")
            else:
                print(f"❌ Features request failed: {features_response.status_code}")
        except Exception as e:
            print(f"❌ Features error: {str(e)}")
        
        # Test 4: Classes endpoint
        print("\n4️⃣ Testing classes endpoint...")
        try:
            classes_response = requests.get(
                f"{API_BASE_URL}/predictions/discharge-outcome/classes",
                headers=headers
            )
            if classes_response.status_code == 200:
                classes_data = classes_response.json()
                print(f"✅ Available classes: {classes_data.get('classes', [])}")
            else:
                print(f"❌ Classes request failed: {classes_response.status_code}")
        except Exception as e:
            print(f"❌ Classes error: {str(e)}")
        
        # Test 5: Prediction
        print("\n5️⃣ Testing prediction endpoint...")
        try:
            prediction_response = requests.post(
                f"{API_BASE_URL}/predictions/discharge-outcome",
                json=SAMPLE_TEST_DATA,
                headers=headers
            )
            
            if prediction_response.status_code == 200:
                result = prediction_response.json()
                print("✅ Prediction successful!")
                print(f"🎯 Predicted Outcome: {result.get('prediction', 'unknown')}")
                print("📊 Prediction Probabilities:")
                for class_name, prob in result.get('prediction_probabilities', {}).items():
                    print(f"   {class_name}: {prob:.4f}")
                print(f"🔧 Model Info: {result.get('model_info', {})}")
            else:
                print(f"❌ Prediction failed with status: {prediction_response.status_code}")
                try:
                    error_detail = prediction_response.json()
                    print(f"Error details: {error_detail}")
                except:
                    print(f"Error text: {prediction_response.text}")
                    
        except Exception as e:
            print(f"❌ Prediction error: {str(e)}")
        
        print("\n" + "=" * 60)
        print("🏁 API Testing Complete!")
        
    except Exception as e:
        print(f"❌ General error occurred: {str(e)}")

def print_api_documentation():
    """Print API documentation"""
    print("\n📚 API Documentation")
    print("=" * 60)
    print("Available endpoints:")
    print("1. POST /predictions/discharge-outcome")
    print("   - Predict discharge outcome")
    print("   - Requires authentication")
    print("   - Body: DischargeOutcomePredictionRequest")
    print()
    print("2. GET /predictions/discharge-outcome/model-info")
    print("   - Get model information")
    print("   - Requires authentication")
    print()
    print("3. GET /predictions/discharge-outcome/health")
    print("   - Check model health")
    print("   - Requires authentication")
    print()
    print("4. GET /predictions/discharge-outcome/features")
    print("   - Get model features list")
    print("   - Requires authentication")
    print()
    print("5. GET /predictions/discharge-outcome/classes")
    print("   - Get prediction classes")
    print("   - Requires authentication")

if __name__ == "__main__":
    print_api_documentation()
    
    user_input = input("\nDo you want to test the API? (y/n): ").strip().lower()
    if user_input == 'y':
        test_discharge_outcome_api()
    else:
        print("Skipping API tests. Make sure to test manually when ready!")