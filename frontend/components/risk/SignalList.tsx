import React from "react";
import { SignalItem } from "@/lib/types";
import { RiskBadge } from "./RiskBadge";
import { UserIcon, ShoppingBagIcon, ShieldIcon } from "../ui/Icons";

export interface SignalListProps {
  signals: SignalItem[];
  title: string;
  category: "customer" | "cart" | "product";
  className?: string;
}

export function SignalList({
  signals,
  title,
  category,
  className = "",
}: SignalListProps) {
  const categoryIcons = {
    customer: <UserIcon size={16} className="text-[var(--accent)]" />,
    cart: <ShoppingBagIcon size={16} className="text-[var(--accent)]" />,
    product: <ShieldIcon size={16} className="text-[var(--accent)]" />,
  };

  return (
    <div
      className={`border border-[var(--border)] rounded-[8px] bg-[var(--surface)] overflow-hidden ${className}`}
    >
      <div className="flex items-center justify-between px-4 py-3 bg-[var(--surface-sunken)] border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          {categoryIcons[category]}
          <h3 className="text-xs font-semibold text-[var(--ink-900)] uppercase tracking-wider">
            {title}
          </h3>
        </div>
        <span className="font-mono text-[11px] text-[var(--ink-400)] tabular-nums">
          {signals.length} {signals.length === 1 ? "signal" : "signals"}
        </span>
      </div>

      <div className="divide-y divide-[var(--border)]">
        {signals.length === 0 ? (
          <div className="p-4 text-xs text-[var(--ink-400)] text-center">
            No anomalous signals detected in this category.
          </div>
        ) : (
          signals.map((sig) => (
            <div
              key={sig.id}
              className="p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-3 hover:bg-[var(--surface-sunken)]/50 transition-colors"
            >
              <div className="space-y-1 max-w-xl">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-[var(--ink-900)]">
                    {sig.name}
                  </span>
                  <RiskBadge level={sig.severity} size="sm" />
                </div>
                <p className="text-xs text-[var(--ink-600)] leading-relaxed">
                  {sig.description}
                </p>
              </div>

              <div className="shrink-0 self-start sm:self-auto">
                <span className="inline-block font-mono text-xs bg-[var(--surface-sunken)] border border-[var(--border)] px-2.5 py-1 rounded-[4px] text-[var(--ink-900)] tabular-nums font-medium">
                  {sig.value}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
