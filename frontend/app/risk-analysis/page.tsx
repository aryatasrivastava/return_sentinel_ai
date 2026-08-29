"use client";

import React, { useState, use } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardHeader } from "@/components/ui/Card";
import { RiskBadge } from "@/components/risk/RiskBadge";
import { RiskScore } from "@/components/risk/RiskScore";
import { ConfidenceIndicator } from "@/components/risk/ConfidenceIndicator";
import { SignalList } from "@/components/risk/SignalList";
import { PolicyBadge } from "@/components/policies/PolicyBadge";
import { AgentTrace } from "@/components/dashboard/AgentTrace";
import {
  mockOrders,
  mockRiskAssessments,
  mockPolicyDecisions,
  mockAgentTraces,
  defaultSignatureTrace,
} from "@/lib/mock-data";

export default function RiskAnalysisPage({
  searchParams,
}: {
  searchParams?: Promise<{ orderId?: string }>;
}) {
  const resolvedParams = searchParams ? use(searchParams) : undefined;
  const paramOrderId = resolvedParams?.orderId;
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);

  const activeOrderId = selectedOrderId ?? paramOrderId ?? "ORD-9421";

  const currentOrder =
    mockOrders.find((o) => o.id === activeOrderId) || mockOrders[0];

  const assessment =
    mockRiskAssessments[currentOrder.id] || mockRiskAssessments["ORD-9421"];

  const policyDecision =
    mockPolicyDecisions[currentOrder.id] || mockPolicyDecisions["ORD-9421"];

  const traceSteps =
    mockAgentTraces[currentOrder.id] || defaultSignatureTrace;

  return (
    <PageContainer>
      {/* Top Order Switcher & Quick Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[var(--surface)] border border-[var(--border)] rounded-[8px] p-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-[var(--ink-600)] uppercase tracking-wider">
            Select Order to Inspect:
          </span>
          <div className="flex items-center gap-1.5 flex-wrap">
            {mockOrders.slice(0, 6).map((order) => (
              <button
                key={order.id}
                type="button"
                onClick={() => setSelectedOrderId(order.id)}
                className={`font-mono text-xs px-2.5 py-1 rounded-[4px] border transition-colors ${
                  order.id === currentOrder.id
                    ? "bg-[var(--accent)] text-white border-[var(--accent)] font-semibold"
                    : "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--ink-900)] hover:bg-[#e2e6f0]"
                }`}
              >
                {order.id}
              </button>
            ))}
          </div>
        </div>

        <div className="text-[11px] text-[var(--ink-400)] font-mono tabular-nums self-end sm:self-auto">
          Evaluated: {currentOrder.createdAt}
        </div>
      </div>

      {/* Hero Header Card: Score + Level + Confidence + Policy Banner */}
      <Card className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Left: Order Info & Status (5 cols) */}
          <div className="lg:col-span-5 space-y-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-xl font-bold text-[var(--ink-900)]">
                {currentOrder.id}
              </span>
              <RiskBadge level={assessment.riskLevel} />
              <PolicyBadge policy={currentOrder.policy} />
            </div>

            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-center font-mono text-[10px] font-bold">
                  {currentOrder.customer.avatarInitials}
                </div>
                <span className="text-sm font-semibold text-[var(--ink-900)]">
                  {currentOrder.customer.name}
                </span>
                <span className="text-xs text-[var(--ink-400)]">
                  ({currentOrder.customer.email})
                </span>
              </div>

              <p className="text-xs text-[var(--ink-600)] leading-relaxed">
                Cart Total:{" "}
                <strong className="font-mono text-[var(--ink-900)]">
                  {currentOrder.currency}
                  {currentOrder.cartValue.toLocaleString("en-IN")}
                </strong>{" "}
                across {currentOrder.itemsCount} items. Account age:{" "}
                {currentOrder.customer.accountAgeDays} days.
              </p>
            </div>
          </div>

          {/* Right: Risk Score & Model Confidence Gauge (7 cols) */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4 bg-[var(--surface-sunken)] p-4 rounded-[6px] border border-[var(--border)]">
            {/* Risk Score */}
            <div>
              <span className="text-[11px] font-medium text-[var(--ink-400)] uppercase tracking-wider block mb-1">
                Calculated Threat Score
              </span>
              <RiskScore score={assessment.riskScore} size="lg" showMeter={true} />
            </div>

            {/* Model Confidence */}
            <div className="space-y-2">
              <span className="text-[11px] font-medium text-[var(--ink-400)] uppercase tracking-wider block">
                Model Certainty & Routing
              </span>
              <ConfidenceIndicator
                confidence={assessment.confidence}
                size="md"
                showLabel={true}
              />
              <span className="text-[11px] text-[var(--ink-600)] block">
                {assessment.confidence >= 85
                  ? "✓ Exceeds 85% autonomous decision threshold"
                  : "⚠ Dispatched to secondary verification queue"}
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Policy Action Banner */}
      <Card className="bg-[var(--surface-sunken)] p-4 border-[var(--border)]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-[var(--ink-900)] uppercase tracking-wider">
                Assigned Defense Action:
              </span>
              <PolicyBadge policy={currentOrder.policy} />
            </div>
            <p className="text-xs text-[var(--ink-600)] leading-relaxed">
              {policyDecision.rationale}
            </p>
          </div>

          <div className="shrink-0 p-3 rounded-[6px] bg-white border border-[var(--border)] text-right">
            <span className="text-[10px] text-[var(--ink-400)] uppercase tracking-wider block">
              Estimated Margin Protected
            </span>
            <span className="font-mono text-base font-bold text-[var(--success)] tabular-nums block">
              ₹{policyDecision.protectedMargin.toLocaleString("en-IN")}
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
            3 Signal Domains Inspected
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SignalList
            category="customer"
            title="Customer History Signals"
            signals={assessment.signals.customer}
          />
          <SignalList
            category="cart"
            title="Cart Composition Signals"
            signals={assessment.signals.cart}
          />
          <SignalList
            category="product"
            title="Catalog Risk Signals"
            signals={assessment.signals.product}
          />
        </div>
      </section>

      {/* Machine Learning Model Feature Importance Breakdown */}
      <Card>
        <CardHeader
          title="ML Model Inference Breakdown"
          subtitle={`Model: ${assessment.mlPrediction.modelName} (${assessment.mlPrediction.modelVersion})`}
          badge={
            <span className="font-mono text-xs bg-[var(--surface-sunken)] border border-[var(--border)] px-2 py-0.5 rounded-[4px] text-[var(--ink-900)]">
              Class: {assessment.mlPrediction.predictedCategory}
            </span>
          }
        />

        <div className="space-y-4">
          <p className="text-xs text-[var(--ink-600)] leading-relaxed">
            The XGBoost ensemble evaluated normalized feature weights across 42 historical and real-time checkout attributes. Below are the top feature drivers influencing this score:
          </p>

          <div className="space-y-3">
            {assessment.mlPrediction.features.map((feat, idx) => (
              <div
                key={idx}
                className="p-3 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] flex flex-col sm:flex-row sm:items-center justify-between gap-2"
              >
                <div className="space-y-0.5 max-w-lg">
                  <div className="flex items-center gap-2">
                    <code className="font-mono text-xs font-semibold text-[var(--ink-900)]">
                      {feat.feature}
                    </code>
                    <span
                      className={`text-[10px] font-semibold px-1.5 py-0.2 rounded-[3px] uppercase ${
                        feat.impact === "positive"
                          ? "bg-[var(--danger-soft)] text-[var(--danger)]"
                          : "bg-[var(--success-soft)] text-[var(--success)]"
                      }`}
                    >
                      {feat.impact === "positive"
                        ? "+ Increases Risk"
                        : "- Mitigates Risk"}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--ink-600)]">
                    {feat.description}
                  </p>
                </div>

                <div className="shrink-0 flex items-center gap-3 self-end sm:self-center">
                  <div className="w-24 bg-[var(--surface)] h-2 rounded-[3px] overflow-hidden border border-[var(--border)]">
                    <div
                      className={`h-full ${
                        feat.impact === "positive"
                          ? "bg-[var(--danger)]"
                          : "bg-[var(--success)]"
                      }`}
                      style={{ width: `${feat.importance * 100}%` }}
                    />
                  </div>
                  <span className="font-mono text-xs font-semibold text-[var(--ink-900)] tabular-nums w-12 text-right">
                    {(feat.importance * 100).toFixed(0)}% wt
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Agent Investigation History (Reusing Signature AgentTrace Component) */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
            Agent Investigation History
          </h2>
          <span className="text-xs text-[var(--ink-400)]">
            LangGraph Orchestrated Trace
          </span>
        </div>

        <AgentTrace
          steps={traceSteps}
          orderId={currentOrder.id}
          title={`Execution Trace for ${currentOrder.id}`}
          subtitle="Chronological sequence of agent tool calls, ML inference, router checks, and final deterministic validation"
        />
      </section>
    </PageContainer>
  );
}
