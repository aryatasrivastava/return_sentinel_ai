import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.risk_prediction import RiskPrediction
from app.models.policy_decision import PolicyDecision
from audit.audit_generator import (
    FALLBACK_EXPLANATION,
    build_audit_prompt,
    generate_audit_explanation,
    generate_and_persist_audit,
)


class TestAuditGenerator(unittest.TestCase):
    def test_build_audit_prompt_factual_structure(self):
        """Verify build_audit_prompt includes all facts and strict factual constraints."""
        decision_data = {
            "risk_level": "HIGH",
            "risk_probability": 0.85,
            "model_confidence": 0.70,
            "is_low_confidence": False,
            "top_risk_factors": [
                "High customer return rate (75.0%)",
                "Multiple sizes of same product in cart (3 sizes)",
            ],
            "recommended_policy": "STORE_CREDIT",
            "final_policy": "STORE_CREDIT",
            "policy_agent_reasoning": {
                "category_scores": {"WARDROBING": 0.3, "BRACKETING": 0.8},
                "chosen_category": "BRACKETING",
            },
            "policy_engine_details": {
                "validation_passed": True,
            },
        }

        prompt = build_audit_prompt(decision_data)

        self.assertIn("Risk Level: HIGH", prompt)
        self.assertIn("Risk Probability: 85.00%", prompt)
        self.assertIn("Model Confidence: 0.700", prompt)
        self.assertIn("Is Low Confidence Fallback: False", prompt)
        self.assertIn("High customer return rate (75.0%)", prompt)
        self.assertIn("Multiple sizes of same product in cart (3 sizes)", prompt)
        self.assertIn("Policy Agent Recommended Policy: STORE_CREDIT", prompt)
        self.assertIn("Final Validated Policy: STORE_CREDIT", prompt)
        self.assertIn("Explain the decision using ONLY the facts provided above", prompt)
        self.assertIn("Do NOT suggest the customer did anything wrong or use accusatory language", prompt)
        self.assertIn("exactly 2 to 4 sentences", prompt)

    def test_build_audit_prompt_low_confidence_fallback_instruction(self):
        """Verify build_audit_prompt specifically instructs model when is_low_confidence is True."""
        decision_data = {
            "risk_level": "MEDIUM",
            "risk_probability": 0.58,
            "model_confidence": 0.16,
            "is_low_confidence": True,
            "top_risk_factors": ["Moderate customer return rate"],
            "recommended_policy": "EXCHANGE_FIRST",
            "final_policy": "EXCHANGE_FIRST",
            "policy_agent_reasoning": {"used_fallback": True},
            "policy_engine_details": {"validation_passed": True},
        }

        prompt = build_audit_prompt(decision_data)

        self.assertIn("Is Low Confidence Fallback: True", prompt)
        self.assertIn("fallback policy due to insufficient confidence/evidence", prompt)

    def test_generate_audit_explanation_missing_api_key(self):
        """Verify fallback explanation returned gracefully when API key is missing."""
        decision_data = {"risk_level": "LOW", "final_policy": "STANDARD_RETURN"}
        with patch("audit.audit_generator.settings.GEMINI_API_KEY", None), \
             patch.dict(os.environ, {}, clear=True):
            explanation = generate_audit_explanation(decision_data)
            self.assertEqual(explanation, FALLBACK_EXPLANATION)

    def test_generate_audit_explanation_exception_fallback(self):
        """Verify exceptions during LLM call are caught and fallback string returned."""
        decision_data = {"risk_level": "HIGH", "final_policy": "STORE_CREDIT"}
        with patch("audit.audit_generator.settings.GEMINI_API_KEY", "dummy-api-key"), \
             patch("google.generativeai.GenerativeModel.generate_content", side_effect=RuntimeError("API Network Timeout")):
            explanation = generate_audit_explanation(decision_data)
            self.assertEqual(explanation, FALLBACK_EXPLANATION)

    def test_generate_audit_explanation_success_mock(self):
        """Verify successful LLM response is cleanly extracted and returned."""
        mock_response = MagicMock()
        mock_response.text = (
            "The order was flagged as high risk due to multiple sizes of the same apparel item in the cart. "
            "Because confidence was high and bracketing behavior was strongly indicated, Store Credit was applied. "
            "This policy mitigates sizing speculation risk while allowing the merchant to retain revenue."
        )

        decision_data = {
            "risk_level": "HIGH",
            "risk_probability": 0.88,
            "model_confidence": 0.76,
            "is_low_confidence": False,
            "top_risk_factors": ["Multiple sizes of same product in cart"],
            "recommended_policy": "STORE_CREDIT",
            "final_policy": "STORE_CREDIT",
        }

        with patch("audit.audit_generator.settings.GEMINI_API_KEY", "dummy-key"), \
             patch("google.generativeai.GenerativeModel.generate_content", return_value=mock_response):
            explanation = generate_audit_explanation(decision_data)
            self.assertEqual(explanation, mock_response.text.strip())

    def test_generate_and_persist_audit_db_update(self):
        """Verify background task updates policy_decisions table in database."""
        with SessionLocal() as db:
            cust = db.query(Customer).first()
            self.assertIsNotNone(cust)
            order = Order(customer_id=cust.id, order_value=Decimal("1500.00"), status="pending")
            db.add(order)
            db.commit()
            db.refresh(order)

            decision = PolicyDecision(order_id=order.id, policy_type="EXCHANGE_FIRST")
            db.add(decision)
            db.commit()

            test_order_id = order.id

        try:
            expected_explanation = "This is a verified test audit explanation."
            with patch("audit.audit_generator.generate_audit_explanation", return_value=expected_explanation):
                generate_and_persist_audit(
                    order_id=test_order_id,
                    decision_data={"risk_level": "MEDIUM", "final_policy": "EXCHANGE_FIRST"},
                )

            with SessionLocal() as db:
                updated_decision = db.query(PolicyDecision).filter(PolicyDecision.order_id == test_order_id).first()
                self.assertIsNotNone(updated_decision)
                self.assertEqual(updated_decision.audit_explanation, expected_explanation)
                self.assertIsNotNone(updated_decision.audit_generated_at)
        finally:
            with SessionLocal() as db:
                db.query(PolicyDecision).filter(PolicyDecision.order_id == test_order_id).delete()
                db.query(Order).filter(Order.id == test_order_id).delete()
                db.commit()


class TestAssessOrderAPIWithAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_assess_order_triggers_audit_in_background(self):
        """Verify assess-order returns instantly and executes audit generation in background."""
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

        mock_explanation = "The order demonstrated minimal risk indicators with strong positive customer history. Standard return was selected as the optimal frictionless policy."

        with patch("audit.audit_generator.generate_audit_explanation", return_value=mock_explanation):
            response = self.client.post("/api/assess-order", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            order_id = data["order_id"]

            self.assertIn("order_id", data)
            self.assertEqual(data["risk_level"], "LOW")
            self.assertGreater(data["latency_ms"], 0)

            # TestClient executes FastAPI BackgroundTasks before returning
            with SessionLocal() as db:
                decision = db.query(PolicyDecision).filter(PolicyDecision.order_id == order_id).first()
                self.assertIsNotNone(decision)
                self.assertEqual(decision.audit_explanation, mock_explanation)
                self.assertIsNotNone(decision.audit_generated_at)


if __name__ == "__main__":
    unittest.main()
