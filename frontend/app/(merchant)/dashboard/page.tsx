"use client";

import React, { useState, useEffect, useCallback } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { StatCard } from "@/components/dashboard/StatCard";
import { AgentTrace } from "@/components/dashboard/AgentTrace";
import { DecisionTable } from "@/components/dashboard/DecisionTable";
import { RiskDistribution } from "@/components/dashboard/RiskDistribution";
import { PolicyDistribution } from "@/components/dashboard/PolicyDistribution";
import { MerchantProtectionSummary } from "@/components/dashboard/MerchantProtectionSummary";
import { EmptyState } from "@/components/ui/EmptyState";
import { LoadingState } from "@/components/ui/LoadingState";
import {
  ShoppingBagIcon,
  ShieldAlertIcon,
  IndianRupeeIcon,
  ActivityIcon,
} from "@/components/ui/Icons";
import { getDashboardStats, BackendDashboardStats } from "@/lib/api/dashboard";
import { getOrders, getOrderDetail, BackendOrderListItem, BackendOrderDetail } from "@/lib/api/orders";
import { mapBackendOrderToOrder } from "@/lib/transforms/orderMapper";
import { traceToSteps } from "@/lib/transforms/traceToSteps";
import { AgentStep } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<BackendDashboardStats | null>(null);
  const [orders, setOrders] = useState<BackendOrderListItem[]>([]);
  const [featuredDetail, setFeaturedDetail] = useState<BackendOrderDetail | null>(null);
  const [featuredSteps, setFeaturedSteps] = useState<AgentStep[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [statsData, ordersData] = await Promise.all([
        getDashboardStats(),
        getOrders({ limit: 5 }),
      ]);

      setStats(statsData);
      setOrders(ordersData);

      // Fetch full decision trace for the most recent order if available
      if (ordersData.length > 0) {
        try {
          const detail = await getOrderDetail(ordersData[0].order_id);
          setFeaturedDetail(detail);
          setFeaturedSteps(traceToSteps(detail.trace_data));
        } catch {
          // Non-critical: if detailed trace fails, leave steps empty
        }
      }
    } catch (err: any) {
      setError(err.message || "Unable to connect to ReturnSentinel backend service.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (isLoading) {
    return (
      <PageContainer>
        <div className="space-y-6">
          <LoadingState rows={4} />
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-7">
              <LoadingState rows={6} />
            </div>
            <div className="lg:col-span-5">
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
          title="Backend Connection Failed"
          description={error || "Failed to load dashboard statistics from backend API."}
          actionLabel="Retry Connection"
          onAction={loadData}
        />
      </PageContainer>
    );
  }

  const mappedOrders = orders.map(mapBackendOrderToOrder);
  const featuredOrderId = featuredDetail ? `ORD-${featuredDetail.order_id}` : (orders[0] ? `ORD-${orders[0].order_id}` : "N/A");

  return (
    <PageContainer>
      {/* 4-Up Stat Cards Row */}
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
            icon={<ShieldAlertIcon size={16} />}
          />

          <StatCard
            label="Est. Margin Protected"
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

        {/* Real Backend Telemetry Bar */}
        <div className="flex items-center justify-between px-1 text-[11px] text-[var(--ink-400)]">
          <span>
            Real-time backend assessment pipeline • Live Postgres telemetry
          </span>
          <span className="font-mono tabular-nums">
            Orders Analyzed: {stats.orders_analyzed}
          </span>
        </div>
      </section>

      {/* Main Grid: Signature Agent Decision Trace + Distributions */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Signature Agent Decision Trace (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <AgentTrace
            steps={featuredSteps}
            orderId={featuredOrderId}
            title="Live Agent Decision Trace"
            subtitle="Autonomous checkout risk investigation sequence in real-time"
          />

          {/* Merchant Protection Summary */}
          <MerchantProtectionSummary
            marginProtected={stats.estimated_margin_protected}
            frictionScore={2.4}
          />
        </div>

        {/* Right Column: Visualizations & Distributions (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <RiskDistribution
            low={stats.risk_distribution.LOW || 0}
            medium={stats.risk_distribution.MEDIUM || 0}
            high={stats.risk_distribution.HIGH || 0}
          />

          <PolicyDistribution
            standardReturn={stats.policy_distribution.STANDARD_RETURN || 0}
            exchangeFirst={stats.policy_distribution.EXCHANGE_FIRST || 0}
            storeCredit={stats.policy_distribution.STORE_CREDIT || 0}
            restockingFee={stats.policy_distribution.RESTOCKING_FEE || 0}
          />
        </div>
      </div>

      {/* Recent AI Decisions Table Row */}
      <section>
        <DecisionTable orders={mappedOrders} />
      </section>
    </PageContainer>
  );
}
