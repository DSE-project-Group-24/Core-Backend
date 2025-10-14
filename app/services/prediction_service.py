import os
import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from typing import List, Dict, Any
from fastapi import HTTPException
import pandas as pd
# Load both SARIMA models at module level
models = {}
model_names = ["sarima_model_M", "sarima_model_S"]

for model_name in model_names:
    try:
        model_path = os.path.join("trained_models", f"{model_name}.pkl")
        if os.path.exists(model_path):
            models[model_name] = joblib.load(model_path)
            print(f"✅ Model {model_name} loaded successfully from {model_path}")
        else:
            print(f"Model file {model_name}.pkl not found at {model_path}")
            models[model_name] = None
    except Exception as e:
        print(f"Error loading model {model_name}: {e}")
        models[model_name] = None


def get_forecast_service(months: int) -> Dict[str, List[Dict[str, Any]]]:
    """Service function to get forecast for both models"""
    forecasts = {"forecast_M": [], "forecast_S": []}
    
    for model_type in ["M", "S"]:
        model_name = f"sarima_model_{model_type}"
        model = models.get(model_name)
        
        if model is None:
            print(f"Warning: Model {model_name} not loaded, returning empty forecast for {model_type}")
            continue
        
        try:
            # Generate forecast
            forecast = model.get_forecast(steps=months)
            forecast_df = forecast.summary_frame()
            
            # Convert to JSON-friendly dict
            forecasts[f"forecast_{model_type}"] = forecast_df.to_dict(orient="records")
            
        except Exception as e:
            print(f"Error generating forecast for {model_name}: {str(e)}")
            continue
    
    if not any(forecasts.values()):  # If both forecasts are empty
        raise HTTPException(
            status_code=500,
            detail="Failed to generate forecasts for both models. Please ensure model files exist in the trained_models directory."
        )
    
    return forecasts


# Load the new daily accident model
daily_model_path = os.path.join("trained_models", "Week_TS.pkl")
try:
    daily_model: SARIMAXResults = SARIMAXResults.load(daily_model_path)
    print("✅ Daily accident SARIMA model loaded successfully.")
except Exception as e:
    daily_model = None
    print(f"Error loading daily SARIMA model: {e}")

def get_daily_forecast(days: int) -> pd.Series:
    """Forecast next 'days' of daily accidents using final_sarima_model."""
    if daily_model is None:
        raise HTTPException(status_code=500, detail="Daily SARIMA model not loaded.")
    
    try:
        forecast = daily_model.forecast(steps=days)
        # Returns a pandas Series with date index and predicted_mean
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")


