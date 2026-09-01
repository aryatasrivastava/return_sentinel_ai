import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graph import run_risk_assessment, risk_assessment_graph
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.product import Product


class TestFullLangGraphPipeline(unittest.TestCase):
    def test_pipeline_low_risk_order(self):
        """Verify full pipeline execution for a low-risk customer cart."""
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "ananya.sharma@example.com").first()
            prod = db.query(Product).filter(Product.sku == "SKU-SHT-006").first()
            self.assertIsNotNone(cust)
            self.assertIsNotNone(prod)
            cust_id = cust.id
            prod_id = prod.id

        cart_items = [
            {"product_id": prod_id, "size": "M", "quantity": 1, "unit_price": 1999.0}
        ]

        state = run_risk_assessment(
            order_id="TEST-ORD-LOW",
            customer_id=cust_id,
            cart_items=cart_items,
        )

        # Assert risk assessment outputs
        self.assertEqual(state["risk_level"], "LOW")
        self.assertFalse(state["is_low_confidence"])
        self.assertIsNotNone(state["risk_probability"])
        self.assertIsNotNone(state["model_confidence"])
        self.assertGreater(len(state["top_risk_factors"]), 0)
        self.assertGreater(len(state["top_risk_factors_detailed"]), 0)

        # Assert policy agent & engine outputs
        self.assertEqual(state["recommended_policy"], "STANDARD_RETURN")
        self.assertEqual(state["final_policy"], "STANDARD_RETURN")
        self.assertTrue(state["validation_passed"])
        self.assertFalse(state["policy_anomaly"])
        self.assertIsNotNone(state["policy_agent_reasoning"])
        self.assertIsNotNone(state["policy_engine_details"])

        # Assert investigation log steps
        step_types = [s.get("step_type") for s in state["investigation_log"]]
        self.assertIn("initial_assessment", step_types)
        self.assertIn("policy_agent", step_types)
        self.assertIn("policy_engine", step_types)

    def test_pipeline_high_risk_repeat_behavior_order(self):
        """Verify full pipeline execution for a high-risk repeat return customer."""
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "sameer.kapoor@example.com").first()
            prod = db.query(Product).filter(Product.sku == "SKU-SHR-002").first()
            self.assertIsNotNone(cust)
            self.assertIsNotNone(prod)
            cust_id = cust.id
            prod_id = prod.id

        cart_items = [
            {"product_id": prod_id, "size": "XL", "quantity": 1, "unit_price": 12999.0},
            {"product_id": prod_id, "size": "XXL", "quantity": 1, "unit_price": 12999.0},
        ]

        state = run_risk_assessment(
            order_id="TEST-ORD-HIGH",
            customer_id=cust_id,
            cart_items=cart_items,
        )

        self.assertEqual(state["risk_level"], "HIGH")
        self.assertIsNotNone(state["final_policy"])
        self.assertTrue(state["validation_passed"])
        self.assertFalse(state["policy_anomaly"])
        self.assertEqual(state["recommended_policy"], state["final_policy"])

    def test_pipeline_low_confidence_fallback(self):
        """Verify that an exhausted low-confidence run triggers fallback in policy agent and validates."""
        with SessionLocal() as db:
            cust = db.query(Customer).filter(Customer.email == "rohan.verma@example.com").first()
            prod = db.query(Product).filter(Product.sku == "SKU-ANK-001").first()
            self.assertIsNotNone(cust)
            self.assertIsNotNone(prod)
            cust_id = cust.id
            prod_id = prod.id

        cart_items = [
            {"product_id": prod_id, "size": "M", "quantity": 1, "unit_price": 7499.0},
            {"product_id": prod_id, "size": "L", "quantity": 1, "unit_price": 7499.0},
            {"product_id": prod_id, "size": "XL", "quantity": 1, "unit_price": 7499.0},
        ]

        testcase_2_features = {
            "customer_return_rate": 0.75,
            "total_previous_orders": 24,
            "total_previous_returns": 18,
            "customer_history_days": 350,
            "days_since_last_order": 6,
            "cart_value": 5400.00,
            "cart_item_count": 5,
            "multiple_sizes_same_product": 1,
            "max_sizes_same_product": 3,
            "average_product_return_rate": 0.45,
            "previous_returns_same_category": 5,
            "avg_days_to_return": 3.2,
        }

        state = run_risk_assessment(
            order_id="TEST-ORD-EXHAUSTED",
            customer_id=cust_id,
            cart_items=cart_items,
            initial_features=testcase_2_features,
        )

        self.assertTrue(state["is_low_confidence"])
        self.assertEqual(state["recommended_policy"], "EXCHANGE_FIRST")
        self.assertEqual(state["final_policy"], "EXCHANGE_FIRST")
        self.assertTrue(state["validation_passed"])
        self.assertFalse(state["policy_anomaly"])
        self.assertTrue(state["policy_agent_reasoning"]["used_fallback"])



if __name__ == "__main__":
    unittest.main()
