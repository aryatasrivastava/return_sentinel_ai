"use client";

import React, { useState, useEffect, useCallback } from "react";
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
  ChevronLeftIcon,
} from "@/components/ui/Icons";
import { getOrders, BackendOrderListItem } from "@/lib/api/orders";
import { mapBackendOrderToOrder } from "@/lib/transforms/orderMapper";

const PAGE_SIZE = 20;

export default function OrdersPage() {
  const [orders, setOrders] = useState<BackendOrderListItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState<string>("ALL");
  const [policyFilter, setPolicyFilter] = useState<string>("ALL");
  const [offset, setOffset] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getOrders({
        limit: PAGE_SIZE,
        offset,
        risk_level: riskFilter !== "ALL" ? riskFilter : undefined,
        policy_type: policyFilter !== "ALL" ? policyFilter : undefined,
      });
      setOrders(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch orders from backend.");
    } finally {
      setIsLoading(false);
    }
  }, [offset, riskFilter, policyFilter]);

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const handleRiskChange = (val: string) => {
    setRiskFilter(val);
    setOffset(0);
  };

  const handlePolicyChange = (val: string) => {
    setPolicyFilter(val);
    setOffset(0);
  };

  const resetFilters = () => {
    setSearchQuery("");
    setRiskFilter("ALL");
    setPolicyFilter("ALL");
    setOffset(0);
  };

  const mappedOrders = orders.map(mapBackendOrderToOrder);
  const hasPrevious = offset > 0;
  const hasNext = orders.length === PAGE_SIZE;

  return (
    <PageContainer>
      {/* Top Filter & Action Bar */}
      <Card className="p-4 space-y-3">
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
          {/* Search Input (Visual presence with status note) */}
          <div className="relative flex-1">
            <SearchIcon
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--ink-400)]"
            />
            <input
              type="text"
              placeholder="Search orders... (Text search pending backend search endpoint)"
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
                onChange={(e) => handleRiskChange(e.target.value)}
                className="bg-transparent text-xs font-medium text-[var(--ink-900)] focus:outline-none cursor-pointer"
              >
                <option value="ALL">All Risk Levels</option>
                <option value="LOW">Low Risk</option>
                <option value="MEDIUM">Medium Risk</option>
                <option value="HIGH">High Risk</option>
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
                onChange={(e) => handlePolicyChange(e.target.value)}
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
            {(riskFilter !== "ALL" || policyFilter !== "ALL" || searchQuery) && (
              <Button variant="ghost" size="sm" onClick={resetFilters}>
                Clear
              </Button>
            )}
          </div>
        </div>

        {/* Telemetry and Pagination Summary */}
        <div className="flex items-center justify-between pt-2 border-t border-[var(--border)]/60 text-[11px] text-[var(--ink-400)]">
          <span>
            Connected to real Postgres orders ledger (Page offset: {offset})
          </span>
          <span className="font-mono tabular-nums">
            Showing {orders.length} order{orders.length === 1 ? "" : "s"} on this page
          </span>
        </div>
      </Card>

      {/* Orders Table Display */}
      {isLoading ? (
        <LoadingState rows={8} />
      ) : error ? (
        <EmptyState
          variant="danger"
          title="Failed to Load Orders"
          description={error}
          actionLabel="Retry"
          onAction={fetchOrders}
        />
      ) : orders.length === 0 ? (
        <EmptyState
          title="No orders found"
          description="No analyzed orders matched your selected filters in the database. Try broadening your filter parameters."
          actionLabel="Reset all filters"
          onAction={resetFilters}
        />
      ) : (
        <div className="space-y-4">
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
                {mappedOrders.map((order) => {
                  const rawId = order.id.replace(/^ORD-/, "");
                  return (
                    <TableRow key={order.id}>
                      {/* Order ID */}
                      <TableCell mono className="font-medium text-[var(--accent)]">
                        <Link
                          href={`/risk-analysis?orderId=${rawId}`}
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
                          </div>
                        </div>
                      </TableCell>

                      {/* Cart Value */}
                      <TableCell mono>
                        {order.currency}
                        {order.cartValue.toLocaleString("en-IN")}
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
                              order.confidence >= 50
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
                        {order.createdAt}
                      </TableCell>

                      {/* Actions */}
                      <TableCell className="text-right">
                        <Link
                          href={`/risk-analysis?orderId=${rawId}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-[4px] bg-[var(--surface-sunken)] hover:bg-[var(--accent-soft)] hover:text-[var(--accent)] text-xs font-medium text-[var(--ink-900)] transition-colors border border-[var(--border)]"
                        >
                          <span>Analyze</span>
                          <ChevronRightIcon size={12} />
                        </Link>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Real Pagination Controls */}
          <div className="flex items-center justify-between px-2 py-1">
            <Button
              variant="secondary"
              size="sm"
              disabled={!hasPrevious}
              onClick={() => setOffset((prev) => Math.max(0, prev - PAGE_SIZE))}
              className="flex items-center gap-1"
            >
              <ChevronLeftIcon size={14} />
              Previous
            </Button>

            <span className="text-xs text-[var(--ink-600)] font-mono">
              Offset {offset} - {offset + orders.length}
            </span>

            <Button
              variant="secondary"
              size="sm"
              disabled={!hasNext}
              onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
              className="flex items-center gap-1"
            >
              Next
              <ChevronRightIcon size={14} />
            </Button>
          </div>
        </div>
      )}
    </PageContainer>
  );
}
