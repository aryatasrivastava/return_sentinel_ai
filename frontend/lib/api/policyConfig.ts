import { apiFetch } from "./client";
import { PolicyType } from "@/lib/types";

export interface PolicyConfigResponse {
  low_risk_allowed: PolicyType[];
  medium_risk_allowed: PolicyType[];
  high_risk_allowed: PolicyType[];
  low_confidence_fallback: PolicyType;
  updated_at?: string;
}

export interface PolicyConfigUpdate {
  low_risk_allowed: PolicyType[];
  medium_risk_allowed: PolicyType[];
  high_risk_allowed: PolicyType[];
  low_confidence_fallback: PolicyType;
}

export async function getPolicyConfig(): Promise<PolicyConfigResponse> {
  return apiFetch<PolicyConfigResponse>("/api/policy-config");
}

export async function updatePolicyConfig(
  data: PolicyConfigUpdate
): Promise<PolicyConfigResponse> {
  return apiFetch<PolicyConfigResponse>("/api/policy-config", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}
