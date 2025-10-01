#!/usr/bin/env python3

import requests
import json

# Quick test to check if we're now getting all 2079+ records
def test_summary_fix():
    base_url = "http://localhost:8000"
    
    # Test credentials - adjust these based on your actual login
    test_credentials = [
        {"email": "doctor@example.com", "password": "password123"},
        {"email": "admin@hospital.lk", "password": "admin123"},
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
            
            # Test summary endpoint
            print("🔍 Testing /analytics/summary endpoint...")
            summary_response = requests.get(f"{base_url}/analytics/summary", headers=headers, timeout=30)
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                total_accidents = data.get("total_accidents", 0)
                
                print(f"📊 Summary Response:")
                print(f"   Total Accidents: {total_accidents}")
                print(f"   Peak Hour: {data.get('peak_accident_hour', 'N/A')}")
                print(f"   Most Common Collision: {data.get('most_common_collision', 'N/A')}")
                
                if total_accidents >= 2079:
                    print(f"🎉 SUCCESS! Got {total_accidents} records (expected 2079+)")
                    print("✅ The pagination fix worked!")
                    break
                elif total_accidents > 996:
                    print(f"🔄 PROGRESS! Got {total_accidents} records (was 996, expected 2079)")
                    print("Getting more records now, but might need more investigation")
                else:
                    print(f"⚠️  Still getting {total_accidents} records (expected 2079)")
                    
            else:
                print(f"❌ Summary endpoint failed: {summary_response.status_code}")
                print(f"Response: {summary_response.text[:300]}...")
                
        except requests.exceptions.Timeout:
            print("⏱️  Request timed out - server might be processing a lot of data (this is good!)")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    print("\n" + "="*60)
    print("Expected outcome:")
    print("✅ Should see debug output in server logs showing patient batches")
    print("✅ Should get 2079+ accident records instead of 996")
    print("✅ No more 414 Request-URI Too Large errors")

if __name__ == "__main__":
    test_summary_fix()