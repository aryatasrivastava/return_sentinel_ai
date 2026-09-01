import json
import logging
import time
from decimal import Decimal
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.risk_prediction import RiskPrediction
from app.models.policy_decision import PolicyDecision
from app.schemas.assess_order import AssessOrderRequest, AssessOrderResponse
from agents.graph import run_risk_assessment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assess-order", tags=["Risk Assessment Pipeline"])


def _get_model_version() -> str:
    """Load the installed XGBoost library version from model_config.json."""
    try:
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_path = base_dir / "ml" / "models" / "model_config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            xgboost_version = config_data.get("library_versions", {}).get("xgboost")
            if xgboost_version:
                return f"xgboost-{xgboost_version}"
    except Exception as e:
        logger.warning(f"Failed to load model_version from config: {e}")
    return "xgboost-unknown"


MODEL_VERSION = _get_model_version()



@router.post("", response_model=AssessOrderResponse, status_code=status.HTTP_200_OK)
def assess_order(
    request: AssessOrderRequest,
    db: Session = Depends(get_db),
):
    """Execute the end-to-end ReturnSentinel AI assessment pipeline for an order/cart session.

    1. Validates customer and product records.
    2. Resolves or automatically generates the Order and OrderItem records.
    3. Runs the LangGraph pipeline (Initial Assessment -> Confidence Router -> Policy Agent -> Policy Engine).
    4. Persists the final risk prediction and policy decision in a database transaction.
    5. Returns the structured assessment and policy decision with measured latency.
    """
    # 1. Validate customer existence
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {request.customer_id} does not exist.",
        )

    # 2. Resolve or generate order_id
    if request.order_id is not None:
        order = db.query(Order).filter(Order.id == request.order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {request.order_id} does not exist.",
            )
        if order.customer_id != request.customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order {request.order_id} does not belong to Customer {request.customer_id}.",
            )
        order_id = order.id
    else:
        # Validate that all requested products exist
        product_ids = [item.product_id for item in request.cart_items]
        existing_products = {
            p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()
        }
        for pid in product_ids:
            if pid not in existing_products:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {pid} does not exist in catalog.",
                )

        total_value = sum(
            Decimal(str(round(item.quantity * item.unit_price, 2)))
            for item in request.cart_items
        )

        new_order = Order(
            customer_id=request.customer_id,
            order_value=total_value,
            status="pending",
        )
        db.add(new_order)
        db.flush()

        for item in request.cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                size=item.size,
                quantity=item.quantity,
                unit_price=Decimal(str(round(item.unit_price, 2))),
            )
            db.add(order_item)
        db.flush()
        order_id = new_order.id

    # 3. Format cart items for the LangGraph pipeline
    cart_items_dicts = [
        {
            "product_id": item.product_id,
            "size": item.size,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
        }
        for item in request.cart_items
    ]

    # 4. Execute pipeline and measure latency
    start_time = time.perf_counter()
    try:
        state = run_risk_assessment(
            order_id=order_id,
            customer_id=request.customer_id,
            cart_items=cart_items_dicts,
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error executing risk assessment pipeline for order {order_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while executing the risk assessment pipeline.",
        )
    elapsed_ms = int(round((time.perf_counter() - start_time) * 1000))

    # 5. Persist prediction and policy decision transactionally
    try:
        risk_prob = float(state.get("risk_probability", 0.0))
        risk_score = Decimal(str(round(risk_prob * 100, 2)))
        confidence = Decimal(str(round(float(state.get("model_confidence", 0.0)), 3)))
        risk_level_str = str(state.get("risk_level", "LOW")).upper()
        investigation_round = int(state.get("investigation_round", 0))
        final_policy_str = str(state.get("final_policy", "STANDARD_RETURN"))

        # Add RiskPrediction record
        risk_pred = RiskPrediction(
            order_id=order_id,
            risk_score=risk_score,
            risk_level=risk_level_str,
            confidence=confidence,
            model_version=MODEL_VERSION,
            investigation_round=investigation_round,
            is_final=True,
        )
        db.add(risk_pred)

        # Add or update PolicyDecision record
        existing_decision = (
            db.query(PolicyDecision).filter(PolicyDecision.order_id == order_id).first()
        )
        if existing_decision:
            existing_decision.policy_type = final_policy_str
            existing_decision.audit_explanation = None
            existing_decision.audit_generated_at = None
        else:
            policy_decision = PolicyDecision(
                order_id=order_id,
                policy_type=final_policy_str,
                audit_explanation=None,
                audit_generated_at=None,
            )
            db.add(policy_decision)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(
            f"Database error persisting risk assessment for order {order_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist assessment results to the database.",
        )

    # 6. Log latency and result details
    logger.info(
        f"assess-order latency: {elapsed_ms}ms, order_id={order_id}, "
        f"customer_id={request.customer_id}, risk_level={state.get('risk_level')}, "
        f"final_policy={state.get('final_policy')}, rounds={state.get('investigation_round')}, "
        f"is_low_confidence={state.get('is_low_confidence')}"
    )

    # 7. Return flat response
    return AssessOrderResponse(
        order_id=order_id,
        risk_probability=round(float(state.get("risk_probability", 0.0)), 4),
        risk_level=str(state.get("risk_level", "LOW")),
        model_confidence=round(float(state.get("model_confidence", 0.0)), 4),
        is_low_confidence=bool(state.get("is_low_confidence", False)),
        investigation_round=int(state.get("investigation_round", 0)),
        recommended_policy=str(state.get("recommended_policy", "STANDARD_RETURN")),
        final_policy=str(state.get("final_policy", "STANDARD_RETURN")),
        validation_passed=bool(state.get("validation_passed", True)),
        policy_anomaly=bool(state.get("policy_anomaly", False)),
        top_risk_factors=list(state.get("top_risk_factors", [])),
        latency_ms=elapsed_ms,
    )
