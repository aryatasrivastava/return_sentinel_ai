import time
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.product import Product

client = TestClient(app)

print("=" * 60)
print("1. DASHBOARD STATS ARITHMETIC VERIFICATION")
print("=" * 60)
stats_res = client.get("/api/dashboard-stats")
stats = stats_res.json()
print("GET /api/dashboard-stats output:")
print(stats)

orders_analyzed = stats["orders_analyzed"]
risk_dist = stats["risk_distribution"]
policy_dist = stats["policy_distribution"]
risk_sum = sum(risk_dist.values())
policy_sum = sum(policy_dist.values())

print(f"\nOrders Analyzed: {orders_analyzed}")
print(f"Risk Distribution: {risk_dist} => Sum: {risk_sum} (Match: {risk_sum == orders_analyzed})")
print(f"Policy Distribution: {policy_dist} => Sum: {policy_sum} (Match: {policy_sum == orders_analyzed})")
print(f"High Risk Orders: {stats['high_risk_orders']}")
print(f"Estimated Margin Protected: {stats['estimated_margin_protected']}")
print(f"False Positive Rate: {stats['false_positive_rate']}")

assert risk_sum == orders_analyzed, f"Risk sum {risk_sum} != orders_analyzed {orders_analyzed}"
assert policy_sum == orders_analyzed, f"Policy sum {policy_sum} != orders_analyzed {orders_analyzed}"
print("\n>>> Dashboard Stats Arithmetic: PERFECT MATCH <<<")

print("\n" + "=" * 60)
print("2. REAL POST /api/assess-order CALLS & LATENCY MEASUREMENTS")
print("=" * 60)

with SessionLocal() as db:
    cust_a = db.query(Customer).filter(Customer.email == "ananya.sharma@example.com").first()
    cust_b = db.query(Customer).filter(Customer.email == "rohan.verma@example.com").first()
    cust_e = db.query(Customer).filter(Customer.email == "sameer.kapoor@example.com").first()
    prod_s = db.query(Product).filter(Product.sku == "SKU-SHT-006").first()
    prod_d = db.query(Product).filter(Product.sku == "SKU-SHR-002").first()

test_cases = [
    {
        "name": "Call 1 - Customer A (Low Risk Shirt)",
        "payload": {
            "customer_id": cust_a.id,
            "cart_items": [{"product_id": prod_s.id, "size": "M", "quantity": 1, "unit_price": float(prod_s.price)}],
        },
    },
    {
        "name": "Call 2 - Customer B (Medium Risk Multi-size)",
        "payload": {
            "customer_id": cust_b.id,
            "cart_items": [
                {"product_id": prod_s.id, "size": "M", "quantity": 1, "unit_price": float(prod_s.price)},
                {"product_id": prod_s.id, "size": "L", "quantity": 1, "unit_price": float(prod_s.price)},
            ],
        },
    },
    {
        "name": "Call 3 - Customer E (High Risk Sherwani Bracketing)",
        "payload": {
            "customer_id": cust_e.id,
            "cart_items": [
                {"product_id": prod_d.id, "size": "XL", "quantity": 1, "unit_price": float(prod_d.price)},
                {"product_id": prod_d.id, "size": "XXL", "quantity": 1, "unit_price": float(prod_d.price)},
            ],
        },
    },
]

assessed_order_ids = []
latencies = []

for tc in test_cases:
    t0 = time.perf_counter()
    res = client.post("/api/assess-order", json=tc["payload"])
    client_elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    assert res.status_code == 200, f"Failed: {res.text}"
    body = res.json()
    order_id = body["order_id"]
    endpoint_latency = body["latency_ms"]
    assessed_order_ids.append(order_id)
    latencies.append((tc["name"], endpoint_latency, client_elapsed_ms, body["risk_level"], body["final_policy"]))
    print(f"[{tc['name']}]")
    print(f"  Order ID: {order_id}")
    print(f"  Risk Level: {body['risk_level']} ({round(body['risk_probability']*100, 2)}%)")
    print(f"  Final Policy: {body['final_policy']}")
    print(f"  Endpoint latency_ms: {endpoint_latency}ms | Total HTTP latency: {client_elapsed_ms}ms")
    print(f"  Top Risk Factors: {body['top_risk_factors']}")

print("\n" + "=" * 60)
print("3. GET /api/orders/{order_id} VERIFICATION (top_risk_factors populated)")
print("=" * 60)
last_order_id = assessed_order_ids[-1]
detail_res = client.get(f"/api/orders/{last_order_id}")
assert detail_res.status_code == 200
detail = detail_res.json()
print(f"GET /api/orders/{last_order_id} response:")
print(f"  Order ID: {detail['order_id']}")
print(f"  Customer: {detail['customer_name']}")
print(f"  Cart Value: {detail['cart_value']}")
print(f"  Risk Level: {detail['risk_level']}")
print(f"  Policy: {detail['policy']}")
print(f"  top_risk_factors: {detail['top_risk_factors']}")
print(f"  trace_data keys: {list(detail['trace_data'].keys()) if detail['trace_data'] else None}")
print(f"  trace_data['top_risk_factors']: {detail['trace_data'].get('top_risk_factors') if detail['trace_data'] else None}")
print(f"  audit_explanation: {detail['audit_explanation']}")
assert detail["top_risk_factors"] is not None and len(detail["top_risk_factors"]) > 0, "top_risk_factors is null!"
print("\n>>> top_risk_factors: SUCCESSFULLY POPULATED (NON-NULL) <<<")
