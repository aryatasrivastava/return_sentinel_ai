import { apiFetch } from "./client";
import { PolicyType } from "@/lib/types";

export interface StorefrontProduct {
  id: number;
  name: string;
  sku: string;
  category: string | null;
  price: number;
}

export interface StorefrontCustomer {
  id: number;
  name: string;
  email: string;
}

export interface AssessCartItemRequest {
  product_id: number;
  size?: string;
  quantity: number;
  unit_price: number;
}

export interface AssessCartRequest {
  customer_id: number;
  cart_items: AssessCartItemRequest[];
  order_id?: number;
}

export interface AssessCartResponse {
  order_id: number;
  risk_probability: number;
  risk_level: string;
  model_confidence: number;
  is_low_confidence: boolean;
  investigation_round: number;
  recommended_policy: string;
  final_policy: PolicyType;
  validation_passed: boolean;
  policy_anomaly: boolean;
  top_risk_factors: string[];
  latency_ms: number;
}

export async function getStorefrontProducts(): Promise<StorefrontProduct[]> {
  return apiFetch<StorefrontProduct[]>("/api/products");
}

export async function getStorefrontCustomers(): Promise<StorefrontCustomer[]> {
  return apiFetch<StorefrontCustomer[]>("/api/customers");
}

export async function assessCartCheckout(
  payload: AssessCartRequest
): Promise<AssessCartResponse> {
  return apiFetch<AssessCartResponse>("/api/assess-order", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
