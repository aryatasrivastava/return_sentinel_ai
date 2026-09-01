import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Feature -> Category Mapping (All 12 features from model_config.json feature_order)
FEATURE_CATEGORIES: Dict[str, str] = {
    "multiple_sizes_same_product": "BRACKETING",
    "max_sizes_same_product": "BRACKETING",
    "customer_return_rate": "REPEAT_BEHAVIOR",
    "total_previous_returns": "REPEAT_BEHAVIOR",
    "previous_returns_same_category": "REPEAT_BEHAVIOR",
    "avg_days_to_return": "REPEAT_BEHAVIOR",
    "average_product_return_rate": "PRODUCT_DRIVEN",
    "customer_history_days": "NEUTRAL",
    "days_since_last_order": "NEUTRAL",
    "total_previous_orders": "NEUTRAL",
    "cart_value": "NEUTRAL",
    "cart_item_count": "NEUTRAL",
}

# Category -> Policy Lean Weights (Category can lean towards multiple policies)
CATEGORY_POLICY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "BRACKETING": {"EXCHANGE_FIRST": 1.0},
    "REPEAT_BEHAVIOR": {"STORE_CREDIT": 1.0, "RESTOCKING_FEE": 0.5},
    "PRODUCT_DRIVEN": {"RESTOCKING_FEE": 1.0},
    "NEUTRAL": {},  # no lean — contributes 0 to every policy's score
}

# Friction Ordering (used strictly for tie-breaking)
# Lower integer means lower customer friction
FRICTION_ORDER: Dict[str, int] = {
    "STANDARD_RETURN": 0,
    "EXCHANGE_FIRST": 1,
    "RESTOCKING_FEE": 2,
    "STORE_CREDIT": 3,
}


def get_feature_category(feature_name: str) -> str:
    """Retrieve the category for a given feature name.

    If the feature is unmapped, logs a warning and defaults to 'NEUTRAL'.
    """
    if feature_name in FEATURE_CATEGORIES:
        return FEATURE_CATEGORIES[feature_name]
    logger.warning(
        f"Feature '{feature_name}' not found in FEATURE_CATEGORIES mapping; defaulting to 'NEUTRAL'."
    )
    return "NEUTRAL"
