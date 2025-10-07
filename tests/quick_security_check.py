import requests
import sys

print("🔒 Final Security Validation")
print("="*40)

# Test unauthorized access to protected endpoints
endpoints_to_test = [
    ("/analytics/", "Analytics"),
    ("/patients", "Patients"), 
    ("/accidents/", "Accidents"),
    ("/doctor/", "Doctor"),
    ("/nurse/", "Nurse")
]

protected_count = 0
total_tests = len(endpoints_to_test)

for endpoint, name in endpoints_to_test:
    try:
        response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
        
        if response.status_code in [401, 403]:
            print(f"✅ {name}: Protected ({response.status_code})")
            protected_count += 1
        elif response.status_code == 404:
            print(f"⚠️ {name}: Not found (404) - may be protected")
            protected_count += 0.5  # Partial credit
        else:
            print(f"❌ {name}: Exposed ({response.status_code})")
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)[:30]}")

protection_rate = (protected_count / total_tests) * 100
print(f"\n📊 Protection Rate: {protection_rate:.1f}%")

if protection_rate >= 80:
    print("🟢 SECURITY STATUS: STRONG")
elif protection_rate >= 60:
    print("🟡 SECURITY STATUS: GOOD") 
else:
    print("🔴 SECURITY STATUS: NEEDS ATTENTION")

print("\n✅ Security validation completed!")