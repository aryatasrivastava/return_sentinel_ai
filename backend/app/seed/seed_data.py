import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.return_ import Return
from app.models.risk_prediction import RiskPrediction
from app.models.policy_decision import PolicyDecision
from app.models.customer_risk_cache import CustomerRiskCache
from app.models.product_risk_cache import ProductRiskCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_database(db: Session) -> None:
    """Clear tables in reverse dependency order for idempotent seeding."""
    logger.info("Cleaning existing seed records...")
    db.query(PolicyDecision).delete()
    db.query(RiskPrediction).delete()
    db.query(Return).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(CustomerRiskCache).delete()
    db.query(ProductRiskCache).delete()
    db.query(Product).delete()
    db.query(Customer).delete()
    db.commit()
    logger.info("Cleaned existing records.")


def seed_products(db: Session) -> dict[str, Product]:
    """Seed 12 products across multiple categories with corresponding ProductRiskCache rows."""
    logger.info("Seeding products & product risk caches...")

    products_spec = [
        {
            "name": "Embroidered Silk Anarkali Suit",
            "sku": "SKU-ANK-001",
            "category": "Ethnic Occasionwear",
            "price": Decimal("7499.00"),
            "return_rate": Decimal("0.3800"),
            "category_return_rate": Decimal("0.3500"),
        },
        {
            "name": "Designer Velvet Sherwani",
            "sku": "SKU-SHR-002",
            "category": "Ethnic Occasionwear",
            "price": Decimal("12999.00"),
            "return_rate": Decimal("0.4200"),
            "category_return_rate": Decimal("0.3500"),
        },
        {
            "name": "Zari Woven Kanjeevaram Saree",
            "sku": "SKU-SAR-003",
            "category": "Bridal & Festive",
            "price": Decimal("18500.00"),
            "return_rate": Decimal("0.4800"),
            "category_return_rate": Decimal("0.4500"),
        },
        {
            "name": "Raw Silk Kurta Pajama Set",
            "sku": "SKU-KUR-004",
            "category": "Ethnic Occasionwear",
            "price": Decimal("3499.00"),
            "return_rate": Decimal("0.2200"),
            "category_return_rate": Decimal("0.3500"),
        },
        {
            "name": "Embellished Bridal Lehenga Choli",
            "sku": "SKU-LEH-005",
            "category": "Bridal & Festive",
            "price": Decimal("24999.00"),
            "return_rate": Decimal("0.5200"),
            "category_return_rate": Decimal("0.4500"),
        },
        {
            "name": "Classic Oxford Cotton Shirt",
            "sku": "SKU-SHT-006",
            "category": "Western Casualwear",
            "price": Decimal("1999.00"),
            "return_rate": Decimal("0.1200"),
            "category_return_rate": Decimal("0.1800"),
        },
        {
            "name": "Slim Fit Chino Trousers",
            "sku": "SKU-CHN-007",
            "category": "Western Casualwear",
            "price": Decimal("2499.00"),
            "return_rate": Decimal("0.1500"),
            "category_return_rate": Decimal("0.1800"),
        },
        {
            "name": "Tailored Linen Blazer",
            "sku": "SKU-BLZ-008",
            "category": "Western Casualwear",
            "price": Decimal("5999.00"),
            "return_rate": Decimal("0.2800"),
            "category_return_rate": Decimal("0.1800"),
        },
        {
            "name": "Handcrafted Leather Juttis",
            "sku": "SKU-JUT-009",
            "category": "Footwear & Accessories",
            "price": Decimal("2199.00"),
            "return_rate": Decimal("0.2500"),
            "category_return_rate": Decimal("0.2200"),
        },
        {
            "name": "Pure Pashmina Shawl",
            "sku": "SKU-SHW-010",
            "category": "Luxury Goods",
            "price": Decimal("8999.00"),
            "return_rate": Decimal("0.0800"),
            "category_return_rate": Decimal("0.1200"),
        },
        {
            "name": "Floral Print Georgette Kurti",
            "sku": "SKU-KRT-011",
            "category": "Western Casualwear",
            "price": Decimal("1499.00"),
            "return_rate": Decimal("0.1400"),
            "category_return_rate": Decimal("0.1800"),
        },
        {
            "name": "Polki Kundan Choker Necklace",
            "sku": "SKU-JWL-012",
            "category": "Jewellery & Luxury Goods",
            "price": Decimal("6499.00"),
            "return_rate": Decimal("0.1900"),
            "category_return_rate": Decimal("0.1500"),
        },
    ]

    products_map: dict[str, Product] = {}
    for spec in products_spec:
        prod = Product(
            name=spec["name"],
            sku=spec["sku"],
            category=spec["category"],
            price=spec["price"],
            created_at=datetime.utcnow() - timedelta(days=180),
        )
        db.add(prod)
        db.flush()

        # Seed precomputed product risk cache
        prod_cache = ProductRiskCache(
            product_id=prod.id,
            return_rate=spec["return_rate"],
            category_return_rate=spec["category_return_rate"],
            updated_at=datetime.utcnow(),
        )
        db.add(prod_cache)
        products_map[spec["sku"]] = prod

    db.commit()
    logger.info(f"Seeded {len(products_map)} products with risk caches.")
    return products_map


