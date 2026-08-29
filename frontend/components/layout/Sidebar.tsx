"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  DashboardIcon,
  ShoppingBagIcon,
  ActivityIcon,
  PolicyIcon,
  AnalyticsIcon,
  SettingsIcon,
  ShieldIcon,
  XIcon,
} from "../ui/Icons";

export interface SidebarProps {
  isMobileOpen: boolean;
  onCloseMobile: () => void;
}

export const navItems = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: DashboardIcon,
  },
  {
    label: "Orders",
    href: "/orders",
    icon: ShoppingBagIcon,
  },
  {
    label: "Risk Analysis",
    href: "/risk-analysis",
    icon: ActivityIcon,
  },
  {
    label: "Policies",
    href: "/policies",
    icon: PolicyIcon,
  },
  {
    label: "Analytics",
    href: "/analytics",
    icon: AnalyticsIcon,
  },
  {
    label: "Settings",
    href: "/settings",
    icon: SettingsIcon,
  },
];

export function Sidebar({ isMobileOpen, onCloseMobile }: SidebarProps) {
  const pathname = usePathname();

  const isLinkActive = (href: string) => {
    if (href === "/dashboard" && (pathname === "/" || pathname === "/dashboard")) {
      return true;
    }
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-xs transition-opacity duration-200"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-[var(--ink-900)] text-white border-r border-[#1e2738] transition-transform duration-200 ease-in-out
          w-[240px]
          md:translate-x-0
          lg:w-[240px]
          md:w-[72px]
          ${isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
        `}
      >
        {/* Brand / Logo Section */}
        <div className="h-16 flex items-center justify-between px-4 lg:px-5 border-b border-[#1e2738] shrink-0">
          <Link
            href="/dashboard"
            onClick={onCloseMobile}
            className="flex items-center gap-2.5 group overflow-hidden"
          >
            <div className="w-8 h-8 rounded-[6px] bg-[var(--accent)] text-white flex items-center justify-center shrink-0 shadow-sm group-hover:bg-[#495bc2] transition-colors">
              <ShieldIcon size={18} />
            </div>

            <div className="flex flex-col md:hidden lg:flex min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-sm tracking-tight text-white truncate">
                  ReturnSentinel
                </span>
                <span className="font-mono text-[10px] bg-[#222d46] text-[#a4b3f6] px-1.5 py-0.2 rounded-[3px] font-medium uppercase tracking-wider">
                  AI
                </span>
              </div>
              <span className="text-[10px] text-[var(--ink-400)] truncate">
                Pre-Checkout Defense
              </span>
            </div>
          </Link>

          {/* Close button for mobile drawer */}
          <button
            type="button"
            onClick={onCloseMobile}
            className="md:hidden text-[var(--ink-400)] hover:text-white p-1 rounded-[4px] focus-visible:ring-1 focus-visible:ring-[var(--focus-ring)]"
            aria-label="Close sidebar"
          >
            <XIcon size={20} />
          </button>
        </div>

        {/* Navigation List */}
        <nav className="flex-1 py-4 px-2 lg:px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const active = isLinkActive(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onCloseMobile}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-[6px] text-xs font-medium transition-colors select-none group relative ${
                  active
                    ? "bg-[var(--accent-soft)] text-[var(--accent)] font-semibold shadow-xs"
                    : "text-[#9eabc0] hover:text-white hover:bg-[#182138]"
                }`}
                title={item.label}
              >
                <Icon
                  size={18}
                  className={`shrink-0 transition-colors ${
                    active
                      ? "text-[var(--accent)]"
                      : "text-[#7b8aa6] group-hover:text-white"
                  }`}
                />

                <span className="md:hidden lg:inline truncate">
                  {item.label}
                </span>

                {/* Subtle active pill indicator on tablet rail */}
                {active && (
                  <span className="hidden md:block lg:hidden absolute right-1 w-1 h-5 rounded-full bg-[var(--accent)]" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer / Merchant Org Status */}
        <div className="p-3 border-t border-[#1e2738] shrink-0 bg-[#0a0f1d]/50">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full bg-[#202c45] border border-[#2b3b5c] text-white flex items-center justify-center font-mono text-xs font-semibold shrink-0">
              AC
            </div>
            <div className="md:hidden lg:flex flex-col min-w-0">
              <span className="text-xs font-medium text-white truncate">
                Acme Retail Inc.
              </span>
              <span className="font-mono text-[10px] text-[var(--success)] flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--success)] shrink-0 animate-pulse" />
                Agent v2.4 Active
              </span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
