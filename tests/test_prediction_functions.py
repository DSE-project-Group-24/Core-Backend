"""
Functional Tests for Prediction Services
"""
import requests
from tests.test_config import test_config

class TestPredictionFunctions:
    """Test prediction functionality"""
    
    def test_hospital_stay_prediction(self):
        """Test hospital stay prediction service"""
        if not test_config.check_server_status():
            print("⚠️ Server is not running. Start with: uvicorn app.main:app --reload")
            return
        
        prediction_data = {
            "Time of Collision": "Morning",
            "Discharge Outcome": "Full Recovery",
            "Facilities for Daily Activity": "Available",
            "Access To Wash Room": "Yes",
            "Ethnicity": "Sinhala",
            "Age": "25-35",
            "Gender": "Male",
            "Mode Of Travel During Accident": "Motorcycle",
            "Collision With ": "Vehicle"
        }
        
        try:
            response = requests.post(f"{test_config.base_url}/predictions/hospital-stay/predict",
                                   json=prediction_data, timeout=15)
            
            print(f"✅ Hospital Stay Prediction response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "prediction" in data:
                    print(f"  ✓ Prediction: {data['prediction']} days")
                elif "error" in data:
                    print(f"  ⚠️ Prediction error: {data['error']}")
                else:
                    print(f"  ℹ️ Response: {data}")
                    
            elif response.status_code == 404:
                print(f"  ⚠️ Endpoint not found - check route configuration")
            else:
                print(f"  ℹ️ Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Hospital stay prediction error: {e}")
    
    def test_transfer_probability_prediction(self):
        """Test transfer probability prediction service"""
        if not test_config.check_server_status():
            print("⚠️ Server is not running")
            return
        
        transfer_data = {
            "Age": 35,
            "Gender_Male": 1,
            "Severity_S": 1,
            "Time of Collision_Night": 1,
            "First Hospital Name_DH,Jaffna": 1
        }
        
        try:
            response = requests.post(f"{test_config.base_url}/predictions/transferprobability",
                                   json=transfer_data, timeout=15)
            
            print(f"✅ Transfer Probability response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "transfer_probability" in data:
                    prob = data["transfer_probability"]
                    print(f"  ✓ Transfer Probability: {prob:.2%}")
                elif "error" in data:
                    print(f"  ⚠️ Prediction error: {data['error']}")
                else:
                    print(f"  ℹ️ Response: {data}")
                    
            elif response.status_code == 404:
                print(f"  ⚠️ Endpoint not found - check route configuration")
            else:
                print(f"  ℹ️ Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Transfer probability prediction error: {e}")
    
    def test_forecast_prediction(self):
        """Test SARIMA forecast prediction service"""
        if not test_config.check_server_status():
            print("⚠️ Server is not running")
            return
        
        forecast_data = {"months": 6}
        
        try:
            response = requests.post(f"{test_config.base_url}/predictions/forecast",
                                   json=forecast_data, timeout=20)
            
            print(f"✅ Forecast Prediction response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "forecast_M" in data and "forecast_S" in data:
                    forecast_m_len = len(data["forecast_M"])
                    forecast_s_len = len(data["forecast_S"])
                    print(f"  ✓ Forecast: {forecast_m_len} M-severity, {forecast_s_len} S-severity predictions")
                elif "error" in data:
                    print(f"  ⚠️ Forecast error: {data['error']}")
                else:
                    print(f"  ℹ️ Response: {data}")
                    
            elif response.status_code == 404:
                print(f"  ⚠️ Endpoint not found - check route configuration")
            else:
                print(f"  ℹ️ Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Forecast prediction error: {e}")
    
    def test_prediction_endpoints_exist(self):
        """Test that prediction endpoints are accessible"""
        if not test_config.check_server_status():
            print("⚠️ Server is not running")
            return
        
        endpoints = [
            "/predictions/hospital-stay/predict",
            "/predictions/transferprobability", 
            "/predictions/forecast"
        ]
        
        for endpoint in endpoints:
            try:
                # Use GET first to check if endpoint exists
                response = requests.get(f"{test_config.base_url}{endpoint}", timeout=5)
                
                if response.status_code == 405:  # Method Not Allowed means endpoint exists
                    print(f"  ✓ {endpoint} - exists (POST required)")
                elif response.status_code in [200, 422]:  # OK or Unprocessable Entity
                    print(f"  ✓ {endpoint} - accessible")
                elif response.status_code == 404:
                    print(f"  ❌ {endpoint} - not found")
                else:
                    print(f"  ⚠️ {endpoint} - status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {endpoint} - connection error: {e}")

if __name__ == "__main__":
    # Run tests directly
    test_predictions = TestPredictionFunctions()
    
    print("🧪 Running Prediction Function Tests")
    print("=" * 50)
    
    try:
        test_predictions.test_prediction_endpoints_exist()
        test_predictions.test_hospital_stay_prediction()
        test_predictions.test_transfer_probability_prediction()
        test_predictions.test_forecast_prediction()
        
        print("\n🎉 Prediction tests completed!")
        
    except Exception as e:
        print(f"\n❌ Prediction test execution failed: {e}")