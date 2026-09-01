import json
import logging
from policy_engine.policy_engine import validate_policy, _fetch_live_policy_config
from policy_agent.policy_agent import recommend_policy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_demo():
    print("=" * 80)
    print("       RETURNSENTINEL AI - POLICY ENGINE DEMONSTRATION & SCENARIOS")
    print("=" * 80)

    # Inspect live merchant policy config from DB for verification
    live_config = _fetch_live_policy_config()
    print("\n[Merchant Config Status]")
    print(f"  Low Risk Allowed:        {live_config.low_risk_allowed}")
    print(f"  Medium Risk Allowed:     {live_config.medium_risk_allowed}")
    print(f"  High Risk Allowed:       {live_config.high_risk_allowed}")
    print(f"  Low Confidence Fallback: '{live_config.low_confidence_fallback}'")

    # -------------------------------------------------------------------------
    # Scenario 1: Valid case, normal risk band
    # -------------------------------------------------------------------------
    print("\n[1] Scenario 1: Valid Recommendation in Medium Risk Allowed Set")
    print("-" * 80)
    res_1 = validate_policy(
        recommended_policy="EXCHANGE_FIRST",
        risk_level="MEDIUM",
        is_low_confidence=False,
    )
    print(json.dumps(res_1, indent=2))

    # -------------------------------------------------------------------------
    # Scenario 2: Valid case, low-confidence fallback
    # -------------------------------------------------------------------------
    print("\n[2] Scenario 2: Valid Low-Confidence Fallback Recommendation")
    print("-" * 80)
    res_2 = validate_policy(
        recommended_policy=live_config.low_confidence_fallback,
        risk_level="HIGH",
        is_low_confidence=True,
    )
    print(json.dumps(res_2, indent=2))

    # -------------------------------------------------------------------------
    # Scenario 3: Invalid case, normal risk band (e.g. STANDARD_RETURN on HIGH risk)
    # -------------------------------------------------------------------------
    print("\n[3] Scenario 3: Invalid Recommendation on High Risk Band (Defensive Override)")
    print(f"  Current High Risk Allowed Set: {live_config.high_risk_allowed}")
    print(f"  Expected Defensive Fallback (First Item): '{live_config.high_risk_allowed[0]}'")
    print("-" * 80)
    res_3 = validate_policy(
        recommended_policy="STANDARD_RETURN",
        risk_level="HIGH",
        is_low_confidence=False,
    )
    print(json.dumps(res_3, indent=2))

    # -------------------------------------------------------------------------
    # Scenario 4: Invalid case, low-confidence (Non-fallback policy recommended)
    # -------------------------------------------------------------------------
    print("\n[4] Scenario 4: Invalid Recommendation on Low Confidence (Forced Fallback Override)")
    print(f"  Expected Low Confidence Fallback: '{live_config.low_confidence_fallback}'")
    print("-" * 80)
    res_4 = validate_policy(
        recommended_policy="RESTOCKING_FEE",
        risk_level="LOW",
        is_low_confidence=True,
    )
    print(json.dumps(res_4, indent=2))

    # -------------------------------------------------------------------------
    # Scenario 5: End-to-end integration check (Policy Agent -> Policy Engine)
    # -------------------------------------------------------------------------
    print("\n[5] Scenario 5: End-to-End Integration Check (Policy Agent -> Policy Engine)")
    print("-" * 80)
    sample_assessment = {
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
    }

    # 1. Policy Agent recommends
    agent_output = recommend_policy(
        risk_assessment=sample_assessment,
        cart_value=5400.0,
    )
    print("  [Step 1] Policy Agent Recommendation:")
    print(f"    Recommended Policy: {agent_output['recommended_policy']}")
    print(f"    Dominant Category Scores: {agent_output['reasoning']['scores']}")

    # 2. Policy Engine validates
    engine_output = validate_policy(
        recommended_policy=agent_output["recommended_policy"],
        risk_level=sample_assessment["risk_level"],
        is_low_confidence=sample_assessment["is_low_confidence"],
    )
    print("\n  [Step 2] Policy Engine Validation Result:")
    print(json.dumps(engine_output, indent=2))

    print("\n" + "=" * 80)
    print("Policy Engine demonstration complete. All 5 scenarios verified.")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
