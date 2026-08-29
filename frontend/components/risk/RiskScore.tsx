import React from "react";
import { RiskLevel } from "@/lib/types";

export interface RiskScoreProps {
  score: number; // 0 - 100
  size?: "md" | "lg";
  showMeter?: boolean;
  className?: string;
}

export function RiskScore({
  score,
  size = "md",
  showMeter = true,
  className = "",
}: RiskScoreProps) {
  let level: RiskLevel = "low";
  if (score >= 70) {
    level = "high";
  } else if (score >= 35) {
    level = "medium";
  }

  const colors = {
    low: {
      text: "text-[var(--success)]",
      bar: "bg-[var(--success)]",
      well: "bg-[var(--success-soft)]",
    },
    medium: {
      text: "text-[var(--warning)]",
      bar: "bg-[var(--warning)]",
      well: "bg-[var(--warning-soft)]",
    },
    high: {
      text: "text-[var(--danger)]",
      bar: "bg-[var(--danger)]",
      well: "bg-[var(--danger-soft)]",
    },
  };

  const current = colors[level];

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      <div className="flex items-baseline gap-1">
        <span
          className={`font-mono font-medium tabular-nums ${current.text} ${
            size === "lg"
              ? "text-[2rem] leading-[2.25rem]"
              : "text-[1.25rem] leading-[1.5rem]"
          }`}
        >
          {score}
        </span>
        <span className="font-mono text-xs text-[var(--ink-400)] font-normal">
          /100
        </span>
      </div>

      {showMeter && (
        <div className="w-full bg-[var(--surface-sunken)] h-1.5 rounded-[3px] overflow-hidden border border-[var(--border)]">
          <div
            className={`h-full rounded-[2px] transition-all duration-500 ${current.bar}`}
            style={{ width: `${Math.min(Math.max(score, 4), 100)}%` }}
          />
        </div>
      )}
    </div>
  );
}
