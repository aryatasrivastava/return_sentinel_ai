import React from "react";
import { Card, CardHeader } from "../ui/Card";
import { ShieldCheckIcon } from "../ui/Icons";

export interface MerchantProtectionSummaryProps {
  marginProtected: number;
  frictionScore: number; // e.g. 2.4 / 10
  currency?: string;
  className?: string;
}

export function MerchantProtectionSummary({
  marginProtected = 8420,
  frictionScore = 2.4,
  currency = "₹",
  className = "",
}: MerchantProtectionSummaryProps) {
  return (
    <Card className={className}>
      <CardHeader
        title="Merchant Protection Summary"
        subtitle="Margin retention balanced with customer checkout experience"
        badge={
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-[var(--success)] bg-[var(--success-soft)] px-2 py-0.5 rounded-[4px] border border-[#bfe7db]">
            <ShieldCheckIcon size={12} />
            Optimized Defense
          </span>
        }
      />

      <div className="space-y-4">
        <p className="text-xs text-[var(--ink-600)] leading-relaxed">
          ReturnSentinel prevented <strong className="text-[var(--ink-900)]">₹8,420</strong> in return logistics and liquidation losses over the past 7 days by dynamically substituting cash refund liabilities with instant exchanges and store credits on 24 flagged carts.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div className="p-3 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1">
            <span className="text-[11px] font-medium text-[var(--ink-400)] uppercase tracking-wider block">
              Direct Margin Protected
            </span>
            <div className="flex items-baseline gap-1">
              <span className="font-mono text-xs font-normal text-[var(--ink-600)]">
                {currency}
              </span>
              <span className="font-mono text-xl font-semibold text-[var(--success)] tabular-nums">
                {marginProtected.toLocaleString("en-IN")}
              </span>
            </div>
            <span className="text-[11px] text-[var(--ink-600)] block">
              From 18 high-risk cart intercepts
            </span>
          </div>

          <div className="p-3 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1">
            <span className="text-[11px] font-medium text-[var(--ink-400)] uppercase tracking-wider block">
              Estimated Buyer Friction Index
            </span>
            <div className="flex items-baseline gap-1">
              <span className="font-mono text-xl font-semibold text-[var(--ink-900)] tabular-nums">
                {frictionScore}
              </span>
              <span className="font-mono text-xs font-normal text-[var(--ink-400)]">
                /10
              </span>
            </div>
            <span className="text-[11px] text-[var(--success)] block font-medium">
              Well below 4.0 churn warning threshold
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
