"""ReturnSentinel AI - Confidence Router & Investigation Loop Demo (Phase 3A Extended).

Demonstrates the LangGraph risk assessment graph across 7 comprehensive scenarios:
1. Scenario 1: Customer A (Low Risk - Ananya Sharma) - Resolves at Round 0 with sufficient confidence.
2. Scenario 2: Customer B (High Risk - Rohan Verma) - Multi-size bracketing cart triggering live data investigation.
3. Scenario 3: Customer C (Uncertain/New Customer - Priya Nair) - Thin history triggering investigation loop.
4. Scenario 4: Customer D (Borderline Low / Mixed Signals - Vikram Malhotra) - Substantial history, moderate return rate.
5. Scenario 5: Customer E (High Risk, Strong Signal - Sameer Kapoor) - Extreme return rate (85.7%), bracketing cart.
6. Scenario 6: Customer F (Clean Repeat Customer - Meera Sen) - 35 orders, 5.7% return rate; resolves in Round 1.
7. Scenario 7: Test Case 2 Reproduction (Elevated Risk, Initial Low Confidence) - Demonstrates confidence router
   distrusting a high-risk-but-low-confidence prediction (probability: 0.7391, confidence: 0.4781 < 0.60).
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from agents.graph import run_risk_assessment
from agents.router import CONFIDENCE_THRESHOLD, MAX_INVESTIGATION_ROUNDS
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.product import Product


def _print_scenario_header(scenario_num: int, title: str, description: str) -> None:
    print("\n" + "=" * 90)
    print(f"  SCENARIO {scenario_num}: {title.upper()}")
    print("=" * 90)
    print(f"Context: {description}\n")


def _print_scenario_results(state: Dict[str, Any]) -> None:
    prob = state.get("risk_probability", 0.0)
    conf = state.get("model_confidence", 0.0)
    print("--- [FINAL RISK ASSESSMENT STATE] ---")
    print(f"  * Order ID              : {state.get('order_id')}")
    print(f"  * Customer ID           : {state.get('customer_id')}")
    print(f"  * Risk Probability      : {prob:.4f} ({prob*100:.1f}%)")
    print(f"  * Risk Level            : {state.get('risk_level')}")
    print(f"  * Model Confidence      : {conf:.4f} (Threshold: {CONFIDENCE_THRESHOLD})")
    print(f"  * Is Low Confidence Flag: {state.get('is_low_confidence')}")
    print(f"  * Investigation Rounds  : {state.get('investigation_round')} (Max: {MAX_INVESTIGATION_ROUNDS})")
    print(f"  * Top Risk Factors      :")
    for idx, factor in enumerate(state.get("top_risk_factors", []), 1):
        print(f"      {idx}. {factor}")
    print(f"  * Recommended Policy    : {state.get('recommended_policy')}")
    print(f"  * Final Validated Policy: {state.get('final_policy')}")
    print(f"  * Validation Passed     : {state.get('validation_passed')}")
    print(f"  * Policy Anomaly Flag   : {state.get('policy_anomaly')}")

    print("\n--- [AGENT DECISION TRACE / INVESTIGATION LOG] ---")
    log = state.get("investigation_log", [])
    for idx, step in enumerate(log, 1):
        step_type = step.get("step_type", "unknown")
        round_num = step.get("round", 0)
        source = step.get("source", "unknown")
        desc = step.get("description", "")
        step_conf = step.get("model_confidence")
        step_prob = step.get("risk_probability")
        lvl = step.get("risk_level")

        conf_str = f" | Conf: {step_conf:.4f} | Risk: {lvl} ({step_prob:.4f})" if step_conf is not None and step_prob is not None else ""
        print(f"  [Step {idx}] ({step_type.upper()} | Round {round_num} | Source: {source}){conf_str}")
        print(f"           Description: {desc}")

        if "feature_diff" in step and step["feature_diff"]:
            print("           Feature Diff vs. Prior Round:")
            for feat_name, diff_vals in step["feature_diff"].items():
                print(f"             - {feat_name}: {diff_vals.get('previous_value')} -> {diff_vals.get('refreshed_value')}")

    print("-" * 90)


def print_summary_table(results: List[Tuple[str, str, Dict[str, Any]]]) -> None:
    print("\n" + "#" * 125)
    print("   RETURNSENTINEL AI: 7-SCENARIO END-TO-END PIPELINE VALIDATION SUMMARY TABLE")
    print("#" * 125)
    header = f"{'Scenario':<12} | {'Profile Description':<24} | {'Final Risk':<10} | {'LowConf':<7} | {'Recommended Policy':<18} | {'Final Policy':<18} | {'Valid':<5} | {'Anomaly'}"
    print(header)
    print("-" * 125)

    for sc_id, desc, state in results:
        lvl = state.get("risk_level", "N/A")
        low_c = state.get("is_low_confidence", False)
        rec_p = state.get("recommended_policy", "N/A")
        fin_p = state.get("final_policy", "N/A")
        val_pass = state.get("validation_passed", False)
        anom = state.get("policy_anomaly", False)

        print(f"{sc_id:<12} | {desc:<24} | {lvl:<10} | {str(low_c):<7} | {str(rec_p):<18} | {str(fin_p):<18} | {str(val_pass):<5} | {str(anom)}")

    print("=" * 125)



def run_all_scenarios() -> List[Tuple[str, str, Dict[str, Any]]]:
    """Execute and display all 7 assessment scenarios."""
    print("=" * 90)
    print("   RETURNSENTINEL AI - CONFIDENCE ROUTER & INVESTIGATION PIPELINE (PHASE 3A)")
    print(f"   Config: CONFIDENCE_THRESHOLD = {CONFIDENCE_THRESHOLD}, MAX_INVESTIGATION_ROUNDS = {MAX_INVESTIGATION_ROUNDS}")
    print("=" * 90)

    db = SessionLocal()
    try:
        custs = {c.email: c.id for c in db.query(Customer).all()}
        prods = {p.sku: p.id for p in db.query(Product).all()}
    finally:
        db.close()

    results: List[Tuple[str, str, Dict[str, Any]]] = []

    # =========================================================================
    # SCENARIO 1: Customer A (Low Risk - Ananya Sharma)
    # =========================================================================
    _print_scenario_header(
        1,
        "Customer A (Low Risk - Ananya Sharma)",
        "Established customer (10 orders, 1 return, 10% rate). Single shirt in cart. "
        "Expected: High confidence at Round 0, immediately sufficient, no investigation needed."
    )
    cart_a = [{"product_id": prods["SKU-SHT-006"], "size": "M", "quantity": 1, "unit_price": 1999.00}]
    state_a = run_risk_assessment("ORD-DEMO-CUST-A", custs["ananya.sharma@example.com"], cart_a)
    _print_scenario_results(state_a)
    results.append(("Scenario 1", "Customer A (Low Risk)", state_a))

    # =========================================================================
    # SCENARIO 2: Customer B (High Risk - Rohan Verma)
    # =========================================================================
    _print_scenario_header(
        2,
        "Customer B (High Risk - Rohan Verma)",
        "Serial returner (20 orders, 15 returns, 75% rate). Cart has multiple sizes of Anarkali suit (M & L). "
        "Expected: Triggers live investigation, identifies rapid turnaround & high category returns."
    )
    cart_b = [
        {"product_id": prods["SKU-ANK-001"], "size": "M", "quantity": 1, "unit_price": 7499.00},
        {"product_id": prods["SKU-ANK-001"], "size": "L", "quantity": 1, "unit_price": 7499.00},
    ]
    state_b = run_risk_assessment("ORD-DEMO-CUST-B", custs["rohan.verma@example.com"], cart_b)
    _print_scenario_results(state_b)
    results.append(("Scenario 2", "Customer B (High Risk)", state_b))

    # =========================================================================
    # SCENARIO 3: Customer C (Uncertain / New Customer - Priya Nair)
    # =========================================================================
    _print_scenario_header(
        3,
        "Customer C (Uncertain / New Customer - Priya Nair)",
        "New customer (1 order, 0 returns, thin tenure). High-value Saree in cart. "
        "Expected: Low confidence due to thin evidence, triggering the live investigation loop."
    )
    cart_c = [{"product_id": prods["SKU-SAR-003"], "size": None, "quantity": 1, "unit_price": 18500.00}]
    state_c = run_risk_assessment("ORD-DEMO-CUST-C", custs["priya.nair@example.com"], cart_c)
    _print_scenario_results(state_c)
    results.append(("Scenario 3", "Customer C (Uncertain/New)", state_c))

    # =========================================================================
    # SCENARIO 4: Customer D (Borderline Low / Mixed Signals - Vikram Malhotra)
    # =========================================================================
    _print_scenario_header(
        4,
        "Customer D (Borderline Low / Mixed Signals - Vikram Malhotra)",
        "Moderate tenure (180 days, 15 orders, 5 returns, 33.3% rate). Single Kurta set in cart. "
        "Expected: Moderate risk profile sits near low-risk boundary."
    )
    cart_d = [{"product_id": prods["SKU-KUR-004"], "size": "L", "quantity": 1, "unit_price": 3499.00}]
    state_d = run_risk_assessment("ORD-DEMO-CUST-D", custs["vikram.malhotra@example.com"], cart_d)
    _print_scenario_results(state_d)
    results.append(("Scenario 4", "Customer D (Borderline Low)", state_d))

    # =========================================================================
    # SCENARIO 5: Customer E (High Risk, Strong Signal - Sameer Kapoor)
    # =========================================================================
    _print_scenario_header(
        5,
        "Customer E (High Risk, Strong Signal - Sameer Kapoor)",
        "Aggressive return history (28 orders, 24 returns, 85.7% rate, 2-day turnaround). Bracketing cart (Sherwani XL & XXL). "
        "Expected: High-risk detection with live table audit confirming wardrobing signature."
    )
    cart_e = [
        {"product_id": prods["SKU-SHR-002"], "size": "XL", "quantity": 1, "unit_price": 12999.00},
        {"product_id": prods["SKU-SHR-002"], "size": "XXL", "quantity": 1, "unit_price": 12999.00},
    ]
    state_e = run_risk_assessment("ORD-DEMO-CUST-E", custs["sameer.kapoor@example.com"], cart_e)
    _print_scenario_results(state_e)
    results.append(("Scenario 5", "Customer E (Strong High Risk)", state_e))

    # =========================================================================
    # SCENARIO 6: Customer F (Clean Repeat Customer - Meera Sen)
    # =========================================================================
    _print_scenario_header(
        6,
        "Customer F (Clean Repeat Customer - Meera Sen)",
        "Long tenure (550 days, 35 orders, 2 returns, 5.7% rate). Single Pashmina Shawl in cart. "
        "Expected: Live investigation refines confidence from 0.5367 to 0.6199 (>= 0.60) and resolves at Round 1."
    )
    cart_f = [{"product_id": prods["SKU-SHW-010"], "size": None, "quantity": 1, "unit_price": 8999.00}]
    state_f = run_risk_assessment("ORD-DEMO-CUST-F", custs["meera.sen@example.com"], cart_f)
    _print_scenario_results(state_f)
    results.append(("Scenario 6", "Customer F (Clean Repeat)", state_f))

    # =========================================================================
    # SCENARIO 7: Test Case 2 Reproduction (Elevated Risk, Low Model Confidence)
    # =========================================================================
    _print_scenario_header(
        7,
        "Test Case 2 Reproduction (Elevated Risk, Low Model Confidence)",
        "Reproduction of Phase 2B Test Case 2 (risk_probability=0.7391 -> HIGH risk, but "
        "model_confidence=0.4781 < 0.60). Router actively distrusts high-risk prediction and triggers live investigation."
    )
    test_case_2_features = {
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
    cart_test_2 = [
        {"product_id": prods["SKU-ANK-001"], "size": "S", "quantity": 1, "unit_price": 1800.00},
        {"product_id": prods["SKU-ANK-001"], "size": "M", "quantity": 2, "unit_price": 1800.00},
        {"product_id": prods["SKU-ANK-001"], "size": "L", "quantity": 2, "unit_price": 1800.00},
    ]
    state_tc2 = run_risk_assessment(
        order_id="ORD-DEMO-TESTCASE-2",
        customer_id=custs["rohan.verma@example.com"],
        cart_items=cart_test_2,
        initial_features=test_case_2_features,
    )
    _print_scenario_results(state_tc2)
    results.append(("Scenario 7", "Test Case 2 Repro", state_tc2))

    print_summary_table(results)
    return results


if __name__ == "__main__":
    run_all_scenarios()
