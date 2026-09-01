import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policy_agent.category_mapping import (
    FEATURE_CATEGORIES,
    CATEGORY_POLICY_WEIGHTS,
    FRICTION_ORDER,
    get_feature_category,
)
from policy_agent.scoring import score_policies, select_policy
from policy_agent.policy_agent import recommend_policy, get_current_policy_config
from app.models.policy_config import PolicyConfig
from app.db.session import SessionLocal


class TestPolicyAgent(unittest.TestCase):
    def test_feature_categories_covers_all_config_features(self):
        """Verify all 12 model features from model_config.json are mapped in FEATURE_CATEGORIES."""
        config_path = (
            Path(__file__).resolve().parent.parent / "ml" / "models" / "model_config.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        expected_features = config["feature_order"]
        self.assertEqual(len(expected_features), 12)
        for feat in expected_features:
            self.assertIn(
                feat,
                FEATURE_CATEGORIES,
                f"Feature '{feat}' from model_config.json is missing in FEATURE_CATEGORIES",
            )

    def test_unmapped_feature_fallback(self):
        """Verify that an unmapped feature defaults to 'NEUTRAL'."""
        self.assertEqual(get_feature_category("non_existent_feature_123"), "NEUTRAL")

    def test_score_policies_strict_allowed_set(self):
        """Verify score_policies never includes policies outside allowed_policies."""
        top_factors = [
            {"feature": "multiple_sizes_same_product", "label": "Bracketing", "shap_value": 0.3},
            {"feature": "customer_return_rate", "label": "Repeat", "shap_value": 0.25},
        ]
        # Only ALLOW STANDARD_RETURN
        scores = score_policies(top_factors, allowed_policies=["STANDARD_RETURN"])
        self.assertEqual(scores, {"STANDARD_RETURN": 0.0})
        self.assertNotIn("EXCHANGE_FIRST", scores)
        self.assertNotIn("STORE_CREDIT", scores)

        # Allow EXCHANGE_FIRST & STORE_CREDIT
        scores2 = score_policies(
            top_factors, allowed_policies=["EXCHANGE_FIRST", "STORE_CREDIT"]
        )
        self.assertEqual(scores2["EXCHANGE_FIRST"], 1.0)
        self.assertEqual(scores2["STORE_CREDIT"], 1.0)
        self.assertNotIn("RESTOCKING_FEE", scores2)

    def test_select_policy_single_winner(self):
        """Verify select_policy picks the single highest-scoring policy without tie-break."""
        scores = {"EXCHANGE_FIRST": 2.0, "STORE_CREDIT": 1.0, "RESTOCKING_FEE": 0.0}
        policy, reasoning = select_policy(
            scores=scores,
            allowed_policies=["EXCHANGE_FIRST", "STORE_CREDIT", "RESTOCKING_FEE"],
            cart_value=4000.0,
            cart_value_median=3000.0,
        )
        self.assertEqual(policy, "EXCHANGE_FIRST")
        self.assertFalse(reasoning["tie_break"]["applied"])

    def test_select_policy_tie_break_high_cart(self):
        """Verify tie-break picks highest friction policy when cart_value > median."""
        scores = {"EXCHANGE_FIRST": 1.0, "RESTOCKING_FEE": 1.0}
        # Friction order: EXCHANGE_FIRST=1, RESTOCKING_FEE=2
        policy, reasoning = select_policy(
            scores=scores,
            allowed_policies=["EXCHANGE_FIRST", "RESTOCKING_FEE"],
            cart_value=4500.0,
            cart_value_median=3000.0,
        )
        self.assertEqual(policy, "RESTOCKING_FEE")
        self.assertTrue(reasoning["tie_break"]["applied"])
        self.assertEqual(reasoning["tie_break"]["selected_by"], "highest_friction")

    def test_select_policy_tie_break_low_cart(self):
        """Verify tie-break picks lowest friction policy when cart_value <= median."""
        scores = {"EXCHANGE_FIRST": 1.0, "RESTOCKING_FEE": 1.0}
        # Friction order: EXCHANGE_FIRST=1, RESTOCKING_FEE=2
        policy, reasoning = select_policy(
            scores=scores,
            allowed_policies=["EXCHANGE_FIRST", "RESTOCKING_FEE"],
            cart_value=2000.0,
            cart_value_median=3000.0,
        )
        self.assertEqual(policy, "EXCHANGE_FIRST")
        self.assertTrue(reasoning["tie_break"]["applied"])
        self.assertEqual(reasoning["tie_break"]["selected_by"], "lowest_friction")

    def test_recommend_policy_low_confidence_short_circuit(self):
        """Verify is_low_confidence = True immediately uses fallback from live DB and skips scoring."""
        assessment = {
            "risk_probability": 0.85,
            "risk_level": "HIGH",
            "confidence": 0.25,
            "is_low_confidence": True,
            "top_risk_factors_detailed": [
                {"feature": "customer_return_rate", "label": "Repeat", "shap_value": 0.5}
            ],
        }
        res = recommend_policy(assessment, cart_value=5000.0)
        self.assertEqual(res["recommended_policy"], "EXCHANGE_FIRST")
        self.assertTrue(res["reasoning"]["used_fallback"])
        self.assertIn("is_low_confidence was True", res["reasoning"]["reason"])

    def test_recommend_policy_high_risk_repeat_behavior(self):
        """Verify repeat behavior features correctly score and select STORE_CREDIT via live DB config."""
        assessment = {
            "risk_probability": 0.78,
            "risk_level": "HIGH",
            "confidence": 0.82,
            "is_low_confidence": False,
            "top_risk_factors_detailed": [
                {"feature": "customer_return_rate", "label": "Elevated customer historical return rate", "shap_value": 0.4},
                {"feature": "previous_returns_same_category", "label": "Prior history of returning items in this specific category", "shap_value": 0.3},
            ],
        }
        res = recommend_policy(assessment, cart_value=4000.0)
        self.assertEqual(res["recommended_policy"], "STORE_CREDIT")
        self.assertFalse(res["reasoning"]["used_fallback"])
        self.assertEqual(res["reasoning"]["scores"]["STORE_CREDIT"], 2.0)
        self.assertEqual(res["reasoning"]["scores"]["RESTOCKING_FEE"], 1.0)

    def test_recommend_policy_real_db_live_config(self):
        """Explicitly verify recommend_policy queries and obeys the live PostgreSQL policy_config row."""
        self.assertIsNotNone(SessionLocal, "SessionLocal must be configured")

        with SessionLocal() as db:
            db_config = db.query(PolicyConfig).filter(PolicyConfig.id == 1).first()
            self.assertIsNotNone(db_config, "Default seeded policy_config row must exist in DB")

            # Verify DB values match the expected seeded defaults
            self.assertEqual(db_config.low_risk_allowed, ["STANDARD_RETURN"])
            self.assertEqual(db_config.medium_risk_allowed, ["STANDARD_RETURN", "EXCHANGE_FIRST", "RESTOCKING_FEE"])
            self.assertEqual(db_config.high_risk_allowed, ["EXCHANGE_FIRST", "STORE_CREDIT", "RESTOCKING_FEE"])
            self.assertEqual(db_config.low_confidence_fallback, "EXCHANGE_FIRST")

        # Test LOW risk order without passing policy_config (exercises live DB query)
        low_risk_assessment = {
            "risk_probability": 0.10,
            "risk_level": "LOW",
            "confidence": 0.88,
            "is_low_confidence": False,
            "top_risk_factors_detailed": [
                {"feature": "customer_return_rate", "label": "Low customer historical return rate", "shap_value": -0.3}
            ],
        }
        res = recommend_policy(low_risk_assessment, cart_value=1500.0)
        self.assertEqual(res["recommended_policy"], "STANDARD_RETURN")
        self.assertEqual(res["reasoning"]["allowed_policies"], ["STANDARD_RETURN"])
        self.assertEqual(res["reasoning"]["scores"], {"STANDARD_RETURN": 0.0})


if __name__ == "__main__":
    unittest.main()
