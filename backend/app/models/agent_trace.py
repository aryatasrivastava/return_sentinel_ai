from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

# Use JSONB on PostgreSQL, standard JSON elsewhere
JSON_TYPE = JSON().with_variant(JSONB, "postgresql")


class AgentTrace(Base):
    __tablename__ = "agent_traces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    trace_data = Column(JSON_TYPE, nullable=False)  # Stores investigation_log, policy_agent_reasoning, policy_engine_details
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow,
    )

    # Relationships
    order = relationship("Order", back_populates="agent_trace")

    def __repr__(self):
        return f"<AgentTrace id={self.id} order_id={self.order_id}>"
