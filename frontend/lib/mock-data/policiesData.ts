import { PolicyDefinition } from "../types";

export const mockPolicyDefinitions: PolicyDefinition[] = [
  {
    id: "STANDARD_RETURN",
    title: "Standard Return",
    description:
      "Full 14-day return window with instant refunds to original payment method. Seamless zero-friction checkout for trusted shoppers.",
    customerFriction: "Low",
    customerFrictionValue: 1, // 1/10
    merchantProtection: "Low",
    merchantProtectionValue: 3, // 3/10
    isEnabled: true,
    triggerCondition: "Risk Score < 35 (Low Risk Baseline)",
    recommendedFor: "Shoppers with return rate < 20% and no multi-size bracketing behavior.",
  },
  {
    id: "EXCHANGE_FIRST",
    title: "Exchange First",
    description:
      "Offers free instant size & color exchanges delivered via courier before refund processing. Eliminates bracketed sizing returns without checkout dropoff.",
    customerFriction: "Medium",
    customerFrictionValue: 3, // 3/10
    merchantProtection: "High",
    merchantProtectionValue: 8, // 8/10
    isEnabled: true,
    triggerCondition: "Risk Score 35-75 OR Size Bracketing Detected in Cart",
    recommendedFor: "Customers purchasing multiple sizes or exhibiting high fit-uncertainty flags.",
  },
  {
    id: "STORE_CREDIT",
    title: "Store Credit Only",
    description:
      "Converts return refunds directly into 100% store credit plus an optional +5% loyalty bonus. Retains merchant revenue inside the ecosystem.",
    customerFriction: "Medium",
    customerFrictionValue: 5, // 5/10
    merchantProtection: "High",
    merchantProtectionValue: 8.5, // 8.5/10
    isEnabled: true,
    triggerCondition: "Risk Score 75-85 OR Repeat Returner (>50% return rate)",
    recommendedFor: "Frequent returners who generate high logistics overhead but maintain strong brand interest.",
  },
  {
    id: "RESTOCKING_FEE",
    title: "Restocking Fee (15%)",
    description:
      "Applies a 15% refurbishment/inspection fee on cash returns for high-risk items, fully waived if customer chooses store credit.",
    customerFriction: "High",
    customerFrictionValue: 7, // 7/10
    merchantProtection: "High",
    merchantProtectionValue: 9.5, // 9.5/10
    isEnabled: true,
    triggerCondition: "Risk Score > 85 OR Flagged Wardrobing / Serial Return Abuse",
    recommendedFor: "Severe risk profiles, bridal/occasionwear wardrobing, and repeated damage claim disputes.",
  },
];
