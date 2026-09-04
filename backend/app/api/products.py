from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.product import Product
from app.models.customer import Customer

router = APIRouter(tags=["Storefront Catalog"])


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: Optional[str] = None
    price: float

    model_config = ConfigDict(from_attributes=True)


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


@router.get("/products", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    """Fetch all catalog products for the customer storefront."""
    products = db.query(Product).order_by(Product.id.asc()).all()
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            sku=p.sku,
            category=p.category,
            price=float(p.price),
        )
        for p in products
    ]


@router.get("/customers", response_model=List[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    """Fetch seeded demo customers for the storefront persona switcher."""
    customers = db.query(Customer).order_by(Customer.id.asc()).all()
    return [
        CustomerResponse(
            id=c.id,
            name=c.name,
            email=c.email,
        )
        for c in customers
    ]
