import { apiFetch } from "./client";

export interface BackendDashboardStats {
  orders_analyzed: number;
  high_risk_orders: number;
  estimated_margin_protected: number;
  false_positive_rate: number | null;
  risk_distribution: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
  };
  policy_distribution: {
    STANDARD_RETURN: number;
    EXCHANGE_FIRST: number;
    STORE_CREDIT: number;
    RESTOCKING_FEE: number;
  };
}

export async function getDashboardStats(): Promise<BackendDashboardStats> {
  return apiFetch<BackendDashboardStats>("/api/dashboard-stats");
}
