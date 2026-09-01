from typing import Any, Dict, List, Optional, Tuple
from policy_agent.category_mapping import (
    CATEGORY_POLICY_WEIGHTS,
    FRICTION_ORDER,
    get_feature_category,
)


def score_policies(
    top_risk_factors_detailed: List[Dict[str, Any]],
    allowed_policies: List[str],
) -> Dict[str, float]:
    """Score allowed policies based on the underlying categories of top risk factors.

    Args:
        top_risk_factors_detailed: List of up to 3 factor dicts with 'feature', 'label', and 'shap_value'.
        allowed_policies: The merchant-configured allowed policies for the order's risk band.

    Returns:
        Dictionary mapping every allowed policy to its calculated float score.
        Policies not in allowed_policies are never included.
    """
    scores: Dict[str, float] = {policy: 0.0 for policy in allowed_policies}
    allowed_set = set(allowed_policies)

    for factor in top_risk_factors_detailed:
        feature_name = factor.get("feature", "")
        category = get_feature_category(feature_name)
        weights = CATEGORY_POLICY_WEIGHTS.get(category, {})

        for policy, weight in weights.items():
            if policy in allowed_set:
                scores[policy] = round(scores[policy] + weight, 4)

    return scores


def select_policy(
    scores: Dict[str, float],
    allowed_policies: List[str],
    cart_value: float,
    cart_value_median: float = 3000.0,
    categories_present: Optional[List[str]] = None,
) -> Tuple[str, Dict[str, Any]]:
    """Select the best return policy from scores, applying deterministic tie-breaking.

    Args:
        scores: Dictionary of scores for allowed policies.
        allowed_policies: Merchant's allowed policies for this risk band.
        cart_value: Total monetary value of the order/cart.
        cart_value_median: Baseline cart value median used for tie-breaking (default: 3000.0).
        categories_present: Optional list of identified category names from top factors.

    Returns:
        Tuple of (selected_policy, reasoning_dict).
    """
    if not allowed_policies:
        raise ValueError("allowed_policies list cannot be empty.")

    # Filter scores strictly to allowed policies
    valid_scores = {p: scores.get(p, 0.0) for p in allowed_policies}
    max_score = max(valid_scores.values())

    # Identify all policies tied with the maximum score
    tied_policies = [p for p, s in valid_scores.items() if s == max_score]

    if len(tied_policies) == 1:
        selected_policy = tied_policies[0]
        tie_break_info = {
            "applied": False,
            "tied_policies": [],
            "strategy": None,
            "reason": "Single policy achieved dominant category score.",
        }
    else:
        # Multiple policies tied for max score: break tie using cart_value relative to median
        if cart_value > cart_value_median:
            # High stakes: choose tied policy with highest friction
            selected_policy = max(
                tied_policies,
                key=lambda p: FRICTION_ORDER.get(p, 0),
            )
            tie_break_info = {
                "applied": True,
                "tied_policies": tied_policies,
                "strategy": "HIGH_CART_VALUE",
                "cart_value": cart_value,
                "cart_value_median": cart_value_median,
                "selected_by": "highest_friction",
                "reason": (
                    f"Tie among {tied_policies} resolved by higher cart value "
                    f"({cart_value} > {cart_value_median}), selecting highest friction policy."
                ),
            }
        else:
            # Standard/low stakes: choose tied policy with lowest friction (default to minimal friction)
            selected_policy = min(
                tied_policies,
                key=lambda p: FRICTION_ORDER.get(p, 0),
            )
            tie_break_info = {
                "applied": True,
                "tied_policies": tied_policies,
                "strategy": "STANDARD_OR_LOW_CART_VALUE",
                "cart_value": cart_value,
                "cart_value_median": cart_value_median,
                "selected_by": "lowest_friction",
                "reason": (
                    f"Tie among {tied_policies} resolved by standard/low cart value "
                    f"({cart_value} <= {cart_value_median}), selecting lowest friction policy."
                ),
            }

    reasoning = {
        "scores": valid_scores,
        "max_score": max_score,
        "categories_present": categories_present if categories_present is not None else [],
        "allowed_policies": allowed_policies,
        "cart_value": cart_value,
        "cart_value_median": cart_value_median,
        "tie_break": tie_break_info,
        "used_fallback": False,
    }

    return selected_policy, reasoning
