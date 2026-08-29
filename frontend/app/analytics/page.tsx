import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { StatCard } from "@/components/dashboard/StatCard";
import { PolicyDistribution } from "@/components/dashboard/PolicyDistribution";
import { Card, CardHeader } from "@/components/ui/Card";
import {
  ShoppingBagIcon,
  ShieldAlertIcon,
  IndianRupeeIcon,
  ActivityIcon,
} from "@/components/ui/Icons";
import { mockDashboardStats } from "@/lib/mock-data";

export default function AnalyticsPage() {
  const stats = mockDashboardStats;

  return (
    <PageContainer>
      {/* 5 Stat Cards Grid */}
      <section className="space-y-2">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            label="Orders Analyzed"
            value={stats.ordersAnalyzed}
            trend="+18.4% volume"
            trendDirection="up"
            icon={<ShoppingBagIcon size={16} />}
          />

          <StatCard
            label="Return Abuse Rate"
            value="14.2"
            suffix="%"
            trend="-3.8% vs last month"
            trendDirection="down"
            icon={<ActivityIcon size={16} />}
          />

          <StatCard
            label="High-Risk Flagged"
            value={stats.highRiskOrders}
            trend="14.2% intercept rate"
            trendDirection="neutral"
            icon={<ShieldAlertIcon size={16} />}
          />

          <StatCard
            label="False Positives"
            value={stats.falsePositiveRate}
            suffix="%"
            trend="-0.4% improvement"
            trendDirection="down"
            icon={<ActivityIcon size={16} />}
          />

          <StatCard
            label="Margin Protected"
            prefix="₹"
            value={stats.marginProtected.toLocaleString("en-IN")}
            trend="+₹2,180 this week"
            trendDirection="up"
            icon={<IndianRupeeIcon size={16} />}
          />
        </div>

        <div className="flex items-center justify-between px-1 text-[11px] text-[var(--ink-400)]">
          <span>Benchmarked across 30-day merchant telemetry window</span>
          <span className="font-mono tabular-nums">Precision: 96.8%</span>
        </div>
      </section>

      {/* Main Analytics Layout: Reused Policy Distribution + Financial Protection Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Policy Distribution (Reused Component) */}
        <div className="lg:col-span-6">
          <PolicyDistribution
            standardReturn={stats.policyDistribution.standardReturn}
            exchangeFirst={stats.policyDistribution.exchangeFirst}
            storeCredit={stats.policyDistribution.storeCredit}
            restockingFee={stats.policyDistribution.restockingFee}
          />
        </div>

        {/* Financial Protection Breakdown */}
        <div className="lg:col-span-6">
          <Card>
            <CardHeader
              title="Financial Margin Protection Breakdown"
              subtitle="Direct cost savings from automated pre-checkout policy routing"
              badge={
                <span className="font-mono text-xs text-[var(--success)] font-semibold">
                  Total: ₹8,420
                </span>
              }
            />

            <div className="space-y-3">
              {[
                {
                  label: "Reverse Logistics Shipping Saved",
                  value: "₹2,740",
                  pct: 32,
                  desc: "Eliminated round-trip courier and handling fees for size bracketing",
                },
                {
                  label: "Dry Cleaning & Inspection Overhead Avoided",
                  value: "₹3,180",
                  pct: 38,
                  desc: "Occasionwear garment refurbishment and tag re-inspection labor",
                },
                {
                  label: "Seasonal Markdown Depreciation Saved",
                  value: "₹2,500",
                  pct: 30,
                  desc: "Prevented bridal wear out-of-stock window during peak season",
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
        </div>
      </div>

      {/* Category Risk Exposure Matrix */}
      <Card>
        <CardHeader
          title="Catalog Category Vulnerability Index"
          subtitle="Return frequency and risk concentration across merchant catalog segments"
        />

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            {
              category: "Ethnic Occasionwear",
              risk: "High",
              returnRate: "38.2%",
              color: "bg-[var(--danger)]",
              topIssue: "Size Bracketing (M/L) & Wardrobing",
            },
            {
              category: "Bridal & Festive Wear",
              risk: "High",
              returnRate: "52.0%",
              color: "bg-[var(--danger)]",
              topIssue: "Single-Event Usage & Post-Event Returns",
            },
            {
              category: "Western Casualwear",
              risk: "Medium",
              returnRate: "21.5%",
              color: "bg-[var(--warning)]",
              topIssue: "Fit Uncertainty & Fabric Feel",
            },
            {
              category: "Menswear Basics",
              risk: "Low",
              returnRate: "12.1%",
              color: "bg-[var(--success)]",
              topIssue: "Minimal Returns; Repeat Reorders",
            },
          ].map((cat, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-2 flex flex-col justify-between"
            >
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-[var(--ink-900)]">
                    {cat.category}
                  </span>
                  <span
                    className={`text-[10px] font-semibold px-1.5 py-0.2 rounded-[3px] uppercase ${
                      cat.risk === "High"
                        ? "bg-[var(--danger-soft)] text-[var(--danger)]"
                        : cat.risk === "Medium"
                        ? "bg-[var(--warning-soft)] text-[var(--warning)]"
                        : "bg-[var(--success-soft)] text-[var(--success)]"
                    }`}
                  >
                    {cat.risk}
                  </span>
                </div>

                <div className="flex items-baseline gap-1 pt-1">
                  <span className="font-mono text-xl font-bold text-[var(--ink-900)] tabular-nums">
                    {cat.returnRate}
                  </span>
                  <span className="text-[11px] text-[var(--ink-400)]">
                    avg return rate
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-[var(--border)]">
                <span className="text-[11px] text-[var(--ink-600)] block">
                  <strong>Dominant pattern:</strong> {cat.topIssue}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </PageContainer>
  );
}
