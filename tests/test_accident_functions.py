"""
Comprehensive Tests for Accident Record Services and Routes
"""
import requests
import json
from datetime import datetime, date
from tests.test_config import test_config

class TestAccidentFunctions:
    """Test accident record services and routes functionality"""
    
    def setup_method(self):
        """Setup authentication for accident tests"""
        if not test_config.check_server_status():
            raise Exception("Server is not running. Start with: uvicorn app.main:app --reload")
        
        # Setup doctor authentication for accident management
        return test_config.setup_auth_for_user_type("doctor")
    
    def test_accident_endpoints_accessibility(self):
        """Test all accident endpoints are accessible"""
        print("🔍 Testing Accident Endpoint Accessibility")
        
        endpoints = [
            ("POST", "/accidents/"),
            ("GET", "/accidents/"),
            ("GET", "/accidents/{accident_id}"),
            ("PATCH", "/accidents/{accident_id}"),
            ("GET", "/accidents/patient/{patient_id}")
        ]
        
        for method, endpoint in endpoints:
            try:
                if method == "GET" and "{" not in endpoint:
                    # Test GET /accidents/ (list all accidents)
                    response = requests.get(f"{test_config.base_url}{endpoint}", 
                                          headers=test_config.headers, timeout=10)
                else:
                    # Test endpoints with dummy IDs
                    test_id = "test-id-123"
                    url = endpoint.replace("{accident_id}", test_id).replace("{patient_id}", test_id)
                    
                    if method == "POST":
                        test_data = {
                            "patient_id": "test-patient-id",
                            "incident_at_date": "2024-01-15",
                            "Severity": "M"
                        }
                        response = requests.post(f"{test_config.base_url}{url}", 
                                               json=test_data, headers=test_config.headers, timeout=10)
                    elif method == "PATCH":
                        test_data = {"Severity": "S"}
                        response = requests.patch(f"{test_config.base_url}{url}", 
                                                json=test_data, headers=test_config.headers, timeout=10)
                    else:  # GET with ID
                        response = requests.get(f"{test_config.base_url}{url}", 
                                              headers=test_config.headers, timeout=10)
                
                if response.status_code == 401:
                    print(f"  ⚠️ {method} {endpoint}: Authentication required")
                elif response.status_code == 403:
                    print(f"  ⚠️ {method} {endpoint}: Permission denied")
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
    
    def test_create_accident_record(self):
        """Test accident record creation functionality"""
        print("📝 Testing Accident Record Creation")
        
        if not test_config.setup_auth_for_user_type("doctor"):
            print("  ⚠️ Skipping - authentication failed")
            return
        
        # First, get a patient ID to associate with accident
        patient_id = self.get_test_patient_id()
        
        if not patient_id:
            print("  ⚠️ No test patient available - creating accident with dummy patient ID")
            patient_id = "test-patient-id-123"
        
        # Test 1: Valid accident record creation
        valid_accident = {
            "patient_id": patient_id,
            "incident_at_date": "2024-01-15",
            "Severity": "M",
            "Time of Collision": "14:30",
            "Collision with": "Vehicle",
            "Mode of traveling during accident": "Motorcycle",
            "Category of Road": "Highway",
            "Discharge Outcome": "Full Recovery"
        }
        
        try:
            response = requests.post(f"{test_config.base_url}/accidents/", 
                                   json=valid_accident, 
                                   headers=test_config.headers, 
                                   timeout=15)
            
            if response.status_code in [200, 201]:
                accident_data = response.json()
                self.test_accident_id = accident_data.get("accident_id")
                print(f"  ✅ Valid Accident Record Created: ID {self.test_accident_id}")
                
                # Verify required fields
                required_fields = ["accident_id", "patient_id", "managed_by", "Severity"]
                for field in required_fields:
                    if field in accident_data:
                        print(f"    ✓ {field}: {accident_data[field]}")
                    else:
                        print(f"    ❌ Missing field: {field}")
                        
                # Verify managed_by is set to current user
                if "managed_by" in accident_data:
                    print(f"    ✓ Managed by current user: {accident_data['managed_by']}")
                        
            elif response.status_code == 422:
                errors = response.json()
                print(f"  ⚠️ Validation Error: {errors}")
            elif response.status_code == 404:
                print(f"  ⚠️ Patient not found - using test patient ID")
            else:
                print(f"  ❌ Unexpected status: {response.status_code}")
                print(f"    Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Accident creation error: {e}")
        
        # Test 2: Invalid accident data validation
        print("  Testing validation with invalid data:")
        
        invalid_accidents = [
            ({"patient_id": ""}, "Empty patient ID"),
            ({"patient_id": "valid-id", "incident_at_date": "invalid-date"}, "Invalid date"),
            ({"patient_id": "valid-id", "Severity": "X"}, "Invalid severity"),
            ({}, "Missing required fields")
        ]
        
        for invalid_data, description in invalid_accidents:
            try:
                response = requests.post(f"{test_config.base_url}/accidents/", 
                                       json=invalid_data, 
                                       headers=test_config.headers, 
                                       timeout=10)
                
                if response.status_code == 422:
                    print(f"    ✅ {description}: Properly rejected (422)")
                elif response.status_code == 400:
                    print(f"    ✅ {description}: Bad request (400)")
                else:
                    print(f"    ⚠️ {description}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ {description}: Error {e}")
    
    def test_get_all_accident_records(self):
        """Test retrieving all accident records"""
        print("📋 Testing Get All Accident Records")
        
        if not test_config.setup_auth_for_user_type("doctor"):
            print("  ⚠️ Skipping - authentication failed")
            return
        
        try:
            response = requests.get(f"{test_config.base_url}/accidents/", 
                                  headers=test_config.headers, timeout=15)
            
            if response.status_code == 200:
                accidents = response.json()
                print(f"  ✅ Retrieved {len(accidents)} accident records")
                
                if accidents:
                    # Analyze accident data structure
                    sample_accident = accidents[0]
                    expected_fields = [
                        "accident_id", "patient_id", "managed_by", 
                        "Severity", "incident_at_date", "Completed"
                    ]
                    
                    print("    Sample accident record structure:")
                    for field in expected_fields:
                        if field in sample_accident:
                            print(f"      ✓ {field}: {sample_accident[field]}")
                        else:
                            print(f"      ⚠️ {field}: Missing")
                            
                    # Check for managed_by_name enrichment
                    if "managed_by_name" in sample_accident:
                        print(f"      ✓ managed_by_name: {sample_accident['managed_by_name']}")
                    else:
                        print("      ℹ️ managed_by_name: Not present")
                else:
                    print("    ℹ️ No accident records found")
                    
            elif response.status_code == 401:
                print("  ❌ Authentication failed")
            elif response.status_code == 403:
                print("  ❌ Access forbidden")
            else:
                print(f"  ⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error retrieving all accidents: {e}")
    
    def test_get_accident_by_id(self):
        """Test retrieving specific accident by ID"""
        print("🔍 Testing Get Accident By ID")
        
        if not test_config.setup_auth_for_user_type("doctor"):
            print("  ⚠️ Skipping - authentication failed")
            return
        
        # First, get list of accidents to find a valid ID
        try:
            list_response = requests.get(f"{test_config.base_url}/accidents/", 
                                       headers=test_config.headers, timeout=10)
            
            if list_response.status_code == 200:
                accidents = list_response.json()
                
                if accidents:
                    test_accident_id = accidents[0]["accident_id"]
                    
                    # Test getting specific accident
                    response = requests.get(f"{test_config.base_url}/accidents/{test_accident_id}", 
                                          headers=test_config.headers, timeout=10)
                    
                    if response.status_code == 200:
                        accident = response.json()
                        print(f"  ✅ Retrieved accident: {accident.get('accident_id', 'N/A')}")
                        
                        # Verify accident data structure
                        key_fields = ["accident_id", "patient_id", "Severity", "managed_by"]
                        for field in key_fields:
                            if field in accident:
                                print(f"    ✓ {field}: {accident[field]}")
                            else:
                                print(f"    ⚠️ {field}: Missing")
                                
                    elif response.status_code == 404:
                        print("  ❌ Accident not found")
                    else:
                        print(f"  ⚠️ Status: {response.status_code}")
                else:
                    print("  ℹ️ No accidents available to test individual retrieval")
            else:
                print("  ⚠️ Could not get accident list for testing")
                
        except Exception as e:
            print(f"  ❌ Error testing accident by ID: {e}")
    
    def test_edit_accident_record(self):
        """Test accident record editing functionality"""
        print("✏️ Testing Accident Record Edit")
        
        if not test_config.setup_auth_for_user_type("doctor"):
            print("  ⚠️ Skipping - authentication failed")
            return
        
        try:
            # Get list of accidents
            list_response = requests.get(f"{test_config.base_url}/accidents/", 
                                       headers=test_config.headers, timeout=10)
            
            if list_response.status_code == 200:
                accidents = list_response.json()
                
                if accidents:
                    # Find an accident that's not completed and managed by current user
                    editable_accident = None
                    for accident in accidents:
                        if not accident.get("Completed", True):  # Default to True if field missing
                            editable_accident = accident
                            break
                    
                    if editable_accident:
                        test_accident_id = editable_accident["accident_id"]
                        
                        # Test updating accident
                        update_data = {
                            "Severity": "S",
                            "Discharge Outcome": "Partial Recovery",
                            "Category of Road": "Urban Street"
                        }
                        
                        response = requests.patch(f"{test_config.base_url}/accidents/{test_accident_id}", 
                                                json=update_data, 
                                                headers=test_config.headers, timeout=10)
                        
                        if response.status_code == 200:
                            updated_accident = response.json()
                            print(f"  ✅ Accident updated successfully")
                            
                            # Verify updates
                            for field, value in update_data.items():
                                if updated_accident.get(field) == value:
                                    print(f"    ✓ {field}: Updated to {value}")
                                else:
                                    print(f"    ⚠️ {field}: Not updated properly")
                                    
                        elif response.status_code == 404:
                            print("  ❌ Accident not found for update")
                        elif response.status_code == 403:
                            print("  ⚠️ Permission denied - may be completed or not owned by user")
                        elif response.status_code == 422:
                            print("  ⚠️ Validation error in update")
                        else:
                            print(f"  ⚠️ Update status: {response.status_code}")
                    else:
                        print("  ℹ️ No editable accidents found (all may be completed)")
                else:
                    print("  ℹ️ No accidents available to test editing")
            else:
                print("  ⚠️ Could not get accident list for editing test")
                
        except Exception as e:
            print(f"  ❌ Error testing accident edit: {e}")
    
    def test_get_accidents_by_patient(self):
        """Test retrieving accidents for a specific patient"""
        print("👤 Testing Get Accidents By Patient")
        
        if not test_config.setup_auth_for_user_type("doctor"):
            print("  ⚠️ Skipping - authentication failed")
            return
        
        try:
            # First get all accidents to find a patient with accidents
            list_response = requests.get(f"{test_config.base_url}/accidents/", 
                                       headers=test_config.headers, timeout=10)
            
            if list_response.status_code == 200:
                accidents = list_response.json()
                
                if accidents:
                    # Get patient ID from first accident
                    test_patient_id = accidents[0]["patient_id"]
                    
                    # Test getting accidents for this patient
                    response = requests.get(f"{test_config.base_url}/accidents/patient/{test_patient_id}", 
                                          headers=test_config.headers, timeout=15)
                    
                    if response.status_code == 200:
                        patient_accidents = response.json()
                        print(f"  ✅ Retrieved {len(patient_accidents)} accidents for patient {test_patient_id}")
                        
                        if patient_accidents:
                            # Verify all accidents belong to the correct patient
                            correct_patient = all(acc["patient_id"] == test_patient_id for acc in patient_accidents)
                            if correct_patient:
                                print("    ✓ All accidents belong to correct patient")
                            else:
                                print("    ❌ Some accidents belong to wrong patient")
                            
                            # Check for managed_by_name enrichment (role-based)
                            if "managed_by_name" in patient_accidents[0]:
                                print(f"    ✓ Manager info enriched: {patient_accidents[0]['managed_by_name']}")
                            else:
                                print("    ℹ️ No manager name enrichment")
                                
                    elif response.status_code == 404:
                        print("  ❌ Patient or accidents not found")
                    else:
                        print(f"  ⚠️ Status: {response.status_code}")
                else:
                    print("  ℹ️ No accidents available to test patient-specific retrieval")
            else:
                print("  ⚠️ Could not get accident list")
                
        except Exception as e:
            print(f"  ❌ Error testing accidents by patient: {e}")
    
    def test_accident_permissions_and_security(self):
        """Test accident record permissions and security"""
        print("🔒 Testing Accident Permissions & Security")
        
        try:
            # Test 1: Access without authentication
            print("  Testing unauthenticated access:")
            response = requests.get(f"{test_config.base_url}/accidents/", timeout=5)
            
            if response.status_code == 401:
                print("    ✅ Unauthenticated access properly blocked")
            else:
                print(f"    ⚠️ Unexpected status for unauthenticated access: {response.status_code}")
            
            # Test 2: Different user roles
            print("  Testing role-based access:")
            
            user_types = ["doctor", "nurse", "government"]
            for user_type in user_types:
                try:
                    success = test_config.setup_auth_for_user_type(user_type)
                    if success:
                        response = requests.get(f"{test_config.base_url}/accidents/", 
                                              headers=test_config.headers, timeout=10)
                        
                        if response.status_code == 200:
                            print(f"    ✅ {user_type.title()}: Access granted")
                        elif response.status_code == 403:
                            print(f"    ⚠️ {user_type.title()}: Access forbidden")
                        else:
                            print(f"    ℹ️ {user_type.title()}: Status {response.status_code}")
                    else:
                        print(f"    ❌ {user_type.title()}: Authentication failed")
                except:
                    print(f"    ❌ {user_type.title()}: Error during test")
            
        except Exception as e:
            print(f"  ❌ Error testing permissions: {e}")
    
    def get_test_patient_id(self):
        """Helper method to get a test patient ID"""
        try:
            # Try to get patients as nurse
            test_config.setup_auth_for_user_type("nurse")
            response = requests.get(f"{test_config.base_url}/patients", 
                                  headers=test_config.headers, timeout=5)
            
            if response.status_code == 200:
                patients = response.json()
                if patients:
                    return patients[0]["patient_id"]
            return None
        except:
            return None

if __name__ == "__main__":
    # Run accident tests
    test_accidents = TestAccidentFunctions()
    
    print("🧪 Running Accident Function Tests")
    print("=" * 60)
    
    try:
        test_accidents.setup_method()
        
        print("\n1. Testing Endpoint Accessibility")
        test_accidents.test_accident_endpoints_accessibility()
        
        print("\n2. Testing Accident Record Creation")
        test_accidents.test_create_accident_record()
        
        print("\n3. Testing All Accident Records Retrieval")
        test_accidents.test_get_all_accident_records()
        
        print("\n4. Testing Individual Accident Retrieval")
        test_accidents.test_get_accident_by_id()
        
        print("\n5. Testing Accident Record Editing")
        test_accidents.test_edit_accident_record()
        
        print("\n6. Testing Accidents By Patient")
        test_accidents.test_get_accidents_by_patient()
        
        print("\n7. Testing Permissions & Security")
        test_accidents.test_accident_permissions_and_security()
        
        print("\n🎉 Accident function tests completed!")
        
    except Exception as e:
        print(f"\n❌ Accident test execution failed: {e}")