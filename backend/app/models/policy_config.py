from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.session import Base

DEFAULT_LOW_RISK_ALLOWED = ["STANDARD_RETURN"]
DEFAULT_MEDIUM_RISK_ALLOWED = ["STANDARD_RETURN", "EXCHANGE_FIRST", "RESTOCKING_FEE"]
DEFAULT_HIGH_RISK_ALLOWED = ["EXCHANGE_FIRST", "STORE_CREDIT", "RESTOCKING_FEE"]
DEFAULT_LOW_CONFIDENCE_FALLBACK = "EXCHANGE_FIRST"


class PolicyConfig(Base):
    __tablename__ = "policy_config"

    id = Column(Integer, primary_key=True, default=1)
    low_risk_allowed = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False)
    medium_risk_allowed = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False)
    high_risk_allowed = Column(JSONB().with_variant(JSON, "sqlite"), nullable=False)
    low_confidence_fallback = Column(String(50), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<PolicyConfig id={self.id} "
            f"low={self.low_risk_allowed} "
            f"medium={self.medium_risk_allowed} "
            f"high={self.high_risk_allowed} "
            f"fallback='{self.low_confidence_fallback}'>"
        )
