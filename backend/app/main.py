import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.api.policy_config import router as policy_config_router
from app.api.assess_order import router as assess_order_router
from app.api.orders import router as orders_router
from app.api.dashboard import router as dashboard_router
from app.api.products import router as products_router
from app.models.policy_config import (
    PolicyConfig,
    DEFAULT_LOW_RISK_ALLOWED,
    DEFAULT_MEDIUM_RISK_ALLOWED,
    DEFAULT_HIGH_RISK_ALLOWED,
    DEFAULT_LOW_CONFIDENCE_FALLBACK,
)

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

            # Ensure default policy_config row exists
            if SessionLocal is not None:
                with SessionLocal() as db:
                    config = db.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
                    if not config:
                        default_cfg = PolicyConfig(
                            id=1,
                            low_risk_allowed=DEFAULT_LOW_RISK_ALLOWED,
                            medium_risk_allowed=DEFAULT_MEDIUM_RISK_ALLOWED,
                            high_risk_allowed=DEFAULT_HIGH_RISK_ALLOWED,
                            low_confidence_fallback=DEFAULT_LOW_CONFIDENCE_FALLBACK,
                        )
                        db.add(default_cfg)
                        db.commit()
                        logger.info("Seeded default policy configuration.")
        except Exception as e:
            logger.warning(f"Database connection/initialization during startup failed: {e}")
    else:
        logger.info("DATABASE_URL not set in environment; skipping database table auto-initialization.")
    yield
    # Shutdown logic (if any)


import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

# CORS Configuration for frontend dev and production
frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
origins = list(set([
    frontend_origin,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(policy_config_router, prefix="/api")
app.include_router(assess_order_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(products_router, prefix="/api")



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
