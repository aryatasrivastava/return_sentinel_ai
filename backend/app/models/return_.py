from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="SET NULL"), nullable=True, index=True)
    reason = Column(Text, nullable=True)
    condition = Column(String(100), nullable=True)  # unused, worn, defective
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="returns")
    order_item = relationship("OrderItem", back_populates="returns")

    def __repr__(self):
        return f"<Return id={self.id} order_id={self.order_id} condition='{self.condition}'>"
