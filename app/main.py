from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from .routers import auth, nurse, patients, admin
from .routers import admin
from .config import settings

app = FastAPI(
    title="Hospital Accicent Data Core Backend",
    description="Core backend service for user auth, data CRUD, and hospital-level role-based access.",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(nurse.router, prefix="/api/nurse", tags=["Nurse Functions"])
# app.include_router(patients.router, prefix="/api/patients", tags=["Patient Management"])
app.include_router(admin.router, prefix="/api/admin", tags=["Hospital Admin"])

@app.get("/")
def root():
    return {"message": "Core Backend API is running"}
