import logging
from app.db.session import engine
from app.db.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """Create all database tables defined in Base metadata."""
    if engine is None:
        raise RuntimeError(
            "Cannot initialize database: DATABASE_URL is not set in environment or .env"
        )
    logger.info("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("All 9 tables created successfully.")


if __name__ == "__main__":
    init_db()
