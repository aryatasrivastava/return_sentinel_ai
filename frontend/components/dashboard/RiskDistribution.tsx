import React from "react";
import { Card, CardHeader } from "../ui/Card";

export interface RiskDistributionProps {
  low: number;
  medium: number;
  high: number;
  className?: string;
}

export function RiskDistribution({
  low,
  medium,
  high,
  className = "",
}: RiskDistributionProps) {
  const total = low + medium + high || 1;
  const lowPct = Math.round((low / total) * 100);
  const medPct = Math.round((medium / total) * 100);
  const highPct = 100 - lowPct - medPct;

  return (
    <Card className={className}>
      <CardHeader
        title="Risk Distribution"
        subtitle="Breakdown of intercepted checkouts by calculated threat level"
      />

      <div className="space-y-4">
        {/* Proportional Segmented Stacked Bar */}
        <div className="w-full h-4 rounded-[4px] overflow-hidden flex bg-[var(--surface-sunken)] border border-[var(--border)]">
          <div
            className="h-full bg-[var(--success)] transition-all duration-300"
            style={{ width: `${lowPct}%` }}
            title={`Low Risk: ${low} (${lowPct}%)`}
          />
          <div
            className="h-full bg-[var(--warning)] transition-all duration-300"
            style={{ width: `${medPct}%` }}
            title={`Medium Risk: ${medium} (${medPct}%)`}
          />
          <div
            className="h-full bg-[var(--danger)] transition-all duration-300"
            style={{ width: `${highPct}%` }}
            title={`High Risk: ${high} (${highPct}%)`}
          />
        </div>

        {/* Legend with Counts and Percentages */}
        <div className="grid grid-cols-3 gap-2 pt-1">
          {/* Low Risk */}
          <div className="p-2.5 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[var(--success)] shrink-0" />
              <span className="text-[11px] font-medium text-[var(--ink-600)]">
                Low Risk
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="font-mono text-base font-semibold text-[var(--ink-900)] tabular-nums">
                {low}
              </span>
              <span className="font-mono text-xs text-[var(--ink-400)] tabular-nums">
                {lowPct}%
              </span>
            </div>
          </div>

          {/* Medium Risk */}
          <div className="p-2.5 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[var(--warning)] shrink-0" />
              <span className="text-[11px] font-medium text-[var(--ink-600)]">
                Medium Risk
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="font-mono text-base font-semibold text-[var(--ink-900)] tabular-nums">
                {medium}
              </span>
              <span className="font-mono text-xs text-[var(--ink-400)] tabular-nums">
                {medPct}%
              </span>
            </div>
          </div>

          {/* High Risk */}
          <div className="p-2.5 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[var(--danger)] shrink-0" />
              <span className="text-[11px] font-medium text-[var(--ink-600)]">
                High Risk
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="font-mono text-base font-semibold text-[var(--ink-900)] tabular-nums">
                {high}
              </span>
              <span className="font-mono text-xs text-[var(--ink-400)] tabular-nums">
                {highPct}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
