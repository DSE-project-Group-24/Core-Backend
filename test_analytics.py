"""
Test file for Accident Analytics API

This file demonstrates how to use the accident analytics API
and provides example responses for testing the frontend integration.
"""

import requests
import json
from datetime import date, timedelta

# API Base URL (adjust as needed)
BASE_URL = "http://localhost:8000"

def test_accident_analytics():
    """Test the main analytics endpoint"""
    
    # Test basic analytics call
    url = f"{BASE_URL}/analytics/accident-eda"
    
    # You'll need to add proper authentication headers
    headers = {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics API working!")
            print(f"Total Records: {data['total_records']}")
            print(f"Peak Hour: {data['peak_accident_hour']}")
            print(f"Common Collision: {data['most_common_collision']}")
            print(f"Avg Income Impact: {data['avg_income_impact']}")
            
            # Show sample data structure
            print("\n📊 Sample Data Structure:")
            print(f"Accident Characteristics: {list(data['accident_characteristics'].keys())}")
            print(f"Demographics: {list(data['demographics'].keys())}")
            print(f"Medical Factors: {list(data['medical_factors'].keys())}")
            
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

def test_with_filters():
    """Test analytics with filters"""
    
    url = f"{BASE_URL}/analytics/accident-eda"
    
    # Example with filters
    params = {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "gender": "Male",
        "age_min": 18,
        "age_max": 65
    }
    
    headers = {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Filtered Analytics working!")
            print(f"Filtered Records: {data['total_records']}")
        else:
            print(f"❌ Filter Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

def test_filter_options():
    """Test getting available filter options"""
    
    url = f"{BASE_URL}/analytics/filters/options"
    
    headers = {
        "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Filter Options API working!")
            print(f"Available Genders: {data['genders']}")
            print(f"Available Ethnicities: {data['ethnicities']}")
            print(f"Age Range: {data['age_range']}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

# Example response structure for your frontend team
EXAMPLE_ANALYTICS_RESPONSE = {
    "accident_characteristics": {
        "hourly_distribution": {
            "0": 15, "1": 8, "2": 5, "3": 3, "4": 7, "5": 12,
            "6": 25, "7": 45, "8": 67, "9": 42, "10": 38, "11": 35,
            "12": 48, "13": 52, "14": 41, "15": 39, "16": 58, "17": 72,
            "18": 69, "19": 45, "20": 38, "21": 32, "22": 28, "23": 22
        },
        "collision_types": {
            "Vehicle": 342,
            "Fixed Object": 198,
            "Pedestrian": 156,
            "Animal": 87,
            "Other Vehicle": 217
        },
        "travel_modes": {
            "Motorcycle": 445,
            "Car": 312,
            "Bicycle": 89,
            "Walking": 76,
            "Bus": 34,
            "Truck": 44
        },
        "road_categories": {
            "Highway": 234,
            "Urban Road": 298,
            "Rural Road": 187,
            "Residential": 156,
            "Industrial": 125
        }
    },
    "demographics": {
        "age_groups": {
            "18-25": 256,
            "26-35": 298,
            "36-45": 187,
            "46-55": 134,
            "56+": 125
        },
        "gender_dist": {
            "Male": 672,
            "Female": 328
        },
        "ethnicity_dist": {
            "Sinhala": 567,
            "Tamil": 234,
            "Muslim": 156,
            "Other": 43
        }
    },
    "medical_factors": {
        "outcomes_dist": {
            "Full Recovery": 456,
            "Partial Recovery": 298,
            "Requires Intervention": 167,
            "Transferred": 79
        },
        "wash_room_access": {
            "True": 823,
            "False": 177
        },
        "avg_hospital_expenditure": 28750.50
    },
    "financial_impact": {
        "income_comparison": {
            "decreased": 567,
            "same": 234,
            "improved": 199
        },
        "avg_income_change": -12500.75,
        "avg_bystander_exp": 2340.50,
        "avg_travel_exp": 890.25
    },
    "temporal_trends": {
        "monthly_trends": {
            "1": 87, "2": 76, "3": 92, "4": 83, "5": 89, "6": 94,
            "7": 98, "8": 103, "9": 87, "10": 91, "11": 85, "12": 95
        },
        "daily_trends": {
            "0": 123, "1": 145, "2": 156, "3": 167, "4": 178,
            "5": 134, "6": 97
        }
    },
    "data_quality": {
        "quality_dist": {
            "Complete": 890,
            "Missing/Incomplete": 110
        },
        "total_records": 1000,
        "completion_rate": 89.0
    },
    "total_records": 1000,
    "peak_accident_hour": 17,
    "most_common_collision": "Vehicle",
    "avg_income_impact": -12500.75,
    "generated_at": "2024-01-01T12:00:00Z"
}

def save_example_response():
    """Save example response to JSON file for frontend team"""
    with open("example_analytics_response.json", "w") as f:
        json.dump(EXAMPLE_ANALYTICS_RESPONSE, f, indent=2)
    print("✅ Example response saved to example_analytics_response.json")

if __name__ == "__main__":
    print("🧪 Testing Accident Analytics API")
    print("=" * 50)
    
    # Save example for frontend team
    save_example_response()
    
    print("\n📝 To test the API:")
    print("1. Make sure your FastAPI server is running on localhost:8000")
    print("2. Replace 'YOUR_JWT_TOKEN_HERE' with a valid JWT token")
    print("3. Uncomment the test functions below")
    
    # Uncomment these lines when you have authentication working:
    # test_accident_analytics()
    # test_with_filters()  
    # test_filter_options()
    
    print("\n🎯 Frontend Integration:")
    print("- Main endpoint: GET /analytics/accident-eda")
    print("- Filter options: GET /analytics/filters/options") 
    print("- Summary stats: GET /analytics/accident-summary")
    print("- Use the example JSON structure for development")