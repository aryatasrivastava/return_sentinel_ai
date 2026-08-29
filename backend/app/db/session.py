from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Base Declarative Class for all models
Base = declarative_base()

# Engine creation with sensible defaults for PostgreSQL / connection pooling
# If DATABASE_URL is not set in .env, engine is None until configured
engine = None
SessionLocal = None

if settings.DATABASE_URL:
    db_url = settings.DATABASE_URL
    # Ensure postgresql:// prefix compatibility with SQLAlchemy (e.g. postgres:// -> postgresql://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    else:
        # PostgreSQL pool settings suitable for serverless / pooled connections (Supabase)
        connect_args = {"connect_timeout": 10}

    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """FastAPI dependency for yielding database sessions."""
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured in .env. "
            "Please set a valid PostgreSQL connection string."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
