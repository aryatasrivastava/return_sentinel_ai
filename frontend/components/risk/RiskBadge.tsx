import React from "react";
import { RiskLevel } from "@/lib/types";
import { ShieldCheckIcon, AlertTriangleIcon, AlertOctagonIcon } from "../ui/Icons";

export interface RiskBadgeProps {
  level: RiskLevel;
  size?: "sm" | "md";
  className?: string;
}

export function RiskBadge({ level, size = "md", className = "" }: RiskBadgeProps) {
  const config = {
    low: {
      label: "Low Risk",
      bg: "bg-[var(--success-soft)]",
      border: "border-[#bfe7db]",
      text: "text-[var(--success)]",
      icon: <ShieldCheckIcon size={size === "sm" ? 12 : 14} />,
    },
    medium: {
      label: "Medium Risk",
      bg: "bg-[var(--warning-soft)]",
      border: "border-[#f2debf]",
      text: "text-[var(--warning)]",
      icon: <AlertTriangleIcon size={size === "sm" ? 12 : 14} />,
    },
    high: {
      label: "High Risk",
      bg: "bg-[var(--danger-soft)]",
      border: "border-[#f5c6c2]",
      text: "text-[var(--danger)]",
      icon: <AlertOctagonIcon size={size === "sm" ? 12 : 14} />,
    },
  };

  const current = config[level] || config.low;

  return (
    <span
      className={`inline-flex items-center font-medium border select-none transition-colors ${
        size === "sm"
          ? "text-[11px] px-1.5 py-0.5 rounded-[4px] gap-1 leading-tight"
          : "text-xs px-2 py-0.5 rounded-[6px] gap-1.5 leading-snug"
      } ${current.bg} ${current.border} ${current.text} ${className}`}
    >
      <span className="shrink-0">{current.icon}</span>
      <span>{current.label}</span>
    </span>
  );
}
