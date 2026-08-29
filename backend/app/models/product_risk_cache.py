from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class ProductRiskCache(Base):
    __tablename__ = "product_risk_cache"

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
    )
    return_rate = Column(Numeric(5, 4), nullable=False, default=0.0000)
    category_return_rate = Column(Numeric(5, 4), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    product = relationship("Product", back_populates="risk_cache")

    def __repr__(self):
        return f"<ProductRiskCache product_id={self.product_id} return_rate={self.return_rate} cat_rate={self.category_return_rate}>"
