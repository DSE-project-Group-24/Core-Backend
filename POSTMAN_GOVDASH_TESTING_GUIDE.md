# Postman Testing Guide for Government Dashboard Analytics API

## 🎯 **Endpoint Details**

**Endpoint:** `POST /govDash/comprehensive`  
**Purpose:** Get comprehensive accident analytics filtered by date range and severity  
**Authentication:** Required (government personnel only)

---

## 🚀 **Setup Steps**

### 1. **Start Your Server**

```bash
cd "C:\Users\User\Desktop\Data Science Project\XXX\Core-Backend"
uvicorn app.main:app --reload --port 8000
```

### 2. **Verify Server is Running**

Check: `http://localhost:8000/docs` - You should see the FastAPI Swagger UI

---

## 🔐 **Authentication Setup**

### **Step 1: Login to Get Token**

**Request:**

- **Method**: `POST`
- **URL**: `http://localhost:8000/auth/login`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):

```json
{
  "email": "government_user@example.com",
  "password": "your_password"
}
```

**Expected Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "123",
    "name": "Gov User",
    "email": "government_user@example.com",
    "role": "government"
  }
}
```

⚠️ **Note**: Make sure your user has government personnel role for this endpoint!

---

## 🧪 **Testing the Comprehensive Analytics Endpoint**

### **Main Test: POST /govDash/comprehensive**

**Request:**

- **Method**: `POST`
- **URL**: `http://localhost:8000/govDash/comprehensive`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer YOUR_ACCESS_TOKEN`
- **Body** (raw JSON):

#### **Test Case 1: Basic Request**

```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "severity": "S"
}
```

#### **Test Case 2: Different Date Range**

```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-06-30",
  "severity": "M"
}
```

#### **Test Case 3: Short Date Range**

```json
{
  "start_date": "2023-06-01",
  "end_date": "2023-06-30",
  "severity": "S"
}
```

### **Expected Response Structure:**

```json
{
  "results": {
    "time of collision": {
      "Morning": 45,
      "Afternoon": 67,
      "Evening": 23,
      "Night": 12,
      "Unknown": 5
    },
    "Collision with": {
      "Motorbike": 89,
      "Car or Van": 34,
      "Heavy Vehicle": 12,
      "Pedestrian": 8,
      "Unknown": 4
    },
    "Road Condition": {
      "Dry": 102,
      "Wet": 34,
      "Slippery": 8,
      "Unknown": 3
    },
    "Road Type": {
      "Straight": 98,
      "Junction": 45,
      "Bend": 23,
      "Unknown": 2
    },
    "Category of Road": {
      "A Class": 67,
      "B Class": 45,
      "Local Road": 34,
      "Unknown": 2
    },
    "Alcohol Consumption": {
      "Yes": 23,
      "No": 124,
      "Unknown": 1
    },
    "Illicit Drugs": {
      "Yes": 5,
      "No": 142,
      "Unknown": 1
    },
    "Time taken to reach hospital": {
      "Less Than 15 Minutes": 67,
      "15 Minutes - 30 Minutes": 45,
      "30 Minutes - 1 Hour": 23,
      "More Than 2 Hour": 12,
      "Unknown": 1
    },
    "Bystander expenditure per day": {
      "0": 89,
      "100": 34,
      "200": 12,
      "500": 8,
      "Unknown": 5
    },
    "Discharge Outcome": {
      "Complete Recovery": 78,
      "Partial Recovery": 45,
      "Further Interventions": 23,
      "Unknown": 2
    },
    "First aid given at seen": {
      "Yes": 89,
      "No": 56,
      "Unknown": 3
    }
  }
}
```

---

## 📊 **Field Descriptions**

### **Request Fields:**

- **`start_date`**: Start date for filtering (YYYY-MM-DD format)
- **`end_date`**: End date for filtering (YYYY-MM-DD format)
- **`severity`**: Severity level - use `"S"` for Serious or `"M"` for Minor

### **Response Fields:**

- **`results`**: Object containing analysis for each accident attribute
- Each key represents a column from the accident records
- Values show count of accidents for each category within that column

