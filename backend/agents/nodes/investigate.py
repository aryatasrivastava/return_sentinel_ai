"""Investigation Node (Phase 3A).

Executes deeper investigation rounds (Rounds 1 & 2) when the confidence router
determines that prediction confidence is insufficient (< 0.60):
- Bypasses cached tables and queries live transactional tables (`orders`, `order_items`, `returns`).
- Recomputes exact features and records a structured feature diff vs. previous round.
- Re-evaluates risk with `predict_return_risk()`.
- Updates state and appends an investigation audit entry to `investigation_log`.
"""

from __future__ import annotations

from typing import Any, Dict

try:
    from ml.training.predict import predict_return_risk
except (ImportError, ModuleNotFoundError):
    from backend.ml.training.predict import predict_return_risk

try:
    from agents.feature_builder import build_features_from_live_data
    from agents.state import AgentState
except (ImportError, ModuleNotFoundError):
    from backend.agents.feature_builder import build_features_from_live_data
    from backend.agents.state import AgentState


def _compute_feature_diff(old_feats: Dict[str, Any], new_feats: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Identify differences between previous and refreshed feature values."""
    diffs: Dict[str, Dict[str, Any]] = {}
    for k, new_v in new_feats.items():
        old_v = old_feats.get(k)
        if old_v != new_v:
            diffs[k] = {
                "previous_value": old_v,
                "refreshed_value": new_v,
            }
    return diffs


def investigate_node(state: AgentState) -> Dict[str, Any]:
    """Execute live re-investigation round to refine features and re-predict risk.

    Args:
        state: Current AgentState.

    Returns:
        Dictionary of updated state fields for LangGraph.
    """
    customer_id = state.get("customer_id")
    cart_items = state.get("cart_items", [])
    old_features = state.get("features", {})
    prev_round = state.get("investigation_round", 0)
    current_round = prev_round + 1
    current_log = list(state.get("investigation_log", []))

    # Pull fresh live data bypassing cache
    refreshed_features = build_features_from_live_data(
        customer_id=customer_id,
        cart_items=cart_items,
    )

    feature_diff = _compute_feature_diff(old_features, refreshed_features)

    # Re-predict risk with refreshed feature vector
    prediction = predict_return_risk(refreshed_features)

    risk_prob = float(prediction["risk_probability"])
    risk_lvl = str(prediction["risk_level"])
    model_conf = float(prediction["confidence"])
    top_factors = list(prediction["top_risk_factors"])
    top_factors_detailed = list(prediction.get("top_risk_factors_detailed", []))

    diff_summary = (
        f"{len(feature_diff)} features updated from live tables"
        if feature_diff else "live tables confirmed cached values"
    )

    log_entry: Dict[str, Any] = {
        "step_type": "investigation",
        "round": current_round,
        "source": "live_data",
        "description": f"Pulled live order and return history bypassing cache (Round {current_round}: {diff_summary}).",
        "feature_diff": feature_diff,
        "risk_probability": risk_prob,
        "risk_level": risk_lvl,
        "model_confidence": model_conf,
        "top_risk_factors": top_factors,
    }
    current_log.append(log_entry)

    return {
        "features": refreshed_features,
        "risk_probability": risk_prob,
        "risk_level": risk_lvl,
        "model_confidence": model_conf,
        "top_risk_factors": top_factors,
        "top_risk_factors_detailed": top_factors_detailed,
        "investigation_round": current_round,
        "investigation_log": current_log,
    }

