import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check database connection and initialize tables if DATABASE_URL is set
    if engine is not None:
        try:
            with engine.connect() as conn:
                logger.info("Successfully connected to the database.")
            # Automatically ensure tables exist on startup if configured
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            logger.warning(f"Database connection check during startup failed: {e}")
    else:
        logger.info("DATABASE_URL not set in environment; skipping database table auto-initialization.")
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "message": "ReturnSentinel AI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }