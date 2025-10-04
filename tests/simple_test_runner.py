"""
Quick test runner - no external dependencies required
Run individual test modules directly
"""
import sys
import os

# Add parent directory to path so we can import from tests
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def run_auth_tests():
    """Run authentication tests"""
    from tests.test_auth_functions import TestAuthenticationFunctions
    
    print("🧪 Running Authentication Tests")
    print("=" * 40)
    
    test_auth = TestAuthenticationFunctions()
    
    tests = [
        ('Server Health', test_auth.test_server_health),
        ('Routes Discovery', test_auth.test_routes_endpoint),
        ('Login Endpoint', test_auth.test_auth_login_endpoint_exists),
        ('Nurse Registration', test_auth.test_nurse_registration_endpoint),
        ('Doctor Registration', test_auth.test_doctor_registration_endpoint),
        ('Invalid Login Handling', test_auth.test_invalid_login_handling)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}")
            test_auth.setup_method()
            test_func()
            print(f"   ✅ PASSED")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")

def run_analytics_tests():
    """Run analytics tests"""
    from tests.test_analytics_functions import TestAnalyticsFunctions
    
    print("\n🧪 Running Analytics Tests")
    print("=" * 40)
    
    test_analytics = TestAnalyticsFunctions()
    
    tests = [
        ('Analytics Endpoint', test_analytics.test_analytics_endpoint_accessibility),
        ('Analytics Filters', test_analytics.test_analytics_with_filters),
        ('Summary Endpoint', test_analytics.test_analytics_summary_endpoint),
        ('Filter Options', test_analytics.test_filter_options_endpoint)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}")
            test_func()
            print(f"   ✅ PASSED")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")

def run_updated_auth_tests():
    """Run updated authentication tests with correct credentials"""
    from tests.test_updated_auth import TestUpdatedAuthenticationFunctions
    
    print("\n🧪 Running Updated Authentication Tests")
    print("=" * 40)
    
    test_auth = TestUpdatedAuthenticationFunctions()
    
    tests = [
        ('Doctor Login', test_auth.test_doctor_login),
        ('Government Login', test_auth.test_government_login),
        ('Nurse Login', test_auth.test_nurse_login),
        ('Hospital Admin Login', test_auth.test_hospital_admin_login),
        ('All Credentials Check', test_auth.test_all_user_types_credentials),
        ('Analytics with Auth', test_auth.test_analytics_with_correct_auth)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}")
            test_auth.setup_method()
            test_func()
            print(f"   ✅ PASSED")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")

def run_prediction_tests():
    """Run prediction tests"""
    from tests.test_prediction_functions import TestPredictionFunctions
    
    print("\n🧪 Running Prediction Tests")
    print("=" * 40)
    
    test_predictions = TestPredictionFunctions()
    
    tests = [
        ('Endpoint Accessibility', test_predictions.test_prediction_endpoints_exist),
        ('Hospital Stay Prediction', test_predictions.test_hospital_stay_prediction),
        ('Transfer Probability', test_predictions.test_transfer_probability_prediction),
        ('Forecast Prediction', test_predictions.test_forecast_prediction)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}")
            test_func()
            print(f"   ✅ PASSED")
        except Exception as e:
            print(f"   ❌ FAILED: {e}")

def main():
    """Main test runner"""
    print("🚀 Core-Backend Functional Tests")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'auth':
            run_auth_tests()
        elif test_type == 'updated_auth':
            run_updated_auth_tests()
        elif test_type == 'analytics':
            run_analytics_tests()
        elif test_type == 'predictions':
            run_prediction_tests()
        else:
            print("Usage: python simple_test_runner.py [auth|updated_auth|analytics|predictions]")
    else:
        # Run all tests
        run_auth_tests()
        run_updated_auth_tests()
        run_analytics_tests()
        run_prediction_tests()
    
    print("\n🎉 Test execution completed!")

if __name__ == "__main__":
    main()