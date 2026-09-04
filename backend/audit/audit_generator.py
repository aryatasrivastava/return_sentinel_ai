"""ReturnSentinel AI Audit Explanation Generator.

Provides asynchronous, LLM-generated plain-English explanations of risk predictions
and policy decisions using Google Gemini.
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import google.generativeai as genai

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.policy_decision import PolicyDecision
from app.models.risk_prediction import RiskPrediction

logger = logging.getLogger(__name__)

FALLBACK_EXPLANATION = (
    "Audit explanation generation failed; decision data is available in "
    "risk_predictions and policy_decisions tables."
)


def build_audit_prompt(decision_data: dict) -> str:
    """Build a structured prompt instructing the LLM to write a neutral, factual explanation.

    Args:
        decision_data: Dictionary containing:
            - risk_level (str)
            - risk_probability (float)
            - model_confidence (float)
            - is_low_confidence (bool)
            - top_risk_factors (list[str])
            - recommended_policy (str)
            - final_policy (str)
            - policy_agent_reasoning (dict | None)
            - policy_engine_details (dict | None)

    Returns:
        Formatted prompt string for the LLM.
    """
    risk_level = decision_data.get("risk_level", "UNKNOWN")
    risk_prob = decision_data.get("risk_probability", 0.0)
    confidence = decision_data.get("model_confidence", 0.0)
    is_low_conf = decision_data.get("is_low_confidence", False)
    top_factors = decision_data.get("top_risk_factors", [])
    recommended_policy = decision_data.get("recommended_policy", "STANDARD_RETURN")
    final_policy = decision_data.get("final_policy", "STANDARD_RETURN")
    agent_reasoning = decision_data.get("policy_agent_reasoning") or {}
    engine_details = decision_data.get("policy_engine_details") or {}

    formatted_factors = "\n".join(f"- {factor}" for factor in top_factors) if top_factors else "- None identified"
    formatted_reasoning = json.dumps(agent_reasoning, indent=2) if agent_reasoning else "None"
    formatted_engine = json.dumps(engine_details, indent=2) if engine_details else "None"

    prompt = f"""You are the audit trail narrator for ReturnSentinel AI, an e-commerce return policy decision system.
Your role is strictly to explain the already-final decision data provided below in a clear, professional, plain-English summary for internal merchant and support teams.

### STRUCTURED DECISION DATA (FACTS ONLY):
- Risk Level: {risk_level}
- Risk Probability: {risk_prob:.2%}
- Model Confidence: {confidence:.3f}
- Is Low Confidence Fallback: {is_low_conf}
- Top Risk Factors (SHAP-derived):
{formatted_factors}
- Policy Agent Recommended Policy: {recommended_policy}
- Final Validated Policy: {final_policy}
- Policy Agent Reasoning: {formatted_reasoning}
- Policy Engine Validation Details: {formatted_engine}

### STRICT GENERATION GUIDELINES:
1. Explain the decision using ONLY the facts provided above — do NOT invent, assume, extrapolate, or infer anything not present in the data.
2. Do NOT restate or imply a different risk score, confidence score, or policy than what is provided.
3. Do NOT suggest the customer did anything wrong or use accusatory language (e.g. use "the order showed elevated indicators of X" rather than "the customer is committing fraud"). Maintain a factual, neutral, and objective tone.
4. Keep the explanation to exactly 2 to 4 sentences covering:
   - What the risk assessment identified from the risk factors.
   - Why that confidence level was reached.
   - Why this specific final return policy was chosen over alternatives.
