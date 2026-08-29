import React from "react";

export interface ConfidenceIndicatorProps {
  confidence: number; // 0 - 100
  size?: "sm" | "md";
  showLabel?: boolean;
  className?: string;
}

export function ConfidenceIndicator({
  confidence,
  size = "md",
  showLabel = false,
  className = "",
}: ConfidenceIndicatorProps) {
  const isHigh = confidence >= 85;

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <div className="flex flex-col">
        <div className="flex items-center gap-1.5">
          <span
            className={`font-mono font-medium tabular-nums text-[var(--ink-900)] ${
              size === "md"
                ? "text-[1.25rem] leading-[1.5rem]"
                : "text-[0.8125rem] leading-[1.125rem]"
            }`}
          >
            {confidence}%
          </span>
          <span
            className={`w-2 h-2 rounded-full ${
              isHigh ? "bg-[var(--success)]" : "bg-[var(--warning)]"
            }`}
            title={isHigh ? "High Confidence" : "Moderate Confidence"}
          />
        </div>
        {showLabel && (
          <span className="text-[11px] text-[var(--ink-400)] leading-tight">
            Model Confidence
          </span>
        )}
      </div>
    </div>
  );
}
