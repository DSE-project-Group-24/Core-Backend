from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.hospital_routes import router as hospital_router
from app.routes.nurse_routes import router as nurse_router
from app.routes.doctor_routes import router as doctor_router
from app.routes.patient_routes import router as patient_router
from app.routes.accident_routes import router as accident_router
from app.routes.medical_routes import router as medical_router
from app.routes.gov_routes import router as gov_router
from app.routes.prediction_routes import router as prediction_router
from app.routes.prediction_transferprobability import router as prediction_transferprobability_router
from app.routes.accident_analytics_routes import router as analytics_router  
from app.routes.transfer_routes import router as transfer_router
from app.routes.discharge_outcome_routes import router as discharge_outcome_router
from app.routes.hospital_stay_service_route import router as hospital_stay_service_router

# from app.routes.govDash_routes import router as gov_dash_routes
from app.routes.govDash_routes import router as govDash_routes 

app = FastAPI(title="FastAPI + Supabase", redirect_slashes=False)


origins = [
    "http://localhost:5173",  
    "http://localhost:3000",  
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "https://roadaccidentcaresystem.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Users"])
app.include_router(hospital_router, prefix="/hospital", tags=["Hospitals"])
app.include_router(nurse_router, prefix="/nurse", tags=["Nurses"])
app.include_router(doctor_router, prefix="/doctor", tags=["Doctors"])
app.include_router(patient_router, prefix="/patients", tags=["Patients"])
app.include_router(accident_router, prefix="/accidents", tags=["Accident Records"])
app.include_router(medical_router, prefix="/medical", tags=["Medical Records"])
app.include_router(gov_router, prefix="/gov/rules", tags=["Government"])
app.include_router(prediction_router, prefix="/predictions", tags=["Predictions"])

app.include_router(prediction_transferprobability_router, prefix="/predictions", tags=["Predictions"])
app.include_router(discharge_outcome_router, prefix="/predictions", tags=["Discharge Outcome Predictions"])
app.include_router(hospital_stay_service_router, prefix="/predictions", tags=["Hospital Stay Predictions"])

# Include analytics routes
app.include_router(analytics_router, prefix="/analytics", tags=["Accident Analytics"])
app.include_router(govDash_routes, prefix="/govDash", tags=["Government Dashboard"])

# transer routes
app.include_router(transfer_router, prefix="/transfers", tags=["Transfers"])


# Add preflight OPTIONS handler (important for Render)
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str = None):
    return {"message": "OK"}



@app.get("/_routes")
def _routes():
    return [{"path": r.path, "methods": list(getattr(r, "methods", []))} for r in app.routes]

