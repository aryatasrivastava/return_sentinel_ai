import React from "react";
import { Card } from "../ui/Card";
import { ArrowUpRightIcon, ArrowDownRightIcon } from "../ui/Icons";

export interface StatCardProps {
  label: string;
  value: string | number;
  trend?: string;
  trendDirection?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
  prefix?: string;
  suffix?: string;
  className?: string;
}

export function StatCard({
  label,
  value,
  trend,
  trendDirection = "up",
  icon,
  prefix,
  suffix,
  className = "",
}: StatCardProps) {
  return (
    <Card className={`flex flex-col justify-between ${className}`}>
      <div className="flex items-start justify-between gap-2 mb-3">
        <span className="text-[0.75rem] leading-[1rem] font-medium text-[var(--ink-400)] uppercase tracking-wider">
          {label}
        </span>
        {icon && (
          <div className="w-7 h-7 rounded-[6px] bg-[var(--surface-sunken)] text-[var(--accent)] flex items-center justify-center shrink-0">
            {icon}
          </div>
        )}
      </div>

      <div className="space-y-2">
        <div className="flex items-baseline gap-1">
          {prefix && (
            <span className="font-mono text-xl font-medium text-[var(--ink-600)]">
              {prefix}
            </span>
          )}
          <span className="font-mono font-medium text-[2rem] leading-[2.25rem] text-[var(--ink-900)] tabular-nums">
            {value}
          </span>
          {suffix && (
            <span className="font-mono text-sm font-normal text-[var(--ink-600)]">
              {suffix}
            </span>
          )}
        </div>

        {trend && (
          <div className="flex items-center gap-1 text-xs">
            {trendDirection === "up" ? (
              <ArrowUpRightIcon
                size={13}
                className="text-[var(--success)] shrink-0"
              />
            ) : trendDirection === "down" ? (
              <ArrowDownRightIcon
                size={13}
                className="text-[var(--accent)] shrink-0"
              />
            ) : null}
            <span
              className={`font-medium ${
                trendDirection === "up"
                  ? "text-[var(--success)]"
                  : "text-[var(--ink-600)]"
              }`}
            >
              {trend}
            </span>
          </div>
        )}
      </div>
    </Card>
  );
}
