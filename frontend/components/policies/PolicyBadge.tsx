import React from "react";
import { PolicyType } from "@/lib/types";

export interface PolicyBadgeProps {
  policy: PolicyType;
  size?: "sm" | "md";
  className?: string;
}

export function PolicyBadge({
  policy,
  size = "md",
  className = "",
}: PolicyBadgeProps) {
  const config = {
    STANDARD_RETURN: {
      label: "Standard Return",
      bg: "bg-[var(--success-soft)]",
      border: "border-[#bfe7db]",
      text: "text-[var(--success)]",
      dot: "bg-[var(--success)]",
    },
    EXCHANGE_FIRST: {
      label: "Exchange First",
      bg: "bg-[var(--accent-soft)]",
      border: "border-[#d0d7f3]",
      text: "text-[var(--accent)]",
      dot: "bg-[var(--accent)]",
    },
    STORE_CREDIT: {
      label: "Store Credit",
      bg: "bg-[var(--warning-soft)]",
      border: "border-[#f2debf]",
      text: "text-[var(--warning)]",
      dot: "bg-[var(--warning)]",
    },
    RESTOCKING_FEE: {
      label: "Restocking Fee",
      bg: "bg-[var(--danger-soft)]",
      border: "border-[#f5c6c2]",
      text: "text-[var(--danger)]",
      dot: "bg-[var(--danger)]",
    },
  };

  const current = config[policy] || config.STANDARD_RETURN;

  return (
    <span
      className={`inline-flex items-center font-medium border select-none transition-colors ${
        size === "sm"
          ? "text-[11px] px-1.5 py-0.5 rounded-[4px] gap-1 leading-tight"
          : "text-xs px-2.5 py-0.5 rounded-[6px] gap-1.5 leading-snug"
      } ${current.bg} ${current.border} ${current.text} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${current.dot}`} />
      <span>{current.label}</span>
    </span>
  );
}
