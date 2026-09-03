from typing import Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class DashboardStatsResponse(BaseModel):
    orders_analyzed: int = Field(..., description="Total number of evaluated orders")
    high_risk_orders: int = Field(..., description="Total number of orders classified as HIGH risk")
    estimated_margin_protected: float = Field(
        ...,
        description="Total cart value protected by applying non-standard return policies (EXCHANGE_FIRST, STORE_CREDIT, RESTOCKING_FEE)",
    )
    false_positive_rate: Optional[float] = Field(
        None,
        description="False positive rate (null because ground-truth post-return fraud validation feedback is not yet recorded)",
    )
    risk_distribution: Dict[str, int] = Field(
        ...,
        description="Count of evaluated orders grouped by risk tier (LOW, MEDIUM, HIGH)",
    )
    policy_distribution: Dict[str, int] = Field(
        ...,
        description="Count of evaluated orders grouped by assigned policy type",
    )

    model_config = ConfigDict(from_attributes=True)
