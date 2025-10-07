"""
Direct Analytics Test - Detailed Report
"""
from tests.test_config import test_config
import requests
import json

def test_analytics_detailed():
    """Comprehensive analytics endpoint testing"""
    
    print("🧪 ANALYTICS ENDPOINT TESTING REPORT")
    print("=" * 60)
    
    # 1. Server Status Check
    print("\n📡 SERVER STATUS CHECK")
    server_up = test_config.check_server_status()
    print(f"   Server Status: {'✅ RUNNING' if server_up else '❌ DOWN'}")
    
    if not server_up:
        print("❌ Cannot proceed - server is not running")
        return
    
    # 2. Authentication Test
    print("\n🔐 AUTHENTICATION TEST")
    auth_success = test_config.setup_auth_for_user_type('doctor')
    print(f"   Doctor Login: {'✅ SUCCESS' if auth_success else '❌ FAILED'}")
    
    if not auth_success:
        print("❌ Cannot test protected endpoints without authentication")
        return
    
    # 3. Main Analytics Endpoint Test
    print("\n📊 MAIN ANALYTICS ENDPOINT TEST")
    try:
        response = requests.get('http://localhost:8000/analytics', 
                              headers=test_config.headers, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS - Data received")
            print(f"   📈 Total Records: {data.get('total_records', 'N/A')}")
            print(f"   📋 Data Sections: {len(data.keys())}")
            
            # Analyze data structure
            print("\n   📂 DATA STRUCTURE ANALYSIS:")
            expected_sections = [
                'accident_characteristics',
                'demographics', 
                'medical_factors',
                'financial_impact',
                'temporal_trends',
                'data_quality'
            ]
            
            for section in expected_sections:
                if section in data:
                    section_type = type(data[section]).__name__
                    print(f"      ✅ {section}: {section_type}")
                else:
                    print(f"      ❌ {section}: Missing")
                    
        elif response.status_code == 401:
            print("   ❌ AUTHENTICATION FAILED")
        elif response.status_code == 403:
            print("   ❌ ACCESS FORBIDDEN")
        elif response.status_code == 404:
            print("   ❌ ENDPOINT NOT FOUND")
        else:
            print(f"   ⚠️ Unexpected Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print("   ❌ REQUEST TIMEOUT (>30 seconds)")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ REQUEST ERROR: {e}")
    
    # 4. Analytics Summary Endpoint Test
    print("\n📋 ANALYTICS SUMMARY ENDPOINT TEST")
    try:
        response = requests.get('http://localhost:8000/analytics/summary', 
                              headers=test_config.headers, timeout=20)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS - Summary data received")
            
            summary_fields = ['total_accidents', 'peak_accident_hour', 'most_common_collision']
            for field in summary_fields:
                if field in data:
                    print(f"      ✅ {field}: {data[field]}")
                else:
                    print(f"      ❌ {field}: Missing")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ REQUEST TIMEOUT")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # 5. Filter Options Endpoint Test
    print("\n🔍 FILTER OPTIONS ENDPOINT TEST")
    try:
        response = requests.get('http://localhost:8000/analytics/filters/options', 
                              headers=test_config.headers, timeout=15)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS - Filter options received")
            
            option_types = ['genders', 'ethnicities', 'collision_types', 'age_range']
            for option_type in option_types:
                if option_type in data:
                    count = len(data[option_type]) if isinstance(data[option_type], list) else 'N/A'
                    print(f"      ✅ {option_type}: {count} options")
                else:
                    print(f"      ❌ {option_type}: Missing")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # 6. Analytics with Filters Test
    print("\n🎯 ANALYTICS FILTERING TEST")
    filter_tests = [
        {"gender": "Male"},
        {"age_min": "25", "age_max": "45"},
        {"start_date": "2023-01-01", "end_date": "2023-12-31"}
    ]
    
    for filters in filter_tests:
        try:
            response = requests.get('http://localhost:8000/analytics', 
                                  params=filters,
                                  headers=test_config.headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('total_records', 0)
                print(f"   ✅ Filter {filters}: {records} records")
            else:
                print(f"   ❌ Filter {filters}: Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Filter {filters}: Error {e}")
    
    print("\n🎉 ANALYTICS TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_analytics_detailed()