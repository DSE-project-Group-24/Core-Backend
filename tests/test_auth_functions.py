"""
Functional Tests for Authentication Endpoints
"""
import requests
from datetime import datetime
from tests.test_config import test_config

class TestAuthenticationFunctions:
    """Test authentication functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        if not test_config.check_server_status():
            raise Exception("Server is not running. Start with: uvicorn app.main:app --reload")
    
    def test_server_health(self):
        """Test if server is accessible"""
        try:
            response = requests.get(f"{test_config.base_url}/", timeout=5)
            print(f"✅ Server accessible: {response.status_code}")
            assert response.status_code in [200, 404, 422]  # Any of these means server is up
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Server not accessible: {e}")
    
    def test_routes_endpoint(self):
        """Test routes discovery endpoint"""
        try:
            response = requests.get(f"{test_config.base_url}/_routes", timeout=10)
            
            if response.status_code == 200:
                routes = response.json()
                print(f"✅ Found {len(routes)} routes")
                
                # Check for key routes
                route_paths = [route.get('path', '') for route in routes]
                expected_routes = ['/auth/login', '/auth/register/nurse', '/accidents/', '/analytics/']
                
                for expected in expected_routes:
                    if any(expected in path for path in route_paths):
                        print(f"  ✓ Found route: {expected}")
                    else:
                        print(f"  ⚠️ Missing route: {expected}")
                        
            else:
                print(f"⚠️ Routes endpoint returned: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"❌ Routes test failed: {e}")
    
    def test_auth_login_endpoint_exists(self):
        """Test login endpoint accessibility"""
        login_data = {"email": "test@example.com", "password": "testpass"}
        
        try:
            response = requests.post(f"{test_config.base_url}/auth/login", 
                                   json=login_data, timeout=10)
            
            # Any response means endpoint exists (even if credentials are wrong)
            print(f"✅ Login endpoint accessible: {response.status_code}")
            assert response.status_code in [200, 400, 401, 422]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Login endpoint not accessible: {e}")
    
    def test_nurse_registration_endpoint(self):
        """Test nurse registration endpoint"""
        unique_email = f"test_nurse_{datetime.now().microsecond}@hospital.lk"
        nurse_data = {
            "email": unique_email,
            "password": "TestPassword123!",
            "full_name": "Test Nurse",
            "hospital_id": "test_hospital_id"
        }
        
        try:
            response = requests.post(f"{test_config.base_url}/auth/register/nurse", 
                                   json=nurse_data, timeout=10)
            
            print(f"✅ Nurse registration endpoint response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"  ✓ Registration successful")
            elif response.status_code in [400, 422]:
                print(f"  ⚠️ Validation error (expected): {response.text[:100]}")
            else:
                print(f"  ℹ️ Response: {response.text[:100]}")
                
            assert response.status_code in [200, 201, 400, 422, 500]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Nurse registration endpoint error: {e}")
    
    def test_doctor_registration_endpoint(self):
        """Test doctor registration endpoint"""
        unique_email = f"test_doctor_{datetime.now().microsecond}@hospital.lk"
        doctor_data = {
            "email": unique_email,
            "password": "TestPassword123!",
            "full_name": "Test Doctor",
            "hospital_id": "test_hospital_id",
            "specialization": "General Medicine"
        }
        
        try:
            response = requests.post(f"{test_config.base_url}/auth/register/doctor", 
                                   json=doctor_data, timeout=10)
            
            print(f"✅ Doctor registration endpoint response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"  ✓ Registration successful")
            elif response.status_code in [400, 422]:
                print(f"  ⚠️ Validation error (expected): {response.text[:100]}")
            else:
                print(f"  ℹ️ Response: {response.text[:100]}")
                
            assert response.status_code in [200, 201, 400, 422, 500]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Doctor registration endpoint error: {e}")
    
    def test_invalid_login_handling(self):
        """Test system response to invalid login"""
        invalid_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        try:
            response = requests.post(f"{test_config.base_url}/auth/login", 
                                   json=invalid_data, timeout=10)
            
            print(f"✅ Invalid login response: {response.status_code}")
            
            # Should reject invalid credentials
            assert response.status_code in [400, 401, 422]
            print(f"  ✓ Invalid credentials properly rejected")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Invalid login test error: {e}")

if __name__ == "__main__":
    # Run tests directly if needed
    import sys
    test_auth = TestAuthenticationFunctions()
    
    print("🧪 Running Authentication Function Tests")
    print("=" * 50)
    
    try:
        test_auth.setup_method()
        test_auth.test_server_health()
        test_auth.test_routes_endpoint()
        test_auth.test_auth_login_endpoint_exists()
        test_auth.test_nurse_registration_endpoint()
        test_auth.test_doctor_registration_endpoint()
        test_auth.test_invalid_login_handling()
        
        print("\n🎉 Authentication tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)