5. {"IMPORTANT: Because is_low_confidence is TRUE, you MUST explicitly state that the system applied a fallback policy due to insufficient confidence/evidence rather than a confident risk-based decision." if is_low_conf else "Explain how the model's confidence and specific category scores supported the chosen policy."}
6. Output plain text ONLY. Do NOT use markdown headers, bullet lists, prefixes, or JSON.
"""
    return prompt.strip()


def generate_deterministic_explanation(decision_data: dict) -> str:
    """Generate a high-quality deterministic audit explanation when LLM API quota or network is unavailable."""
    risk_level = decision_data.get("risk_level", "LOW")
    risk_prob = decision_data.get("risk_probability", 0.0)
    risk_pct = f"{risk_prob * 100:.1f}%" if risk_prob <= 1.0 else f"{risk_prob:.1f}%"
    confidence = decision_data.get("model_confidence", 0.0)
    conf_pct = f"{confidence * 100:.1f}%" if confidence <= 1.0 else f"{confidence:.1f}%"
    is_low_conf = decision_data.get("is_low_confidence", False)
    final_policy = decision_data.get("final_policy", "STANDARD_RETURN")
    top_factors = decision_data.get("top_risk_factors") or []

    factors_summary = ", ".join(top_factors[:2]) if top_factors else "standard customer and cart checkout telemetry"

    policy_names = {
        "STANDARD_RETURN": "Standard 14-Day Return window with full refund",
        "EXCHANGE_FIRST": "Exchange First to prioritize size/item replacement over cash refund",
        "STORE_CREDIT": "Store Credit only to mitigate return abuse while preserving customer retention",
        "RESTOCKING_FEE": "Restocking Fee deduction to offset reverse logistics and liquidation costs",
    }
    policy_desc = policy_names.get(final_policy, final_policy)

    if is_low_conf:
        return (
            f"The order was evaluated with an estimated {risk_level} risk score ({risk_pct}) influenced by {factors_summary}. "
            f"Because model certainty ({conf_pct}) fell below the autonomous decision threshold, the system safely applied {policy_desc} "
            f"as the merchant's configured fallback policy."
        )
    else:
        return (
            f"The order was classified as {risk_level} return abuse risk ({risk_pct} probability) with {conf_pct} model confidence, "
            f"driven primarily by {factors_summary}. Based on category risk scoring and active merchant policy constraints, "
            f"the system enforced {policy_desc}."
        )


def generate_audit_explanation(decision_data: dict) -> str:
    """Invoke the Google Gemini LLM to generate a concise, human-readable audit explanation.

    Args:
        decision_data: Dictionary containing structured decision facts.

    Returns:
        Generated 2-4 sentence explanation, or a graceful structured fallback upon API limit/failure.
    """
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not configured. Returning deterministic audit explanation.")
        return generate_deterministic_explanation(decision_data)

    try:
        genai.configure(api_key=api_key)
        model_name = settings.GEMINI_MODEL or "gemini-3.6-flash"
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 2048,
            },
        )
        prompt = build_audit_prompt(decision_data)
        response = model.generate_content(prompt)

        if response and response.text:
            explanation = response.text.strip()
            return explanation
        else:
            logger.warning("Gemini model returned empty response or text.")
            return generate_deterministic_explanation(decision_data)

    except Exception as e:
        logger.warning(f"Gemini API call failed or quota exceeded ({e}). Generating high-quality deterministic audit explanation.")
        return generate_deterministic_explanation(decision_data)


def generate_and_persist_audit(
    order_id: int,
    decision_data: Optional[Dict[str, Any]] = None,
) -> None:
    """Background task to generate the audit explanation and update the policy_decisions row.

    Opens a fresh database session (never reusing a request-scoped session).

    Args:
        order_id: The ID of the order whose policy decision is being audited.
        decision_data: Structured decision facts passed from the request context.
    """
    start_time = time.perf_counter()
    logger.info(f"Starting background audit trail generation for order_id={order_id}")

    db = SessionLocal()
    try:
        # If decision_data is not fully provided, enrich from database rows
        if decision_data is None:
            decision_data = {}

        pred = (
            db.query(RiskPrediction)
            .filter(RiskPrediction.order_id == order_id)
            .order_by(RiskPrediction.id.desc())
            .first()
        )
        policy_decision = (
            db.query(PolicyDecision)
            .filter(PolicyDecision.order_id == order_id)
            .first()
        )

        if not policy_decision:
            logger.error(f"Cannot generate audit: PolicyDecision row not found for order_id={order_id}")
            return

        # Ensure baseline attributes exist in decision_data
        if "risk_level" not in decision_data and pred:
            decision_data["risk_level"] = pred.risk_level
        if "risk_probability" not in decision_data and pred:
            decision_data["risk_probability"] = float(pred.risk_score) / 100.0
        if "model_confidence" not in decision_data and pred:
            decision_data["model_confidence"] = float(pred.confidence)
        if "is_low_confidence" not in decision_data and pred:
            decision_data["is_low_confidence"] = bool(pred.confidence is not None and float(pred.confidence) < 0.5)
        if "final_policy" not in decision_data and policy_decision:
            decision_data["final_policy"] = policy_decision.policy_type

        # Enrich top_risk_factors from AgentTrace if present
        if "top_risk_factors" not in decision_data:
            from app.models.agent_trace import AgentTrace
            trace = db.query(AgentTrace).filter(AgentTrace.order_id == order_id).first()
            if trace and isinstance(trace.trace_data, dict):
                factors = trace.trace_data.get("top_risk_factors")
                if factors:
                    decision_data["top_risk_factors"] = factors

        # Generate audit explanation
        explanation = generate_audit_explanation(decision_data)

        # Update policy_decision row
        policy_decision.audit_explanation = explanation
        policy_decision.audit_generated_at = datetime.now(timezone.utc)
        db.commit()

        elapsed_ms = int(round((time.perf_counter() - start_time) * 1000))
        logger.info(
            f"Successfully generated and persisted audit explanation for order_id={order_id} in {elapsed_ms}ms"
        )

    except Exception as e:
        db.rollback()
        logger.error(
            f"Failed to generate and persist audit explanation for order_id={order_id}: {e}",
            exc_info=True,
        )
    finally:
        db.close()
