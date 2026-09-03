import { BackendOrderListItem, BackendOrderDetail } from "@/lib/api/orders";
import { Order, RiskLevel, PolicyType, OrderStatus } from "@/lib/types";

export function mapBackendOrderToOrder(
  bOrder: BackendOrderListItem | BackendOrderDetail
): Order {
  const nameParts = (bOrder.customer_name || "Customer").trim().split(/\s+/);
  const avatarInitials =
    nameParts.length >= 2
      ? `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase()
      : nameParts[0].slice(0, 2).toUpperCase();

  const riskLevelLower = (bOrder.risk_level || "low").toLowerCase() as RiskLevel;
  const rawConfidence = bOrder.confidence !== null ? bOrder.confidence : 0;
  const confidencePct = Math.round(rawConfidence <= 1.0 ? rawConfidence * 100 : rawConfidence);
  const riskScoreNum = bOrder.risk_score !== null ? Math.round(bOrder.risk_score) : 0;

  const orderDate = bOrder.created_at ? new Date(bOrder.created_at) : new Date();
  const dateFormatted = `${orderDate.toLocaleDateString("en-IN")} ${orderDate.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}`;

  const items = (bOrder as BackendOrderDetail).items;
  const itemsCount = items && items.length > 0 ? items.reduce((acc, it) => acc + (it.quantity || 1), 0) : 1;

  return {
    id: `ORD-${bOrder.order_id}`,
    customer: {
      id: String((bOrder as BackendOrderDetail).customer_id || bOrder.order_id),
      name: bOrder.customer_name || "Unknown Customer",
      email: `${bOrder.customer_name?.toLowerCase().replace(/[^a-z0-9]/g, ".") || "customer"}@example.com`,
      avatarInitials,
      returnRate: 0.25,
      previousReturns: 1,
      totalOrders: 4,
      accountAgeDays: 120,
      lifetimeValue: bOrder.cart_value * 2.5,
    },
    cartValue: bOrder.cart_value || 0,
    currency: "₹",
    riskScore: riskScoreNum,
    confidence: confidencePct,
    policy: (bOrder.policy || "STANDARD_RETURN") as PolicyType,
    status: (bOrder.status || "processed") as OrderStatus,
    createdAt: dateFormatted,
    itemsCount,
    riskLevel: riskLevelLower,
  };
}
