import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.policy_config import (
    PolicyConfig,
    DEFAULT_LOW_RISK_ALLOWED,
    DEFAULT_MEDIUM_RISK_ALLOWED,
    DEFAULT_HIGH_RISK_ALLOWED,
    DEFAULT_LOW_CONFIDENCE_FALLBACK,
)
from app.schemas.policy_config import PolicyConfigUpdate, PolicyConfigResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/policy-config", tags=["Policy Config"])


@router.get("", response_model=PolicyConfigResponse)
def get_policy_config(db: Session = Depends(get_db)):
    """Fetch the merchant return policy configuration.

    Returns the single-row config or creates/returns default values if no row
    exists.
    """
    config = db.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
    if not config:
        logger.info("No policy_config row found; creating default configuration.")
        config = PolicyConfig(
            id=1,
            low_risk_allowed=DEFAULT_LOW_RISK_ALLOWED,
            medium_risk_allowed=DEFAULT_MEDIUM_RISK_ALLOWED,
            high_risk_allowed=DEFAULT_HIGH_RISK_ALLOWED,
            low_confidence_fallback=DEFAULT_LOW_CONFIDENCE_FALLBACK,
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("", response_model=PolicyConfigResponse)
def update_policy_config(
    config_in: PolicyConfigUpdate,
    db: Session = Depends(get_db),
):
    """Update the merchant return policy configuration."""
    config = db.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
    if not config:
        config = PolicyConfig(id=1)
        db.add(config)

    config.low_risk_allowed = config_in.low_risk_allowed
    config.medium_risk_allowed = config_in.medium_risk_allowed
    config.high_risk_allowed = config_in.high_risk_allowed
    config.low_confidence_fallback = config_in.low_confidence_fallback
    config.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(config)
    return config
