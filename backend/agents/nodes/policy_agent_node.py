"""Policy Agent Node for LangGraph pipeline.

Consumes the finalized risk assessment state and cart value to recommend a merchant return policy.
"""

from __future__ import annotations

from typing import Any, Dict

try:
    from agents.state import AgentState
    from policy_agent.policy_agent import recommend_policy
except (ImportError, ModuleNotFoundError):
    from backend.agents.state import AgentState
    from backend.policy_agent.policy_agent import recommend_policy


def policy_agent_node(state: AgentState) -> Dict[str, Any]:
    """Execute the Policy Agent recommendation step.

    Args:
        state: Current AgentState containing risk_level, is_low_confidence,
            top_risk_factors_detailed, features, and investigation_log.

    Returns:
        Dictionary of state updates including recommended_policy, policy_agent_reasoning,
        and appended investigation_log entry.
    """
    risk_assessment = {
        "risk_level": state.get("risk_level"),
        "is_low_confidence": bool(state.get("is_low_confidence", False)),
        "top_risk_factors_detailed": state.get("top_risk_factors_detailed", []),
    }
    cart_value = float(state.get("features", {}).get("cart_value", 0.0))

    result = recommend_policy(risk_assessment=risk_assessment, cart_value=cart_value)

    recommended_policy = result["recommended_policy"]
    reasoning = result["reasoning"]

    current_log = list(state.get("investigation_log", []))
    current_log.append({
        "step_type": "policy_agent",
        "description": f"Policy Agent recommended {recommended_policy}",
        "recommended_policy": recommended_policy,
        "reasoning": reasoning,
    })

    return {
        "recommended_policy": recommended_policy,
        "policy_agent_reasoning": reasoning,
        "investigation_log": current_log,
    }
