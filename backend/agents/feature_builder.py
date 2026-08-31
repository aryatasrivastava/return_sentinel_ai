"""ReturnSentinel AI Feature Builder (Phase 3A).

This module extracts and computes the exact 12-feature vector required by the
XGBoost risk model (`predict_return_risk()`).

Supports two operational modes:
1. `build_features_from_cache()`: Round 0 assessment using `CustomerRiskCache`
   and `ProductRiskCache` database rows + realtime cart properties.
2. `build_features_from_live_data()`: Rounds 1 & 2 re-investigation querying
   live `orders`, `order_items`, `returns`, and catalog tables directly to
   recompute real-time behavioral metrics, bypassing caches.

Both functions strictly enforce:
- Exact 12-column feature ordering matching `model_config.json`.
- Phase 2A documented edge-case defaults:
  * `customer_return_rate = 0.0` when `total_previous_orders == 0`
  * `days_since_last_order = customer_history_days` when `total_previous_orders == 0`
  * `avg_days_to_return = 0.0` when `total_previous_returns == 0`
  * `previous_returns_same_category = 0` when `total_previous_returns == 0`
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set
from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.customer_risk_cache import CustomerRiskCache
from app.models.product import Product
from app.models.product_risk_cache import ProductRiskCache
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.return_ import Return

# Exact 12 feature names in order specified by model_config.json
FEATURE_ORDER: List[str] = [
    "customer_return_rate",
    "total_previous_orders",
    "total_previous_returns",
    "customer_history_days",
    "days_since_last_order",
    "cart_value",
    "cart_item_count",
    "multiple_sizes_same_product",
    "max_sizes_same_product",
    "average_product_return_rate",
    "previous_returns_same_category",
    "avg_days_to_return",
]


def _compute_cart_features(cart_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute realtime cart-level features directly from the cart items payload.

    Args:
        cart_items: List of dictionaries with keys `product_id`, `size`, `quantity`, `unit_price`.

    Returns:
        Dictionary with cart_value, cart_item_count, multiple_sizes_same_product, max_sizes_same_product.
    """
    total_val = 0.0
    total_count = 0
    product_sizes: Dict[Any, Set[str]] = defaultdict(set)

    for item in cart_items:
        qty = int(item.get("quantity", 1))
        unit_price = float(item.get("unit_price", 0.0))
        prod_id = item.get("product_id")
        size = item.get("size")

        total_val += unit_price * qty
        total_count += qty

        if prod_id is not None and size is not None:
            product_sizes[prod_id].add(str(size).strip().upper())

    # Detect size bracketing (multiple sizes of the same product in cart)
    max_sizes = 1
    multiple_sizes = 0

    for prod_id, sizes in product_sizes.items():
        size_count = len(sizes)
        if size_count > max_sizes:
            max_sizes = size_count
        if size_count > 1:
            multiple_sizes = 1

    return {
        "cart_value": round(float(total_val), 2),
        "cart_item_count": max(1, total_count) if cart_items else 1,
        "multiple_sizes_same_product": multiple_sizes,
        "max_sizes_same_product": max_sizes,
    }


def _resolve_customer(db: Session, customer_id: Any) -> Optional[Customer]:
    """Lookup Customer by integer ID, string ID, or email."""
    if isinstance(customer_id, int) or (isinstance(customer_id, str) and customer_id.isdigit()):
        cust = db.query(Customer).filter(Customer.id == int(customer_id)).first()
        if cust:
            return cust
    if isinstance(customer_id, str):
        cust = db.query(Customer).filter(Customer.email == customer_id).first()
        if cust:
            return cust
        cust = db.query(Customer).filter(Customer.name.ilike(f"%{customer_id}%")).first()
        if cust:
            return cust
    return None


