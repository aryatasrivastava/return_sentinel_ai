"""ReturnSentinel AI LangGraph Risk Assessment Graph (Phase 3A).

Wires the initial assessment node, investigate node, confidence router,
and terminal nodes into an executable LangGraph StateGraph.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from langgraph.graph import END, StateGraph

try:
    from agents.state import AgentState
    from agents.nodes.initial_assessment import initial_assessment_node
    from agents.nodes.investigate import investigate_node
    from agents.router import route_on_confidence, finalize_low_confidence_node
except (ImportError, ModuleNotFoundError):
    from backend.agents.state import AgentState
    from backend.agents.nodes.initial_assessment import initial_assessment_node
    from backend.agents.nodes.investigate import investigate_node
    from backend.agents.router import route_on_confidence, finalize_low_confidence_node


def build_risk_graph() -> StateGraph:
    """Construct and configure the LangGraph StateGraph for Phase 3A."""
    workflow = StateGraph(AgentState)

    # Add pipeline nodes
    workflow.add_node("initial_assessment", initial_assessment_node)
    workflow.add_node("investigate", investigate_node)
    workflow.add_node("finalize_low_confidence", finalize_low_confidence_node)

    # Set starting node
    workflow.set_entry_point("initial_assessment")

    # Routing from initial assessment
    workflow.add_conditional_edges(
        "initial_assessment",
        route_on_confidence,
        {
            "sufficient": END,
            "investigate": "investigate",
            "exhausted": "finalize_low_confidence",
        },
    )

    # Routing from investigate loop (can loop back up to max rounds)
    workflow.add_conditional_edges(
        "investigate",
        route_on_confidence,
        {
            "sufficient": END,
            "investigate": "investigate",
            "exhausted": "finalize_low_confidence",
        },
    )

    # Terminal edge from low confidence finalizer
    workflow.add_edge("finalize_low_confidence", END)

    return workflow


# Compiled graph instance
risk_assessment_graph = build_risk_graph().compile()


def run_risk_assessment(
    order_id: str | int,
    customer_id: str | int,
    cart_items: List[Dict[str, Any]],
    initial_features: Optional[Dict[str, Any]] = None,
) -> AgentState:
    """Execute the full risk assessment and investigation pipeline for an incoming cart.

    Args:
        order_id: Order identifier.
        customer_id: Customer ID or identifier.
        cart_items: List of cart item dicts (`product_id`, `size`, `quantity`, `unit_price`).
        initial_features: Optional pre-configured 12-feature dict (useful for test cases).

    Returns:
        Final AgentState after graph completion.
    """
    initial_state: AgentState = {
        "order_id": str(order_id),
        "customer_id": str(customer_id),
        "cart_items": cart_items,
        "features": initial_features if initial_features is not None else {},
        "risk_probability": None,
        "risk_level": None,
        "model_confidence": None,
        "top_risk_factors": [],
        "investigation_round": 0,
        "is_low_confidence": False,
        "investigation_log": [],
    }

    final_output = risk_assessment_graph.invoke(initial_state)
    return final_output
