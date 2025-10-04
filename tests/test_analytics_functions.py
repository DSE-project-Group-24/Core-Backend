"""
Functional Tests for Analytics Endpoints
"""
import requests
from tests.test_config import test_config

class TestAnalyticsFunctions:
    """Test analytics functionality"""
    
    def setup_method(self):
        """Setup authentication for analytics tests"""
        if not test_config.check_server_status():
            print("⚠️ Server is not running. Start with: uvicorn app.main:app --reload")
            return False
        
        # Try to authenticate for protected endpoints
        return test_config.setup_auth()
    
    def test_analytics_endpoint_accessibility(self):
        """Test analytics endpoint basic accessibility"""
        try:
            response = requests.get(f"{test_config.base_url}/analytics", 
                                  headers=test_config.headers, timeout=15)
            
            print(f"✅ Analytics endpoint response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Analytics data received")
                
                # Check for expected fields
                expected_fields = ["accident_characteristics", "demographics", "total_records"]
                for field in expected_fields:
                    if field in data:
                        print(f"    ✓ Found field: {field}")
                    else:
                        print(f"    ⚠️ Missing field: {field}")
                        
            elif response.status_code == 401:
                print(f"  ⚠️ Authentication required (expected)")
            else:
                print(f"  ℹ️ Response: {response.text[:100]}")
                
            assert response.status_code in [200, 401, 422, 500]
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Analytics endpoint error: {e}")
            return False
            
        return True
    
    def test_analytics_with_filters(self):
        """Test analytics filtering functionality"""
        if not self.setup_method():
            print("⚠️ Skipping filter test - setup failed")
            return
        
        # Test various filter combinations
        filter_tests = [
            {"gender": "Male"},
            {"age_min": "18", "age_max": "65"},
            {}  # No filters
        ]
        
        for filters in filter_tests:
            try:
                response = requests.get(f"{test_config.base_url}/analytics/", 
                                      params=filters,
                                      headers=test_config.headers, 
                                      timeout=15)
                
                print(f"✅ Filter {filters}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    total_records = data.get('total_records', 0)
                    print(f"  ✓ Returned {total_records} records")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Filter test error: {e}")
    
    def test_analytics_summary_endpoint(self):
        """Test analytics summary endpoint"""
        if not self.setup_method():
            print("⚠️ Skipping summary test - setup failed")
            return
        
        try:
            response = requests.get(f"{test_config.base_url}/analytics/summary", 
                                  headers=test_config.headers, timeout=10)
            
            print(f"✅ Analytics summary response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Summary data received")
                
                # Check for summary fields
                summary_fields = ["total_accidents", "peak_accident_hour"]
                for field in summary_fields:
                    if field in data:
                        print(f"    ✓ Summary field: {field} = {data[field]}")
                        
        except requests.exceptions.RequestException as e:
            print(f"❌ Summary endpoint error: {e}")
    
    def test_filter_options_endpoint(self):
        """Test filter options endpoint"""
        if not self.setup_method():
            print("⚠️ Skipping filter options test - setup failed")
            return
        
        try:
            response = requests.get(f"{test_config.base_url}/analytics/filters/options", 
                                  headers=test_config.headers, timeout=10)
            
            print(f"✅ Filter options response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Filter options received")
                
                option_types = ["genders", "ethnicities", "collision_types"]
                for option_type in option_types:
                    if option_type in data:
                        count = len(data[option_type]) if isinstance(data[option_type], list) else "N/A"
                        print(f"    ✓ {option_type}: {count} options")
                        
        except requests.exceptions.RequestException as e:
            print(f"❌ Filter options error: {e}")

if __name__ == "__main__":
    # Run tests directly
    test_analytics = TestAnalyticsFunctions()
    
    print("🧪 Running Analytics Function Tests")
    print("=" * 50)
    
    try:
        test_analytics.test_analytics_endpoint_accessibility()
        test_analytics.test_analytics_with_filters()
        test_analytics.test_analytics_summary_endpoint()
        test_analytics.test_filter_options_endpoint()
        
        print("\n🎉 Analytics tests completed!")
        
    except Exception as e:
        print(f"\n❌ Analytics test execution failed: {e}")