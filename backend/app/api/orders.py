import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db.session import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.risk_prediction import RiskPrediction
from app.models.policy_decision import PolicyDecision
from app.models.agent_trace import AgentTrace
from app.schemas.orders import (
    OrderItemDetailSchema,
    OrderListItemSchema,
    OrderDetailSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders Dashboard"])


@router.get("", response_model=List[OrderListItemSchema], status_code=status.HTTP_200_OK)
def list_orders(
    limit: int = Query(20, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    risk_level: Optional[str] = Query(None, description="Optional filter by risk level (LOW, MEDIUM, HIGH)"),
    policy_type: Optional[str] = Query(None, description="Optional filter by policy type (STANDARD_RETURN, etc.)"),
    db: Session = Depends(get_db),
):
    """Retrieve a paginated list of orders joined with latest risk assessment and policy decisions."""
    # Subquery for the latest risk prediction per order to avoid duplicate join rows
    latest_pred_subquery = (
        db.query(
            RiskPrediction.order_id,
            func.max(RiskPrediction.id).label("max_id"),
        )
        .group_by(RiskPrediction.order_id)
        .subquery()
    )

    query = (
        db.query(
            Order.id.label("order_id"),
            Customer.name.label("customer_name"),
            Order.order_value.label("cart_value"),
            RiskPrediction.risk_score,
            RiskPrediction.risk_level,
            RiskPrediction.confidence,
            PolicyDecision.policy_type.label("policy"),
            Order.status,
            Order.created_at,
        )
        .join(Customer, Order.customer_id == Customer.id)
        .outerjoin(
            latest_pred_subquery,
            Order.id == latest_pred_subquery.c.order_id,
        )
        .outerjoin(
            RiskPrediction,
            RiskPrediction.id == latest_pred_subquery.c.max_id,
        )
        .outerjoin(PolicyDecision, PolicyDecision.order_id == Order.id)
    )

    if risk_level:
        query = query.filter(func.upper(RiskPrediction.risk_level) == risk_level.strip().upper())

    if policy_type:
        query = query.filter(func.upper(PolicyDecision.policy_type) == policy_type.strip().upper())

    rows = (
        query.order_by(Order.created_at.desc(), Order.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = []
    for row in rows:
        results.append(
            OrderListItemSchema(
                order_id=row.order_id,
                customer_name=row.customer_name,
                cart_value=float(row.cart_value) if row.cart_value is not None else 0.0,
                risk_score=float(row.risk_score) if row.risk_score is not None else None,
                risk_level=row.risk_level.upper() if row.risk_level else None,
                confidence=float(row.confidence) if row.confidence is not None else None,
                policy=row.policy.upper() if row.policy else None,
                status=row.status,
                created_at=row.created_at,
            )
        )
    return results


@router.get("/{order_id}", response_model=OrderDetailSchema, status_code=status.HTTP_200_OK)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve comprehensive details for a specific order including items, trace, and audit trail."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} does not exist.",
        )

    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    customer_name = customer.name if customer else "Unknown Customer"

    # Fetch order items joined with product
    items_rows = (
        db.query(OrderItem, Product)
        .outerjoin(Product, OrderItem.product_id == Product.id)
        .filter(OrderItem.order_id == order_id)
        .all()
    )

    items_detail = []
    for order_item, product in items_rows:
        unit_price = float(order_item.unit_price) if order_item.unit_price is not None else 0.0
        total_price = float(round(unit_price * order_item.quantity, 2))
        items_detail.append(
            OrderItemDetailSchema(
                product_id=order_item.product_id,
                product_name=product.name if product else None,
                sku=product.sku if product else None,
                size=order_item.size,
                quantity=order_item.quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
        )

    # Fetch latest risk prediction
    pred = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.order_id == order_id)
        .order_by(RiskPrediction.id.desc())
        .first()
    )

    # Fetch policy decision
    decision = (
        db.query(PolicyDecision)
        .filter(PolicyDecision.order_id == order_id)
        .first()
    )

    # Fetch agent trace
    trace = (
        db.query(AgentTrace)
        .filter(AgentTrace.order_id == order_id)
        .first()
    )

    # Extract top_risk_factors: from direct trace_data field or derived from investigation_log steps
    top_risk_factors = None
    if trace and trace.trace_data:
        if "top_risk_factors" in trace.trace_data and trace.trace_data["top_risk_factors"]:
            top_risk_factors = trace.trace_data["top_risk_factors"]
        elif "investigation_log" in trace.trace_data and isinstance(trace.trace_data["investigation_log"], list):
            for step in reversed(trace.trace_data["investigation_log"]):
                if isinstance(step, dict) and "top_risk_factors" in step and step["top_risk_factors"]:
                    top_risk_factors = step["top_risk_factors"]
                    break

    return OrderDetailSchema(
        order_id=order.id,
        customer_id=order.customer_id,
        customer_name=customer_name,
        cart_value=float(order.order_value) if order.order_value is not None else 0.0,
        risk_score=float(pred.risk_score) if pred and pred.risk_score is not None else None,
        risk_level=pred.risk_level.upper() if pred and pred.risk_level else None,
        confidence=float(pred.confidence) if pred and pred.confidence is not None else None,
        policy=decision.policy_type.upper() if decision and decision.policy_type else None,
        status=order.status,
        created_at=order.created_at,
        items=items_detail,
        trace_data=trace.trace_data if trace else None,
        top_risk_factors=top_risk_factors,
        audit_explanation=decision.audit_explanation if decision else None,
        audit_generated_at=decision.audit_generated_at if decision else None,
    )
