"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { StorefrontProvider, useStorefront } from "@/lib/storefront/StorefrontContext";
import { ShoppingBagIcon, ShieldCheckIcon, UserIcon } from "@/components/ui/Icons";

function StorefrontNavbar() {
  const pathname = usePathname();
  const { customers, selectedCustomer, setSelectedCustomer, cartCount, isLoadingCustomers } =
    useStorefront();

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-stone-200">
      {/* Demo Persona Switcher Bar */}
      <div className="bg-stone-900 text-stone-200 text-xs py-2 px-4 border-b border-stone-800">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 font-mono text-[10px] font-bold uppercase tracking-wider bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30">
              Demo Mode
            </span>
            <span className="text-stone-300">
              Simulating live customer checkout session
            </span>
          </div>

          <div className="flex items-center gap-2">
            <UserIcon size={14} className="text-stone-400 shrink-0" />
            <label htmlFor="customer-persona" className="text-stone-400 font-medium">
              Shopping as:
            </label>
            {isLoadingCustomers ? (
              <span className="text-stone-400">Loading personas...</span>
            ) : (
              <select
                id="customer-persona"
                value={selectedCustomer?.id || ""}
                onChange={(e) => {
                  const found = customers.find((c) => c.id === Number(e.target.value));
                  if (found) setSelectedCustomer(found);
                }}
                className="bg-stone-800 text-amber-300 border border-stone-700 text-xs rounded px-2.5 py-1 font-medium focus:outline-none focus:ring-1 focus:ring-amber-400 cursor-pointer"
              >
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} (ID #{c.id} - {c.email})
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>
      </div>

      {/* Main Boutique Navbar */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
        {/* Brand Logo */}
        <Link href="/storefront" className="group flex items-baseline gap-2">
          <span className="font-serif text-2xl font-bold tracking-tight text-stone-900 group-hover:text-amber-700 transition-colors">
            ATELIER SENTINEL
          </span>
          <span className="hidden md:inline-block text-[11px] uppercase tracking-widest text-stone-600 font-sans font-medium">
            Occasionwear & Luxury Fashion
          </span>
        </Link>

        {/* Navigation & Cart */}
        <div className="flex items-center gap-4">
          <Link
            href="/storefront"
            className={`text-xs font-semibold uppercase tracking-wider transition-colors px-3 py-1.5 rounded ${
              pathname === "/storefront"
                ? "text-stone-950 bg-stone-100 font-bold"
                : "text-stone-700 hover:text-stone-950"
            }`}
          >
            Collection
          </Link>

          <Link
            href="/storefront/cart"
            className="relative flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-semibold uppercase tracking-wider text-stone-700 hover:text-stone-950 bg-stone-50 border border-stone-200 transition-colors"
          >
            <ShoppingBagIcon size={16} />
            <span>Bag</span>
            {cartCount > 0 && (
              <span className="ml-1 px-1.5 py-0.2 rounded-full bg-amber-600 text-white font-mono text-[11px] font-bold">
                {cartCount}
              </span>
            )}
          </Link>

          {/* Quick return link to merchant dashboard */}
          <Link
            href="/dashboard"
            className="hidden sm:inline-flex items-center gap-1 text-xs font-medium text-emerald-800 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 rounded transition-colors"
          >
            <ShieldCheckIcon size={14} />
            <span>Merchant Admin</span>
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function StorefrontLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <StorefrontProvider>
      <div className="min-h-screen bg-stone-50 text-stone-900 font-sans flex flex-col">
        <StorefrontNavbar />
        <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8">
          {children}
        </main>
        <footer className="border-t border-stone-200 bg-white py-6 text-center text-xs text-stone-600">
          <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <span>© 2026 Atelier Sentinel Boutique • Middleware Powered by ReturnSentinel AI</span>
            <span className="font-mono text-[11px] text-stone-600">
              Demo Environment • Zero Real Payments Processed
            </span>
          </div>
        </footer>
      </div>
    </StorefrontProvider>
  );
}
