"use client";

import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { PolicyCard } from "@/components/policies/PolicyCard";
import { Card, CardHeader } from "@/components/ui/Card";
import { mockPolicyDefinitions } from "@/lib/mock-data";
import {
  ShieldCheckIcon,
  PolicyIcon,
  CheckCircleIcon,
} from "@/components/ui/Icons";

export default function PoliciesPage() {
  const policies = mockPolicyDefinitions;

  return (
    <PageContainer>
      {/* Top Banner / Summary */}
      <Card className="bg-[var(--surface)] p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <PolicyIcon size={20} className="text-[var(--accent)]" />
              <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
                Active Return Policy Matrix
              </h2>
            </div>
            <p className="text-xs text-[var(--ink-600)] max-w-2xl leading-relaxed">
              ReturnSentinel deploys non-blocking defensive policies to intercept high-risk carts before checkout. Policies automatically activate based on deterministic merchant rules and real-time risk scores.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <div className="px-3 py-1.5 rounded-[6px] bg-[var(--success-soft)] border border-[#bfe7db] text-xs font-medium text-[var(--success)] flex items-center gap-1.5">
              <ShieldCheckIcon size={14} />
              Policy Engine: Enforcing
            </div>
          </div>
        </div>
      </Card>

      {/* Grid of Policy Cards */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
            Configured Policies ({policies.length})
          </h2>
          <span className="text-xs text-[var(--ink-400)]">
            Click toggle to enable / disable policies in simulation
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {policies.map((policy) => (
            <PolicyCard key={policy.id} policy={policy} />
          ))}
        </div>
      </section>

      {/* Deterministic Rule Engine Hierarchy Table */}
      <Card>
        <CardHeader
          title="Deterministic Policy Engine Rules"
          subtitle="Strict rule priority hierarchy evaluated by Policy Agent"
          badge={
            <span className="font-mono text-xs bg-[var(--surface-sunken)] border border-[var(--border)] px-2 py-0.5 rounded-[4px] text-[var(--ink-600)]">
              4 Active Rules
            </span>
          }
        />

        <div className="space-y-3">
          {[
            {
              id: "PR-401",
              name: "Severe Serial Returner Mitigation",
              condition: "Customer Lifetime Return Rate > 80% AND Lifetime Orders >= 10",
              action: "Enforce RESTOCKING_FEE (15%) on cash refund with 100% store credit waiver",
              priority: "Priority 1 (Highest)",
              status: "Active",
            },
            {
              id: "PR-402",
              name: "Duplicate SKU Size Bracketing Defense",
              condition: "Cart contains >= 2 sizes of same style SKU in high-risk apparel categories",
              action: "Enforce EXCHANGE_FIRST with instant courier swap guarantee",
              priority: "Priority 2",
              status: "Active",
            },
            {
              id: "PR-403",
              name: "High Frequency Returner Retention",
              condition: "Customer Return Rate 50% - 80% OR Account Flag: Repeat Wardrobing",
              action: "Enforce STORE_CREDIT only with +5% loyalty bonus credit",
              priority: "Priority 3",
              status: "Active",
            },
            {
              id: "PR-404",
              name: "Standard Checkout Pass-Through",
              condition: "Calculated Risk Score < 35 AND Zero Anomaly Signals",
              action: "Standard 14-Day Full Return Window with zero buyer friction",
              priority: "Priority 4 (Default)",
              status: "Active",
            },
          ].map((rule) => (
            <div
              key={rule.id}
              className="p-3.5 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div className="space-y-1 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-[var(--accent)]">
                    {rule.id}
                  </span>
                  <span className="text-xs font-semibold text-[var(--ink-900)]">
                    {rule.name}
                  </span>
                  <span className="text-[10px] font-semibold text-[var(--ink-400)] bg-white px-1.5 py-0.2 rounded-[3px] border border-[var(--border)]">
                    {rule.priority}
                  </span>
                </div>
                <p className="text-xs text-[var(--ink-600)]">
                  <strong>Trigger: </strong> {rule.condition}
                </p>
                <p className="text-xs text-[var(--ink-900)]">
                  <strong>Action: </strong> {rule.action}
                </p>
              </div>

              <div className="shrink-0 flex items-center gap-2 self-end md:self-center">
                <span className="inline-flex items-center gap-1 text-xs font-medium text-[var(--success)] bg-[var(--success-soft)] px-2 py-0.5 rounded-[4px] border border-[#bfe7db]">
                  <CheckCircleIcon size={12} />
                  {rule.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </PageContainer>
  );
}