def _format_feature_dict(features_raw: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all 12 keys are present, correctly typed, and strictly ordered."""
    ordered_dict: Dict[str, Any] = {}
    for key in FEATURE_ORDER:
        val = features_raw.get(key)
        if val is None:
            # Fallback safe defaults if somehow missing
            if key in ("customer_return_rate", "average_product_return_rate", "avg_days_to_return", "cart_value"):
                ordered_dict[key] = 0.0
            elif key in ("multiple_sizes_same_product",):
                ordered_dict[key] = 0
            elif key in ("max_sizes_same_product", "cart_item_count"):
                ordered_dict[key] = 1
            else:
                ordered_dict[key] = 0
        else:
            if key in ("customer_return_rate", "average_product_return_rate", "avg_days_to_return", "cart_value"):
                ordered_dict[key] = round(float(val), 4 if key != "cart_value" else 2)
            elif key in ("total_previous_orders", "total_previous_returns", "customer_history_days",
                         "days_since_last_order", "cart_item_count", "multiple_sizes_same_product",
                         "max_sizes_same_product", "previous_returns_same_category"):
                ordered_dict[key] = int(val)
            else:
                ordered_dict[key] = val
    return ordered_dict


def build_features_from_cache(
    customer_id: Any,
    cart_items: List[Dict[str, Any]],
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """Mode 1 (Round 0): Build 12-feature dict using precomputed database caches and cart items.

    Reads `customer_risk_cache` and `product_risk_cache`.
    Computes cart features in realtime.
    Applies Phase 2A edge-case defaults.

    Args:
        customer_id: Database customer ID or identifier.
        cart_items: List of cart item dicts (product_id, size, quantity, unit_price).
        db: Optional SQLAlchemy Session. If None, creates and closes a local session.

    Returns:
        12-feature dictionary strictly ordered by `FEATURE_ORDER`.
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        cart_feats = _compute_cart_features(cart_items)
        customer = _resolve_customer(db, customer_id)

        now_utc = datetime.now(timezone.utc)
        if customer and customer.created_at:
            created = customer.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            customer_history_days = max(0, (now_utc - created).days)
        else:
            customer_history_days = 0

        # Query CustomerRiskCache
        cache_row: Optional[CustomerRiskCache] = None
        if customer:
            cache_row = db.query(CustomerRiskCache).filter(
                CustomerRiskCache.customer_id == customer.id
            ).first()

        if cache_row:
            total_previous_orders = int(cache_row.order_count)
            total_previous_returns = int(cache_row.previous_returns)
            customer_return_rate = float(cache_row.return_rate)
            if cache_row.days_since_last_order is not None:
                days_since_last_order = int(cache_row.days_since_last_order)
            else:
                days_since_last_order = customer_history_days
        else:
            # New or un-cached customer defaults
            total_previous_orders = 0
            total_previous_returns = 0
            customer_return_rate = 0.0
            days_since_last_order = customer_history_days

        # Edge-case defaults for customer history
        if total_previous_orders == 0:
            customer_return_rate = 0.0
            days_since_last_order = customer_history_days

        # Query ProductRiskCache for items in cart
        prod_rates: List[float] = []
        for item in cart_items:
            p_id = item.get("product_id")
            qty = int(item.get("quantity", 1))
            prod_rate = 0.20  # catalog default baseline

            if p_id is not None:
                # Find product cache
                p_cache = None
                if isinstance(p_id, int) or (isinstance(p_id, str) and str(p_id).isdigit()):
                    p_cache = db.query(ProductRiskCache).filter(
                        ProductRiskCache.product_id == int(p_id)
                    ).first()
                elif isinstance(p_id, str):
                    prod = db.query(Product).filter(Product.sku == p_id).first()
                    if prod:
                        p_cache = db.query(ProductRiskCache).filter(
                            ProductRiskCache.product_id == prod.id
                        ).first()

                if p_cache and p_cache.return_rate is not None:
                    prod_rate = float(p_cache.return_rate)

            for _ in range(qty):
                prod_rates.append(prod_rate)

        average_product_return_rate = (
            sum(prod_rates) / len(prod_rates) if prod_rates else 0.20
        )

        # Cache-mode category returns & turnaround defaults
        if total_previous_returns == 0:
            previous_returns_same_category = 0
            avg_days_to_return = 0.0
        else:
            # Estimate from cached behavioral signals or default
            previous_returns_same_category = min(1, total_previous_returns)
            avg_days_to_return = 12.0  # standard cached placeholder when returns exist

        raw_features = {
            "customer_return_rate": customer_return_rate,
            "total_previous_orders": total_previous_orders,
            "total_previous_returns": total_previous_returns,
            "customer_history_days": customer_history_days,
            "days_since_last_order": days_since_last_order,
            "cart_value": cart_feats["cart_value"],
            "cart_item_count": cart_feats["cart_item_count"],
            "multiple_sizes_same_product": cart_feats["multiple_sizes_same_product"],
            "max_sizes_same_product": cart_feats["max_sizes_same_product"],
            "average_product_return_rate": average_product_return_rate,
            "previous_returns_same_category": previous_returns_same_category,
            "avg_days_to_return": avg_days_to_return,
        }

        return _format_feature_dict(raw_features)

    finally:
        if should_close_db:
            db.close()


def build_features_from_live_data(
    customer_id: Any,
    cart_items: List[Dict[str, Any]],
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """Mode 2 (Rounds 1+): Build 12-feature dict querying live database tables directly.

    Queries `orders`, `order_items`, `returns`, and `products` to compute
    exact real-time return rates, recency, category overlap, and return turnarounds.
    Bypasses `customer_risk_cache` and `product_risk_cache`.
    Applies Phase 2A edge-case defaults.

    Args:
        customer_id: Database customer ID or identifier.
        cart_items: List of cart item dicts (product_id, size, quantity, unit_price).
        db: Optional SQLAlchemy Session. If None, creates and closes a local session.

    Returns:
        12-feature dictionary strictly ordered by `FEATURE_ORDER`.
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        cart_feats = _compute_cart_features(cart_items)
        customer = _resolve_customer(db, customer_id)

        now_utc = datetime.now(timezone.utc)
        if customer and customer.created_at:
            created = customer.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            customer_history_days = max(0, (now_utc - created).days)
        else:
            customer_history_days = 0

        # Query live orders for customer
        orders: List[Order] = []
        if customer:
            orders = (
                db.query(Order)
                .filter(Order.customer_id == customer.id)
                .order_by(Order.created_at.desc())
                .all()
            )

        total_previous_orders = len(orders)

        # Days since last order
        if total_previous_orders > 0 and orders[0].created_at:
            last_order_dt = orders[0].created_at
            if last_order_dt.tzinfo is None:
                last_order_dt = last_order_dt.replace(tzinfo=timezone.utc)
            raw_recency = (now_utc - last_order_dt).days
            days_since_last_order = min(max(0, raw_recency), customer_history_days)
        else:
            days_since_last_order = customer_history_days

        # Query live returns for this customer's orders
        returns: List[Return] = []
        if orders:
            order_ids = [o.id for o in orders]
            returns = (
                db.query(Return)
                .filter(Return.order_id.in_(order_ids))
                .all()
            )

        total_previous_returns = len(returns)

        # Live customer return rate
        if total_previous_orders > 0:
            customer_return_rate = round(total_previous_returns / total_previous_orders, 4)
        else:
            customer_return_rate = 0.0

        # Compute average days to return from live timestamps
        return_turnaround_days: List[float] = []
        order_map = {o.id: o for o in orders}

        for ret in returns:
            associated_order = order_map.get(ret.order_id)
            if associated_order and associated_order.created_at and ret.created_at:
                o_dt = associated_order.created_at
                r_dt = ret.created_at
                if o_dt.tzinfo is None:
                    o_dt = o_dt.replace(tzinfo=timezone.utc)
                if r_dt.tzinfo is None:
                    r_dt = r_dt.replace(tzinfo=timezone.utc)
                diff_days = max(0.0, (r_dt - o_dt).total_seconds() / 86400.0)
                return_turnaround_days.append(diff_days)

        if total_previous_returns > 0 and return_turnaround_days:
            avg_days_to_return = round(sum(return_turnaround_days) / len(return_turnaround_days), 2)
        else:
            avg_days_to_return = 0.0

        # Determine categories of products in current cart
        cart_categories: Set[str] = set()
        for item in cart_items:
            p_id = item.get("product_id")
            if p_id is not None:
                p_obj = None
                if isinstance(p_id, int) or (isinstance(p_id, str) and str(p_id).isdigit()):
                    p_obj = db.query(Product).filter(Product.id == int(p_id)).first()
                elif isinstance(p_id, str):
                    p_obj = db.query(Product).filter(Product.sku == p_id).first()
                if p_obj and p_obj.category:
                    cart_categories.add(p_obj.category.strip())

        # Count past returns belonging to these same categories
        cat_return_count = 0
        if cart_categories and returns:
            for ret in returns:
                if ret.order_item_id:
                    oi = db.query(OrderItem).filter(OrderItem.id == ret.order_item_id).first()
                    if oi and oi.product and oi.product.category:
                        if oi.product.category.strip() in cart_categories:
                            cat_return_count += 1
                else:
                    # Check items of the returned order
                    ret_order = order_map.get(ret.order_id)
                    if ret_order and ret_order.order_items:
                        for oi in ret_order.order_items:
                            if oi.product and oi.product.category and oi.product.category.strip() in cart_categories:
                                cat_return_count += 1
                                break

        previous_returns_same_category = min(total_previous_returns, cat_return_count)

        # Recompute fine-grained average product return rate from catalog data
        prod_rates: List[float] = []
        for item in cart_items:
            p_id = item.get("product_id")
            qty = int(item.get("quantity", 1))
            rate = 0.20  # catalog default

            if p_id is not None:
                p_obj = None
                if isinstance(p_id, int) or (isinstance(p_id, str) and str(p_id).isdigit()):
                    p_obj = db.query(Product).filter(Product.id == int(p_id)).first()
                elif isinstance(p_id, str):
                    p_obj = db.query(Product).filter(Product.sku == p_id).first()

                if p_obj:
                    # Query live order item and return counts for this product
                    total_prod_items = db.query(OrderItem).filter(OrderItem.product_id == p_obj.id).count()
                    total_prod_returns = (
                        db.query(Return)
                        .join(OrderItem, Return.order_item_id == OrderItem.id)
                        .filter(OrderItem.product_id == p_obj.id)
                        .count()
                    )
                    if total_prod_items > 0:
                        rate = round(total_prod_returns / total_prod_items, 4)
                    elif p_obj.risk_cache and p_obj.risk_cache.return_rate is not None:
                        rate = float(p_obj.risk_cache.return_rate)

            for _ in range(qty):
                prod_rates.append(rate)

        average_product_return_rate = (
            sum(prod_rates) / len(prod_rates) if prod_rates else 0.20
        )

        raw_features = {
            "customer_return_rate": customer_return_rate,
            "total_previous_orders": total_previous_orders,
            "total_previous_returns": total_previous_returns,
            "customer_history_days": customer_history_days,
            "days_since_last_order": days_since_last_order,
            "cart_value": cart_feats["cart_value"],
            "cart_item_count": cart_feats["cart_item_count"],
            "multiple_sizes_same_product": cart_feats["multiple_sizes_same_product"],
            "max_sizes_same_product": cart_feats["max_sizes_same_product"],
            "average_product_return_rate": average_product_return_rate,
            "previous_returns_same_category": previous_returns_same_category,
            "avg_days_to_return": avg_days_to_return,
        }

        return _format_feature_dict(raw_features)

    finally:
        if should_close_db:
            db.close()