def seed_customers_and_orders(db: Session, products: dict[str, Product]) -> None:
    """Seed Customers A (Low Risk), B (High Risk), C (Uncertain) and related transactions."""
    now = datetime.utcnow()

    # ==========================================
    # CUSTOMER A: Low Risk Profile
    # ~10 previous orders, ~1 return -> Low historical return rate (10%)
    # Normal cart behavior, high trust
    # ==========================================
    logger.info("Seeding Customer A (Low Risk)...")
    cust_a = Customer(
        name="Ananya Sharma",
        email="ananya.sharma@example.com",
        created_at=now - timedelta(days=220),
    )
    db.add(cust_a)
    db.flush()

    cust_a_cache = CustomerRiskCache(
        customer_id=cust_a.id,
        return_rate=Decimal("0.1000"),
        previous_returns=1,
        order_count=10,
        days_since_last_order=4,
        behavior_flags={
            "is_serial_returner": False,
            "size_bracketing_detected": False,
            "loyalty_tier": "Gold",
            "trust_score": 94,
        },
        updated_at=now,
    )
    db.add(cust_a_cache)

    # Orders for Customer A (10 historical orders, 1 returned)
    for i in range(1, 11):
        order_date = now - timedelta(days=200 - i * 19)
        val = Decimal("2499.00") if i % 2 == 0 else Decimal("3998.00")
        ord_a = Order(
            customer_id=cust_a.id,
            order_value=val,
            status="completed",
            created_at=order_date,
        )
        db.add(ord_a)
        db.flush()

        item_a = OrderItem(
            order_id=ord_a.id,
            product_id=products["SKU-SHT-006"].id,
            size="M",
            quantity=1,
            unit_price=Decimal("1999.00"),
        )
        db.add(item_a)
        db.flush()

        # Only Order #4 was returned due to defective stitch
        if i == 4:
            ret_a = Return(
                order_id=ord_a.id,
                order_item_id=item_a.id,
                reason="Minor stitch flaw on left sleeve cuff",
                condition="defective",
                created_at=order_date + timedelta(days=3),
            )
            db.add(ret_a)

        # Risk & policy evaluation for order 10 (most recent)
        if i == 10:
            pred_a = RiskPrediction(
                order_id=ord_a.id,
                risk_score=Decimal("18.50"),
                risk_level="low",
                confidence=Decimal("0.960"),
                model_version="xgboost-v2.4",
                investigation_round=0,
                is_final=True,
                created_at=order_date,
            )
            db.add(pred_a)

            policy_a = PolicyDecision(
                order_id=ord_a.id,
                policy_type="STANDARD_RETURN",
                audit_explanation="Low return rate (10%) and regular order cadence. Zero size bracketing detected.",
                audit_generated_at=order_date + timedelta(seconds=15),
                created_at=order_date,
            )
            db.add(policy_a)

    # ==========================================
    # CUSTOMER B: High Risk Profile
    # ~20 previous orders, ~15 returns -> High return rate (75%)
    # Multi-size cart pattern (bracketing), high value
    # ==========================================
    logger.info("Seeding Customer B (High Risk)...")
    cust_b = Customer(
        name="Rohan Verma",
        email="rohan.verma@example.com",
        created_at=now - timedelta(days=365),
    )
    db.add(cust_b)
    db.flush()

    cust_b_cache = CustomerRiskCache(
        customer_id=cust_b.id,
        return_rate=Decimal("0.7500"),
        previous_returns=15,
        order_count=20,
        days_since_last_order=1,
        behavior_flags={
            "is_serial_returner": True,
            "size_bracketing_detected": True,
            "bracketing_frequency": 5,
            "repeat_wardrobing_suspect": True,
        },
        updated_at=now,
    )
    db.add(cust_b_cache)

    # 20 Orders for Customer B (15 returns)
    for i in range(1, 21):
        order_date = now - timedelta(days=350 - i * 17)
        is_bracketing_order = (i == 20 or i == 15)
        val = Decimal("14998.00") if is_bracketing_order else Decimal("7499.00")

        ord_b = Order(
            customer_id=cust_b.id,
            order_value=val,
            status="completed" if i < 20 else "pending",
            created_at=order_date,
        )
        db.add(ord_b)
        db.flush()

        if is_bracketing_order:
            # Multi-size order: Same product in Size M and Size L
            item_b1 = OrderItem(
                order_id=ord_b.id,
                product_id=products["SKU-ANK-001"].id,
                size="M",
                quantity=1,
                unit_price=Decimal("7499.00"),
            )
            item_b2 = OrderItem(
                order_id=ord_b.id,
                product_id=products["SKU-ANK-001"].id,
                size="L",
                quantity=1,
                unit_price=Decimal("7499.00"),
            )
            db.add(item_b1)
            db.add(item_b2)
            db.flush()
        else:
            item_b = OrderItem(
                order_id=ord_b.id,
                product_id=products["SKU-SHR-002"].id,
                size="XL",
                quantity=1,
                unit_price=Decimal("12999.00"),
            )
            db.add(item_b)
            db.flush()

        # 15 returns across orders
        if i <= 15:
            ret_b = Return(
                order_id=ord_b.id,
                reason="Did not fit as expected after trial",
                condition="worn" if i % 3 == 0 else "unused",
                created_at=order_date + timedelta(days=2),
            )
            db.add(ret_b)

        # Risk & policy for the high-risk bracketing order (Order #20)
        if i == 20:
            pred_b = RiskPrediction(
                order_id=ord_b.id,
                risk_score=Decimal("84.20"),
                risk_level="high",
                confidence=Decimal("0.935"),
                model_version="xgboost-v2.4",
                investigation_round=0,
                is_final=True,
                created_at=order_date,
            )
            db.add(pred_b)

            policy_b = PolicyDecision(
                order_id=ord_b.id,
                policy_type="EXCHANGE_FIRST",
                audit_explanation="High return rate (75%) across 20 orders with multi-size bracketing on SKU-ANK-001 (M, L). Routed to instant size exchange.",
                audit_generated_at=order_date + timedelta(seconds=12),
                created_at=order_date,
            )
            db.add(policy_b)

    # ==========================================
    # CUSTOMER C: Uncertain Profile (New Customer)
    # 1 recent order, 0 returns, low evidence
    # ==========================================
    logger.info("Seeding Customer C (Uncertain)...")
    cust_c = Customer(
        name="Priya Nair",
        email="priya.nair@example.com",
        created_at=now - timedelta(days=3),
    )
    db.add(cust_c)
    db.flush()

    cust_c_cache = CustomerRiskCache(
        customer_id=cust_c.id,
        return_rate=Decimal("0.0000"),
        previous_returns=0,
        order_count=1,
        days_since_last_order=1,
        behavior_flags={
            "is_new_customer": True,
            "insufficient_history": True,
        },
        updated_at=now,
    )
    db.add(cust_c_cache)

    ord_c = Order(
        customer_id=cust_c.id,
        order_value=Decimal("18500.00"),
        status="pending",
        created_at=now - timedelta(hours=6),
    )
    db.add(ord_c)
    db.flush()

    item_c = OrderItem(
        order_id=ord_c.id,
        product_id=products["SKU-SAR-003"].id,
        size=None,
        quantity=1,
        unit_price=Decimal("18500.00"),
    )
    db.add(item_c)
    db.flush()

    pred_c = RiskPrediction(
        order_id=ord_c.id,
        risk_score=Decimal("46.00"),
        risk_level="medium",
        confidence=Decimal("0.480"),  # Low confidence -> Uncertain
        model_version="xgboost-v2.4",
        investigation_round=0,
        is_final=False,
        created_at=now - timedelta(hours=6),
    )
    db.add(pred_c)

    policy_c = PolicyDecision(
        order_id=ord_c.id,
        policy_type="STANDARD_RETURN",
        audit_explanation="New customer with zero prior transaction history. Confidence below threshold (48%). Standard policy applied pending further signals.",
        audit_generated_at=now - timedelta(hours=6, seconds=-20),
        created_at=now - timedelta(hours=6),
    )
    db.add(policy_c)

    # ==========================================
    # CUSTOMER D: Borderline Low / Mixed Signals Profile
    # 15 previous orders, 5 returns -> 33.3% return rate
    # Substantial order history with mixed behavioral signals
    # ==========================================
    logger.info("Seeding Customer D (Borderline Low / Mixed Signals)...")
    cust_d = Customer(
        name="Vikram Malhotra",
        email="vikram.malhotra@example.com",
        created_at=now - timedelta(days=180),
    )
    db.add(cust_d)
    db.flush()

    cust_d_cache = CustomerRiskCache(
        customer_id=cust_d.id,
        return_rate=Decimal("0.3333"),
        previous_returns=5,
        order_count=15,
        days_since_last_order=14,
        behavior_flags={
            "is_serial_returner": False,
            "size_bracketing_detected": False,
            "tenure_tier": "Medium",
        },
        updated_at=now,
    )
    db.add(cust_d_cache)

    # 15 Orders for Customer D (5 returns)
    for i in range(1, 16):
        order_date = now - timedelta(days=175 - i * 11)
        ord_d = Order(
            customer_id=cust_d.id,
            order_value=Decimal("3499.00"),
            status="completed",
            created_at=order_date,
        )
        db.add(ord_d)
        db.flush()

        item_d = OrderItem(
            order_id=ord_d.id,
            product_id=products["SKU-KUR-004"].id,
            size="L",
            quantity=1,
            unit_price=Decimal("3499.00"),
        )
        db.add(item_d)
        db.flush()

        # Returns on orders 3, 6, 9, 12, 14
        if i in (3, 6, 9, 12, 14):
            ret_d = Return(
                order_id=ord_d.id,
                order_item_id=item_d.id,
                reason="Slight size variance, exchanged for better fit",
                condition="unused",
                created_at=order_date + timedelta(days=14),
            )
            db.add(ret_d)

    # ==========================================
    # CUSTOMER E: High Risk, Strong Signal Profile
    # 28 previous orders, 24 returns -> 85.7% return rate
    # Fast return turnaround (1-2 days), wardrobing pattern
    # ==========================================
    logger.info("Seeding Customer E (High Risk, Strong Signal)...")
    cust_e = Customer(
        name="Sameer Kapoor",
        email="sameer.kapoor@example.com",
        created_at=now - timedelta(days=400),
    )
    db.add(cust_e)
    db.flush()

    cust_e_cache = CustomerRiskCache(
        customer_id=cust_e.id,
        return_rate=Decimal("0.8571"),
        previous_returns=24,
        order_count=28,
        days_since_last_order=3,
        behavior_flags={
            "is_serial_returner": True,
            "size_bracketing_detected": True,
            "repeat_wardrobing_suspect": True,
            "bracketing_frequency": 8,
        },
        updated_at=now,
    )
    db.add(cust_e_cache)

    # 28 Orders for Customer E (24 returns)
    for i in range(1, 29):
        order_date = now - timedelta(days=390 - i * 13)
        ord_e = Order(
            customer_id=cust_e.id,
            order_value=Decimal("12999.00"),
            status="completed",
            created_at=order_date,
        )
        db.add(ord_e)
        db.flush()

        item_e = OrderItem(
            order_id=ord_e.id,
            product_id=products["SKU-SHR-002"].id,
            size="XL",
            quantity=1,
            unit_price=Decimal("12999.00"),
        )
        db.add(item_e)
        db.flush()

        # 24 returns across 28 orders with rapid turnaround (1-2 days)
        if i <= 24:
            ret_e = Return(
                order_id=ord_e.id,
                order_item_id=item_e.id,
                reason="Fit not suitable for event",
                condition="worn" if i % 2 == 0 else "unused",
                created_at=order_date + timedelta(days=2),
            )
            db.add(ret_e)

    # ==========================================
    # CUSTOMER F: Clean Repeat Customer Profile
    # 35 previous orders, 2 returns -> 5.7% return rate
    # Long tenure (550 days), high trust score
    # ==========================================
    logger.info("Seeding Customer F (Clean Repeat Customer)...")
    cust_f = Customer(
        name="Meera Sen",
        email="meera.sen@example.com",
        created_at=now - timedelta(days=550),
    )
    db.add(cust_f)
    db.flush()

    cust_f_cache = CustomerRiskCache(
        customer_id=cust_f.id,
        return_rate=Decimal("0.0571"),
        previous_returns=2,
        order_count=35,
        days_since_last_order=20,
        behavior_flags={
            "loyalty_tier": "Platinum",
            "trust_score": 98,
            "is_serial_returner": False,
            "size_bracketing_detected": False,
        },
        updated_at=now,
    )
    db.add(cust_f_cache)

    # 35 Orders for Customer F (2 returns)
    for i in range(1, 36):
        order_date = now - timedelta(days=540 - i * 15)
        ord_f = Order(
            customer_id=cust_f.id,
            order_value=Decimal("5999.00") if i % 3 == 0 else Decimal("2499.00"),
            status="completed",
            created_at=order_date,
        )
        db.add(ord_f)
        db.flush()

        prod_key = "SKU-BLZ-008" if i % 3 == 0 else "SKU-CHN-007"
        item_f = OrderItem(
            order_id=ord_f.id,
            product_id=products[prod_key].id,
            size="M",
            quantity=1,
            unit_price=Decimal("5999.00") if i % 3 == 0 else Decimal("2499.00"),
        )
        db.add(item_f)
        db.flush()

        # Only 2 returns (orders 10 and 25) with 24-day normal turnaround
        if i in (10, 25):
            ret_f = Return(
                order_id=ord_f.id,
                order_item_id=item_f.id,
                reason="Fabric color slightly different from display",
                condition="unused",
                created_at=order_date + timedelta(days=24),
            )
            db.add(ret_f)

    db.commit()
    logger.info("Successfully seeded Customers A, B, C, D, E, and F with full transactional traces.")


def run_seed() -> None:
    """Entry point for running database seeding."""
    if engine is None:
        raise RuntimeError(
            "Cannot run seed: DATABASE_URL is not set in environment or .env"
        )

    logger.info("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        clean_database(db)
        products = seed_products(db)
        seed_customers_and_orders(db, products)
        logger.info("Deterministic database seeding completed successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
