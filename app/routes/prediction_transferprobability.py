from fastapi import APIRouter, Body
from app.services.prediction_transferprobability_service import make_prediction

router = APIRouter()

@router.post("/transferprobability")
def predict(data: dict = Body(...)):
    try:
        result = make_prediction(data)
        return {"message": "Prediction complete", **result}
    except Exception as e:
        return {"error": str(e)}
