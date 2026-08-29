import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { StatCard } from "@/components/dashboard/StatCard";
import { AgentTrace } from "@/components/dashboard/AgentTrace";
import { DecisionTable } from "@/components/dashboard/DecisionTable";
import { RiskDistribution } from "@/components/dashboard/RiskDistribution";
import { PolicyDistribution } from "@/components/dashboard/PolicyDistribution";
import { MerchantProtectionSummary } from "@/components/dashboard/MerchantProtectionSummary";
import {
  ShoppingBagIcon,
  ShieldAlertIcon,
  IndianRupeeIcon,
  ActivityIcon,
} from "@/components/ui/Icons";
import {
  mockDashboardStats,
  mockOrders,
  defaultSignatureTrace,
} from "@/lib/mock-data";

export default function DashboardPage() {
  const stats = mockDashboardStats;

  return (
    <PageContainer>
      {/* 4-Up Stat Cards Row */}
      <section className="space-y-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Orders Analyzed"
            value={stats.ordersAnalyzed}
            trend={stats.trends.ordersAnalyzedDelta}
            trendDirection="up"
            icon={<ShoppingBagIcon size={16} />}
          />

          <StatCard
            label="High-Risk Flagged"
            value={stats.highRiskOrders}
            trend={stats.trends.highRiskDelta}
            trendDirection="down"
            icon={<ShieldAlertIcon size={16} />}
          />

          <StatCard
            label="Est. Margin Protected"
            prefix="₹"
            value={stats.marginProtected.toLocaleString("en-IN")}
            trend={stats.trends.marginDelta}
            trendDirection="up"
            icon={<IndianRupeeIcon size={16} />}
          />

          <StatCard
            label="False Positive Rate"
            value={stats.falsePositiveRate}
            suffix="%"
            trend={stats.trends.falsePositiveDelta}
            trendDirection="down"
            icon={<ActivityIcon size={16} />}
          />
        </div>

        {/* Demo Data Disclaimer */}
        <div className="flex items-center justify-between px-1 text-[11px] text-[var(--ink-400)]">
          <span>
            Showing simulated merchant benchmark data (Order session telemetry: active)
          </span>
          <span className="font-mono tabular-nums">
            Sync latency: 24ms
          </span>
        </div>
      </section>

      {/* Main Grid: Signature Agent Decision Trace + Distributions */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Signature Agent Decision Trace (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <AgentTrace
            steps={defaultSignatureTrace}
            orderId="ORD-9421"
            title="Live Agent Decision Trace"
            subtitle="Autonomous checkout risk investigation sequence in real-time"
          />

          {/* Merchant Protection Summary */}
          <MerchantProtectionSummary
            marginProtected={stats.marginProtected}
            frictionScore={2.4}
          />
        </div>

        {/* Right Column: Visualizations & Recent Decisions (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <RiskDistribution
            low={stats.riskDistribution.low}
            medium={stats.riskDistribution.medium}
            high={stats.riskDistribution.high}
          />

          <PolicyDistribution
            standardReturn={stats.policyDistribution.standardReturn}
            exchangeFirst={stats.policyDistribution.exchangeFirst}
            storeCredit={stats.policyDistribution.storeCredit}
            restockingFee={stats.policyDistribution.restockingFee}
          />
        </div>
      </div>

      {/* Recent AI Decisions Table Row */}
      <section>
        <DecisionTable orders={mockOrders} />
      </section>
    </PageContainer>
  );
}
