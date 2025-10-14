from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.auth.dependencies import get_current_user
from app.services import hospital_stay_service

router = APIRouter()


@router.post('/hospital-stay-predict', dependencies=[Depends(get_current_user)])
async def predict(payload: Dict[str, Any]):
    """Accepts body with `data` key containing a list of records.

    Example body:
    { "data": [ {...}, {...} ] }
    """
    try:
        if 'data' not in payload:
            raise HTTPException(status_code=400, detail='Payload must contain `data` list')
        data = payload['data']
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail='`data` must be a list of records')
        result = hospital_stay_service.predict_records(data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
