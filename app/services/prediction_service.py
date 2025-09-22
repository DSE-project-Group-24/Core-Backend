# import joblib
# import os
# from typing import List, Dict, Any
# from fastapi import HTTPException

# # Load trained SARIMA model at module level (like your working example)
# try:
#     model_path = os.path.join("trained_models", "sarima_model_M.pkl")
#     if os.path.exists(model_path):
#         model = joblib.load(model_path)
#         print(f"Model loaded successfully from {model_path}")
#     else:
#         print(f"Model file not found at {model_path}")
#         model = None
# except Exception as e:
#     print(f"Error loading model: {e}")
#     model = None

# def get_forecast_service(months: int) -> List[Dict[str, Any]]:
#     """Service function to get forecast"""
#     if model is None:
#         raise HTTPException(
#             status_code=500,
#             detail="Model not loaded. Please ensure sarima_model.pkl exists in the trained_models directory."
#         )
    
#     try:
#         # Generate forecast (same logic as your working example)
#         forecast = model.get_forecast(steps=months)
#         forecast_df = forecast.summary_frame()
        
#         # Convert to JSON-friendly dict
#         return forecast_df.to_dict(orient="records")
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error generating forecast: {str(e)}"
#         )


import os
import joblib
from typing import List, Dict, Any
from fastapi import HTTPException

# Load both SARIMA models at module level
models = {}
model_names = ["sarima_model_M", "sarima_model_S"]

for model_name in model_names:
    try:
        model_path = os.path.join("trained_models", f"{model_name}.pkl")
        if os.path.exists(model_path):
            models[model_name] = joblib.load(model_path)
            print(f"Model {model_name} loaded successfully from {model_path}")
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