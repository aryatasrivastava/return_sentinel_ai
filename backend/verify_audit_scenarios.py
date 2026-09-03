"""Verification script to test async audit trail generation across multiple scenarios."""

import os
import sys
import time
from decimal import Decimal
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.policy_decision import PolicyDecision
from app.models.risk_prediction import RiskPrediction

client = TestClient(app)

def run_scenario(name: str, payload: dict):
    print(f"\n" + "=" * 60)
    print(f"RUNNING SCENARIO: {name}")
    print("=" * 60)
    
    t0 = time.perf_counter()
    response = client.post("/api/assess-order", json=payload)
    client_duration_ms = (time.perf_counter() - t0) * 1000
    
    print(f"HTTP Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error Response: {response.text}")
        return
        
    data = response.json()
    order_id = data["order_id"]
    print(f"Observed Client Request Latency: {client_duration_ms:.2f}ms")
    print(f"Endpoint Reported latency_ms: {data['latency_ms']}ms")
    print(f"Order ID: {order_id}")
    print(f"Risk Level: {data['risk_level']}")
    print(f"Risk Probability: {data['risk_probability']}")
    print(f"Model Confidence: {data['model_confidence']}")
    print(f"Is Low Confidence: {data['is_low_confidence']}")
    print(f"Recommended Policy: {data['recommended_policy']}")
    print(f"Final Policy: {data['final_policy']}")
    print(f"Top Risk Factors: {data['top_risk_factors']}")
    
    # Query database for audit explanation
    with SessionLocal() as db:
        decision = db.query(PolicyDecision).filter(PolicyDecision.order_id == order_id).first()
        if decision:
            print(f"\n--- Database PolicyDecision Record ---")
            print(f"Policy Type: {decision.policy_type}")
            print(f"Audit Generated At: {decision.audit_generated_at}")
            print(f"Audit Explanation:\n{decision.audit_explanation}")
        else:
            print("ERROR: PolicyDecision not found in DB!")

def main():
    with SessionLocal() as db:
        cust_a = db.query(Customer).filter(Customer.email == "ananya.sharma@example.com").first()
        cust_b = db.query(Customer).filter(Customer.email == "rohan.verma@example.com").first()
        cust_c = db.query(Customer).filter(Customer.email == "priya.nair@example.com").first()
        cust_e = db.query(Customer).filter(Customer.email == "sameer.kapoor@example.com").first()
        
        prod_low = db.query(Product).filter(Product.sku == "SKU-SHT-006").first()
        prod_med = db.query(Product).filter(Product.sku == "SKU-ANK-001").first()
        prod_high = db.query(Product).filter(Product.sku == "SKU-SHR-002").first()

    # Scenario 1: Low Risk (Customer A)
    run_scenario(
        "Scenario 1: Low Risk / Standard Return (Customer A)",
        {
            "customer_id": cust_a.id,
            "cart_items": [
                {"product_id": prod_low.id, "size": "M", "quantity": 1, "unit_price": float(prod_low.price)}
            ]
        }
    )

    print("\nWaiting 15 seconds to respect Gemini API free-tier RPM...")
    time.sleep(15)

    # Scenario 2: Low Confidence Fallback (Customer B)
    run_scenario(
        "Scenario 2: Low Confidence Fallback (Customer B)",
        {
            "customer_id": cust_b.id,
            "cart_items": [
                {"product_id": prod_med.id, "size": "M", "quantity": 1, "unit_price": float(prod_med.price)},
                {"product_id": prod_med.id, "size": "L", "quantity": 1, "unit_price": float(prod_med.price)},
                {"product_id": prod_med.id, "size": "XL", "quantity": 1, "unit_price": float(prod_med.price)}
            ]
        }
    )

    print("\nWaiting 15 seconds to respect Gemini API free-tier RPM...")
    time.sleep(15)

    # Scenario 3: High Risk / Bracketing Dominated (Customer C)
    run_scenario(
        "Scenario 3: High Risk / Bracketing Dominated (Customer C)",
        {
            "customer_id": cust_c.id,
            "cart_items": [
                {"product_id": prod_med.id, "size": "S", "quantity": 1, "unit_price": float(prod_med.price)},
                {"product_id": prod_med.id, "size": "M", "quantity": 1, "unit_price": float(prod_med.price)},
                {"product_id": prod_med.id, "size": "L", "quantity": 1, "unit_price": float(prod_med.price)}
            ]
        }
    )

    print("\nWaiting 15 seconds to respect Gemini API free-tier RPM...")
    time.sleep(15)

    # Scenario 4: High Risk / Repeat Behavior (Customer E)
    run_scenario(
        "Scenario 4: High Risk / Repeat Behavior (Customer E)",
        {
            "customer_id": cust_e.id,
            "cart_items": [
                {"product_id": prod_high.id, "size": "XL", "quantity": 1, "unit_price": float(prod_high.price)},
                {"product_id": prod_high.id, "size": "XXL", "quantity": 1, "unit_price": float(prod_high.price)}
            ]
        }
    )

if __name__ == "__main__":
    main()
