import os
import sys
import unittest
from decimal import Decimal
from unittest.mock import patch
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
from app.models.agent_trace import AgentTrace


class TestReadEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.patcher = patch(
            "audit.audit_generator.generate_audit_explanation",
            return_value="Mocked test audit explanation for fast read-endpoint testing.",
        )
        cls.patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.patcher.stop()

    def setUp(self):
        self.created_order_ids = []

    def tearDown(self):
        if self.created_order_ids:
            with SessionLocal() as db:
                db.query(Order).filter(Order.id.in_(self.created_order_ids)).delete(synchronize_session=False)
                db.commit()

    def test_assess_order_persists_agent_trace_synchronously(self):
        """Verify POST /api/assess-order creates an AgentTrace record with the correct trace_data."""
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
        order_id = data["order_id"]
        self.created_order_ids.append(order_id)

        with SessionLocal() as db:
            trace = db.query(AgentTrace).filter(AgentTrace.order_id == order_id).first()
            self.assertIsNotNone(trace)
            self.assertIsInstance(trace.trace_data, dict)
            self.assertIn("investigation_log", trace.trace_data)
            self.assertIn("policy_agent_reasoning", trace.trace_data)
            self.assertIn("policy_engine_details", trace.trace_data)
            self.assertIn("top_risk_factors", trace.trace_data)
            self.assertIsInstance(trace.trace_data["top_risk_factors"], list)
            self.assertGreater(len(trace.trace_data["top_risk_factors"]), 0)

            # Check that investigation_log contains pipeline step dicts
            investigation_log = trace.trace_data["investigation_log"]
            self.assertIsInstance(investigation_log, list)
            step_types = [s.get("step_type") for s in investigation_log]
            self.assertIn("initial_assessment", step_types)
            self.assertIn("policy_agent", step_types)
            self.assertIn("policy_engine", step_types)

    def test_get_orders_list_and_pagination(self):
        """Verify GET /api/orders returns paginated and formatted list of orders."""
        response = self.client.get("/api/orders?limit=5&offset=0")
        self.assertEqual(response.status_code, 200)
        orders = response.json()
        self.assertIsInstance(orders, list)
        self.assertLessEqual(len(orders), 5)

        if orders:
            first = orders[0]
            self.assertIn("order_id", first)
            self.assertIn("customer_name", first)
            self.assertIn("cart_value", first)
            self.assertIn("status", first)
            self.assertIn("created_at", first)

    def test_get_orders_filtering(self):
        """Verify GET /api/orders filtering by risk_level and policy_type."""
        # Filter by risk_level
        res_high = self.client.get("/api/orders?risk_level=HIGH")
        self.assertEqual(res_high.status_code, 200)
        for ord_data in res_high.json():
            self.assertEqual(ord_data["risk_level"], "HIGH")

        # Filter by policy_type
        res_policy = self.client.get("/api/orders?policy_type=STANDARD_RETURN")
        self.assertEqual(res_policy.status_code, 200)
        for ord_data in res_policy.json():
            self.assertEqual(ord_data["policy"], "STANDARD_RETURN")

    def test_get_order_detail_success(self):
        """Verify GET /api/orders/{order_id} returns full order details including trace, top_risk_factors, and audit."""
        # Create an assessed order first
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "sameer.kapoor@example.com").first()
            prod = db.query(Product).filter(Product.sku == "SKU-SHR-002").first()
            cust_id = cust.id
            prod_id = prod.id

        payload = {
            "customer_id": cust_id,
            "cart_items": [
                {"product_id": prod_id, "size": "XL", "quantity": 1, "unit_price": 12999.0},
                {"product_id": prod_id, "size": "XXL", "quantity": 1, "unit_price": 12999.0},
            ],
        }
        create_res = self.client.post("/api/assess-order", json=payload)
        self.assertEqual(create_res.status_code, 200)
        order_id = create_res.json()["order_id"]
        self.created_order_ids.append(order_id)

        detail_res = self.client.get(f"/api/orders/{order_id}")
        self.assertEqual(detail_res.status_code, 200)
        detail = detail_res.json()

        self.assertEqual(detail["order_id"], order_id)
        self.assertEqual(detail["customer_name"], "Sameer Kapoor")
        self.assertEqual(detail["risk_level"], "HIGH")
        self.assertEqual(detail["policy"], "STORE_CREDIT")
        self.assertIsInstance(detail["items"], list)
        self.assertEqual(len(detail["items"]), 2)
        self.assertIsNotNone(detail["trace_data"])
        self.assertIn("investigation_log", detail["trace_data"])
        self.assertIn("policy_agent_reasoning", detail["trace_data"])
        self.assertIn("policy_engine_details", detail["trace_data"])
        self.assertIsNotNone(detail["top_risk_factors"])
        self.assertIsInstance(detail["top_risk_factors"], list)
        self.assertGreater(len(detail["top_risk_factors"]), 0)
        self.assertEqual(detail["audit_explanation"], "Mocked test audit explanation for fast read-endpoint testing.")
        self.assertIsNotNone(detail["audit_generated_at"])

    def test_get_order_detail_not_found(self):
        """Verify GET /api/orders/{order_id} returns 404 for non-existent order."""
        response = self.client.get("/api/orders/99999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Order with ID 99999999 does not exist", response.text)

    def test_get_dashboard_stats(self):
        """Verify GET /api/dashboard-stats returns correctly computed aggregate statistics without double-counting."""
        response = self.client.get("/api/dashboard-stats")
        self.assertEqual(response.status_code, 200)
        stats = response.json()

        orders_analyzed = stats["orders_analyzed"]
        self.assertGreater(orders_analyzed, 0)
        self.assertIn("high_risk_orders", stats)
        self.assertGreaterEqual(stats["high_risk_orders"], 0)
        self.assertIn("estimated_margin_protected", stats)
        self.assertGreaterEqual(stats["estimated_margin_protected"], 0.0)

        # Confirm false_positive_rate is strictly null
        self.assertIsNone(stats["false_positive_rate"])

        # Confirm risk_distribution sums to exactly orders_analyzed
        self.assertIn("risk_distribution", stats)
        risk_sum = sum(stats["risk_distribution"].values())
        self.assertEqual(
            risk_sum,
            orders_analyzed,
            f"risk_distribution sum ({risk_sum}) must match orders_analyzed ({orders_analyzed})",
        )

        # Confirm policy_distribution sums to exactly orders_analyzed
        self.assertIn("policy_distribution", stats)
        policy_sum = sum(stats["policy_distribution"].values())
        self.assertEqual(
            policy_sum,
            orders_analyzed,
            f"policy_distribution sum ({policy_sum}) must match orders_analyzed ({orders_analyzed})",
        )


if __name__ == "__main__":
    unittest.main()
