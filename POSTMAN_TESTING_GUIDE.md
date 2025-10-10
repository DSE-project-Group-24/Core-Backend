# Postman Testing Guide for Discharge Outcome Prediction API

## 🚀 **Setup Steps**

### 1. **Start Your Server**

First, make sure your FastAPI server is running:

```bash
cd "C:\Users\User\Desktop\Data Science Project\XXX\Core-Backend"
uvicorn app.main:app --reload --port 8000
```

Your server should be accessible at: `http://localhost:8000`

### 2. **Verify Server is Running**

Check if the server is running by visiting: `http://localhost:8000/docs`
You should see the FastAPI interactive documentation (Swagger UI).

---

## 🔐 **Authentication Setup**

Since all endpoints require authentication (`get_current_user`), you'll need to authenticate first.

### **Step 1: Login to Get Token**

**Request:**

- **Method**: `POST`
- **URL**: `http://localhost:8000/auth/login`
- **Headers**: `Content-Type: application/json`
- **Body** (raw JSON):

```json
{
  "email": "your_email@example.com",
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
    "name": "John Doe",
    "email": "your_email@example.com",
    "role": "nurse"
  }
}
```

### **Step 2: Use Token for Subsequent Requests**

For all discharge outcome API calls, add this header:

- **Key**: `Authorization`
- **Value**: `Bearer YOUR_ACCESS_TOKEN_HERE`

---

## 🧪 **Testing the Discharge Outcome Endpoints**

### **Test 1: Health Check**

**Request:**

- **Method**: `GET`
- **URL**: `http://localhost:8000/predictions/discharge-outcome/health`
- **Headers**:
  - `Authorization: Bearer YOUR_TOKEN`

**Expected Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "trained_models/catboost_top25_model.cbm",
  "features_count": 25,
  "classes_count": 3
}
```

---

### **Test 2: Get Model Information**

**Request:**

- **Method**: `GET`
- **URL**: `http://localhost:8000/predictions/discharge-outcome/model-info`
- **Headers**:
  - `Authorization: Bearer YOUR_TOKEN`

**Expected Response:**

```json
{
  "features": [
    "Current Hospital Name",
    "Family Current Status",
    "Type of injury No 1",
    "..."
  ],
  "total_features": 25,
  "classes": ["Complete Recovery", "Further Interventions", "Partial Recovery"],
  "model_type": "CatBoost Classifier",
  "description": "Trained model for predicting patient discharge outcomes using top 25 features"
}
```

---

### **Test 3: Get Features List**

**Request:**

- **Method**: `GET`
- **URL**: `http://localhost:8000/predictions/discharge-outcome/features`
- **Headers**:
  - `Authorization: Bearer YOUR_TOKEN`

**Expected Response:**

```json
{
  "features": [
    "Current Hospital Name",
    "Family Current Status",
    "Type of injury No 1",
    "Traveling Expenditure per day",
    "First Hospital Name",
    "..."
  ],
  "total_features": 25,
  "description": "These are the 25 most important features used by the CatBoost model"
}
```

---

### **Test 4: Get Prediction Classes**

**Request:**

- **Method**: `GET`
- **URL**: `http://localhost:8000/predictions/discharge-outcome/classes`
- **Headers**:
  - `Authorization: Bearer YOUR_TOKEN`

**Expected Response:**

```json
{
  "classes": ["Complete Recovery", "Further Interventions", "Partial Recovery"],
  "description": "Possible discharge outcome predictions"
}
```

---

### **Test 5: Make a Prediction (Main Test)**

**Request:**

