"""
Complete Functional Test Suite Runner
Run all functional tests for the Core-Backend system
"""
import sys
import time
from tests.test_config import test_config
from tests.test_auth_functions import TestAuthenticationFunctions
from tests.test_analytics_functions import TestAnalyticsFunctions
from tests.test_prediction_functions import TestPredictionFunctions

def run_test_class(test_class, class_name):
    """Run all test methods in a test class"""
    print(f"\n🔍 Testing {class_name}")
    print("-" * 50)
    
    instance = test_class()
    test_methods = [method for method in dir(instance) if method.startswith('test_')]
    
    passed = 0
    total = len(test_methods)
    
    for method_name in test_methods:
        try:
            print(f"\n📋 Running {method_name.replace('test_', '').replace('_', ' ').title()}")
            test_method = getattr(instance, method_name)
            test_method()
            passed += 1
            print(f"   ✅ PASSED")
            
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"\n📊 {class_name} Results: {passed}/{total} passed ({success_rate:.1f}%)")
    
    return passed, total

def main():
    """Run complete functional test suite"""
    print("=" * 70)
    print("🧪 CORE-BACKEND FUNCTIONAL TEST SUITE")
    print("=" * 70)
    
    # Check server status first
    print("🔍 Checking server status...")
    if not test_config.check_server_status():
        print("❌ Server is not running!")
        print("💡 Start your server first with: uvicorn app.main:app --reload")
        print("   Then run this test again.")
        return False
    
    print("✅ Server is accessible")
    
    # Test categories to run
    test_classes = [
        (TestAuthenticationFunctions, "Authentication Functions"),
        (TestAnalyticsFunctions, "Analytics Functions"),
        (TestPredictionFunctions, "Prediction Functions")
    ]
    
    total_passed = 0
    total_tests = 0
    results = {}
    
    start_time = time.time()
    
    # Run each test category
    for test_class, class_name in test_classes:
        try:
            passed, total = run_test_class(test_class, class_name)
            total_passed += passed
            total_tests += total
            
            results[class_name] = {
                'passed': passed,
                'total': total,
                'success_rate': (passed / total) * 100 if total > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ {class_name} execution failed: {e}")
            results[class_name] = {'passed': 0, 'total': 0, 'success_rate': 0}
    
    # Generate final report
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("📈 FUNCTIONAL TEST SUMMARY REPORT")
    print("=" * 70)
    
    overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    for category, result in results.items():
        if result['success_rate'] >= 80:
            status = "✅ EXCELLENT"
        elif result['success_rate'] >= 60:
            status = "⚠️ GOOD"
        elif result['success_rate'] >= 40:
            status = "⚠️ NEEDS WORK"
        else:
            status = "❌ CRITICAL"
            
        print(f"{status} {category}: {result['passed']}/{result['total']} ({result['success_rate']:.1f}%)")
    
    print(f"\n🎯 Overall Results: {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
    print(f"⏱️ Test Duration: {duration:.1f} seconds")
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    if overall_success_rate >= 85:
        print("✅ Excellent! Your system is functioning well.")
        print("   Ready for integration testing and deployment.")
    elif overall_success_rate >= 70:
        print("✅ Good progress! Most functions are working.")
        print("   Address failing tests before production deployment.")
    elif overall_success_rate >= 50:
        print("⚠️ Some issues found. Review failed tests.")
        print("   Focus on critical authentication and data handling.")
    else:
        print("❌ Significant issues detected!")
        print("   Review server logs and database connections.")
        print("   Ensure all dependencies are installed and configured.")
    
    # Next steps
    print(f"\n🚀 NEXT STEPS:")
    print("1. Review any failed tests above")
    print("2. Check server logs for detailed error messages")
    print("3. Verify database connections and model files")
    print("4. Test with real user scenarios")
    
    return overall_success_rate >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)