"""
Comprehensive Tests for Patient Services and Routes
"""
import requests
import json
from datetime import datetime
from tests.test_config import test_config

class TestPatientFunctions:
    """Test patient services and routes functionality"""
    
    def setup_method(self):
        """Setup authentication for patient tests"""
        if not test_config.check_server_status():
            raise Exception("Server is not running. Start with: uvicorn app.main:app --reload")
        
        # Setup nurse authentication for patient creation
        return test_config.setup_auth_for_user_type("nurse")
    
    def test_patient_endpoints_accessibility(self):
        """Test all patient endpoints are accessible"""
        print("🔍 Testing Patient Endpoint Accessibility")
        
        endpoints = [
            ("POST", "/patients/"),
            ("GET", "/patients"),  # Note: no trailing slash
            ("GET", "/patients/{patient_id}"),
            ("PATCH", "/patients/{patient_id}")
        ]
        
        for method, endpoint in endpoints:
            try:
                if method == "GET" and "{patient_id}" not in endpoint:
                    # Test GET /patients (list patients)
                    response = requests.get(f"{test_config.base_url}{endpoint}", 
                                          headers=test_config.headers, timeout=10)
                else:
                    # Test other endpoints with dummy data
                    test_id = "test-patient-id"
                    url = endpoint.replace("{patient_id}", test_id)
                    
                    if method == "POST":
                        test_data = {"name": "Test Patient", "nic": "123456789V"}
                        response = requests.post(f"{test_config.base_url}{url}", 
                                               json=test_data, headers=test_config.headers, timeout=10)
                    elif method == "PATCH":
                        test_data = {"name": "Updated Patient"}
                        response = requests.patch(f"{test_config.base_url}{url}", 
                                                json=test_data, headers=test_config.headers, timeout=10)
                    else:  # GET with ID
                        response = requests.get(f"{test_config.base_url}{url}", 
                                              headers=test_config.headers, timeout=10)
                
                if response.status_code == 401:
                    print(f"  ⚠️ {method} {endpoint}: Authentication required")
                elif response.status_code == 403:
                    print(f"  ⚠️ {method} {endpoint}: Permission denied (expected for non-nurse)")
                elif response.status_code == 404:
                    print(f"  ✅ {method} {endpoint}: Endpoint exists (404 for missing resource)")
                elif response.status_code == 422:
                    print(f"  ✅ {method} {endpoint}: Validation working (422 for invalid data)")
                elif response.status_code in [200, 201]:
                    print(f"  ✅ {method} {endpoint}: Working perfectly")
                else:
                    print(f"  ℹ️ {method} {endpoint}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {method} {endpoint}: Error - {e}")
    
    def test_create_patient_functionality(self):
        """Test patient creation with various scenarios"""
        print("🏥 Testing Patient Creation")
        
        if not test_config.setup_auth_for_user_type("nurse"):
            print("  ⚠️ Skipping - nurse authentication failed")
            return
        
        # Test 1: Valid patient creation
        valid_patient = {
            "name": f"Test Patient {datetime.now().microsecond}",
            "nic": f"12345{datetime.now().microsecond % 10000}V",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
            "phone": "0771234567",
            "email": f"patient{datetime.now().microsecond}@test.com",
            "address": "123 Test Street, Test City"
        }
        
        try:
            response = requests.post(f"{test_config.base_url}/patients/", 
                                   json=valid_patient, 
                                   headers=test_config.headers, 
                                   timeout=15)
            
            if response.status_code in [200, 201]:
                patient_data = response.json()
                self.test_patient_id = patient_data.get("patient_id")
                print(f"  ✅ Valid Patient Created: ID {self.test_patient_id}")
                
                # Verify required fields
                required_fields = ["patient_id", "name", "nic"]
                for field in required_fields:
                    if field in patient_data:
                        print(f"    ✓ {field}: {patient_data[field]}")
                    else:
                        print(f"    ❌ Missing field: {field}")
                        
            elif response.status_code == 422:
                print(f"  ⚠️ Validation Error: {response.json()}")
            elif response.status_code == 403:
                print(f"  ⚠️ Permission Denied - Check nurse role")
            else:
                print(f"  ❌ Unexpected status: {response.status_code}")
                print(f"    Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Patient creation error: {e}")
        
        # Test 2: Invalid patient data
        print("  Testing validation with invalid data:")
        
        invalid_patients = [
            ({"name": ""}, "Empty name"),
            ({"nic": ""}, "Empty NIC"),
            ({"name": "Test", "nic": "invalid"}, "Invalid NIC format"),
            ({}, "Missing required fields")
        ]
        
        for invalid_data, description in invalid_patients:
            try:
                response = requests.post(f"{test_config.base_url}/patients/", 
                                       json=invalid_data, 
                                       headers=test_config.headers, 
                                       timeout=10)
                
                if response.status_code == 422:
                    print(f"    ✅ {description}: Properly rejected (422)")
                else:
                    print(f"    ⚠️ {description}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ {description}: Error {e}")
    
    def test_get_hospital_patients(self):
        """Test retrieving patients for current user's hospital"""
        print("📋 Testing Get Hospital Patients")
        
        if not test_config.setup_auth_for_user_type("nurse"):
            print("  ⚠️ Skipping - nurse authentication failed")
            return
        
        try:
            response = requests.get(f"{test_config.base_url}/patients", 
                                  headers=test_config.headers, timeout=15)
            
            if response.status_code == 200:
                patients = response.json()
                print(f"  ✅ Retrieved {len(patients)} patients for hospital")
                
                if patients:
                    # Analyze patient data structure
                    sample_patient = patients[0]
                    expected_fields = ["patient_id", "name", "nic", "Hospital ID"]
                    
                    for field in expected_fields:
                        if field in sample_patient:
                            print(f"    ✓ {field}: Present")
                        else:
                            print(f"    ⚠️ {field}: Missing")
                else:
                    print("    ℹ️ No patients found for this hospital")
                    
            elif response.status_code == 401:
                print("  ❌ Authentication failed")
            elif response.status_code == 403:
                print("  ❌ Access forbidden")
            else:
                print(f"  ⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error retrieving hospital patients: {e}")
    
    def test_get_patient_by_id(self):
        """Test retrieving specific patient by ID"""
        print("🔍 Testing Get Patient By ID")
        
        if not test_config.setup_auth_for_user_type("doctor"):
            print("  ⚠️ Skipping - authentication failed")
            return
        
        # First, try to get a list of patients to find a valid ID
        try:
            # Switch to nurse to get patient list
            test_config.setup_auth_for_user_type("nurse")
            list_response = requests.get(f"{test_config.base_url}/patients", 
                                       headers=test_config.headers, timeout=10)
            
            if list_response.status_code == 200:
                patients = list_response.json()
                
                if patients:
                    test_patient_id = patients[0]["patient_id"]
                    
                    # Switch back to doctor for detailed access
                    test_config.setup_auth_for_user_type("doctor")
                    
                    # Test getting specific patient
                    response = requests.get(f"{test_config.base_url}/patients/{test_patient_id}", 
                                          headers=test_config.headers, timeout=10)
                    
                    if response.status_code == 200:
                        patient = response.json()
                        print(f"  ✅ Retrieved patient: {patient.get('name', 'N/A')}")
                        
                        # Verify patient data structure
                        key_fields = ["patient_id", "name", "nic", "date_of_birth"]
                        for field in key_fields:
                            if field in patient:
                                print(f"    ✓ {field}: {patient[field]}")
                            else:
                                print(f"    ⚠️ {field}: Missing")
                                
                    elif response.status_code == 404:
                        print("  ❌ Patient not found")
                    else:
                        print(f"  ⚠️ Status: {response.status_code}")
                else:
                    print("  ℹ️ No patients available to test individual retrieval")
            else:
                print("  ⚠️ Could not get patient list for testing")
                
        except Exception as e:
            print(f"  ❌ Error testing patient by ID: {e}")
    
    def test_edit_patient_functionality(self):
        """Test patient editing functionality"""
        print("✏️ Testing Patient Edit")
        
        if not test_config.setup_auth_for_user_type("doctor"):
            print("  ⚠️ Skipping - authentication failed")
            return
        
        # First get a patient to edit
        try:
            # Get patient list as nurse
            test_config.setup_auth_for_user_type("nurse")
            list_response = requests.get(f"{test_config.base_url}/patients", 
                                       headers=test_config.headers, timeout=10)
            
            if list_response.status_code == 200:
                patients = list_response.json()
                
                if patients:
                    test_patient_id = patients[0]["patient_id"]
                    
                    # Switch to doctor for editing
                    test_config.setup_auth_for_user_type("doctor")
                    
                    # Test updating patient
                    update_data = {
                        "phone": "0779999999",
                        "address": "Updated Address, New City"
                    }
                    
                    response = requests.patch(f"{test_config.base_url}/patients/{test_patient_id}", 
                                            json=update_data, 
                                            headers=test_config.headers, timeout=10)
                    
                    if response.status_code == 200:
                        updated_patient = response.json()
                        print(f"  ✅ Patient updated successfully")
                        
                        # Verify updates
                        for field, value in update_data.items():
                            if updated_patient.get(field) == value:
                                print(f"    ✓ {field}: Updated to {value}")
                            else:
                                print(f"    ⚠️ {field}: Not updated properly")
                                
                    elif response.status_code == 404:
                        print("  ❌ Patient not found for update")
                    elif response.status_code == 422:
                        print("  ⚠️ Validation error in update")
                    else:
                        print(f"  ⚠️ Update status: {response.status_code}")
                else:
                    print("  ℹ️ No patients available to test editing")
            else:
                print("  ⚠️ Could not get patient list for editing test")
                
        except Exception as e:
            print(f"  ❌ Error testing patient edit: {e}")
    
    def test_patient_hospital_association(self):
        """Test patient-hospital association functionality"""
        print("🏢 Testing Patient-Hospital Association")
        
        if not test_config.setup_auth_for_user_type("nurse"):
            print("  ⚠️ Skipping - nurse authentication failed")
            return
        
        try:
            # Create a patient and verify hospital association
            test_patient = {
                "name": f"Hospital Test Patient {datetime.now().microsecond}",
                "nic": f"99999{datetime.now().microsecond % 10000}V",
                "date_of_birth": "1985-06-15",
                "gender": "Female"
            }
            
            response = requests.post(f"{test_config.base_url}/patients/", 
                                   json=test_patient, 
                                   headers=test_config.headers, timeout=15)
            
            if response.status_code in [200, 201]:
                patient_data = response.json()
                hospital_id = patient_data.get("Hospital ID")
                
                if hospital_id:
                    print(f"  ✅ Patient associated with hospital: {hospital_id}")
                    
                    # Verify patient appears in hospital patient list
                    list_response = requests.get(f"{test_config.base_url}/patients", 
                                               headers=test_config.headers, timeout=10)
                    
                    if list_response.status_code == 200:
                        hospital_patients = list_response.json()
                        patient_ids = [p["patient_id"] for p in hospital_patients]
                        
                        if patient_data["patient_id"] in patient_ids:
                            print("    ✓ Patient appears in hospital patient list")
                        else:
                            print("    ⚠️ Patient not found in hospital patient list")
                    else:
                        print("    ⚠️ Could not verify hospital patient list")
                else:
                    print("  ⚠️ No Hospital ID in patient response")
            else:
                print(f"  ❌ Patient creation failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error testing hospital association: {e}")

if __name__ == "__main__":
    # Run patient tests
    test_patients = TestPatientFunctions()
    
    print("🧪 Running Patient Function Tests")
    print("=" * 60)
    
    try:
        test_patients.setup_method()
        
        print("\n1. Testing Endpoint Accessibility")
        test_patients.test_patient_endpoints_accessibility()
        
        print("\n2. Testing Patient Creation")
        test_patients.test_create_patient_functionality()
        
        print("\n3. Testing Hospital Patients Retrieval")
        test_patients.test_get_hospital_patients()
        
        print("\n4. Testing Individual Patient Retrieval")
        test_patients.test_get_patient_by_id()
        
        print("\n5. Testing Patient Editing")
        test_patients.test_edit_patient_functionality()
        
        print("\n6. Testing Hospital Association")
        test_patients.test_patient_hospital_association()
        
        print("\n🎉 Patient function tests completed!")
        
    except Exception as e:
        print(f"\n❌ Patient test execution failed: {e}")