- **Method**: `POST`
- **URL**: `http://localhost:8000/predictions/discharge-outcome`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer YOUR_TOKEN`
- **Body** (raw JSON):

```json
{
  "current_hospital_name": "DGH – Kilinochchi",
  "family_current_status": "Moderately Affected",
  "type_of_injury_no_1": "fracture",
  "traveling_expenditure_per_day": "100-200",
  "first_hospital_name": "DGH – Kilinochchi",
  "date_of_birth": "1990-05-15",
  "site_of_injury_no1": "head injury",
  "approximate_speed": "40 - 80 km/h",
  "incident_at_time_and_date": "2023-10-15",
  "hospital_distance_from_home": "5-10 Km",
  "mode_of_transport_to_the_hospital": "Ambulance",
  "educational_qualification": "O/L or A/L",
  "time_taken_to_reach_hospital": "Less Than 15 Minutes",
  "any_other_hospital_admission_expenditure": "No Other Expenses",
  "site_of_injury_no_2": "no secondary injury found",
  "occupation": "Student",
  "family_monthly_income_before_accident": "30000-45000",
  "collision_with": "Motorbike",
  "life_style": "Living with care givers",
  "collision_force_from": "Front",
  "road_type": "Straight",
  "type_of_injury_no_2": "abrasion"
}
```

**Expected Response:**

```json
{
  "prediction": "Complete Recovery",
  "prediction_probabilities": {
    "Complete Recovery": 0.7543,
    "Further Interventions": 0.1234,
    "Partial Recovery": 0.1223
  },
  "preprocessed_features": {
    "Current Hospital Name": "DGH – Kilinochchi",
    "Family Current Status": "Moderately Affected",
    "Type of injury No 1": "fracture",
    "..."
  },
  "model_info": {
    "model_type": "CatBoost Classifier",
    "features_used": 25,
    "classes": [
      "Complete Recovery",
      "Further Interventions",
      "Partial Recovery"
    ]
  }
}
```

---

## 📚 **Postman Collection Setup**

### **Create a Postman Collection:**

1. **Open Postman**
2. **Create New Collection**: "Discharge Outcome Prediction API"
3. **Add Environment Variables**:
   - `base_url`: `http://localhost:8000`
   - `auth_token`: (will be set after login)

### **Collection Structure:**

```
📁 Discharge Outcome Prediction API
├── 🔐 Authentication
│   └── POST Login
├── ✅ Health & Info
│   ├── GET Health Check
│   ├── GET Model Info
│   ├── GET Features
│   └── GET Classes
└── 🎯 Predictions
    └── POST Predict Discharge Outcome
```

### **Environment Variables Usage:**

- **Base URL**: `{{base_url}}`
- **Authorization Header**: `Bearer {{auth_token}}`

---

## 🚨 **Common Issues & Troubleshooting**

### **1. Server Not Running**

**Error**: Connection refused
**Solution**: Make sure your server is running on port 8000

### **2. Authentication Error**

**Error**: `401 Unauthorized`
**Solution**:

- Get a valid token from `/auth/login`
- Add `Authorization: Bearer YOUR_TOKEN` header

### **3. Model Not Loaded**

**Error**: "Model not loaded. Please check server logs."
**Solution**:

- Check if `catboost_top25_model.cbm` exists in `trained_models/`
- Install CatBoost: `pip install catboost`
- Restart the server

### **4. Import Errors**

**Error**: Module import issues
**Solution**:

- Install dependencies: `pip install -r requirements.txt`
- Check Python environment

### **5. Validation Errors**

**Error**: `422 Unprocessable Entity`
**Solution**:

- Check JSON format in request body
- Ensure date format is `YYYY-MM-DD`

---

## 🎯 **Testing Checklist**

- [ ] Server is running (`http://localhost:8000/docs` works)
- [ ] Successfully logged in and got auth token
- [ ] Health check returns "healthy" status
- [ ] Model info shows 25 features and 3 classes
- [ ] Features endpoint returns all 25 feature names
- [ ] Classes endpoint returns 3 prediction classes
- [ ] Prediction endpoint accepts sample data and returns valid prediction
- [ ] All responses have correct structure and data types
- [ ] Error handling works (try invalid token, malformed JSON)

---

## 📱 **Quick Test Commands**

### **Using cURL (Alternative to Postman):**

```bash
# Health Check
curl -X GET "http://localhost:8000/predictions/discharge-outcome/health" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Make Prediction
curl -X POST "http://localhost:8000/predictions/discharge-outcome" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "current_hospital_name": "DGH – Kilinochchi",
    "family_current_status": "Moderately Affected",
    "type_of_injury_no_1": "fracture"
  }'
```

This comprehensive guide should help you test the discharge outcome prediction API thoroughly using Postman! 🚀
