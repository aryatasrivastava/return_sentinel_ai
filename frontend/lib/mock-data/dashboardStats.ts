import { DashboardStats } from "../types";

export const mockDashboardStats: DashboardStats = {
  ordersAnalyzed: 127,
  highRiskOrders: 18,
  marginProtected: 8420,
  falsePositiveRate: 3.2,
  trends: {
    ordersAnalyzedDelta: "+18.4% vs last week",
    highRiskDelta: "-2.1% fraud exposure",
    marginDelta: "+₹2,180 protected this week",
    falsePositiveDelta: "-0.4% improvement",
  },
  riskDistribution: {
    low: 84,     // 66.1%
    medium: 25,  // 19.7%
    high: 18,    // 14.2%
  },
  policyDistribution: {
    standardReturn: 78, // 61.4%
    exchangeFirst: 28,  // 22.0%
    storeCredit: 15,    // 11.8%
    restockingFee: 6,   // 4.8%
  },
};
