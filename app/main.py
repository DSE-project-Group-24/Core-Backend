
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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI + Supabase")


origins = [
    "http://localhost:5173",  # React Vite default
    "http://localhost:3000",  # React CRA default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register routes
app.include_router(auth_router, prefix="/auth", tags=["Users"])
app.include_router(hospital_router, prefix="/hospital", tags=["Hospitals"])
app.include_router(nurse_router, prefix="/nurse", tags=["Nurses"])
app.include_router(doctor_router, prefix="/doctor", tags=["Doctors"])
app.include_router(patient_router, prefix="/patients", tags=["Patients"])
app.include_router(accident_router, prefix="/accidents", tags=["Accident Records"])
app.include_router(medical_router, prefix="/medical", tags=["Medical Records"])
app.include_router(gov_router, prefix="/gov/rules", tags=["Government"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # your React dev server
        "http://127.0.0.1:5173"    # optional alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





@app.get("/_routes")
def _routes():
    return [{"path": r.path, "methods": list(getattr(r, "methods", []))} for r in app.routes]