import { apiFetch } from "./client";
import { PolicyType } from "@/lib/types";
import { BackendTraceData } from "@/lib/transforms/traceToSteps";

export interface BackendOrderItemDetail {
  product_id: number;
  product_name?: string | null;
  sku?: string | null;
  size?: string | null;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface BackendOrderListItem {
  order_id: number;
  customer_name: string;
  cart_value: number;
  risk_score: number | null;
  risk_level: string | null;
  confidence: number | null;
  policy: PolicyType | null;
  status: string;
  created_at: string;
}

export interface BackendOrderDetail {
  order_id: number;
  customer_id: number;
  customer_name: string;
  cart_value: number;
  risk_score: number | null;
  risk_level: string | null;
  confidence: number | null;
  policy: PolicyType | null;
  status: string;
  created_at: string;
  items: BackendOrderItemDetail[];
  trace_data: BackendTraceData | null;
  top_risk_factors: string[] | null;
  audit_explanation: string | null;
  audit_generated_at: string | null;
}

export interface GetOrdersParams {
  limit?: number;
  offset?: number;
  risk_level?: string;
  policy_type?: string;
}

export async function getOrders(
  params: GetOrdersParams = {}
): Promise<BackendOrderListItem[]> {
  const searchParams = new URLSearchParams();
  if (params.limit !== undefined) searchParams.set("limit", String(params.limit));
  if (params.offset !== undefined) searchParams.set("offset", String(params.offset));
  if (params.risk_level && params.risk_level !== "ALL") {
    searchParams.set("risk_level", params.risk_level);
  }
  if (params.policy_type && params.policy_type !== "ALL") {
    searchParams.set("policy_type", params.policy_type);
  }

  const queryString = searchParams.toString();
  const path = `/api/orders${queryString ? `?${queryString}` : ""}`;
  return apiFetch<BackendOrderListItem[]>(path);
}

export async function getOrderDetail(
  orderId: number | string
): Promise<BackendOrderDetail> {
  const cleanId = String(orderId).replace(/^ORD-?/i, "");
  return apiFetch<BackendOrderDetail>(`/api/orders/${cleanId}`);
}
