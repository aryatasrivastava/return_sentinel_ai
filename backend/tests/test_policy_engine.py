import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy_engine.policy_engine import validate_policy, _fetch_live_policy_config
from policy_agent.policy_agent import recommend_policy
from app.models.policy_config import PolicyConfig
from app.db.session import SessionLocal


class TestPolicyEngine(unittest.TestCase):
    def test_validate_policy_valid_normal_risk_bands(self):
        """Verify that policies within the allowed sets pass validation with anomaly=False."""
        # LOW risk -> STANDARD_RETURN is allowed by default
        res_low = validate_policy("STANDARD_RETURN", risk_level="LOW", is_low_confidence=False)
        self.assertTrue(res_low["validation_passed"])
        self.assertFalse(res_low["anomaly"])
        self.assertEqual(res_low["final_policy"], "STANDARD_RETURN")
        self.assertEqual(res_low["details"]["risk_level"], "LOW")

        # MEDIUM risk -> EXCHANGE_FIRST is allowed by default
        res_med = validate_policy("EXCHANGE_FIRST", risk_level="MEDIUM", is_low_confidence=False)
        self.assertTrue(res_med["validation_passed"])
        self.assertFalse(res_med["anomaly"])
        self.assertEqual(res_med["final_policy"], "EXCHANGE_FIRST")

        # HIGH risk -> STORE_CREDIT is allowed by default
        res_high = validate_policy("STORE_CREDIT", risk_level="HIGH", is_low_confidence=False)
        self.assertTrue(res_high["validation_passed"])
        self.assertFalse(res_high["anomaly"])
        self.assertEqual(res_high["final_policy"], "STORE_CREDIT")

    def test_validate_policy_valid_low_confidence(self):
        """Verify that matching low_confidence_fallback passes validation when is_low_confidence=True."""
        res = validate_policy("EXCHANGE_FIRST", risk_level="HIGH", is_low_confidence=True)
        self.assertTrue(res["validation_passed"])
        self.assertFalse(res["anomaly"])
        self.assertEqual(res["final_policy"], "EXCHANGE_FIRST")
        self.assertEqual(res["details"]["checked_against"], "EXCHANGE_FIRST")

    def test_validate_policy_invalid_normal_risk_band(self):
        """Verify that an unapproved policy for a risk band triggers anomaly and safe fallback."""
        # STANDARD_RETURN is NOT in default high_risk_allowed (["EXCHANGE_FIRST", "STORE_CREDIT", "RESTOCKING_FEE"])
        res = validate_policy("STANDARD_RETURN", risk_level="HIGH", is_low_confidence=False)
        self.assertFalse(res["validation_passed"])
        self.assertTrue(res["anomaly"])
        # Should fall back to first item in high_risk_allowed ('EXCHANGE_FIRST')
        self.assertEqual(res["final_policy"], "EXCHANGE_FIRST")
        self.assertEqual(res["details"]["rejected_policy"], "STANDARD_RETURN")
        self.assertEqual(res["details"]["risk_level"], "HIGH")
        self.assertIn("falling back to a safe default", res["details"]["reason"])

    def test_validate_policy_invalid_low_confidence(self):
        """Verify that a non-fallback policy when is_low_confidence=True triggers anomaly and forces fallback."""
        res = validate_policy("STORE_CREDIT", risk_level="MEDIUM", is_low_confidence=True)
        self.assertFalse(res["validation_passed"])
        self.assertTrue(res["anomaly"])
        self.assertEqual(res["final_policy"], "EXCHANGE_FIRST")
        self.assertEqual(res["details"]["rejected_policy"], "STORE_CREDIT")
        self.assertEqual(res["details"]["checked_against"], "EXCHANGE_FIRST")

    def test_validate_policy_invalid_risk_level_raises(self):
        """Verify that an invalid risk_level string raises ValueError."""
        with self.assertRaises(ValueError):
            validate_policy("STANDARD_RETURN", risk_level="CRITICAL", is_low_confidence=False)

        with self.assertRaises(ValueError):
            validate_policy("STANDARD_RETURN", risk_level=123, is_low_confidence=False)

    def test_validate_policy_real_db_live_config(self):
        """Verify that validate_policy independently queries the live PostgreSQL database."""
        self.assertIsNotNone(SessionLocal, "SessionLocal must be available")

        with SessionLocal() as db:
            db_cfg = db.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
            self.assertIsNotNone(db_cfg, "Seeded policy_config row must exist in DB")
            expected_high_allowed = list(db_cfg.high_risk_allowed)
            expected_fallback = str(db_cfg.low_confidence_fallback)

        # Validate against live high risk allowed set
        res_valid = validate_policy(expected_high_allowed[0], risk_level="HIGH", is_low_confidence=False)
        self.assertTrue(res_valid["validation_passed"])
        self.assertEqual(res_valid["final_policy"], expected_high_allowed[0])

        # Validate against live low confidence fallback
        res_fb = validate_policy(expected_fallback, risk_level="LOW", is_low_confidence=True)
        self.assertTrue(res_fb["validation_passed"])
        self.assertEqual(res_fb["final_policy"], expected_fallback)

    def test_end_to_end_agent_to_engine_pipeline(self):
        """End-to-end test verifying Policy Agent recommendation feeds cleanly into Policy Engine."""
        assessment = {
            "risk_probability": 0.82,
            "risk_level": "HIGH",
            "confidence": 0.80,
            "is_low_confidence": False,
            "top_risk_factors_detailed": [
                {
                    "feature": "customer_return_rate",
                    "label": "Elevated customer historical return rate",
                    "shap_value": 0.42,
                },
                {
                    "feature": "previous_returns_same_category",
                    "label": "Prior history of returning items in this specific category",
                    "shap_value": 0.38,
                },
            ],
        }

        # Policy Agent produces recommendation
        agent_rec = recommend_policy(assessment, cart_value=5400.0)
        self.assertEqual(agent_rec["recommended_policy"], "STORE_CREDIT")

        # Policy Engine validates recommendation
        engine_res = validate_policy(
            recommended_policy=agent_rec["recommended_policy"],
            risk_level=assessment["risk_level"],
            is_low_confidence=assessment["is_low_confidence"],
        )
        self.assertTrue(engine_res["validation_passed"])
        self.assertFalse(engine_res["anomaly"])
        self.assertEqual(engine_res["final_policy"], "STORE_CREDIT")


if __name__ == "__main__":
    unittest.main()
