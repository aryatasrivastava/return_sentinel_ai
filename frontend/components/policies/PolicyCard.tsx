"use client";

import React, { useState } from "react";
import { PolicyDefinition } from "@/lib/types";
import { Card } from "../ui/Card";
import { PolicyBadge } from "./PolicyBadge";

export interface PolicyCardProps {
  policy: PolicyDefinition;
  className?: string;
}

export function PolicyCard({ policy, className = "" }: PolicyCardProps) {
  const [isEnabled, setIsEnabled] = useState(policy.isEnabled);

  const getFrictionColor = (value: number) => {
    if (value <= 3) return "bg-[var(--success)]";
    if (value <= 6) return "bg-[var(--warning)]";
    return "bg-[var(--danger)]";
  };

  const getProtectionColor = (value: number) => {
    if (value >= 7) return "bg-[var(--success)]";
    if (value >= 4) return "bg-[var(--warning)]";
    return "bg-[var(--danger)]";
  };

  return (
    <Card className={`flex flex-col justify-between ${className}`}>
      <div className="space-y-4">
        {/* Header with Title, Badge & Toggle */}
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
                {policy.title}
              </h3>
              <PolicyBadge policy={policy.id} size="sm" />
            </div>
            <p className="text-xs text-[var(--ink-600)] leading-relaxed">
              {policy.description}
            </p>
          </div>

          {/* Toggle Switch */}
          <button
            type="button"
            role="switch"
            aria-checked={isEnabled}
            onClick={() => setIsEnabled(!isEnabled)}
            className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] ${
              isEnabled ? "bg-[var(--accent)]" : "bg-[var(--ink-400)]/40"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${
                isEnabled ? "translate-x-4" : "translate-x-0"
              }`}
            />
          </button>
        </div>

        {/* Trigger Condition Well */}
        <div className="p-3 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] space-y-1">
          <span className="text-[11px] font-medium text-[var(--ink-400)] uppercase tracking-wider block">
            Activation Trigger
          </span>
          <span className="font-mono text-xs text-[var(--ink-900)] block font-medium">
            {policy.triggerCondition}
          </span>
        </div>

        {/* Target Profile Description */}
        <div className="text-xs text-[var(--ink-600)] space-y-1">
          <span className="font-medium text-[var(--ink-900)]">Recommended For: </span>
          <span>{policy.recommendedFor}</span>
        </div>
      </div>

      {/* Labeled Meters for Friction & Protection */}
      <div className="mt-5 pt-4 border-t border-[var(--border)] space-y-3">
        {/* Customer Friction Meter */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[var(--ink-600)] font-medium">
              Customer Friction:
            </span>
            <span className="font-mono text-[var(--ink-900)] font-medium tabular-nums">
              {policy.customerFriction} ({policy.customerFrictionValue}/10)
            </span>
          </div>
          <div className="w-full bg-[var(--surface-sunken)] h-2 rounded-[3px] overflow-hidden border border-[var(--border)]">
            <div
              className={`h-full rounded-[2px] ${getFrictionColor(
                policy.customerFrictionValue
              )}`}
              style={{ width: `${policy.customerFrictionValue * 10}%` }}
            />
          </div>
        </div>

        {/* Merchant Protection Meter */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[var(--ink-600)] font-medium">
              Margin Defense Level:
            </span>
            <span className="font-mono text-[var(--ink-900)] font-medium tabular-nums">
              {policy.merchantProtection} ({policy.merchantProtectionValue}/10)
            </span>
          </div>
          <div className="w-full bg-[var(--surface-sunken)] h-2 rounded-[3px] overflow-hidden border border-[var(--border)]">
            <div
              className={`h-full rounded-[2px] ${getProtectionColor(
                policy.merchantProtectionValue
              )}`}
              style={{ width: `${policy.merchantProtectionValue * 10}%` }}
            />
          </div>
        </div>
      </div>
    </Card>
  );
}
