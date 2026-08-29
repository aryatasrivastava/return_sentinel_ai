"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { BellIcon, MenuIcon } from "../ui/Icons";

export interface HeaderProps {
  onOpenMobileSidebar: () => void;
}

const routeTitles: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": {
    title: "Executive Dashboard",
    subtitle: "Real-time checkout risk scoring & automated policy interventions",
  },
  "/orders": {
    title: "Orders & Risk Assessments",
    subtitle: "Live feed of analyzed carts, evaluated risks, and assigned return policies",
  },
  "/risk-analysis": {
    title: "Agent Risk Deep Dive",
    subtitle: "Granular multi-signal investigation & XGBoost machine learning breakdown",
  },
  "/policies": {
    title: "Policy Engine Configuration",
    subtitle: "Defensive return policies and deterministic threshold rules",
  },
  "/analytics": {
    title: "Margin & Risk Analytics",
    subtitle: "Return abuse mitigation impact, false positive tracking, and trends",
  },
  "/settings": {
    title: "System Settings",
    subtitle: "Merchant profile, risk sensitivity thresholds, and webhook notifications",
  },
};

export function Header({ onOpenMobileSidebar }: HeaderProps) {
  const pathname = usePathname();

  const currentMeta =
    routeTitles[pathname] ||
    (pathname.startsWith("/orders")
      ? routeTitles["/orders"]
      : pathname.startsWith("/risk-analysis")
      ? routeTitles["/risk-analysis"]
      : {
          title: "ReturnSentinel AI",
          subtitle: "Protecting e-commerce margins from return abuse — before checkout.",
        });

  return (
    <header className="sticky top-0 z-30 bg-[var(--surface)] border-b border-[var(--border)] h-16 shrink-0 flex items-center justify-between px-4 sm:px-6 md:px-8">
      {/* Left: Mobile hamburger + Page Title */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          type="button"
          onClick={onOpenMobileSidebar}
          className="md:hidden text-[var(--ink-600)] hover:text-[var(--ink-900)] p-1.5 rounded-[6px] hover:bg-[var(--surface-sunken)] focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] shrink-0"
          aria-label="Open navigation menu"
        >
          <MenuIcon size={20} />
        </button>

        <div className="min-w-0">
          <h1 className="text-[1.125rem] sm:text-[1.375rem] sm:leading-[1.75rem] font-semibold text-[var(--ink-900)] tracking-tight truncate">
            {currentMeta.title}
          </h1>
          <p className="hidden sm:block text-xs text-[var(--ink-600)] truncate">
            {currentMeta.subtitle}
          </p>
        </div>
      </div>

      {/* Right: Org Placeholder & Notification Bell */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Merchant Store Selector */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] text-xs text-[var(--ink-900)]">
          <span className="w-2 h-2 rounded-full bg-[var(--success)] shrink-0" />
          <span className="font-medium truncate max-w-[150px]">
            Acme Retail Inc.
          </span>
          <span className="text-[var(--ink-400)] font-mono text-[10px]">
            (PROD)
          </span>
        </div>

        {/* Notification Bell */}
        <button
          type="button"
          className="relative p-2 rounded-[6px] text-[var(--ink-600)] hover:text-[var(--ink-900)] hover:bg-[var(--surface-sunken)] border border-[var(--border)] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)]"
          aria-label="Notifications (3 unread alerts)"
        >
          <BellIcon size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[var(--accent)] rounded-full ring-2 ring-white" />
        </button>
      </div>
    </header>
  );
}
