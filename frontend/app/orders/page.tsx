"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card } from "@/components/ui/Card";
import {
  TableContainer,
  Table,
  TableHead,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
} from "@/components/ui/Table";
import { RiskBadge } from "@/components/risk/RiskBadge";
import { PolicyBadge } from "@/components/policies/PolicyBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
import {
  SearchIcon,
  FilterIcon,
  ChevronRightIcon,
} from "@/components/ui/Icons";
import { mockOrders } from "@/lib/mock-data";

export default function OrdersPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState<string>("ALL");
  const [policyFilter, setPolicyFilter] = useState<string>("ALL");

  // Demonstration flags for empty / loading states (can be toggled during QA)
  const [demoState, setDemoState] = useState<"normal" | "empty" | "loading">(
    "normal"
  );

  /*
   * FILTERING LOGIC:
   * Structured for clean transition to real backend/API layer.
   * When integrating a real API, replace this client filter with:
   * const { data: orders, isLoading } = useOrdersQuery({ search, risk, policy });
   */
  const filteredOrders = useMemo(() => {
    return mockOrders.filter((order) => {
      // 1. Text Search Filter (Order ID, Customer Name, Customer Email)
      if (searchQuery.trim() !== "") {
        const q = searchQuery.toLowerCase();
        const matchesId = order.id.toLowerCase().includes(q);
        const matchesName = order.customer.name.toLowerCase().includes(q);
        const matchesEmail = order.customer.email.toLowerCase().includes(q);
        if (!matchesId && !matchesName && !matchesEmail) return false;
      }

      // 2. Risk Level Filter
      if (riskFilter !== "ALL" && order.riskLevel !== riskFilter) {
        return false;
      }

      // 3. Policy Filter
      if (policyFilter !== "ALL" && order.policy !== policyFilter) {
        return false;
      }

      return true;
    });
  }, [searchQuery, riskFilter, policyFilter]);

  const resetFilters = () => {
    setSearchQuery("");
    setRiskFilter("ALL");
    setPolicyFilter("ALL");
    setDemoState("normal");
  };

  return (
    <PageContainer>
      {/* Top Filter & Action Bar */}
      <Card className="p-4 space-y-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          {/* Search Input */}
          <div className="relative flex-1">
            <SearchIcon
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--ink-400)]"
            />
            <input
              type="text"
              placeholder="Search by Order ID, customer name, or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] text-xs text-[var(--ink-900)] placeholder-[var(--ink-400)] focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring)] transition-all"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
            {/* Risk Filter */}
            <div className="flex items-center gap-1.5 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] px-2.5 py-1.5">
              <FilterIcon size={14} className="text-[var(--ink-400)] shrink-0" />
              <label htmlFor="risk-select" className="text-xs text-[var(--ink-600)] font-medium">
                Risk:
              </label>
              <select
                id="risk-select"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="bg-transparent text-xs font-medium text-[var(--ink-900)] focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Risk Levels</option>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
              </select>
            </div>

            {/* Policy Filter */}
            <div className="flex items-center gap-1.5 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] px-2.5 py-1.5">
              <label htmlFor="policy-select" className="text-xs text-[var(--ink-600)] font-medium">
                Policy:
              </label>
              <select
                id="policy-select"
                value={policyFilter}
                onChange={(e) => setPolicyFilter(e.target.value)}
                className="bg-transparent text-xs font-medium text-[var(--ink-900)] focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Policies</option>
                <option value="STANDARD_RETURN">Standard Return</option>
                <option value="EXCHANGE_FIRST">Exchange First</option>
                <option value="STORE_CREDIT">Store Credit</option>
                <option value="RESTOCKING_FEE">Restocking Fee</option>
              </select>
            </div>

            {/* Clear Filters Button */}
            {(searchQuery || riskFilter !== "ALL" || policyFilter !== "ALL") && (
              <Button variant="ghost" size="sm" onClick={resetFilters}>
                Clear
              </Button>
            )}
          </div>
        </div>

        {/* State Simulator Bar (Demo helpers to showcase Loading / Empty state UI) */}
        <div className="flex items-center justify-between pt-2 border-t border-[var(--border)]/60 text-[11px] text-[var(--ink-400)]">
          <div className="flex items-center gap-2">
            <span>QA UI State preview:</span>
            <button
              type="button"
              onClick={() => setDemoState("normal")}
              className={`px-2 py-0.5 rounded-[4px] border ${
                demoState === "normal"
                  ? "bg-[var(--accent)] text-white border-[var(--accent)] font-medium"
                  : "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--ink-600)]"
              }`}
            >
              Normal Feed
            </button>
            <button
              type="button"
              onClick={() => setDemoState("loading")}
              className={`px-2 py-0.5 rounded-[4px] border ${
                demoState === "loading"
                  ? "bg-[var(--accent)] text-white border-[var(--accent)] font-medium"
                  : "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--ink-600)]"
              }`}
            >
              Loading Skeleton
            </button>
            <button
              type="button"
              onClick={() => setDemoState("empty")}
              className={`px-2 py-0.5 rounded-[4px] border ${
                demoState === "empty"
                  ? "bg-[var(--accent)] text-white border-[var(--accent)] font-medium"
                  : "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--ink-600)]"
              }`}
            >
              Empty State
            </button>
          </div>

          <span className="font-mono tabular-nums">
            Showing {filteredOrders.length} of {mockOrders.length} orders
          </span>
        </div>
      </Card>

      {/* Orders Table Display */}
      {demoState === "loading" ? (
        <LoadingState rows={6} />
      ) : demoState === "empty" || filteredOrders.length === 0 ? (
        <EmptyState
          title="No orders found"
          description="No analyzed orders matched your search criteria or selected filters. Try broadening your filter parameters."
          actionLabel="Reset all filters"
          onAction={resetFilters}
        />
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <tr>
                <TableHeaderCell>Order ID</TableHeaderCell>
                <TableHeaderCell>Customer</TableHeaderCell>
                <TableHeaderCell>Cart Value</TableHeaderCell>
                <TableHeaderCell>Risk Score</TableHeaderCell>
                <TableHeaderCell>Confidence</TableHeaderCell>
                <TableHeaderCell>Assigned Policy</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
                <TableHeaderCell>Evaluated At</TableHeaderCell>
                <TableHeaderCell className="text-right">Actions</TableHeaderCell>
              </tr>
            </TableHead>
            <TableBody>
              {filteredOrders.map((order) => (
                <TableRow key={order.id}>
                  {/* Order ID */}
                  <TableCell mono className="font-medium text-[var(--accent)]">
                    <Link
                      href={`/risk-analysis?orderId=${order.id}`}
                      className="hover:underline"
                    >
                      {order.id}
                    </Link>
                  </TableCell>

                  {/* Customer */}
                  <TableCell>
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-center font-mono text-[11px] font-medium text-[var(--ink-900)]">
                        {order.customer.avatarInitials}
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="font-medium text-[var(--ink-900)] truncate max-w-[150px]">
                          {order.customer.name}
                        </span>
                        <span className="text-[11px] text-[var(--ink-400)] truncate max-w-[150px]">
                          {order.customer.email}
                        </span>
                      </div>
                    </div>
                  </TableCell>

                  {/* Cart Value */}
                  <TableCell mono>
                    {order.currency}
                    {order.cartValue.toLocaleString("en-IN")}
                    <span className="text-[11px] text-[var(--ink-400)] block font-normal">
                      {order.itemsCount} {order.itemsCount === 1 ? "item" : "items"}
                    </span>
                  </TableCell>

                  {/* Risk Score */}
                  <TableCell>
                    <div className="space-y-1">
                      <div className="flex items-center gap-1.5">
                        <RiskBadge level={order.riskLevel} size="sm" />
                      </div>
                      <span className="font-mono text-[11px] text-[var(--ink-600)] tabular-nums block">
                        Score: {order.riskScore}/100
                      </span>
                    </div>
                  </TableCell>

                  {/* Confidence */}
                  <TableCell mono>
                    <div className="flex items-center gap-1.5">
                      <span className="font-medium">{order.confidence}%</span>
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          order.confidence >= 85
                            ? "bg-[var(--success)]"
                            : "bg-[var(--warning)]"
                        }`}
                      />
                    </div>
                  </TableCell>

                  {/* Policy */}
                  <TableCell>
                    <PolicyBadge policy={order.policy} size="sm" />
                  </TableCell>

                  {/* Status */}
                  <TableCell>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-[4px] text-[11px] font-medium uppercase tracking-wider ${
                        order.status === "flagged"
                          ? "bg-[var(--danger-soft)] text-[var(--danger)] border border-[#f5c6c2]"
                          : order.status === "under_review"
                          ? "bg-[var(--warning-soft)] text-[var(--warning)] border border-[#f2debf]"
                          : "bg-[var(--surface-sunken)] text-[var(--ink-600)] border border-[var(--border)]"
                      }`}
                    >
                      {order.status.replace("_", " ")}
                    </span>
                  </TableCell>

                  {/* Evaluated At */}
                  <TableCell mono className="text-xs text-[var(--ink-600)]">
                    {order.createdAt.split(" ")[1]}
                    <span className="text-[10px] text-[var(--ink-400)] block">
                      {order.createdAt.split(" ")[0]}
                    </span>
                  </TableCell>

                  {/* Actions */}
                  <TableCell className="text-right">
                    <Link
                      href={`/risk-analysis?orderId=${order.id}`}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[4px] bg-[var(--surface-sunken)] hover:bg-[var(--accent-soft)] hover:text-[var(--accent)] text-xs font-medium text-[var(--ink-900)] transition-colors border border-[var(--border)]"
                    >
                      <span>Analyze</span>
                      <ChevronRightIcon size={12} />
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </PageContainer>
  );
}
