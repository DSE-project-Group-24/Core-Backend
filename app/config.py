import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Hospital Accident Data Core Backend"
    VERSION: str = "1.0.0"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]  # React frontend

    # Supabase / PostgreSQL
    SUPABASE_URL: str 
    SUPABASE_KEY: str 
    DATABASE_URL: str  # PostgreSQL connection string

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()