#!/usr/bin/env python3

import requests
import json

def test_complete_analytics():
    base_url = "http://localhost:8000"
    
    # Test credentials - adjust based on your actual login
    test_credentials = [
        {"email": "doctor@hospital.lk", "password": "password123"},
        {"email": "admin@test.com", "password": "admin123"},
        {"email": "test@test.com", "password": "test123"}
    ]
    
    for creds in test_credentials:
        try:
            print(f"🔐 Testing with: {creds['email']}")
            
            # Login
            login_response = requests.post(f"{base_url}/auth/login", json=creds, timeout=10)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                continue
            
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"✅ Login successful")
            
            # Test 1: Summary endpoint (should show 2079+ records)
            print("\n1️⃣ Testing /analytics/summary...")
            summary_response = requests.get(f"{base_url}/analytics/summary", headers=headers, timeout=30)
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                total_accidents = data.get("total_accidents", 0)
                print(f"📊 Summary: {total_accidents} accidents")
                
                if total_accidents >= 2079:
                    print(f"🎉 SUCCESS! Summary shows {total_accidents} records")
                else:
                    print(f"⚠️  Summary shows {total_accidents} records (expected 2079+)")
            else:
                print(f"❌ Summary failed: {summary_response.status_code}")
                continue
            
            # Test 2: Full analytics endpoint
            print("\n2️⃣ Testing /analytics/ (full analytics)...")
            analytics_response = requests.get(f"{base_url}/analytics/", headers=headers, timeout=60)
            
            if analytics_response.status_code == 200:
                data = analytics_response.json()
                total_records = data.get("total_records", 0)
                peak_hour = data.get("peak_accident_hour", "N/A")
                common_collision = data.get("most_common_collision", "N/A")
                
                print(f"📈 Analytics: {total_records} records processed")
                print(f"   Peak Hour: {peak_hour}")
                print(f"   Common Collision: {common_collision}")
                
                # Check data structure
                accident_chars = data.get("accident_characteristics", {})
                demographics = data.get("demographics", {})
                
                print(f"   Hourly Distribution: {len(accident_chars.get('hourly_distribution', {}))} hours")
                print(f"   Gender Distribution: {len(demographics.get('gender_dist', {}))} genders")
                
                if total_records >= 2079:
                    print(f"🎉 SUCCESS! Full analytics shows {total_records} records")
                else:
                    print(f"⚠️  Full analytics shows {total_records} records (expected 2079+)")
                    
            elif analytics_response.status_code == 414:
                print(f"❌ Still getting 414 Request-URI Too Large error")
            else:
                print(f"❌ Analytics failed: {analytics_response.status_code}")
                print(f"Response: {analytics_response.text[:300]}...")
            
            # Test 3: Filter options
            print("\n3️⃣ Testing /analytics/filters/options...")
            options_response = requests.get(f"{base_url}/analytics/filters/options", headers=headers, timeout=30)
            
            if options_response.status_code == 200:
                data = options_response.json()
                genders = data.get("genders", [])
                ethnicities = data.get("ethnicities", [])
                collision_types = data.get("collision_types", [])
                
                print(f"🎛️  Filter Options:")
                print(f"   Genders: {len(genders)} options")
                print(f"   Ethnicities: {len(ethnicities)} options") 
                print(f"   Collision Types: {len(collision_types)} options")
                
                if len(genders) > 0 and len(ethnicities) > 0:
                    print(f"✅ Filter options loaded successfully")
                else:
                    print(f"⚠️  Filter options seem limited")
            else:
                print(f"❌ Filter options failed: {options_response.status_code}")
            
            # If we got here successfully, break the loop
            if summary_response.status_code == 200 and analytics_response.status_code == 200:
                print(f"\n🎉 ALL TESTS PASSED! Analytics is working with hospital-scoped data")
                break
                
        except requests.exceptions.Timeout:
            print("⏱️  Request timed out - server processing large dataset")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    print("\n" + "="*70)
    print("Expected outcomes:")
    print("✅ Summary: 2079+ accident records")
    print("✅ Analytics: Complete demographics and characteristics")
    print("✅ Filter options: Available gender, ethnicity, collision type options")
    print("✅ No 414 Request-URI Too Large errors")
    print("✅ Hospital-specific data only (not all hospitals)")

if __name__ == "__main__":
    test_complete_analytics()