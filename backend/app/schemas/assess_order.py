from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CartItemSchema(BaseModel):
    product_id: int = Field(..., description="ID of the catalog product")
    size: Optional[str] = Field(None, description="Selected size variant (e.g. S, M, L, XL)")
    quantity: int = Field(default=1, ge=1, description="Quantity of items selected")
    unit_price: float = Field(..., ge=0.0, description="Unit price per item")


class AssessOrderRequest(BaseModel):
    customer_id: int = Field(..., description="ID of the purchasing customer")
    cart_items: List[CartItemSchema] = Field(
        ...,
        min_length=1,
        description="List of cart items being purchased (at least 1 required)",
    )
    order_id: Optional[int] = Field(
        None,
        description="Optional existing order ID; if omitted, a new order row is generated",
    )


class AssessOrderResponse(BaseModel):
    order_id: int = Field(..., description="ID of the evaluated order")
    risk_probability: float = Field(..., description="Predicted return abuse risk probability")
    risk_level: str = Field(..., description="Categorical risk tier (LOW, MEDIUM, HIGH)")
    model_confidence: float = Field(..., description="Model prediction confidence score")
    is_low_confidence: bool = Field(..., description="Flag indicating exhausted confidence budget")
    investigation_round: int = Field(..., description="Investigation rounds executed")
    recommended_policy: str = Field(..., description="Policy recommended by Policy Agent")
    final_policy: str = Field(..., description="Final validated policy approved by Policy Engine")
    validation_passed: bool = Field(..., description="Whether policy validation succeeded")
    policy_anomaly: bool = Field(..., description="Whether policy anomaly was detected and overridden")
    top_risk_factors: List[str] = Field(..., description="Top 3 human-readable risk explanations")
    latency_ms: int = Field(..., description="Total pipeline execution latency in milliseconds")

    model_config = ConfigDict(from_attributes=True)
