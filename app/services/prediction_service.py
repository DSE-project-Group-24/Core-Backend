import joblib
import os
from typing import List, Dict, Any
from fastapi import HTTPException

# Load trained SARIMA model at module level (like your working example)
try:
    model_path = os.path.join("trained_models", "sarima_model.pkl")
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print(f"Model loaded successfully from {model_path}")
    else:
        print(f"Model file not found at {model_path}")
        model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def get_forecast_service(months: int) -> List[Dict[str, Any]]:
    """Service function to get forecast"""
    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded. Please ensure sarima_model.pkl exists in the trained_models directory."
        )
    
    try:
        # Generate forecast (same logic as your working example)
        forecast = model.get_forecast(steps=months)
        forecast_df = forecast.summary_frame()
        
        # Convert to JSON-friendly dict
        return forecast_df.to_dict(orient="records")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating forecast: {str(e)}"
        )
