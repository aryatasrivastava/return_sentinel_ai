import logging
from typing import Dict, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db.session import get_db
from app.models.order import Order
from app.models.risk_prediction import RiskPrediction
from app.models.policy_decision import PolicyDecision
from app.schemas.dashboard import DashboardStatsResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard-stats", tags=["Dashboard Aggregates"])


@router.get("", response_model=DashboardStatsResponse, status_code=status.HTTP_200_OK)
def get_dashboard_stats(
    db: Session = Depends(get_db),
):
    """Retrieve aggregate platform statistics computed from orders, risk predictions, and policy decisions.

    Notes on metric heuristics:
    1. false_positive_rate: Set to None (JSON null) because the platform does not currently record
       downstream post-return merchant confirmations / ground-truth fraud labels.
    2. estimated_margin_protected: Computed as the sum of order_value for all orders where a
       protective/friction return policy was applied (policy_type != 'STANDARD_RETURN', e.g. EXCHANGE_FIRST,
       STORE_CREDIT, RESTOCKING_FEE).
    """
    # Subquery for the latest risk prediction ID per order to prevent double-counting
    latest_pred_subquery = (
        db.query(
            RiskPrediction.order_id,
            func.max(RiskPrediction.id).label("max_id"),
        )
        .group_by(RiskPrediction.order_id)
        .subquery()
    )

    # 1. Total assessed orders
    orders_analyzed = (
        db.query(func.count(func.distinct(PolicyDecision.order_id))).scalar() or 0
    )

    # 2. High risk orders (from latest prediction per order)
    high_risk_orders = (
        db.query(func.count(RiskPrediction.id))
        .join(latest_pred_subquery, RiskPrediction.id == latest_pred_subquery.c.max_id)
        .filter(func.upper(RiskPrediction.risk_level) == "HIGH")
        .scalar()
        or 0
    )

    # 3. Estimated margin protected
    # Sum of cart_value for orders where protective policy was assigned (policy_type != 'STANDARD_RETURN')
    margin_protected_raw = (
        db.query(func.sum(Order.order_value))
        .join(PolicyDecision, Order.id == PolicyDecision.order_id)
        .filter(func.upper(PolicyDecision.policy_type) != "STANDARD_RETURN")
        .scalar()
    )
    estimated_margin_protected = float(round(margin_protected_raw, 2)) if margin_protected_raw else 0.0

    # 4. Risk distribution (from latest prediction per order)
    risk_rows = (
        db.query(
            func.upper(RiskPrediction.risk_level).label("level"),
            func.count(RiskPrediction.id).label("count"),
        )
        .join(latest_pred_subquery, RiskPrediction.id == latest_pred_subquery.c.max_id)
        .group_by(func.upper(RiskPrediction.risk_level))
        .all()
    )
    risk_distribution: Dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for row in risk_rows:
        if row.level:
            risk_distribution[row.level] = int(row.count)

    # 5. Policy distribution
    policy_rows = (
        db.query(
            func.upper(PolicyDecision.policy_type).label("policy"),
            func.count(PolicyDecision.id).label("count"),
        )
        .group_by(func.upper(PolicyDecision.policy_type))
        .all()
    )
    policy_distribution: Dict[str, int] = {
        "STANDARD_RETURN": 0,
        "EXCHANGE_FIRST": 0,
        "STORE_CREDIT": 0,
        "RESTOCKING_FEE": 0,
    }
    for row in policy_rows:
        if row.policy:
            policy_distribution[row.policy] = int(row.count)

    return DashboardStatsResponse(
        orders_analyzed=orders_analyzed,
        high_risk_orders=high_risk_orders,
        estimated_margin_protected=estimated_margin_protected,
        false_positive_rate=None,
        risk_distribution=risk_distribution,
        policy_distribution=policy_distribution,
    )
