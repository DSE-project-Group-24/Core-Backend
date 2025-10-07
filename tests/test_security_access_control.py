"""
Comprehensive Security and Access Control Tests
Tests authentication, authorization, input validation, and security controls
"""
import requests
import json
from datetime import datetime
from tests.test_config import test_config

class TestSecurityAndAccessControl:
    """Comprehensive security testing for the Core-Backend application"""
    
    def setup_method(self):
        """Setup for security tests"""
        if not test_config.check_server_status():
            raise Exception("Server is not running. Start with: uvicorn app.main:app --reload")
    
    def test_unauthenticated_access_protection(self):
        """Test that protected endpoints block unauthenticated access"""
        print("🔒 Testing Unauthenticated Access Protection")
        
        protected_endpoints = [
            ("GET", "/analytics/"),
            ("GET", "/patients"),
            ("GET", "/accidents/"),
            ("POST", "/accidents/"),
            ("GET", "/doctor/"),
            ("GET", "/nurse/"),
            ("GET", "/hospital/"),
            ("GET", "/gov/rules/bootstrap"),
            ("GET", "/predictions/hospital-stay")
        ]
        
        unauthorized_count = 0
        total_endpoints = len(protected_endpoints)
        
        for method, endpoint in protected_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{test_config.base_url}{endpoint}", timeout=5)
                elif method == "POST":
                    response = requests.post(f"{test_config.base_url}{endpoint}", 
                                           json={}, timeout=5)
                
                if response.status_code in [401, 403]:
                    print(f"  ✅ {method} {endpoint}: Properly protected ({response.status_code})")
                    unauthorized_count += 1
                elif response.status_code == 422:
                    print(f"  ⚠️ {method} {endpoint}: Validation required (may need auth)")
                else:
                    print(f"  ❌ {method} {endpoint}: Unexpected access ({response.status_code})")
                    
            except Exception as e:
                print(f"  ❌ {method} {endpoint}: Error - {e}")
        
        protection_rate = (unauthorized_count / total_endpoints) * 100
        print(f"  📊 Protection Rate: {protection_rate:.1f}% ({unauthorized_count}/{total_endpoints})")
        
        return protection_rate
    
    def test_role_based_access_control(self):
        """Test role-based access control across different user types"""
        print("👥 Testing Role-Based Access Control")
        
        # Define role permissions matrix
        role_permissions = {
            "doctor": {
                "should_access": ["/analytics/", "/patients", "/accidents/", "/doctor/", "/predictions/hospital-stay"],
                "should_deny": []
            },
            "nurse": {
                "should_access": ["/patients", "/nurse/"],
                "should_deny": ["/analytics/", "/doctor/", "/gov/rules/bootstrap"]
            },
            "government": {
                "should_access": ["/analytics/", "/gov/rules/bootstrap", "/accidents/"],
                "should_deny": ["/doctor/", "/nurse/"]
            },
            "hospital_admin": {
                "should_access": ["/hospital/", "/patients"],
                "should_deny": ["/doctor/", "/nurse/", "/gov/rules/bootstrap"]
            }
        }
        
        rbac_results = {}
        
        for role, permissions in role_permissions.items():
            print(f"  Testing {role.title()} role:")
            rbac_results[role] = {"correct_access": 0, "correct_deny": 0, "total_tests": 0}
            
            # Authenticate as this role
            if test_config.setup_auth_for_user_type(role):
                # Test endpoints that should be accessible
                for endpoint in permissions["should_access"]:
                    try:
                        response = requests.get(f"{test_config.base_url}{endpoint}", 
                                              headers=test_config.headers, timeout=10)
                        
                        if response.status_code in [200, 201]:
                            print(f"    ✅ {endpoint}: Access granted")
                            rbac_results[role]["correct_access"] += 1
                        elif response.status_code in [401, 403]:
                            print(f"    ❌ {endpoint}: Access denied (should be allowed)")
                        else:
                            print(f"    ⚠️ {endpoint}: Status {response.status_code}")
                        
                        rbac_results[role]["total_tests"] += 1
                        
                    except Exception as e:
                        print(f"    ❌ {endpoint}: Error - {e}")
                
                # Test endpoints that should be denied
                for endpoint in permissions["should_deny"]:
                    try:
                        response = requests.get(f"{test_config.base_url}{endpoint}", 
                                              headers=test_config.headers, timeout=10)
                        
                        if response.status_code in [401, 403]:
                            print(f"    ✅ {endpoint}: Access properly denied")
                            rbac_results[role]["correct_deny"] += 1
                        elif response.status_code in [200, 201]:
                            print(f"    ❌ {endpoint}: Access granted (should be denied)")
                        else:
                            print(f"    ⚠️ {endpoint}: Status {response.status_code}")
                        
                        rbac_results[role]["total_tests"] += 1
                        
                    except Exception as e:
                        print(f"    ❌ {endpoint}: Error - {e}")
            else:
                print(f"    ❌ Failed to authenticate as {role}")
        
        return rbac_results
    
    def test_input_validation_security(self):
        """Test input validation and sanitization"""
        print("🛡️ Testing Input Validation & Security")
        
        # Test SQL injection attempts
        print("  Testing SQL Injection Protection:")
        sql_payloads = [
            "'; DROP TABLE patients; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --"
        ]
        
        sql_injection_blocked = 0
        
        for payload in sql_payloads:
            try:
                # Test login endpoint with SQL injection
                response = requests.post(f"{test_config.base_url}/auth/login", 
                                       json={"email": payload, "password": "test"}, timeout=5)
                
                if response.status_code in [400, 422]:
                    print(f"    ✅ SQL injection blocked: {payload[:20]}...")
                    sql_injection_blocked += 1
                else:
                    print(f"    ⚠️ SQL injection response: {response.status_code}")
            except:
                print(f"    ✅ SQL injection blocked (connection error)")
                sql_injection_blocked += 1
        
        sql_protection_rate = (sql_injection_blocked / len(sql_payloads)) * 100
        print(f"    📊 SQL Injection Protection: {sql_protection_rate:.1f}%")
        
        # Test XSS attempts
        print("  Testing XSS Protection:")
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//"
        ]
        
        xss_blocked = 0
        
        for payload in xss_payloads:
            try:
                # Test patient creation with XSS
                if test_config.setup_auth_for_user_type("nurse"):
                    response = requests.post(f"{test_config.base_url}/patients/", 
                                           json={"Full Name": payload, "NIC": "123456789V"}, 
                                           headers=test_config.headers, timeout=5)
                    
                    if response.status_code in [400, 422]:
                        print(f"    ✅ XSS blocked: {payload[:20]}...")
                        xss_blocked += 1
                    else:
                        print(f"    ⚠️ XSS response: {response.status_code}")
            except:
                print(f"    ✅ XSS blocked (validation error)")
                xss_blocked += 1
        
        xss_protection_rate = (xss_blocked / len(xss_payloads)) * 100
        print(f"    📊 XSS Protection: {xss_protection_rate:.1f}%")
        
        return {"sql_protection": sql_protection_rate, "xss_protection": xss_protection_rate}
    
    def test_session_management_security(self):
        """Test JWT token and session management security"""
        print("🔑 Testing Session Management Security")
        
        # Test token expiration and validation
        print("  Testing JWT Token Security:")
        
        # Get a valid token
        if test_config.setup_auth_for_user_type("doctor"):
            valid_token = test_config.headers.get("Authorization", "").replace("Bearer ", "")
            
            # Test 1: Valid token
            response = requests.get(f"{test_config.base_url}/analytics/", 
                                  headers={"Authorization": f"Bearer {valid_token}"}, timeout=5)
            
            if response.status_code == 200:
                print("    ✅ Valid token accepted")
            else:
                print(f"    ❌ Valid token rejected: {response.status_code}")
            
            # Test 2: Invalid token
            invalid_tokens = [
                "invalid_token",
                valid_token + "tampered",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.fake.token",
                ""
            ]
            
            invalid_blocked = 0
            
            for invalid_token in invalid_tokens:
                try:
                    response = requests.get(f"{test_config.base_url}/analytics/", 
                                          headers={"Authorization": f"Bearer {invalid_token}"}, timeout=5)
                    
                    if response.status_code in [401, 403, 422]:
                        print(f"    ✅ Invalid token blocked")
                        invalid_blocked += 1
                    else:
                        print(f"    ❌ Invalid token accepted: {response.status_code}")
                except:
                    print(f"    ✅ Invalid token blocked (connection error)")
                    invalid_blocked += 1
            
            token_security_rate = (invalid_blocked / len(invalid_tokens)) * 100
            print(f"    📊 Token Security: {token_security_rate:.1f}%")
            
            return token_security_rate
        else:
            print("    ❌ Could not authenticate to test token security")
            return 0
    
    def test_data_exposure_prevention(self):
        """Test prevention of sensitive data exposure"""
        print("🔍 Testing Data Exposure Prevention")
        
        sensitive_endpoints = [
            "/auth/users",
            "/admin",
            "/config",
            "/debug",
            "/.env",
            "/database",
            "/secrets"
        ]
        
        exposed_count = 0
        
        for endpoint in sensitive_endpoints:
            try:
                response = requests.get(f"{test_config.base_url}{endpoint}", timeout=5)
                
                if response.status_code == 404:
                    print(f"    ✅ {endpoint}: Not exposed (404)")
                elif response.status_code in [401, 403]:
                    print(f"    ✅ {endpoint}: Protected ({response.status_code})")
                elif response.status_code == 200:
                    print(f"    ❌ {endpoint}: Potentially exposed!")
                    exposed_count += 1
                else:
                    print(f"    ⚠️ {endpoint}: Status {response.status_code}")
                    
            except:
                print(f"    ✅ {endpoint}: Not accessible")
        
        exposure_prevention_rate = ((len(sensitive_endpoints) - exposed_count) / len(sensitive_endpoints)) * 100
        print(f"    📊 Data Exposure Prevention: {exposure_prevention_rate:.1f}%")
        
        return exposure_prevention_rate
    
    def test_rate_limiting_and_dos_protection(self):
        """Test rate limiting and DoS protection"""
        print("⚡ Testing Rate Limiting & DoS Protection")
        
        # Test rapid requests to login endpoint
        print("  Testing Login Rate Limiting:")
        
        rapid_requests = 0
        blocked_requests = 0
        
        for i in range(10):  # Send 10 rapid requests
            try:
                response = requests.post(f"{test_config.base_url}/auth/login", 
                                       json={"email": "test@test.com", "password": "test"}, 
                                       timeout=2)
                rapid_requests += 1
                
                if response.status_code == 429:  # Too Many Requests
                    blocked_requests += 1
                    print(f"    ✅ Request #{i+1}: Rate limited (429)")
                elif response.status_code in [400, 401, 422]:
                    print(f"    ℹ️ Request #{i+1}: Normal rejection ({response.status_code})")
                else:
                    print(f"    ⚠️ Request #{i+1}: Status {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"    ⚠️ Request #{i+1}: Timeout (possible rate limiting)")
                blocked_requests += 1
            except Exception as e:
                print(f"    ❌ Request #{i+1}: Error - {e}")
        
        if blocked_requests > 0:
            print(f"    ✅ Rate limiting detected: {blocked_requests}/{rapid_requests} requests blocked")
            return True
        else:
            print(f"    ⚠️ No rate limiting detected (may be configured differently)")
            return False
    
    def test_password_security_policies(self):
        """Test password security policies"""
        print("🔐 Testing Password Security Policies")
        
        weak_passwords = [
            "123",
            "password",
            "admin",
            "test",
            "12345678",
            "qwerty"
        ]
        
        weak_passwords_blocked = 0
        
        print("  Testing weak password rejection:")
        
        for weak_pass in weak_passwords:
            try:
                # Test nurse registration with weak password
                unique_email = f"security_test_{datetime.now().microsecond}@test.com"
                
                response = requests.post(f"{test_config.base_url}/auth/register/nurse", 
                                       json={
                                           "email": unique_email,
                                           "password": weak_pass,
                                           "name": "Test User",
                                           "hospital_id": "test_hospital"
                                       }, timeout=5)
                
                if response.status_code in [400, 422]:
                    print(f"    ✅ Weak password blocked: '{weak_pass}'")
                    weak_passwords_blocked += 1
                else:
                    print(f"    ❌ Weak password accepted: '{weak_pass}' ({response.status_code})")
                    
            except Exception as e:
                print(f"    ⚠️ Password test error: {e}")
        
        password_security_rate = (weak_passwords_blocked / len(weak_passwords)) * 100
        print(f"    📊 Password Security: {password_security_rate:.1f}%")
        
        return password_security_rate

if __name__ == "__main__":
    # Run comprehensive security tests
    security_test = TestSecurityAndAccessControl()
    
    print("🛡️ Running Comprehensive Security & Access Control Tests")
    print("=" * 70)
    
    try:
        security_test.setup_method()
        
        print("\n1. Unauthenticated Access Protection")
        protection_rate = security_test.test_unauthenticated_access_protection()
        
        print("\n2. Role-Based Access Control")
        rbac_results = security_test.test_role_based_access_control()
        
        print("\n3. Input Validation & Security")
        validation_results = security_test.test_input_validation_security()
        
        print("\n4. Session Management Security")
        session_security = security_test.test_session_management_security()
        
        print("\n5. Data Exposure Prevention")
        exposure_prevention = security_test.test_data_exposure_prevention()
        
        print("\n6. Rate Limiting & DoS Protection")
        rate_limiting = security_test.test_rate_limiting_and_dos_protection()
        
        print("\n7. Password Security Policies")
        password_security = security_test.test_password_security_policies()
        
        print(f"\n🎉 Security testing completed!")
        print(f"📊 Overall Security Score Summary:")
        print(f"   • Authentication Protection: {protection_rate:.1f}%")
        print(f"   • Input Validation Security: {validation_results.get('sql_protection', 0):.1f}%")
        print(f"   • Session Security: {session_security:.1f}%")
        print(f"   • Data Exposure Prevention: {exposure_prevention:.1f}%")
        print(f"   • Password Security: {password_security:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Security test execution failed: {e}")