from fastapi import APIRouter, Depends, HTTPException
from app.models.discharge_outcome import (
    DischargeOutcomePredictionRequest,
    DischargeOutcomePredictionResponse,
    DischargeOutcomeModelInfo
)
from app.services.discharge_outcome_service import (
    predict_discharge_outcome_service,
    get_discharge_outcome_model_info_service,
    get_discharge_outcome_model_health_service
)
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/discharge-outcome", response_model=DischargeOutcomePredictionResponse, dependencies=[Depends(get_current_user)])
def predict_discharge_outcome(
    request: DischargeOutcomePredictionRequest,
    user=Depends(get_current_user)
):
    """
    Predict patient discharge outcome based on input features.
    
    This endpoint uses a trained CatBoost model to predict the likely discharge outcome
    for a patient based on various medical and demographic factors.
    
    **Possible outcomes:**
    - Complete Recovery
    - Further Interventions
    - Partial Recovery
    """
    try:
        result = predict_discharge_outcome_service(request)
        return DischargeOutcomePredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/discharge-outcome/model-info", response_model=DischargeOutcomeModelInfo)
def get_discharge_outcome_model_info(user=Depends(get_current_user)):
    """
    Get information about the discharge outcome prediction model.
    
    Returns details about the features used, possible classes, and model type.
    """
    try:
        result = get_discharge_outcome_model_info_service()
        return DischargeOutcomeModelInfo(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

@router.get("/discharge-outcome/health")
def get_discharge_outcome_model_health(user=Depends(get_current_user)):
    """
    Check the health status of the discharge outcome prediction model.
    
    Returns information about whether the model is loaded and ready to make predictions.
    """
    try:
        return get_discharge_outcome_model_health_service()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/discharge-outcome/features")
def get_discharge_outcome_features(user=Depends(get_current_user)):
    """
    Get the list of features used by the discharge outcome prediction model.
    
    Returns the 25 most important features used by the CatBoost model.
    """
    try:
        model_info = get_discharge_outcome_model_info_service()
        return {
            "features": model_info["features"],
            "total_features": model_info["total_features"],
            "description": "These are the 25 most important features used by the CatBoost model"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get features: {str(e)}")

@router.get("/discharge-outcome/classes")
def get_discharge_outcome_classes(user=Depends(get_current_user)):
    """
    Get the possible prediction classes for discharge outcomes.
    
    Returns the three possible discharge outcome classes that the model can predict.
    """
    try:
        model_info = get_discharge_outcome_model_info_service()
        return {
            "classes": model_info["classes"],
            "description": "Possible discharge outcome predictions"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get classes: {str(e)}")