---

## ⚠️ **Common Issues & Troubleshooting**

### **1. Authentication Error (401)**

**Error**: `401 Unauthorized`
**Solutions**:

- Ensure you're logged in with government personnel role
- Check if Authorization header is properly set: `Bearer YOUR_TOKEN`
- Token might be expired - get a new one

### **2. Permission Error (403)**

**Error**: `403 Forbidden`
**Solutions**:

- Make sure your user has government personnel role
- Check if the `government_personnel_required` dependency is satisfied

### **3. Validation Error (422)**

**Error**: `422 Unprocessable Entity`
**Solutions**:

- Check date format: must be `YYYY-MM-DD`
- Ensure severity is either `"S"` or `"M"`
- Verify all required fields are provided

### **4. Server Error (500)**

**Error**: `500 Internal Server Error`
**Solutions**:

- Check server logs for specific error details
- Database connection issues
- Invalid date range (end_date before start_date)

### **5. Empty Results**

**Response**: Empty categories or "No Data"
**Causes**:

- No accidents found for the specified filters
- Date range might be too narrow
- Severity filter might not match any records

---

## 🧪 **Testing Checklist**

### **Pre-requisites:**

- [ ] Server is running on port 8000
- [ ] User has government personnel role
- [ ] Valid authentication token obtained

### **Test Scenarios:**

- [ ] **Valid Request**: Proper date range and severity
- [ ] **Different Severities**: Test both "S" and "M"
- [ ] **Various Date Ranges**: Wide range, narrow range, recent dates
- [ ] **Edge Cases**: Same start and end date
- [ ] **Invalid Data**: Wrong date format, invalid severity
- [ ] **No Results**: Date range with no accidents

### **Response Validation:**

- [ ] Status code is 200
- [ ] Response contains `results` object
- [ ] Each column has category counts
- [ ] Counts are positive integers
- [ ] No null or undefined values

---

## 🔧 **Advanced Testing with cURL**

### **Basic Request:**

```bash
curl -X POST "http://localhost:8000/govDash/comprehensive" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "severity": "S"
  }'
```

### **Test Different Severity:**

```bash
curl -X POST "http://localhost:8000/govDash/comprehensive" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "severity": "M"
  }'
```

---

## 📈 **Understanding the Results**

The response provides statistical breakdowns for 11 key accident attributes:

1. **Time of collision** - When accidents occur
2. **Collision with** - What vehicles/objects were involved
3. **Road Condition** - State of the road surface
4. **Road Type** - Geometry of the road (straight, junction, etc.)
5. **Category of Road** - Road classification (A Class, B Class, etc.)
6. **Alcohol Consumption** - Involvement of alcohol
7. **Illicit Drugs** - Involvement of illegal substances
8. **Time taken to reach hospital** - Emergency response time
9. **Bystander expenditure per day** - Daily costs for bystanders
10. **Discharge Outcome** - Patient recovery status
11. **First aid given at seen** - Whether first aid was provided at scene

Each attribute shows the count of accidents falling into different categories, helping identify patterns and trends in accident data.

---

## 🎯 **Sample Postman Collection**

You can import this collection structure into Postman:

```json
{
  "info": {
    "name": "Government Dashboard Analytics",
    "description": "Test comprehensive accident analytics"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{auth_token}}",
        "type": "string"
      }
    ]
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/auth/login",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"government_user@example.com\",\n  \"password\": \"your_password\"\n}"
        }
      }
    },
    {
      "name": "Comprehensive Analytics - Serious",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/govDash/comprehensive",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"start_date\": \"2023-01-01\",\n  \"end_date\": \"2023-12-31\",\n  \"severity\": \"S\"\n}"
        }
      }
    },
    {
      "name": "Comprehensive Analytics - Minor",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/govDash/comprehensive",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"start_date\": \"2024-01-01\",\n  \"end_date\": \"2024-06-30\",\n  \"severity\": \"M\"\n}"
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "auth_token",
      "value": ""
    }
  ]
}
```

This comprehensive guide should help you thoroughly test the government dashboard analytics endpoint! 🚀
