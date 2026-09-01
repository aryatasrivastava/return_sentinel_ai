"""ReturnSentinel AI State Schema for LangGraph Pipeline (Phase 3A).

Defines the typed state passed between the initial assessment node,
investigation loop node, confidence router, and terminal outputs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """Typed dictionary representing the full state of the risk assessment pipeline.

    Attributes:
        order_id: Unique identifier for the order/cart session being evaluated.
        customer_id: Unique identifier or database ID of the customer.
        cart_items: List of item dictionaries in the current cart:
            - product_id (int | str)
            - size (str | None)
            - quantity (int)
            - unit_price (float | Decimal)
        features: Exact 12-feature dictionary formatted for `predict_return_risk()`.
        risk_probability: Predicted return abuse risk probability in [0, 1].
        risk_level: Categorical risk tier ("LOW", "MEDIUM", "HIGH").
        model_confidence: Ingested prediction confidence score (2 * |prob - 0.5|).
        top_risk_factors: Top 3 human-readable SHAP risk explanations.
        investigation_round: Integer counter tracking investigation round
            (0 = initial cached pass, 1 = first live re-investigation, 2 = second live re-investigation).
        is_low_confidence: Boolean flag indicating if the final assessment remains below
            confidence threshold after all allowed investigation rounds are exhausted.
        investigation_log: Audit trail of steps, data sources queried, feature diffs,
            and confidence transitions for explainability and Agent Decision Trace.
    """

    order_id: str
    customer_id: str
    cart_items: List[Dict[str, Any]]
    features: Dict[str, Any]
    risk_probability: Optional[float]
    risk_level: Optional[str]
    model_confidence: Optional[float]
    top_risk_factors: List[str]
    top_risk_factors_detailed: List[Dict[str, Any]]
    investigation_round: int
    is_low_confidence: bool
    recommended_policy: Optional[str]
    policy_agent_reasoning: Optional[Dict[str, Any]]
    final_policy: Optional[str]
    validation_passed: Optional[bool]
    policy_anomaly: Optional[bool]
    policy_engine_details: Optional[Dict[str, Any]]
    investigation_log: List[Dict[str, Any]]

