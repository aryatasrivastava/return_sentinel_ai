"""Confidence Router and Conditional Routing Logic (Phase 3A).

This module governs the decision logic after each risk prediction round:
- If `model_confidence >= CONFIDENCE_THRESHOLD` (0.60): routes to graph completion (`sufficient`).
- If `model_confidence < CONFIDENCE_THRESHOLD` and `investigation_round < MAX_INVESTIGATION_ROUNDS` (2):
  triggers deeper live re-investigation (`investigate`).
- If investigation budget is exhausted (reached `MAX_INVESTIGATION_ROUNDS` with confidence still < 0.60):
  routes to `finalize_low_confidence` to set `is_low_confidence = True` and finish cleanly.
"""

from __future__ import annotations

from typing import Any, Dict

try:
    from agents.state import AgentState
except (ImportError, ModuleNotFoundError):
    from backend.agents.state import AgentState

# Named constants specified by system requirements
CONFIDENCE_THRESHOLD: float = 0.40
MAX_INVESTIGATION_ROUNDS: int = 2



def route_on_confidence(state: AgentState | Dict[str, Any]) -> str:
    """Evaluate current state confidence against threshold and investigation round budget.

    Args:
        state: Current AgentState.

    Returns:
        One of:
        - "sufficient": Prediction confidence is high enough to trust (>= 0.40).
        - "investigate": Prediction confidence is low (< 0.40) and investigation rounds remain (< 2),
          or mandatory live verification is triggered for Round 0 HIGH-risk orders.
        - "exhausted": Investigation budget reached (2 rounds) without achieving threshold confidence.
    """
    model_confidence = state.get("model_confidence")
    if model_confidence is None:
        model_confidence = 0.0

    investigation_round = state.get("investigation_round", 0)
    risk_level = state.get("risk_level")

    # Safeguard: a HIGH-risk order must be checked against live data at least
    # once before being accepted, even if its round-0 (cached-data) confidence
    # already clears the threshold. This prevents finalizing the highest-stakes
    # decisions on cached data alone. This rule applies only when transitioning
    # out of round 0 — once at least one investigation round has run, normal
    # confidence-threshold logic governs (see below), so this cannot cause an
    # extra loop beyond the existing MAX_INVESTIGATION_ROUNDS cap.
    if investigation_round == 0 and risk_level == "HIGH" and model_confidence >= CONFIDENCE_THRESHOLD:
        return "investigate"

    if model_confidence >= CONFIDENCE_THRESHOLD:
        return "sufficient"
    elif investigation_round < MAX_INVESTIGATION_ROUNDS:
        return "investigate"
    else:
        return "exhausted"



def finalize_low_confidence_node(state: AgentState) -> Dict[str, Any]:
    """Terminal node invoked when investigation budget is exhausted with low confidence.

    Explicitly flags `is_low_confidence = True` and appends a final log entry.

    Args:
        state: Current AgentState.

    Returns:
        Dictionary of state updates.
    """
    current_round = state.get("investigation_round", 0)
    current_log = list(state.get("investigation_log", []))

    log_entry: Dict[str, Any] = {
        "step_type": "router_exhausted",
        "round": current_round,
        "source": "confidence_router",
        "description": (
            f"Investigation round budget ({MAX_INVESTIGATION_ROUNDS} rounds) exhausted. "
            f"Proceeding with low confidence flag (is_low_confidence=True)."
        ),
        "is_low_confidence": True,
        "final_confidence": state.get("model_confidence"),
        "final_risk_level": state.get("risk_level"),
        "final_risk_probability": state.get("risk_probability"),
    }
    current_log.append(log_entry)

    return {
        "is_low_confidence": True,
        "investigation_log": current_log,
    }
