import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.policy_config import (
    PolicyConfig,
    DEFAULT_LOW_RISK_ALLOWED,
    DEFAULT_MEDIUM_RISK_ALLOWED,
    DEFAULT_HIGH_RISK_ALLOWED,
    DEFAULT_LOW_CONFIDENCE_FALLBACK,
)
from policy_agent.category_mapping import get_feature_category
from policy_agent.scoring import score_policies, select_policy

logger = logging.getLogger(__name__)


def get_current_policy_config(db: Optional[Session] = None) -> PolicyConfig:
    """Fetch the active single-row policy_config from the database.

    If no DB session or row is available, returns a default PolicyConfig instance.
    """
    if db is not None:
        cfg = db.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
        if cfg:
            return cfg

    if SessionLocal is not None:
        try:
            with SessionLocal() as session:
                cfg = session.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
                if cfg:
                    return cfg
        except Exception as e:
            logger.warning(f"Unable to query policy_config from DB: {e}; falling back to defaults.")

    return PolicyConfig(
        id=1,
        low_risk_allowed=DEFAULT_LOW_RISK_ALLOWED,
        medium_risk_allowed=DEFAULT_MEDIUM_RISK_ALLOWED,
        high_risk_allowed=DEFAULT_HIGH_RISK_ALLOWED,
        low_confidence_fallback=DEFAULT_LOW_CONFIDENCE_FALLBACK,
    )


def recommend_policy(
    risk_assessment: Dict[str, Any],
    cart_value: float,
    policy_config: Optional[PolicyConfig] = None,
    db: Optional[Session] = None,
    cart_value_median: float = 3000.0,
) -> Dict[str, Any]:
    """Recommend a return policy for an order based on risk assessment and merchant config.

    Args:
        risk_assessment: Dictionary containing:
            - risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
            - is_low_confidence: bool
            - top_risk_factors_detailed: list of dicts with 'feature', 'label', 'shap_value'
        cart_value: Total monetary value of the order/cart.
        policy_config: Optional pre-fetched PolicyConfig object.
        db: Optional database Session to load policy_config.
        cart_value_median: Threshold cart value for tie-breaking (default: 3000.0).

    Returns:
        Dictionary containing:
        {
            "recommended_policy": str,
            "reasoning": dict
        }
    """
    # 1. Resolve Policy Config
    if policy_config is None:
        policy_config = get_current_policy_config(db=db)

    # 2. Short-circuit if low confidence flag is set
    if risk_assessment.get("is_low_confidence", False):
        fallback = policy_config.low_confidence_fallback
        return {
            "recommended_policy": fallback,
            "reasoning": {
                "used_fallback": True,
                "reason": "is_low_confidence was True; risk-band scoring was skipped",
                "fallback_policy": fallback,
                "cart_value": cart_value,
            },
        }

    # 3. Determine allowed policies from merchant config based on risk level
    risk_level = str(risk_assessment.get("risk_level", "MEDIUM")).upper()
    if risk_level == "LOW":
        allowed_policies: List[str] = policy_config.low_risk_allowed
    elif risk_level == "HIGH":
        allowed_policies = policy_config.high_risk_allowed
    else:
        allowed_policies = policy_config.medium_risk_allowed

    # 4. Extract detailed top factors and categories
    top_factors: List[Dict[str, Any]] = risk_assessment.get(
        "top_risk_factors_detailed", []
    )
    categories_present = [
        get_feature_category(f.get("feature", ""))
        for f in top_factors
    ]

    # 5. Score policies within the allowed set
    scores = score_policies(
        top_risk_factors_detailed=top_factors,
        allowed_policies=allowed_policies,
    )

    # 6. Select highest-scoring policy with tie-breaking
    chosen_policy, reasoning = select_policy(
        scores=scores,
        allowed_policies=allowed_policies,
        cart_value=cart_value,
        cart_value_median=cart_value_median,
        categories_present=categories_present,
    )

    return {
        "recommended_policy": chosen_policy,
        "reasoning": reasoning,
    }
