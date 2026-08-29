from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class CustomerRiskCache(Base):
    __tablename__ = "customer_risk_cache"

    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
    )
    return_rate = Column(Numeric(5, 4), nullable=False, default=0.0000)
    previous_returns = Column(Integer, nullable=False, default=0)
    order_count = Column(Integer, nullable=False, default=0)
    days_since_last_order = Column(Integer, nullable=True)
    behavior_flags = Column(JSON, nullable=True)  # JSONB on Postgres, standard JSON elsewhere
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    customer = relationship("Customer", back_populates="risk_cache")

    def __repr__(self):
        return f"<CustomerRiskCache customer_id={self.customer_id} return_rate={self.return_rate} orders={self.order_count}>"
