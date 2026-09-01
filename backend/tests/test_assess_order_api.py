import os
import sys
import unittest
from decimal import Decimal
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.risk_prediction import RiskPrediction
from app.models.policy_decision import PolicyDecision


class TestAssessOrderAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_customer_not_found(self):
        """Verify 404 response when non-existent customer_id is provided."""
        payload = {
            "customer_id": 999999,
            "cart_items": [
                {"product_id": 1, "size": "M", "quantity": 1, "unit_price": 1999.0}
            ],
        }
        response = self.client.post("/api/assess-order", json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Customer with ID 999999 does not exist", response.text)

    def test_product_not_found_in_auto_create(self):
        """Verify 404 response when product in cart does not exist in catalog."""
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "ananya.sharma@example.com").first()
            self.assertIsNotNone(cust)
            cust_id = cust.id

        payload = {
            "customer_id": cust_id,
            "cart_items": [
                {"product_id": 999999, "size": "M", "quantity": 1, "unit_price": 1999.0}
            ],
        }
        response = self.client.post("/api/assess-order", json=payload)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Product with ID 999999 does not exist", response.text)

    def test_order_mismatch_with_customer(self):
        """Verify 400 response when order_id belongs to a different customer."""
        with SessionLocal() as db:
            cust_a = db.query(Customer).filter(Customer.email == "ananya.sharma@example.com").first()
            cust_e = db.query(Customer).filter(Customer.email == "sameer.kapoor@example.com").first()
            order_e = db.query(Order).filter(Order.customer_id == cust_e.id).first()
            self.assertIsNotNone(cust_a)
            self.assertIsNotNone(cust_e)
            self.assertIsNotNone(order_e)

        payload = {
            "customer_id": cust_a.id,
            "order_id": order_e.id,
            "cart_items": [
                {"product_id": 1, "size": "M", "quantity": 1, "unit_price": 1999.0}
            ],
        }
        response = self.client.post("/api/assess-order", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn(f"Order {order_e.id} does not belong to Customer {cust_a.id}", response.text)

    def test_auto_create_order_customer_a_low_risk(self):
        """Verify auto-order creation and complete assessment pipeline for Customer A."""
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "ananya.sharma@example.com").first()
            prod = db.query(Product).filter(Product.sku == "SKU-SHT-006").first()
            self.assertIsNotNone(cust)
            self.assertIsNotNone(prod)
            cust_id = cust.id
            prod_id = prod.id
            prod_price = float(prod.price)

        payload = {
            "customer_id": cust_id,
            "cart_items": [
                {"product_id": prod_id, "size": "M", "quantity": 1, "unit_price": prod_price}
            ],
        }

        response = self.client.post("/api/assess-order", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Assert response shape & types
        self.assertIn("order_id", data)
        self.assertIsInstance(data["order_id"], int)
        self.assertEqual(data["risk_level"], "LOW")
        self.assertFalse(data["is_low_confidence"])
        self.assertEqual(data["recommended_policy"], "STANDARD_RETURN")
        self.assertEqual(data["final_policy"], "STANDARD_RETURN")
        self.assertTrue(data["validation_passed"])
        self.assertFalse(data["policy_anomaly"])
        self.assertIsInstance(data["top_risk_factors"], list)
        self.assertGreater(len(data["top_risk_factors"]), 0)
        self.assertGreater(data["latency_ms"], 0)

        # Assert database persistence
        created_order_id = data["order_id"]
        with SessionLocal() as db:
            order = db.query(Order).filter(Order.id == created_order_id).first()
            self.assertIsNotNone(order)
            self.assertEqual(order.customer_id, cust_id)
            self.assertEqual(order.order_value, Decimal(str(round(prod_price, 2))))

            order_items = db.query(OrderItem).filter(OrderItem.order_id == created_order_id).all()
            self.assertEqual(len(order_items), 1)
            self.assertEqual(order_items[0].product_id, prod_id)

            pred = db.query(RiskPrediction).filter(RiskPrediction.order_id == created_order_id).first()
            self.assertIsNotNone(pred)
            self.assertEqual(pred.risk_level, "low")
            self.assertTrue(pred.is_final)

            decision = db.query(PolicyDecision).filter(PolicyDecision.order_id == created_order_id).first()
            self.assertIsNotNone(decision)
            self.assertEqual(decision.policy_type, "STANDARD_RETURN")

    def test_existing_order_customer_e_high_risk(self):
        """Verify assessment execution using an existing order ID for Customer E."""
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "sameer.kapoor@example.com").first()
            prod = db.query(Product).filter(Product.sku == "SKU-SHR-002").first()
            order = db.query(Order).filter(Order.customer_id == cust.id).first()
            self.assertIsNotNone(cust)
            self.assertIsNotNone(prod)
            self.assertIsNotNone(order)
            cust_id = cust.id
            prod_id = prod.id
            order_id = order.id

        payload = {
            "customer_id": cust_id,
            "order_id": order_id,
            "cart_items": [
                {"product_id": prod_id, "size": "XL", "quantity": 1, "unit_price": 12999.0},
                {"product_id": prod_id, "size": "XXL", "quantity": 1, "unit_price": 12999.0},
            ],
        }

        response = self.client.post("/api/assess-order", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["order_id"], order_id)
        self.assertEqual(data["risk_level"], "HIGH")
        self.assertEqual(data["recommended_policy"], "STORE_CREDIT")
        self.assertEqual(data["final_policy"], "STORE_CREDIT")
        self.assertTrue(data["validation_passed"])
        self.assertFalse(data["policy_anomaly"])
        self.assertGreater(data["latency_ms"], 0)

        # Assert database persistence
        with SessionLocal() as db:
            decision = db.query(PolicyDecision).filter(PolicyDecision.order_id == order_id).first()
            self.assertIsNotNone(decision)
            self.assertEqual(decision.policy_type, "STORE_CREDIT")

    def test_customer_b_low_confidence_fallback(self):
        """Verify assessment execution for Customer B triggering low-confidence fallback."""
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "rohan.verma@example.com").first()
            prod = db.query(Product).filter(Product.sku == "SKU-ANK-001").first()
            self.assertIsNotNone(cust)
            self.assertIsNotNone(prod)
            cust_id = cust.id
            prod_id = prod.id

        payload = {
            "customer_id": cust_id,
            "cart_items": [
                {"product_id": prod_id, "size": "M", "quantity": 1, "unit_price": 7499.0},
                {"product_id": prod_id, "size": "L", "quantity": 1, "unit_price": 7499.0},
                {"product_id": prod_id, "size": "XL", "quantity": 1, "unit_price": 7499.0},
            ],
        }

        response = self.client.post("/api/assess-order", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["risk_level"], "HIGH")
        self.assertTrue(data["is_low_confidence"])
        self.assertEqual(data["recommended_policy"], "EXCHANGE_FIRST")
        self.assertEqual(data["final_policy"], "EXCHANGE_FIRST")
        self.assertTrue(data["validation_passed"])
        self.assertFalse(data["policy_anomaly"])
        self.assertGreater(data["latency_ms"], 0)


if __name__ == "__main__":
    unittest.main()
