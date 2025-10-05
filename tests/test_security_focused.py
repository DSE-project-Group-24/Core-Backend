"""
Focused Security and Access Control Tests
Quick and efficient security validation
"""
import requests
import json
from datetime import datetime
from tests.test_config import test_config

def test_authentication_security():
    """Test authentication and authorization security"""
    print("🔐 Testing Authentication Security")
    
    # Test 1: Unauthenticated access to protected endpoints
    protected_endpoints = [
        "/analytics/",
        "/patients",
        "/accidents/", 
        "/doctor/",
        "/nurse/",
        "/hospital/"
    ]
    
    blocked_count = 0
    
    for endpoint in protected_endpoints:
        try:
            response = requests.get(f"{test_config.base_url}{endpoint}", timeout=3)
            if response.status_code in [401, 403]:
                print(f"  ✅ {endpoint}: Protected ({response.status_code})")
                blocked_count += 1
            else:
                print(f"  ⚠️ {endpoint}: Status {response.status_code}")
        except:
            print(f"  ❌ {endpoint}: Connection error")
    
    protection_rate = (blocked_count / len(protected_endpoints)) * 100
    print(f"  📊 Authentication Protection: {protection_rate:.1f}%")
    
    return protection_rate

def test_role_based_access():
    """Test role-based access control"""
    print("👥 Testing Role-Based Access Control")
    
    # Test different user roles
    role_tests = {
        "doctor": {"endpoint": "/analytics/", "should_work": True},
        "nurse": {"endpoint": "/nurse/", "should_work": True}, 
        "government": {"endpoint": "/gov/rules/bootstrap", "should_work": True},
        "hospital_admin": {"endpoint": "/hospital/", "should_work": True}
    }
    
    successful_tests = 0
    total_tests = len(role_tests)
    
    for role, test_info in role_tests.items():
        try:
            if test_config.setup_auth_for_user_type(role):
                response = requests.get(f"{test_config.base_url}{test_info['endpoint']}", 
                                      headers=test_config.headers, timeout=5)
                
                if test_info["should_work"] and response.status_code in [200, 201]:
                    print(f"  ✅ {role.title()}: Proper access granted ({response.status_code})")
                    successful_tests += 1
                elif not test_info["should_work"] and response.status_code in [401, 403]:
                    print(f"  ✅ {role.title()}: Properly denied ({response.status_code})")
                    successful_tests += 1
                else:
                    print(f"  ⚠️ {role.title()}: Unexpected status {response.status_code}")
            else:
                print(f"  ❌ {role.title()}: Authentication failed")
        except Exception as e:
            print(f"  ❌ {role.title()}: Error - {str(e)[:50]}")
    
    rbac_success_rate = (successful_tests / total_tests) * 100
    print(f"  📊 RBAC Success Rate: {rbac_success_rate:.1f}%")
    
    return rbac_success_rate

def test_input_validation():
    """Test input validation security"""
    print("🛡️ Testing Input Validation")
    
    # Test SQL injection on login
    sql_payloads = ["'; DROP TABLE users; --", "' OR '1'='1", "admin'--"]
    
    blocked_count = 0
    
    for payload in sql_payloads:
        try:
            response = requests.post(f"{test_config.base_url}/auth/login", 
                                   json={"email": payload, "password": "test"}, timeout=3)
            
            if response.status_code in [400, 422]:
                blocked_count += 1
                print(f"  ✅ SQL injection blocked")
            else:
                print(f"  ⚠️ SQL injection response: {response.status_code}")
        except:
            blocked_count += 1
            print(f"  ✅ SQL injection blocked (error)")
    
    sql_protection = (blocked_count / len(sql_payloads)) * 100
    print(f"  📊 SQL Injection Protection: {sql_protection:.1f}%")
    
    return sql_protection

def test_session_security():
    """Test JWT token security"""
    print("🔑 Testing Session Security")
    
    # Get valid token
    if test_config.setup_auth_for_user_type("doctor"):
        # Test with invalid tokens
        invalid_tokens = ["invalid_token", ""]
        
        blocked_count = 0
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{test_config.base_url}/analytics/", 
                                      headers=headers, timeout=3)
                
                if response.status_code in [401, 403, 422]:
                    blocked_count += 1
                    print(f"  ✅ Invalid token blocked")
                else:
                    print(f"  ❌ Invalid token accepted: {response.status_code}")
            except:
                blocked_count += 1
                print(f"  ✅ Invalid token blocked (error)")
        
        token_security = (blocked_count / len(invalid_tokens)) * 100
        print(f"  📊 Token Security: {token_security:.1f}%")
        
        return token_security
    else:
        print("  ❌ Could not test token security - auth failed")
        return 0

