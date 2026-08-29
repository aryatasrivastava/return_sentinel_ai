from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class PolicyDecision(Base):
    __tablename__ = "policy_decisions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    policy_type = Column(String(50), nullable=False)  # STANDARD_RETURN, EXCHANGE_FIRST, STORE_CREDIT, RESTOCKING_FEE
    audit_explanation = Column(Text, nullable=True)  # Populated asynchronously by audit trail LLM
    audit_generated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="policy_decision")

    def __repr__(self):
        return f"<PolicyDecision id={self.id} order_id={self.order_id} policy='{self.policy_type}'>"
