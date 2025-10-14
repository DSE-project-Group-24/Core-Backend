# Discharge Outcome Prediction API

## Overview

The Discharge Outcome Prediction API is integrated into the existing FastAPI backend to predict patient discharge outcomes using a trained CatBoost machine learning model. This API provides predictions for three possible discharge outcomes based on patient data and accident/injury information.

## Integration Details

### Files Added/Modified

#### New Files Created:

1. **`app/models/discharge_outcome.py`** - Pydantic models for request/response
2. **`app/services/discharge_outcome_service.py`** - Core prediction service and preprocessing
3. **`app/routes/discharge_outcome_routes.py`** - FastAPI routes for the API endpoints
4. **`test_discharge_outcome_api.py`** - Test script for validation

#### Modified Files:

1. **`app/main.py`** - Added discharge outcome router to the main application

### Model Information

- **Model Type**: CatBoost Classifier
- **Model File**: `trained_models/catboost_top25_model.cbm`
- **Features Used**: 25 most important features selected during training
- **Prediction Classes**:
  - Complete Recovery
  - Further Interventions
  - Partial Recovery

### Dependencies

- **CatBoost**: Already included in `requirements.txt`
- **pandas**: For data preprocessing
- **numpy**: For numerical operations
- **re**: For text preprocessing

## API Endpoints

All endpoints require authentication and are prefixed with `/predictions`

### 1. Predict Discharge Outcome

**POST** `/predictions/discharge-outcome`

Predicts patient discharge outcome based on input features.

**Request Body**: `DischargeOutcomePredictionRequest`

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

**Response**: `DischargeOutcomePredictionResponse`

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
    "Family Current Status": "Moderately Affected"
    // ... other preprocessed features
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

### 2. Get Model Information

**GET** `/predictions/discharge-outcome/model-info`

Returns detailed information about the model.

**Response**: `DischargeOutcomeModelInfo`

```json
{
  "features": ["Current Hospital Name", "Family Current Status", ...],
  "total_features": 25,
  "classes": ["Complete Recovery", "Further Interventions", "Partial Recovery"],
  "model_type": "CatBoost Classifier",
  "description": "Trained model for predicting patient discharge outcomes using top 25 features"
}
```

### 3. Health Check

**GET** `/predictions/discharge-outcome/health`

Checks if the model is loaded and ready for predictions.

**Response**:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "trained_models/catboost_top25_model.cbm",
  "features_count": 25,
  "classes_count": 3
}
```

### 4. Get Features List

**GET** `/predictions/discharge-outcome/features`

Returns the list of features used by the model.

**Response**:

```json
{
  "features": ["Current Hospital Name", "Family Current Status", ...],
  "total_features": 25,
  "description": "These are the 25 most important features used by the CatBoost model"
}
```

### 5. Get Prediction Classes

**GET** `/predictions/discharge-outcome/classes`

Returns the possible prediction outcomes.

**Response**:

```json
{
  "classes": ["Complete Recovery", "Further Interventions", "Partial Recovery"],
  "description": "Possible discharge outcome predictions"
}
```

## Model Features (Top 25)

1. Current Hospital Name
2. Family Current Status
3. Type of injury No 1
4. Traveling Expenditure per day
5. First Hospital Name
6. Date Of Birth_year
7. Site of Injury No1
8. Approximate Speed
9. Incident At Time and Date_month
10. Hospital Distance From Home
11. Date Of Birth_month
12. Mode of Transport to the Hospital
13. Educational Qualification
14. Time Taken To Reach Hospital
15. Any Other Hospital Admission Expenditure
16. Site of injury No 2
17. Occupation
18. Date Of Birth_day
19. Family Monthly Income Before Accident
20. Collision With
21. Incident At Time and Date_day
22. Life Style
23. Collision Force From
24. Road Type
25. Type of Injury No 2

## Data Preprocessing

The service includes comprehensive preprocessing that matches the training pipeline:

### Text Normalization

- Case conversion to lowercase
- Whitespace normalization
- Special character handling

### Injury Site Standardization

- Maps injury descriptions to standardized categories
- Handles variations in medical terminology
- Groups similar injury sites

### Injury Type Standardization

- Standardizes injury type descriptions
- Maps medical terms to consistent categories

### Date Feature Engineering

- Extracts year, month, and day from date fields
- Handles date parsing errors gracefully

### Missing Value Handling

- Fills missing values with -999 (training standard)
- Ensures all required features are present

## Authentication & Security

- All endpoints require valid user authentication
- Uses existing `get_current_user` dependency
- Follows the same security patterns as other API endpoints

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication
- **500 Internal Server Error**: Model loading issues, prediction failures

## Testing

Use the provided test script:

```bash
python test_discharge_outcome_api.py
```

## Usage Examples

### JavaScript/Frontend Integration

```javascript
// Predict discharge outcome
const predictionData = {
  current_hospital_name: "DGH – Kilinochchi",
  family_current_status: "Moderately Affected",
  // ... other fields
};

const response = await fetch("/predictions/discharge-outcome", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify(predictionData),
});

const result = await response.json();
console.log("Predicted outcome:", result.prediction);
console.log("Probabilities:", result.prediction_probabilities);
```

### Python Client Example

```python
import requests

# Get model health
response = requests.get(
    'http://localhost:8000/predictions/discharge-outcome/health',
    headers={'Authorization': f'Bearer {token}'}
)
health = response.json()
print(f"Model status: {health['status']}")

# Make prediction
prediction_response = requests.post(
    'http://localhost:8000/predictions/discharge-outcome',
    json=prediction_data,
    headers={'Authorization': f'Bearer {token}'}
)
result = prediction_response.json()
print(f"Prediction: {result['prediction']}")
```

## Troubleshooting

### Common Issues

1. **Model not loading**

   - Check if `catboost_top25_model.cbm` exists in `trained_models/`
   - Verify CatBoost is installed: `pip install catboost`

2. **Import errors**

   - Ensure all dependencies are installed from `requirements.txt`
   - Check Python environment compatibility

3. **Prediction failures**

   - Verify input data format matches the expected schema
   - Check for required fields and data types

4. **Authentication errors**
   - Ensure valid authentication token is provided
   - Check if user has required permissions

## Performance Considerations

- Model loads once at startup (singleton pattern)
- Predictions are fast (typically < 100ms)
- Memory usage is minimal after model loading
- Preprocessing is optimized for single predictions

## Future Enhancements

1. **Batch Predictions**: Support for multiple predictions in single request
2. **Model Versioning**: Support for multiple model versions
3. **Feature Importance**: Return feature importance scores
4. **Prediction Explanations**: Add SHAP/LIME explanations
5. **Model Monitoring**: Add prediction logging and monitoring

## Integration with Existing System

The discharge outcome prediction seamlessly integrates with your existing system:

- Uses the same authentication system
- Follows established API patterns
- Maintains consistent error handling
- Leverages existing database connections (if needed)
- Compatible with current frontend architecture

This integration provides powerful ML capabilities while maintaining the existing system's reliability and security standards.