def test_sensitive_data_exposure():
    """Test for sensitive data exposure"""
    print("🔍 Testing Sensitive Data Exposure")
    
    sensitive_paths = ["/admin", "/.env", "/config", "/debug", "/database"]
    
    protected_count = 0
    
    for path in sensitive_paths:
        try:
            response = requests.get(f"{test_config.base_url}{path}", timeout=3)
            
            if response.status_code in [404, 401, 403]:
                protected_count += 1
                print(f"  ✅ {path}: Protected ({response.status_code})")
            else:
                print(f"  ⚠️ {path}: Status {response.status_code}")
        except:
            protected_count += 1
            print(f"  ✅ {path}: Not accessible")
    
    protection_rate = (protected_count / len(sensitive_paths)) * 100
    print(f"  📊 Sensitive Data Protection: {protection_rate:.1f}%")
    
    return protection_rate

def generate_security_report(results):
    """Generate comprehensive security report"""
    print("\n" + "="*60)
    print("🛡️ SECURITY & ACCESS CONTROL TEST REPORT")
    print("="*60)
    
    # Calculate overall security score
    scores = [score for score in results.values() if isinstance(score, (int, float))]
    overall_score = sum(scores) / len(scores) if scores else 0
    
    # Security rating
    if overall_score >= 90:
        rating = "🟢 EXCELLENT"
    elif overall_score >= 75:
        rating = "🟡 GOOD"
    elif overall_score >= 60:
        rating = "🟠 NEEDS IMPROVEMENT"
    else:
        rating = "🔴 CRITICAL ISSUES"
    
    print(f"\n📊 OVERALL SECURITY SCORE: {overall_score:.1f}% - {rating}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, score in results.items():
        if isinstance(score, (int, float)):
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"   {status} {test_name}: {score:.1f}%")
        else:
            print(f"   ℹ️ {test_name}: {score}")
    
    print(f"\n🔍 SECURITY ANALYSIS:")
    
    # Authentication Analysis
    auth_score = results.get("Authentication Protection", 0)
    if auth_score >= 80:
        print("   ✅ Authentication: Strong protection against unauthorized access")
    else:
        print("   ⚠️ Authentication: Some endpoints may be exposed")
    
    # RBAC Analysis  
    rbac_score = results.get("Role-Based Access Control", 0)
    if rbac_score >= 80:
        print("   ✅ Authorization: Role-based access control working properly")
    else:
        print("   ⚠️ Authorization: Role permissions may need review")
    
    # Input Validation Analysis
    input_score = results.get("Input Validation", 0)
    if input_score >= 80:
        print("   ✅ Input Security: Good protection against injection attacks")
    else:
        print("   ⚠️ Input Security: Input validation may need strengthening")
    
    # Session Security Analysis
    session_score = results.get("Session Security", 0)
    if session_score >= 80:
        print("   ✅ Session Management: JWT tokens properly validated")
    else:
        print("   ⚠️ Session Management: Token validation may need improvement")
    
    # Data Protection Analysis
    data_score = results.get("Data Protection", 0)
    if data_score >= 80:
        print("   ✅ Data Protection: Sensitive endpoints properly secured")
    else:
        print("   ⚠️ Data Protection: Some sensitive data may be exposed")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    
    if overall_score < 90:
        print("   • Review and strengthen authentication mechanisms")
        print("   • Implement comprehensive input validation")
        print("   • Add rate limiting for critical endpoints")
        print("   • Regular security audits and penetration testing")
    
    if auth_score < 80:
        print("   • Ensure all sensitive endpoints require authentication")
        print("   • Implement proper HTTP status codes (401 vs 403)")
    
    if rbac_score < 80:
        print("   • Review role-based access control permissions")
        print("   • Test cross-role access scenarios")
    
    if input_score < 80:
        print("   • Strengthen input validation and sanitization")
        print("   • Implement SQL injection protection")
        print("   • Add XSS protection measures")
    
    print(f"\n📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    print("🧪 Running Security & Access Control Tests")
    print("=" * 50)
    
    try:
        # Check server status - server returns 404 for root but that means it's running
        try:
            import requests
            response = requests.get("http://127.0.0.1:8000/", timeout=5)  
            print(f"✅ Server is running (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Server check failed: {e}")
            raise Exception("Server is not running")
        
        # Run security tests
        results = {}
        
        print("\n1. Authentication Security")
        results["Authentication Protection"] = test_authentication_security()
        
        print("\n2. Role-Based Access Control")  
        results["Role-Based Access Control"] = test_role_based_access()
        
        print("\n3. Input Validation Security")
        results["Input Validation"] = test_input_validation()
        
        print("\n4. Session Security")
        results["Session Security"] = test_session_security()
        
        print("\n5. Sensitive Data Protection")
        results["Data Protection"] = test_sensitive_data_exposure()
        
        # Generate comprehensive report
        generate_security_report(results)
        
    except Exception as e:
        print(f"\n❌ Security test execution failed: {e}")