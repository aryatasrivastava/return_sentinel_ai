import logging
from typing import Any, Dict, List
from app.db.session import SessionLocal
from app.models.policy_config import (
    PolicyConfig,
    DEFAULT_LOW_RISK_ALLOWED,
    DEFAULT_MEDIUM_RISK_ALLOWED,
    DEFAULT_HIGH_RISK_ALLOWED,
    DEFAULT_LOW_CONFIDENCE_FALLBACK,
)

logger = logging.getLogger(__name__)


def _fetch_live_policy_config() -> PolicyConfig:
    """Independently queries the live single-row policy_config from the database.

    Defensively falls back to defaults if database connection or row is absent.
    """
    if SessionLocal is not None:
        try:
            with SessionLocal() as session:
                cfg = session.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
                if cfg:
                    return cfg
        except Exception as e:
            logger.warning(
                f"Policy Engine could not query live policy_config from DB: {e}; using defaults."
            )

    return PolicyConfig(
        id=1,
        low_risk_allowed=DEFAULT_LOW_RISK_ALLOWED,
        medium_risk_allowed=DEFAULT_MEDIUM_RISK_ALLOWED,
        high_risk_allowed=DEFAULT_HIGH_RISK_ALLOWED,
        low_confidence_fallback=DEFAULT_LOW_CONFIDENCE_FALLBACK,
    )


def validate_policy(
    recommended_policy: str,
    risk_level: str,
    is_low_confidence: bool,
) -> Dict[str, Any]:
    """Validate that the recommended policy strictly adheres to merchant configuration.

    This function independently fetches policy_config and never trusts caller-passed config.
    If valid, returns the recommended policy unchanged.
    If invalid, logs a warning, raises an anomaly flag, and falls back to a deterministic safe default.

    Args:
        recommended_policy: The policy suggested upstream (e.g. by the Policy Agent).
        risk_level: 'LOW', 'MEDIUM', or 'HIGH'.
        is_low_confidence: Boolean indicating whether confidence investigation budget was exhausted.

    Returns:
        Structured dictionary:
        {
            "final_policy": str,
            "validation_passed": bool,
            "anomaly": bool,
            "details": dict
        }

    Raises:
        ValueError: If risk_level is invalid or structurally malformed.
    """
    # 1. Validate risk_level input
    if not isinstance(risk_level, str):
        raise ValueError(f"risk_level must be a string, got {type(risk_level).__name__}")

    norm_risk_level = risk_level.strip().upper()
    if norm_risk_level not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError(
            f"Invalid risk_level: '{risk_level}'. Expected 'LOW', 'MEDIUM', or 'HIGH'."
        )

    # 2. Independently fetch live policy_config from database
    policy_config = _fetch_live_policy_config()

    # 3. Determine applicable validation rules
    if is_low_confidence:
        expected_fallback: str = policy_config.low_confidence_fallback
        checked_against = expected_fallback
        is_valid = (recommended_policy == expected_fallback)
        safe_fallback = expected_fallback
    else:
        if norm_risk_level == "LOW":
            allowed_list: List[str] = policy_config.low_risk_allowed
        elif norm_risk_level == "HIGH":
            allowed_list = policy_config.high_risk_allowed
        else:
            allowed_list = policy_config.medium_risk_allowed

        checked_against = allowed_list
        is_valid = (recommended_policy in allowed_list)
        safe_fallback = allowed_list[0] if allowed_list else policy_config.low_confidence_fallback

    # 4. Success path
    if is_valid:
        return {
            "final_policy": recommended_policy,
            "validation_passed": True,
            "anomaly": False,
            "details": {
                "risk_level": norm_risk_level,
                "is_low_confidence": is_low_confidence,
                "checked_against": checked_against,
            },
        }

    # 5. Anomaly path: recommended policy not permitted under active merchant config
    details = {
        "risk_level": norm_risk_level,
        "is_low_confidence": is_low_confidence,
        "rejected_policy": recommended_policy,
        "checked_against": checked_against,
        "reason": (
            "Policy Agent's recommendation was not in the merchant's currently "
            "allowed set for this risk band/case; falling back to a safe default."
        ),
    }

    logger.warning(
        f"Policy Engine Anomaly: Recommended policy '{recommended_policy}' failed validation "
        f"against {checked_against} (risk_level={norm_risk_level}, is_low_confidence={is_low_confidence}). "
        f"Overriding with safe default '{safe_fallback}'. Details: {details}"
    )

    return {
        "final_policy": safe_fallback,
        "validation_passed": False,
        "anomaly": True,
        "details": details,
    }
