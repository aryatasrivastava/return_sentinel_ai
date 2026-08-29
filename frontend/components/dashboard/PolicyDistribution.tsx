import React from "react";
import { Card, CardHeader } from "../ui/Card";

export interface PolicyDistributionProps {
  standardReturn: number;
  exchangeFirst: number;
  storeCredit: number;
  restockingFee: number;
  className?: string;
}

export function PolicyDistribution({
  standardReturn,
  exchangeFirst,
  storeCredit,
  restockingFee,
  className = "",
}: PolicyDistributionProps) {
  const total =
    standardReturn + exchangeFirst + storeCredit + restockingFee || 1;

  const pStd = Math.round((standardReturn / total) * 100);
  const pExch = Math.round((exchangeFirst / total) * 100);
  const pStore = Math.round((storeCredit / total) * 100);
  const pRestock = 100 - pStd - pExch - pStore;

  const items = [
    {
      name: "Standard Return",
      count: standardReturn,
      pct: pStd,
      color: "bg-[var(--success)]",
      textColor: "text-[var(--success)]",
    },
    {
      name: "Exchange First",
      count: exchangeFirst,
      pct: pExch,
      color: "bg-[var(--accent)]",
      textColor: "text-[var(--accent)]",
    },
    {
      name: "Store Credit",
      count: storeCredit,
      pct: pStore,
      color: "bg-[var(--warning)]",
      textColor: "text-[var(--warning)]",
    },
    {
      name: "Restocking Fee",
      count: restockingFee,
      pct: pRestock,
      color: "bg-[var(--danger)]",
      textColor: "text-[var(--danger)]",
    },
  ];

  return (
    <Card className={className}>
      <CardHeader
        title="Policy Distribution"
        subtitle="Defensive return policies enforced by deterministic engine"
      />

      <div className="space-y-4">
        {/* Proportional Segmented Stacked Bar */}
        <div className="w-full h-4 rounded-[4px] overflow-hidden flex bg-[var(--surface-sunken)] border border-[var(--border)]">
          {items.map((item, idx) => (
            <div
              key={idx}
              className={`h-full ${item.color} transition-all duration-300`}
              style={{ width: `${item.pct}%` }}
              title={`${item.name}: ${item.count} (${item.pct}%)`}
            />
          ))}
        </div>

        {/* Legend Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          {items.map((item, idx) => (
            <div
              key={idx}
              className="p-2 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1"
            >
              <div className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${item.color} shrink-0`} />
                <span className="text-[11px] font-medium text-[var(--ink-600)] truncate">
                  {item.name}
                </span>
              </div>
              <div className="flex items-baseline justify-between">
                <span className="font-mono text-base font-semibold text-[var(--ink-900)] tabular-nums">
                  {item.count}
                </span>
                <span className="font-mono text-xs text-[var(--ink-400)] tabular-nums">
                  {item.pct}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
