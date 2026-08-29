import { PolicyDecision } from "../types";

export const mockPolicyDecisions: Record<string, PolicyDecision> = {
  "ORD-9421": {
    orderId: "ORD-9421",
    policy: "EXCHANGE_FIRST",
    policyName: "Exchange First Policy",
    rationale:
      "Customer exhibiting size bracketing on high-return occasionwear with 64.3% historical return rate. Policy Agent routes to 'Exchange First' to allow instant size swaps while preventing cash outflows, protecting ₹3,450 margin without blocking checkout conversion.",
    protectedMargin: 3450,
    customerFrictionScore: 3.5,
    merchantProtectionScore: 8.2,
    engineRulesTriggered: [
      "RULE_BRACKET_04: Duplicate SKU across sizing",
      "RULE_HIST_02: Return rate > 50% in 180 days",
      "RULE_MARGIN_01: Occasionwear ticket > ₹3,000",
    ],
    estimatedMarginSaved: 3450,
    decidedAt: "2026-08-26 14:18:24",
  },
  "ORD-9419": {
    orderId: "ORD-9419",
    policy: "RESTOCKING_FEE",
    policyName: "15% Restocking Fee Policy",
    rationale:
      "Serial return rate of 88.2% on premium bridal wear with 3 historical damage claims. Deterministic Policy Engine triggered maximum margin defense via non-blocking 15% restocking fee (₹1,860) on cash refunds, with 100% store credit waiver option.",
    protectedMargin: 8900,
    customerFrictionScore: 6.8,
    merchantProtectionScore: 9.5,
    engineRulesTriggered: [
      "RULE_SERIAL_01: Return rate > 80% with >10 orders",
      "RULE_CATEGORY_BRIDAL: High inspection refurbishment penalty",
      "RULE_PREV_DISPUTE: Historical damage claim history",
    ],
    estimatedMarginSaved: 8900,
    decidedAt: "2026-08-26 13:22:05",
  },
  "ORD-9420": {
    orderId: "ORD-9420",
    policy: "STANDARD_RETURN",
    policyName: "Standard Full-Refund Return",
    rationale:
      "Low risk score (18/100) and 96% model confidence. Customer exhibits verified sizing consistency and staple basics purchase profile. Full 14-day standard return window with zero merchant friction.",
    protectedMargin: 0,
    customerFrictionScore: 1.0,
    merchantProtectionScore: 4.0,
    engineRulesTriggered: ["RULE_DEFAULT_PASS: Risk score < 30 threshold"],
    estimatedMarginSaved: 0,
    decidedAt: "2026-08-26 13:54:11",
  },
};
