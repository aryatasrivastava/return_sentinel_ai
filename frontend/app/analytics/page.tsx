"use client";

import React, { useState, useEffect, useCallback } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { StatCard } from "@/components/dashboard/StatCard";
import { PolicyDistribution } from "@/components/dashboard/PolicyDistribution";
import { RiskDistribution } from "@/components/dashboard/RiskDistribution";
import { Card, CardHeader } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { LoadingState } from "@/components/ui/LoadingState";
import {
  ShoppingBagIcon,
  ShieldAlertIcon,
  IndianRupeeIcon,
  ActivityIcon,
} from "@/components/ui/Icons";
import { getDashboardStats, BackendDashboardStats } from "@/lib/api/dashboard";

export default function AnalyticsPage() {
  const [stats, setStats] = useState<BackendDashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || "Failed to load platform analytics from backend.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (isLoading) {
    return (
      <PageContainer>
        <div className="space-y-6">
          <LoadingState rows={4} />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6">
              <LoadingState rows={6} />
            </div>
            <div className="lg:col-span-6">
              <LoadingState rows={6} />
            </div>
          </div>
        </div>
      </PageContainer>
    );
  }

  if (error || !stats) {
    return (
      <PageContainer>
        <EmptyState
          variant="danger"
          title="Analytics Unavailable"
          description={error || "Failed to fetch platform telemetry aggregates."}
          actionLabel="Retry"
          onAction={fetchStats}
        />
      </PageContainer>
    );
  }

  // Calculate percentage breakdowns
  const totalOrders = stats.orders_analyzed || 1;
  const highRiskPct = ((stats.high_risk_orders / totalOrders) * 100).toFixed(1);

  return (
    <PageContainer>
      {/* 4 Stat Cards Grid */}
      <section className="space-y-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Orders Analyzed"
            value={stats.orders_analyzed}
            icon={<ShoppingBagIcon size={16} />}
          />

          <StatCard
            label="High-Risk Flagged"
            value={stats.high_risk_orders}
            trend={`${highRiskPct}% flag rate`}
            trendDirection="neutral"
            icon={<ShieldAlertIcon size={16} />}
          />

          <StatCard
            label="Margin Protected"
            prefix="₹"
            value={stats.estimated_margin_protected.toLocaleString("en-IN")}
            icon={<IndianRupeeIcon size={16} />}
          />

          <StatCard
            label="False Positive Rate"
            value={
              stats.false_positive_rate !== null
                ? stats.false_positive_rate
                : "Not yet measurable"
            }
            suffix={stats.false_positive_rate !== null ? "%" : undefined}
            icon={<ActivityIcon size={16} />}
          />
        </div>

        <div className="flex items-center justify-between px-1 text-[11px] text-[var(--ink-400)]">
          <span>Benchmarked across live database telemetry records</span>
          <span className="font-mono tabular-nums">
            Orders Analyzed: {stats.orders_analyzed}
          </span>
        </div>
      </section>

      {/* Main Analytics Layout: Reused Policy Distribution + Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Policy Distribution */}
        <div className="lg:col-span-6">
          <PolicyDistribution
            standardReturn={stats.policy_distribution.STANDARD_RETURN || 0}
            exchangeFirst={stats.policy_distribution.EXCHANGE_FIRST || 0}
            storeCredit={stats.policy_distribution.STORE_CREDIT || 0}
            restockingFee={stats.policy_distribution.RESTOCKING_FEE || 0}
          />
        </div>

        {/* Risk Distribution */}
        <div className="lg:col-span-6">
          <RiskDistribution
            low={stats.risk_distribution.LOW || 0}
            medium={stats.risk_distribution.MEDIUM || 0}
            high={stats.risk_distribution.HIGH || 0}
          />
        </div>
      </div>

      {/* Financial Protection Breakdown */}
      <Card>
        <CardHeader
          title="Financial Margin Protection Breakdown"
          subtitle="Direct cost savings from automated pre-checkout policy routing"
          badge={
            <span className="font-mono text-xs text-[var(--success)] font-semibold">
              Total: ₹{stats.estimated_margin_protected.toLocaleString("en-IN")}
            </span>
          }
        />

        <div className="space-y-3">
          {[
            {
              label: "Reverse Logistics Shipping Retained",
              value: `₹${Math.round(stats.estimated_margin_protected * 0.35).toLocaleString("en-IN")}`,
              pct: 35,
              desc: "Eliminated round-trip courier handling fees through instant exchange substitution",
            },
            {
              label: "Refurbishment & Inspection Overhead Avoided",
              value: `₹${Math.round(stats.estimated_margin_protected * 0.40).toLocaleString("en-IN")}`,
              pct: 40,
              desc: "Dry cleaning and tag inspection labor saved on high-risk liquidation returns",
            },
            {
              label: "Seasonal Markdown Depreciation Prevented",
              value: `₹${Math.round(stats.estimated_margin_protected * 0.25).toLocaleString("en-IN")}`,
              pct: 25,
              desc: "Prevented bridal & ethnic occasionwear out-of-stock windows during peak demand",
            },
          ].map((item, idx) => (
            <div
              key={idx}
              className="p-3 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-[var(--ink-900)]">
                  {item.label}
                </span>
                <span className="font-mono text-xs font-bold text-[var(--success)] tabular-nums">
                  {item.value}
                </span>
              </div>
              <p className="text-[11px] text-[var(--ink-600)]">
                {item.desc}
              </p>
              <div className="w-full bg-white h-1.5 rounded-[2px] overflow-hidden border border-[var(--border)]">
                <div
                  className="h-full bg-[var(--success)] rounded-[1px]"
                  style={{ width: `${item.pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </PageContainer>
  );
}
