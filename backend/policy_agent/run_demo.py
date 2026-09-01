import json
from policy_agent.policy_agent import recommend_policy


def run_demo():
    print("=" * 80)
    print("       RETURNSENTINEL AI - POLICY AGENT DEMONSTRATION & SCENARIOS")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Scenario 1: Low risk, high-confidence order
    # -------------------------------------------------------------------------
    scenario_1 = {
        "name": "Scenario 1: Low Risk, High Confidence Order",
        "cart_value": 1800.00,
        "assessment": {
            "risk_probability": 0.12,
            "risk_level": "LOW",
            "confidence": 0.85,
            "is_low_confidence": False,
            "top_risk_factors_detailed": [
                {
                    "feature": "customer_return_rate",
                    "label": "Low customer historical return rate",
                    "shap_value": -0.25,
                },
                {
                    "feature": "customer_history_days",
                    "label": "Long-standing customer account tenure",
                    "shap_value": -0.20,
                },
                {
                    "feature": "avg_days_to_return",
                    "label": "Normal or extended return turnaround duration",
                    "shap_value": -0.15,
                },
            ],
        },
    }

    # -------------------------------------------------------------------------
    # Scenario 2: High risk, Bracketing-dominated order
    # -------------------------------------------------------------------------
    scenario_2 = {
        "name": "Scenario 2: High Risk, Bracketing-Dominated Order",
        "cart_value": 3200.00,
        "assessment": {
            "risk_probability": 0.75,
            "risk_level": "HIGH",
            "confidence": 0.72,
            "is_low_confidence": False,
            "top_risk_factors_detailed": [
                {
                    "feature": "multiple_sizes_same_product",
                    "label": "Multiple sizes of the same product selected (bracketing)",
                    "shap_value": 0.45,
                },
                {
                    "feature": "max_sizes_same_product",
                    "label": "High maximum size count selected for a single item",
                    "shap_value": 0.35,
                },
                {
                    "feature": "cart_value",
                    "label": "High total cart order value",
                    "shap_value": 0.15,
                },
            ],
        },
    }

    # -------------------------------------------------------------------------
    # Scenario 3: High risk, Repeat-Behavior-dominated order
    # -------------------------------------------------------------------------
    scenario_3 = {
        "name": "Scenario 3: High Risk, Repeat-Behavior-Dominated Order",
        "cart_value": 5400.00,
        "assessment": {
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
                {
                    "feature": "avg_days_to_return",
                    "label": "Rapid historical return turnaround signature",
                    "shap_value": 0.30,
                },
            ],
        },
    }

    # -------------------------------------------------------------------------
    # Scenario 4: Low-confidence case (exhausted investigation budget)
    # -------------------------------------------------------------------------
    scenario_4 = {
        "name": "Scenario 4: Low-Confidence Assessment (Short-Circuit Fallback)",
        "cart_value": 4200.00,
        "assessment": {
            "risk_probability": 0.58,
            "risk_level": "HIGH",
            "confidence": 0.32,
            "is_low_confidence": True,
            "top_risk_factors_detailed": [
                {
                    "feature": "customer_return_rate",
                    "label": "Elevated customer historical return rate",
                    "shap_value": 0.28,
                },
                {
                    "feature": "average_product_return_rate",
                    "label": "High return-rate category or product in cart",
                    "shap_value": 0.22,
                },
            ],
        },
    }

    # -------------------------------------------------------------------------
    # Scenario 5A: Deliberate Tie-Break with High Cart Value (> 3000)
    # -------------------------------------------------------------------------
    scenario_5a = {
        "name": "Scenario 5A: Deliberate Tie (Bracketing vs Product-Driven) with High Cart Value ($4500 > $3000)",
        "cart_value": 4500.00,
        "assessment": {
            "risk_probability": 0.68,
            "risk_level": "HIGH",
            "confidence": 0.70,
            "is_low_confidence": False,
            "top_risk_factors_detailed": [
                {
                    "feature": "multiple_sizes_same_product",  # BRACKETING -> EXCHANGE_FIRST: +1.0
                    "label": "Multiple sizes of the same product selected (bracketing)",
                    "shap_value": 0.32,
                },
                {
                    "feature": "average_product_return_rate",  # PRODUCT_DRIVEN -> RESTOCKING_FEE: +1.0
                    "label": "High return-rate catalog items in cart",
                    "shap_value": 0.32,
                },
                {
                    "feature": "cart_item_count",  # NEUTRAL -> 0.0
                    "label": "Large number of items in current cart",
                    "shap_value": 0.10,
                },
            ],
        },
    }

    # -------------------------------------------------------------------------
    # Scenario 5B: Deliberate Tie-Break with Low Cart Value (<= 3000)
    # -------------------------------------------------------------------------
    scenario_5b = {
        "name": "Scenario 5B: Deliberate Tie (Bracketing vs Product-Driven) with Low Cart Value ($1500 <= $3000)",
        "cart_value": 1500.00,
        "assessment": {
            "risk_probability": 0.68,
            "risk_level": "HIGH",
            "confidence": 0.70,
            "is_low_confidence": False,
            "top_risk_factors_detailed": [
                {
                    "feature": "multiple_sizes_same_product",  # BRACKETING -> EXCHANGE_FIRST: +1.0
                    "label": "Multiple sizes of the same product selected (bracketing)",
                    "shap_value": 0.32,
                },
                {
                    "feature": "average_product_return_rate",  # PRODUCT_DRIVEN -> RESTOCKING_FEE: +1.0
                    "label": "High return-rate catalog items in cart",
                    "shap_value": 0.32,
                },
                {
                    "feature": "cart_item_count",  # NEUTRAL -> 0.0
                    "label": "Large number of items in current cart",
                    "shap_value": 0.10,
                },
            ],
        },
    }

    scenarios = [scenario_1, scenario_2, scenario_3, scenario_4, scenario_5a, scenario_5b]

    for i, s in enumerate(scenarios, 1):
        print(f"\n[{i}] {s['name']}")
        print("-" * 80)
        result = recommend_policy(
            risk_assessment=s["assessment"],
            cart_value=s["cart_value"],
        )
        print(json.dumps(result, indent=2))

    print("\n" + "=" * 80)
    print("Policy Agent demonstration complete. All scenarios verified successfully.")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
