"use client";

import React from "react";
import Link from "next/link";
import { useStorefront } from "@/lib/storefront/StorefrontContext";
import { ShoppingBagIcon, ChevronRightIcon, ArrowRightIcon, XIcon } from "@/components/ui/Icons";

export default function StorefrontCartPage() {
  const { cart, updateQuantity, removeFromCart, clearCart, cartTotal, selectedCustomer } =
    useStorefront();

  // Check if cart has size bracketing (>= 2 different sizes of the same product ID)
  const productSizesCount: Record<number, Set<string>> = {};
  cart.forEach((item) => {
    if (!productSizesCount[item.product_id]) {
      productSizesCount[item.product_id] = new Set();
    }
    productSizesCount[item.product_id].add(item.size);
  });
  const hasBracketing = Object.values(productSizesCount).some((sizes) => sizes.size >= 2);

  if (cart.length === 0) {
    return (
      <div className="max-w-xl mx-auto my-12 bg-white rounded-xl border border-stone-200 p-10 text-center space-y-4 shadow-sm">
        <div className="w-14 h-14 mx-auto rounded-full bg-stone-100 flex items-center justify-center text-stone-600">
          <ShoppingBagIcon size={24} />
        </div>
        <h2 className="font-serif text-2xl font-bold text-stone-900">
          Your Shopping Bag is Empty
        </h2>
        <p className="text-xs text-stone-600 max-w-sm mx-auto leading-relaxed">
          Looks like you haven&apos;t added any luxury pieces or occasionwear yet. Browse the collection to get started.
        </p>
        <div className="pt-2">
          <Link
            href="/storefront"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-stone-900 hover:bg-stone-800 text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-sm"
          >
            <span>Explore Collection</span>
            <ArrowRightIcon size={14} />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-xs text-stone-600 font-medium">
        <Link href="/storefront" className="hover:text-stone-900 transition-colors">
          Collection
        </Link>
        <ChevronRightIcon size={12} />
        <span className="text-stone-900 font-semibold">Shopping Bag ({cart.length} items)</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Cart Items Table / List (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-white rounded-xl border border-stone-200 overflow-hidden shadow-sm">
            <div className="p-4 bg-stone-50 border-b border-stone-200 flex items-center justify-between">
              <h2 className="font-serif text-base font-bold text-stone-900">
                Bag Items
              </h2>
              <button
                type="button"
                onClick={clearCart}
                className="text-xs font-medium text-stone-600 hover:text-red-700 transition-colors"
              >
                Clear Bag
              </button>
            </div>

            <div className="divide-y divide-stone-100">
              {cart.map((item) => (
                <div
                  key={`${item.product_id}-${item.size}`}
                  className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  {/* Item Description */}
                  <div className="space-y-1 max-w-md">
                    <div className="flex items-center gap-2">
                      <span className="font-serif text-sm font-bold text-stone-900">
                        {item.name}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-900 font-mono text-[10px] font-bold">
                        Size: {item.size}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-stone-600 font-mono">
                      <span>{item.category || "Apparel"}</span>
                      <span>•</span>
                      <span>{item.sku}</span>
                      <span>•</span>
                      <span>₹{item.price.toLocaleString("en-IN")} each</span>
                    </div>
                  </div>

                  {/* Quantity and Price Stepper */}
                  <div className="flex items-center justify-between sm:justify-end gap-6 shrink-0">
                    <div className="flex items-center border border-stone-300 rounded-lg bg-stone-50 overflow-hidden">
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.product_id, item.size, item.quantity - 1)}
                        className="px-2.5 py-1 text-stone-600 hover:bg-stone-200 text-xs font-bold transition-colors"
                        aria-label="Decrease quantity"
                      >
                        -
                      </button>
                      <span className="px-3 py-1 text-xs font-mono font-bold text-stone-900">
                        {item.quantity}
                      </span>
                      <button
                        type="button"
                        onClick={() => updateQuantity(item.product_id, item.size, item.quantity + 1)}
                        className="px-2.5 py-1 text-stone-600 hover:bg-stone-200 text-xs font-bold transition-colors"
                        aria-label="Increase quantity"
                      >
                        +
                      </button>
                    </div>

                    <div className="font-mono text-sm font-bold text-stone-900 tabular-nums min-w-[70px] text-right">
                      ₹{(item.price * item.quantity).toLocaleString("en-IN")}
                    </div>

                    <button
                      type="button"
                      onClick={() => removeFromCart(item.product_id, item.size)}
                      className="p-1.5 text-stone-600 hover:text-red-700 transition-colors rounded hover:bg-stone-100"
                      title="Remove item"
                    >
                      <XIcon size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bracketing Notice (Demo Informational) */}
          {hasBracketing && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-3">
              <span className="text-base leading-none mt-0.5">⚠️</span>
              <div className="space-y-1">
                <span className="font-bold">Multi-Size Bracketing Scenario Active:</span>
                <p className="text-amber-800 leading-relaxed">
                  Your bag contains multiple sizes of the same apparel item. ReturnSentinel AI evaluates size bracketing signals at checkout to safeguard merchant margins while preserving smooth customer exchanges.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Order Summary Card (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl border border-stone-200 p-5 space-y-4 shadow-sm">
            <h2 className="font-serif text-base font-bold text-stone-900 border-b border-stone-100 pb-3">
              Order Summary
            </h2>

            <div className="space-y-2 text-xs text-stone-600">
              <div className="flex items-center justify-between">
                <span>Subtotal ({cart.reduce((c, i) => c + i.quantity, 0)} items)</span>
                <span className="font-mono font-medium text-stone-900">
                  ₹{cartTotal.toLocaleString("en-IN")}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Standard Delivery</span>
                <span className="text-emerald-700 font-semibold uppercase text-[11px]">
                  FREE
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Estimated Taxes & Packaging</span>
                <span className="text-stone-600 text-[11px]">Included</span>
              </div>
            </div>

            <div className="border-t border-stone-200 pt-3 flex items-baseline justify-between text-sm font-bold text-stone-900">
              <span>Total Due</span>
              <span className="font-mono text-lg text-stone-900">
                ₹{cartTotal.toLocaleString("en-IN")}
              </span>
            </div>

            {/* Shopping As Persona Banner */}
            <div className="p-3 bg-stone-50 rounded-lg border border-stone-200 text-[11px] text-stone-600 space-y-0.5">
              <span className="text-[10px] uppercase font-bold tracking-wider text-stone-600 block">
                Purchasing Customer Persona:
              </span>
              <span className="font-semibold text-stone-900 block truncate">
                {selectedCustomer?.name || "Guest Customer"}
              </span>
              <span className="text-stone-600 font-mono text-[10px] block truncate">
                ID #{selectedCustomer?.id} • {selectedCustomer?.email}
              </span>
            </div>

            <Link
              href="/storefront/checkout"
              className="w-full py-3 px-4 rounded-lg bg-stone-900 hover:bg-stone-800 text-white text-xs font-semibold uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-sm"
            >
              <span>Proceed to Checkout</span>
              <ArrowRightIcon size={14} />
            </Link>

            <div className="text-center pt-1">
              <Link
                href="/storefront"
                className="text-xs text-stone-600 hover:text-stone-900 font-medium underline-offset-2 hover:underline transition-all"
              >
                ← Continue Shopping
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
