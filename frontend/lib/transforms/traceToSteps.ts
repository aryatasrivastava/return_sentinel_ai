import { AgentStep } from "@/lib/types";

export interface BackendTraceData {
  investigation_log?: Array<{
    step_type?: string;
    round?: number;
    source?: string;
    risk_level?: string;
    risk_probability?: number;
    model_confidence?: number;
    description?: string;
    feature_diff?: Record<string, any>;
    top_risk_factors?: string[];
    recommended_policy?: string;
    final_policy?: string;
    validation_passed?: boolean;
    anomaly?: boolean;
    reasoning?: Record<string, any>;
    details?: Record<string, any>;
  }>;
  policy_agent_reasoning?: Record<string, any>;
  policy_engine_details?: Record<string, any>;
  top_risk_factors?: string[];
}

/**
 * Transforms real, round-level backend Agent Decision Trace data into the visual AgentStep[]
 * consumed by the AgentTrace component.
 *
 * Note: This is an honest round-level mapping corresponding to actual backend investigation rounds,
 * Policy Agent evaluations, and Policy Engine deterministic validation passes.
 */
export function traceToSteps(traceData?: BackendTraceData | null): AgentStep[] {
  if (!traceData || !traceData.investigation_log || traceData.investigation_log.length === 0) {
    return [];
  }

  return traceData.investigation_log.map((entry, index) => {
    const stepId = `step_${index + 1}`;
    const stepType = entry.step_type;

    if (stepType === "initial_assessment" || stepType === "investigation") {
      const roundNum = entry.round !== undefined ? entry.round : index;
      const sourceLabel =
        entry.source === "cached"
          ? "Cached Assessment"
          : entry.source === "live_data"
          ? "Live Investigation"
          : "Risk Inference";

      const riskPct =
        entry.risk_probability !== undefined
          ? `${(entry.risk_probability * 100).toFixed(1)}%`
          : undefined;

      const confVal =
        entry.model_confidence !== undefined
          ? `${(entry.model_confidence * 100).toFixed(1)}%`
          : undefined;

      const metricsSummary = [
        entry.risk_level ? `Risk Level: ${entry.risk_level.toUpperCase()}` : null,
        riskPct ? `Risk Prob: ${riskPct}` : null,
        confVal ? `Confidence: ${confVal}` : null,
      ]
        .filter(Boolean)
        .join(" | ");

      const payloadData: Record<string, any> = {};
      if (entry.feature_diff && Object.keys(entry.feature_diff).length > 0) {
        payloadData.feature_diff = entry.feature_diff;
      }
      if (entry.top_risk_factors && entry.top_risk_factors.length > 0) {
        payloadData.top_risk_factors = entry.top_risk_factors;
      }

      return {
        id: stepId,
        type: "ml",
        label: `Round ${roundNum}: ${sourceLabel}`,
        detail: entry.description || metricsSummary,
        status: "complete",
        output: Object.keys(payloadData).length > 0 ? JSON.stringify(payloadData, null, 2) : undefined,
      };
    } else if (stepType === "policy_agent") {
      const policyRec = entry.recommended_policy || "EVALUATED";
      const reasoning = entry.reasoning || traceData.policy_agent_reasoning;

      let detailText = entry.description || `Policy Agent evaluated category scoring -> Recommended: ${policyRec}`;
      if (reasoning?.scores) {
        const scoreEntries = Object.entries(reasoning.scores)
          .map(([pol, score]) => `${pol}: ${score}`)
          .join(", ");
        detailText = `Scores: [${scoreEntries}]. Recommended: ${policyRec}`;
      }

      return {
        id: stepId,
        type: "agent",
        label: entry.description || `Policy Agent Recommendation: ${policyRec}`,
        detail: detailText,
        status: "complete",
        output: reasoning ? JSON.stringify(reasoning, null, 2) : undefined,
      };
    } else if (stepType === "policy_engine") {
      const finalPolicy = entry.final_policy || "APPROVED";
      const isPassed = entry.validation_passed ?? true;
      const isAnomaly = entry.anomaly ?? false;
      const details = entry.details || traceData.policy_engine_details;

      return {
        id: stepId,
        type: "policy",
        label: entry.description || `Policy Engine: ${finalPolicy}`,
        detail: `Deterministic Validation: ${isPassed ? "PASSED" : "FAILED"}${
          isAnomaly ? " (Policy Anomaly Detected - Overridden)" : ""
        }`,
        status: "complete",
        output: details ? JSON.stringify(details, null, 2) : undefined,
      };
    } else {
      return {
        id: stepId,
        type: "routing",
        label: entry.description || `Pipeline Step: ${stepType}`,
        status: "complete",
      };
    }
  });
}
