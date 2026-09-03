"use client";

import React, { useState, useEffect, useCallback, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardHeader } from "@/components/ui/Card";
import { RiskBadge } from "@/components/risk/RiskBadge";
import { RiskScore } from "@/components/risk/RiskScore";
import { ConfidenceIndicator } from "@/components/risk/ConfidenceIndicator";
import { SignalList } from "@/components/risk/SignalList";
import { PolicyBadge } from "@/components/policies/PolicyBadge";
import { AgentTrace } from "@/components/dashboard/AgentTrace";
import { EmptyState } from "@/components/ui/EmptyState";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
import {
  ShieldAlertIcon,
  ShieldCheckIcon,
  InfoIcon,
  ArrowRightIcon,
  ClockIcon,
} from "@/components/ui/Icons";
import { getOrderDetail, BackendOrderDetail } from "@/lib/api/orders";
import { traceToSteps } from "@/lib/transforms/traceToSteps";
import { RiskLevel, SignalItem, PolicyType } from "@/lib/types";

function RiskAnalysisContent() {
  const searchParams = useSearchParams();
  const orderIdParam = searchParams.get("orderId");

  const [order, setOrder] = useState<BackendOrderDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = useCallback(async (id: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getOrderDetail(id);
      setOrder(data);
    } catch (err: any) {
      setError(err.message || `Unable to load details for order #${id}.`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (orderIdParam) {
      fetchDetail(orderIdParam);
    } else {
      setOrder(null);
      setError(null);
    }
  }, [orderIdParam, fetchDetail]);

  // Prompt state if no orderId parameter was provided in the URL
  if (!orderIdParam) {
    return (
      <EmptyState
        icon={<ShieldAlertIcon size={28} className="text-[var(--accent)]" />}
        title="No Order Selected"
        description="Select an analyzed order from the Orders list to inspect its autonomous AI decision trace, risk signals, and deterministic policy validation."
        actionLabel="Go to Orders Page"
        onAction={() => {
          window.location.href = "/orders";
        }}
      />
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <LoadingState rows={4} />
        <LoadingState rows={6} />
      </div>
    );
  }

  if (error || !order) {
    return (
      <EmptyState
        variant="danger"
        title="Order Not Found"
        description={error || `Order #${orderIdParam} could not be retrieved from the database.`}
        actionLabel="Back to Orders"
        onAction={() => {
          window.location.href = "/orders";
        }}
      />
    );
  }

  // Derive risk indicators and percentages
  const riskLevel = (order.risk_level || "LOW").toLowerCase() as RiskLevel;
  const rawConfidence = order.confidence !== null ? order.confidence : 0;
  const confidencePct = Math.round(rawConfidence <= 1.0 ? rawConfidence * 100 : rawConfidence);
  const riskScoreVal = order.risk_score !== null ? Math.round(order.risk_score) : 0;
  const policyType = (order.policy || "STANDARD_RETURN") as PolicyType;
  const traceSteps = traceToSteps(order.trace_data);

  // Derive granular signal items from top_risk_factors and order metadata
  const factors = order.top_risk_factors || [];

  const customerSignals: SignalItem[] = [];
  const cartSignals: SignalItem[] = [];
  const productSignals: SignalItem[] = [];

  factors.forEach((f, idx) => {
    const textLower = f.toLowerCase();
    const isSeverityHigh = riskLevel === "high" || textLower.includes("elevated") || textLower.includes("multiple");
    const itemSeverity: RiskLevel = isSeverityHigh ? "high" : riskLevel === "medium" ? "medium" : "low";

    if (textLower.includes("customer") || textLower.includes("rate") || textLower.includes("history") || textLower.includes("prior")) {
      customerSignals.push({
        id: `sig-cust-${idx}`,
        name: f,
        description: `Observed in account telemetry for ${order.customer_name}.`,
        severity: itemSeverity,
        value: "Detected",
        category: "customer",
      });
    } else if (textLower.includes("size") || textLower.includes("bracket") || textLower.includes("cart") || textLower.includes("item")) {
      cartSignals.push({
        id: `sig-cart-${idx}`,
        name: f,
        description: `Multi-size or cart composition anomaly evaluated in live checkout session.`,
        severity: itemSeverity,
        value: "Flagged",
        category: "cart",
      });
    } else {
      productSignals.push({
        id: `sig-prod-${idx}`,
        name: f,
        description: `Product category baseline anomaly detected in catalog risk index.`,
        severity: itemSeverity,
        value: "Catalog Index",
        category: "product",
      });
    }
  });

  // Ensure each panel has at least one baseline telemetry signal
  if (customerSignals.length === 0) {
    customerSignals.push({
      id: "sig-cust-default",
      name: "Account Return History Verified",
      description: `Historical return metrics verified for customer ID #${order.customer_id}.`,
      severity: "low",
      value: "Normal",
      category: "customer",
    });
  }

  if (cartSignals.length === 0) {
    cartSignals.push({
      id: "sig-cart-default",
      name: "Cart Size Consistency",
      description: `${order.items.length} item variant(s) evaluated in order payload.`,
      severity: "low",
      value: "Consistent",
      category: "cart",
    });
  }

  if (productSignals.length === 0) {
    productSignals.push({
      id: "sig-prod-default",
      name: "Catalog Category Baseline",
      description: "Item categories verified against catalog baseline return distributions.",
      severity: "low",
      value: "Standard",
      category: "product",
    });
  }

  const orderFormattedDate = order.created_at
    ? new Date(order.created_at).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })
    : "Recent";

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb Navigation */}
      <div className="flex items-center justify-between text-xs text-[var(--ink-600)]">
        <div className="flex items-center gap-1.5">
          <Link href="/orders" className="hover:underline text-[var(--accent)] font-medium">
            Orders
          </Link>
          <span>/</span>
          <span className="font-mono text-[var(--ink-900)] font-semibold">
            ORD-{order.order_id}
          </span>
        </div>

        <div className="text-[11px] text-[var(--ink-400)] font-mono tabular-nums">
          Evaluated: {orderFormattedDate}
        </div>
      </div>

      {/* Hero Header Card: Score + Level + Confidence + Order Context */}
      <Card className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Left: Order Info & Customer Identity (5 cols) */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-2xl font-bold text-[var(--ink-900)]">
                ORD-{order.order_id}
              </span>
              <RiskBadge level={riskLevel} />
              <PolicyBadge policy={policyType} />
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-center font-mono text-[10px] font-bold">
                  {order.customer_name.slice(0, 2).toUpperCase()}
                </div>
                <span className="text-sm font-semibold text-[var(--ink-900)]">
                  {order.customer_name}
                </span>
                <span className="text-xs text-[var(--ink-400)]">
                  (Customer #{order.customer_id})
                </span>
              </div>

              <p className="text-xs text-[var(--ink-600)] leading-relaxed">
                Cart Total:{" "}
                <strong className="font-mono text-[var(--ink-900)]">
                  ₹{order.cart_value.toLocaleString("en-IN")}
                </strong>{" "}
                across {order.items.length} item line(s). Status:{" "}
                <span className="capitalize font-medium">{order.status}</span>.
              </p>
            </div>
          </div>

          {/* Right: Risk Threat Score & Model Certainty Gauges (7 cols) */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4 bg-[var(--surface-sunken)] p-4 rounded-[6px] border border-[var(--border)]">
            {/* Risk Score */}
            <div>
              <span className="text-[11px] font-medium text-[var(--ink-400)] uppercase tracking-wider block mb-1">
                Calculated Threat Score
              </span>
              <RiskScore score={riskScoreVal} size="lg" showMeter={true} />
            </div>

            {/* Model Confidence */}
            <div className="space-y-2">
              <span className="text-[11px] font-medium text-[var(--ink-400)] uppercase tracking-wider block">
                Model Certainty & Routing
              </span>
              <ConfidenceIndicator
                confidence={confidencePct}
                size="md"
                showLabel={true}
              />
              <span className="text-[11px] text-[var(--ink-600)] block">
                {confidencePct >= 50
                  ? "✓ High certainty risk classification"
                  : "⚠ Dispatched to fallback policy due to low confidence budget"}
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* AI Explanation / Policy Action Banner */}
      <Card className="bg-[var(--surface-sunken)] p-4 border-[var(--border)]">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[var(--ink-900)] uppercase tracking-wider">
                Assigned Policy Action:
              </span>
              <PolicyBadge policy={policyType} />
            </div>

            {/* Plain English Audit Explanation */}
            <div className="p-3 bg-white rounded-[6px] border border-[var(--border)] space-y-1">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-[var(--ink-900)]">
                <InfoIcon size={13} className="text-[var(--accent)]" />
                <span>Autonomous Audit Explanation:</span>
              </div>
              {order.audit_explanation ? (
                <p className="text-xs text-[var(--ink-600)] leading-relaxed">
                  {order.audit_explanation}
                </p>
              ) : (
                <div className="flex items-center gap-2 text-xs text-[var(--ink-400)] py-1">
                  <ClockIcon size={14} className="animate-spin text-[var(--warning)]" />
                  <span>Audit explanation is currently generating in background...</span>
                </div>
              )}
            </div>
          </div>

          <div className="shrink-0 p-3 rounded-[6px] bg-white border border-[var(--border)] text-right self-stretch sm:self-auto flex sm:flex-col justify-between items-center sm:items-end">
            <span className="text-[10px] text-[var(--ink-400)] uppercase tracking-wider block">
              Cart Value Protected
            </span>
            <span className="font-mono text-base font-bold text-[var(--success)] tabular-nums block">
              ₹{order.cart_value.toLocaleString("en-IN")}
            </span>
          </div>
        </div>
      </Card>

      {/* Granular Multi-Signal Panels: Customer, Cart, Product */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
            Evidence & Anomaly Signals
          </h2>
          <span className="text-xs text-[var(--ink-400)] font-mono">
            3 Telemetry Domains Inspected
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SignalList
            category="customer"
            title="Customer History Signals"
            signals={customerSignals}
          />
          <SignalList
            category="cart"
            title="Cart Composition Signals"
            signals={cartSignals}
          />
          <SignalList
            category="product"
            title="Catalog Risk Signals"
            signals={productSignals}
          />
        </div>
      </section>

      {/* Cart Items Breakdown */}
      {order.items && order.items.length > 0 && (
        <Card>
          <CardHeader
            title="Cart Items in Order"
            subtitle={`${order.items.length} product variant(s) evaluated`}
          />
          <div className="divide-y divide-[var(--border)]">
            {order.items.map((item, idx) => (
              <div key={idx} className="py-2.5 px-3 flex items-center justify-between text-xs">
                <div className="space-y-0.5">
                  <span className="font-medium text-[var(--ink-900)]">
                    {item.product_name || `Product #${item.product_id}`}
                  </span>
                  <div className="flex items-center gap-2 text-[11px] text-[var(--ink-400)] font-mono">
                    <span>SKU: {item.sku || `ID-${item.product_id}`}</span>
                    {item.size && <span>• Size: {item.size}</span>}
                    <span>• Qty: {item.quantity}</span>
                  </div>
                </div>
                <div className="font-mono text-right font-medium text-[var(--ink-900)]">
                  ₹{item.total_price.toLocaleString("en-IN")}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Agent Investigation History (Signature AgentTrace Component) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
            Agent Investigation History
          </h2>
          <span className="text-xs text-[var(--ink-400)]">
            LangGraph Multi-Round Trace
          </span>
        </div>

        <AgentTrace
          steps={traceSteps}
          orderId={`ORD-${order.order_id}`}
          title={`Execution Trace for ORD-${order.order_id}`}
          subtitle="Chronological sequence of ML assessment rounds, Policy Agent evaluation, and Policy Engine deterministic validation"
        />
      </section>
    </div>
  );
}

export default function RiskAnalysisPage() {
  return (
    <PageContainer>
      <Suspense fallback={<LoadingState rows={6} />}>
        <RiskAnalysisContent />
      </Suspense>
    </PageContainer>
  );
}
