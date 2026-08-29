from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_score = Column(Numeric(5, 2), nullable=False)
    risk_level = Column(String(20), nullable=False)  # low, medium, high
    confidence = Column(Numeric(4, 3), nullable=False)
    model_version = Column(String(50), nullable=True)  # e.g. "xgboost-v2.4"
    investigation_round = Column(Integer, nullable=False, default=0)
    is_final = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="risk_predictions")

    def __repr__(self):
        return f"<RiskPrediction id={self.id} order_id={self.order_id} score={self.risk_score} level='{self.risk_level}' confidence={self.confidence}>"
