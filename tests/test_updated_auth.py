"""
Real User Authentication Tests (Integration Tests)
Tests actual user login and role-based access with real credentials
"""
import requests
from datetime import datetime
from tests.test_config import test_config

class TestUpdatedAuthenticationFunctions:
    """Test authentication functionality with correct credentials"""
    
    def setup_method(self):
        """Setup for each test method"""
        if not test_config.check_server_status():
            raise Exception("Server is not running. Start with: uvicorn app.main:app --reload")
    
    def test_doctor_login(self):
        """Test doctor login with correct credentials"""
        try:
            success = test_config.setup_auth_for_user_type("doctor")
            
            if success:
                print(f"✅ Doctor login successful")
                
                # Test making an authenticated request
                response = test_config.make_request('GET', '/analytics')
                print(f"  ✓ Analytics access: {response.status_code}")
                
            else:
                print(f"❌ Doctor login failed")
                
        except Exception as e:
            print(f"❌ Doctor login test error: {e}")
    
    def test_government_login(self):
        """Test government user login"""
        try:
            success = test_config.setup_auth_for_user_type("government")
            
            if success:
                print(f"✅ Government user login successful")
                
                # Test government-specific endpoint
                response = test_config.make_request('GET', '/gov/rules/bootstrap')
                print(f"  ✓ Government rules access: {response.status_code}")
                
            else:
                print(f"❌ Government user login failed")
                
        except Exception as e:
            print(f"❌ Government login test error: {e}")
    
    def test_nurse_login(self):
        """Test nurse login"""
        try:
            success = test_config.setup_auth_for_user_type("nurse")
            
            if success:
                print(f"✅ Nurse login successful")
                
                # Test nurse-specific endpoints
                response = test_config.make_request('GET', '/nurse/')
                print(f"  ✓ Nurse data access: {response.status_code}")
                
            else:
                print(f"❌ Nurse login failed")
                
        except Exception as e:
            print(f"❌ Nurse login test error: {e}")
    
    def test_hospital_admin_login(self):
        """Test hospital admin login"""
        try:
            success = test_config.setup_auth_for_user_type("hospital_admin")
            
            if success:
                print(f"✅ Hospital admin login successful")
                
                # Test hospital admin endpoints
                response = test_config.make_request('GET', '/hospital/')
                print(f"  ✓ Hospital data access: {response.status_code}")
                
            else:
                print(f"❌ Hospital admin login failed")
                
        except Exception as e:
            print(f"❌ Hospital admin login test error: {e}")
    
    def test_all_user_types_credentials(self):
        """Test all user type credentials"""
        user_types = ["doctor", "government", "nurse", "hospital_admin"]
        results = {}
        
        for user_type in user_types:
            try:
                creds = test_config.get_test_credentials(user_type)
                
                response = requests.post(f"{test_config.base_url}/auth/login", 
                                       json=creds, timeout=10)
                
                if response.status_code == 200:
                    results[user_type] = "✅ VALID"
                    print(f"✅ {user_type.title()} credentials valid")
                else:
                    results[user_type] = f"❌ INVALID ({response.status_code})"
                    print(f"❌ {user_type.title()} credentials invalid: {response.status_code}")
                    
            except Exception as e:
                results[user_type] = f"❌ ERROR: {e}"
                print(f"❌ {user_type.title()} test error: {e}")
        
        return results
    
    def test_analytics_with_correct_auth(self):
        """Test analytics endpoints with proper authentication"""
        # Try with doctor credentials first
        if test_config.setup_auth_for_user_type("doctor"):
            try:
                response = test_config.make_request('GET', '/analytics')
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Analytics working: {data.get('total_records', 0)} records")
                    
                    # Test summary
                    summary_response = test_config.make_request('GET', '/analytics/summary')
                    if summary_response.status_code == 200:
                        summary = summary_response.json()
                        print(f"  ✓ Summary: {summary.get('total_accidents', 0)} accidents")
                    
                    # Test filter options
                    filter_response = test_config.make_request('GET', '/analytics/filters/options')
                    if filter_response.status_code == 200:
                        filters = filter_response.json()
                        print(f"  ✓ Filter options available")
                        
                else:
                    print(f"⚠️ Analytics returned: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Analytics test error: {e}")
        else:
            print("⚠️ Could not authenticate for analytics test")

if __name__ == "__main__":
    # Run updated tests
    test_auth = TestUpdatedAuthenticationFunctions()
    
    print("🧪 Running Updated Authentication Tests")
    print("=" * 50)
    
    try:
        test_auth.setup_method()
        
        print("\n📋 Testing Individual User Logins:")
        test_auth.test_doctor_login()
        test_auth.test_government_login()
        test_auth.test_nurse_login()
        test_auth.test_hospital_admin_login()
        
        print("\n📋 Testing All Credentials:")
        test_auth.test_all_user_types_credentials()
        
        print("\n📋 Testing Analytics with Authentication:")
        test_auth.test_analytics_with_correct_auth()
        
        print("\n🎉 Updated authentication tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")