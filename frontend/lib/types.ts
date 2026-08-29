export type RiskLevel = "low" | "medium" | "high";

export type PolicyType =
  | "STANDARD_RETURN"
  | "EXCHANGE_FIRST"
  | "STORE_CREDIT"
  | "RESTOCKING_FEE";

export interface Customer {
  id: string;
  name: string;
  email: string;
  avatarInitials: string;
  returnRate: number; // e.g. 0.42 = 42%
  previousReturns: number;
  totalOrders: number;
  accountAgeDays: number;
  lifetimeValue: number;
  riskTag?: string;
}

export interface OrderItem {
  id: string;
  name: string;
  sku: string;
  category: string;
  size?: string;
  price: number;
  quantity: number;
  historicalCategoryReturnRate: number;
}

export type OrderStatus = "flagged" | "processed" | "delivered" | "under_review";

export interface Order {
  id: string;
  customer: Customer;
  cartValue: number;
  currency: string;
  riskScore: number; // 0 - 100
  confidence: number; // 0 - 100
  policy: PolicyType;
  status: OrderStatus;
  createdAt: string;
  itemsCount: number;
  items?: OrderItem[];
  riskLevel: RiskLevel;
}

export interface SignalItem {
  id: string;
  name: string;
  description: string;
  severity: RiskLevel;
  value: string;
  category: "customer" | "cart" | "product";
}

export interface MLFeatureWeight {
  feature: string;
  importance: number; // 0 - 1.0
  impact: "positive" | "negative";
  description: string;
}

export interface MLPrediction {
  modelName: string;
  modelVersion: string;
  rawScore: number;
  confidenceScore: number;
  features: MLFeatureWeight[];
  predictedCategory: "Wardrobing Risk" | "Serial Returner" | "Standard Shopper" | "High Velocity Flagger";
}

export interface RiskAssessment {
  orderId: string;
  riskScore: number;
  riskLevel: RiskLevel;
  confidence: number;
  evaluatedAt: string;
  signals: {
    customer: SignalItem[];
    cart: SignalItem[];
    product: SignalItem[];
  };
  mlPrediction: MLPrediction;
}

export interface PolicyDecision {
  orderId: string;
  policy: PolicyType;
  policyName: string;
  rationale: string;
  protectedMargin: number;
  customerFrictionScore: number; // 1 - 10
  merchantProtectionScore: number; // 1 - 10
  engineRulesTriggered: string[];
  estimatedMarginSaved: number;
  decidedAt: string;
}

export interface AgentStep {
  id: string;
  type: "agent" | "tool" | "ml" | "routing" | "policy";
  label: string;
  detail?: string;
  status: "complete" | "pending";
  timestamp?: string;
  output?: string;
  durationMs?: number;
}

export interface DashboardStats {
  ordersAnalyzed: number;
  highRiskOrders: number;
  marginProtected: number;
  falsePositiveRate: number;
  trends: {
    ordersAnalyzedDelta: string;
    highRiskDelta: string;
    marginDelta: string;
    falsePositiveDelta: string;
  };
  riskDistribution: {
    low: number;
    medium: number;
    high: number;
  };
  policyDistribution: {
    standardReturn: number;
    exchangeFirst: number;
    storeCredit: number;
    restockingFee: number;
  };
}

export interface PolicyDefinition {
  id: PolicyType;
  title: string;
  description: string;
  customerFriction: "Low" | "Medium" | "High";
  customerFrictionValue: number; // 1-10
  merchantProtection: "Low" | "Medium" | "High";
  merchantProtectionValue: number; // 1-10
  isEnabled: boolean;
  triggerCondition: string;
  recommendedFor: string;
}
