from supabase import create_client, Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# --- Supabase Client ---
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# --- PostgreSQL (SQLAlchemy) ---
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
