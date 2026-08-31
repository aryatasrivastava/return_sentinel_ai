"""Initial Assessment Node (Phase 3A).

Executes Round 0 of the return-risk evaluation pipeline:
- Builds initial feature vector using precomputed cached data (customer/product risk cache).
- Performs inference via the trained XGBoost model (`predict_return_risk`).
- Initializes state fields and appends the initial assessment entry to `investigation_log`.
"""

from __future__ import annotations

from typing import Any, Dict

try:
    from ml.training.predict import predict_return_risk
except (ImportError, ModuleNotFoundError):
    from backend.ml.training.predict import predict_return_risk

try:
    from agents.feature_builder import build_features_from_cache
    from agents.state import AgentState
except (ImportError, ModuleNotFoundError):
    from backend.agents.feature_builder import build_features_from_cache
    from backend.agents.state import AgentState


def initial_assessment_node(state: AgentState) -> Dict[str, Any]:
    """Execute Round 0 initial assessment using cached data.

    Args:
        state: Current AgentState containing order_id, customer_id, cart_items, and investigation_log.

    Returns:
        Dictionary of state updates for LangGraph.
    """
    customer_id = state.get("customer_id")
    cart_items = state.get("cart_items", [])
    current_log = list(state.get("investigation_log", []))

    # If features are already explicitly provided in state (e.g. synthetic test case injection),
    # use them; otherwise, build from cache
    if "features" in state and state["features"]:
        features = state["features"]
    else:
        features = build_features_from_cache(customer_id=customer_id, cart_items=cart_items)

    # Ingest prediction
    prediction = predict_return_risk(features)

    risk_prob = float(prediction["risk_probability"])
    risk_lvl = str(prediction["risk_level"])
    model_conf = float(prediction["confidence"])
    top_factors = list(prediction["top_risk_factors"])

    log_entry: Dict[str, Any] = {
        "step_type": "initial_assessment",
        "round": 0,
        "source": "cached",
        "description": "Initial assessment using cached customer risk cache and product catalog metadata.",
        "risk_probability": risk_prob,
        "risk_level": risk_lvl,
        "model_confidence": model_conf,
        "top_risk_factors": top_factors,
    }
    current_log.append(log_entry)

    return {
        "features": features,
        "risk_probability": risk_prob,
        "risk_level": risk_lvl,
        "model_confidence": model_conf,
        "top_risk_factors": top_factors,
        "investigation_round": 0,
        "is_low_confidence": False,
        "investigation_log": current_log,
    }
