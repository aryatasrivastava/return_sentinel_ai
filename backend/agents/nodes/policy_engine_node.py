"""Policy Engine Node for LangGraph pipeline.

Independently validates the Policy Agent recommendation against live merchant config.
"""

from __future__ import annotations

from typing import Any, Dict

try:
    from agents.state import AgentState
    from policy_engine.policy_engine import validate_policy
except (ImportError, ModuleNotFoundError):
    from backend.agents.state import AgentState
    from backend.policy_engine.policy_engine import validate_policy


def policy_engine_node(state: AgentState) -> Dict[str, Any]:
    """Execute the Policy Engine validation step.

    Args:
        state: Current AgentState containing recommended_policy, risk_level,
            is_low_confidence, and investigation_log.

    Returns:
        Dictionary of state updates including final_policy, validation_passed,
        policy_anomaly, policy_engine_details, and appended investigation_log entry.
    """
    recommended_policy = str(state.get("recommended_policy", ""))
    risk_level = str(state.get("risk_level", "MEDIUM"))
    is_low_confidence = bool(state.get("is_low_confidence", False))

    result = validate_policy(
        recommended_policy=recommended_policy,
        risk_level=risk_level,
        is_low_confidence=is_low_confidence,
    )

    final_policy = result["final_policy"]
    validation_passed = result["validation_passed"]
    policy_anomaly = result["anomaly"]
    details = result["details"]

    current_log = list(state.get("investigation_log", []))
    current_log.append({
        "step_type": "policy_engine",
        "description": f"Policy Engine validated -> final_policy={final_policy} (anomaly={policy_anomaly})",
        "final_policy": final_policy,
        "validation_passed": validation_passed,
        "anomaly": policy_anomaly,
        "details": details,
    })

    return {
        "final_policy": final_policy,
        "validation_passed": validation_passed,
        "policy_anomaly": policy_anomaly,
        "policy_engine_details": details,
        "investigation_log": current_log,
    }
