"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useStorefront } from "@/lib/storefront/StorefrontContext";
import { assessCartCheckout, AssessCartResponse } from "@/lib/api/storefront";
import { PolicyType } from "@/lib/types";
import { LoadingState } from "@/components/ui/LoadingState";
import { EmptyState } from "@/components/ui/EmptyState";
import {
  ShieldCheckIcon,
  CheckCircleIcon,
  ShoppingBagIcon,
  ChevronRightIcon,
  ArrowRightIcon,
  RefreshCwIcon,
} from "@/components/ui/Icons";

interface CustomerPolicyCardProps {
  policy: PolicyType;
}

function CustomerPolicyCard({ policy }: CustomerPolicyCardProps) {
  switch (policy) {
    case "STANDARD_RETURN":
      return (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-full bg-emerald-600 text-white flex items-center justify-center">
              <CheckCircleIcon size={14} />
            </span>
            <span className="font-serif text-sm font-bold">
              Standard 30-Day Return Guarantee
            </span>
          </div>
          <p className="text-xs text-emerald-800 leading-relaxed pl-7">
            You can return any unworn item with tags attached within 30 days for a <strong>100% full refund</strong> to your original payment method. Includes complimentary courier doorstep pickup.
          </p>
        </div>
      );

    case "EXCHANGE_FIRST":
      return (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-950 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-full bg-amber-600 text-white flex items-center justify-center">
              <RefreshCwIcon size={14} />
            </span>
            <span className="font-serif text-sm font-bold">
              Instant Courier Exchange Protection
            </span>
          </div>
          <p className="text-xs text-amber-800 leading-relaxed pl-7">
            Need an alternate size, color, or style? This order qualifies for <strong>free, instant doorstep courier exchange</strong> with expedited dispatch of your replacement before returning.
          </p>
        </div>
      );

    case "STORE_CREDIT":
      return (
        <div className="p-4 rounded-xl bg-purple-50 border border-purple-200 text-purple-950 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-full bg-purple-600 text-white flex items-center justify-center">
              <ShieldCheckIcon size={14} />
            </span>
            <span className="font-serif text-sm font-bold">
              Store Credit Return & Loyalty Bonus
            </span>
          </div>
          <p className="text-xs text-purple-800 leading-relaxed pl-7">
            Returns on this designer selection will be issued as <strong>100% non-expiring Store Credit</strong> plus an additional <strong>+5% loyalty bonus credit</strong> credited directly to your account.
          </p>
        </div>
      );

    case "RESTOCKING_FEE":
      return (
        <div className="p-4 rounded-xl bg-stone-100 border border-stone-300 text-stone-900 space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-full bg-stone-700 text-white flex items-center justify-center">
              <ShieldCheckIcon size={14} />
            </span>
            <span className="font-serif text-sm font-bold">
              Standard Return & Inspection Policy
            </span>
          </div>
          <p className="text-xs text-stone-700 leading-relaxed pl-7">
            Items may be returned for <strong>100% store credit with zero deductions</strong>, or a standard 15% garment inspection and re-tagging fee applies to refunds back to original card.
          </p>
        </div>
      );

    default:
      return (
        <div className="p-4 rounded-xl bg-stone-50 border border-stone-200 text-xs text-stone-700">
          Standard merchant return policies apply to this order.
        </div>
      );
  }
}

export default function StorefrontCheckoutPage() {
  const { cart, cartTotal, selectedCustomer, clearCart } = useStorefront();

  const [assessment, setAssessment] = useState<AssessCartResponse | null>(null);
  const [isAssessing, setIsAssessing] = useState<boolean>(true);
  const [assessmentError, setAssessmentError] = useState<string | null>(null);

  // Simulated Payment Form State
  const [paymentMethod, setPaymentMethod] = useState<string>("upi");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [confirmedOrderId, setConfirmedOrderId] = useState<number | null>(null);

  // Trigger real-time pre-checkout policy evaluation via POST /api/assess-order
  const performAssessment = useCallback(async () => {
    if (cart.length === 0 || !selectedCustomer) {
      setIsAssessing(false);
      return;
    }

    setIsAssessing(true);
    setAssessmentError(null);

    try {
      const payload = {
        customer_id: selectedCustomer.id,
        cart_items: cart.map((item) => ({
          product_id: item.product_id,
          size: item.size,
          quantity: item.quantity,
          unit_price: item.price,
        })),
      };

      const result = await assessCartCheckout(payload);
      setAssessment(result);
    } catch (err: any) {
      setAssessmentError(err.message || "Failed to retrieve pre-checkout policy evaluation.");
    } finally {
      setIsAssessing(false);
    }
  }, [cart, selectedCustomer]);

  useEffect(() => {
    performAssessment();
  }, [performAssessment]);

  const handleCompletePurchase = () => {
    if (!assessment) return;
    setIsSubmitting(true);

    setTimeout(() => {
      setConfirmedOrderId(assessment.order_id);
      clearCart();
      setIsSubmitting(false);
    }, 600);
  };

  // 1. Order Confirmed Screen
  if (confirmedOrderId) {
    const finalPolicy = assessment?.final_policy || "STANDARD_RETURN";

    return (
      <div className="max-w-2xl mx-auto bg-white rounded-2xl border border-stone-200 p-8 text-center space-y-6 shadow-sm my-4">
        <div className="w-16 h-16 mx-auto rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
          <CheckCircleIcon size={32} />
        </div>

        <div className="space-y-1.5">
          <span className="text-xs font-bold uppercase tracking-widest text-emerald-700 font-mono">
            Payment Completed (Simulated)
          </span>
          <h1 className="font-serif text-3xl font-bold text-stone-900">
            Thank You For Your Order!
          </h1>
          <p className="text-xs text-stone-600">
            Order Confirmation Reference:{" "}
            <strong className="font-mono text-stone-900 font-bold">
              ORD-{confirmedOrderId}
            </strong>
          </p>
        </div>

        {/* Applied Policy Confirmation */}
        <div className="text-left bg-stone-50 p-4 rounded-xl border border-stone-200 space-y-2">
          <span className="text-[10px] font-bold uppercase tracking-wider text-stone-600 block">
            Applicable Return Policy for this Purchase:
          </span>
          <CustomerPolicyCard policy={finalPolicy} />
        </div>

        {/* Dual Actions: Merchant Admin Link + Storefront Link */}
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href={`/risk-analysis?orderId=${confirmedOrderId}`}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-sm"
          >
            <ShieldCheckIcon size={15} />
            <span>Inspect in Merchant Admin</span>
          </Link>

          <Link
            href="/storefront"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-stone-900 hover:bg-stone-800 text-white text-xs font-semibold uppercase tracking-wider transition-colors shadow-sm"
          >
            <span>Back to Storefront</span>
            <ArrowRightIcon size={14} />
          </Link>
        </div>
      </div>
    );
  }

  // 2. Empty Cart
  if (cart.length === 0) {
    return (
      <div className="max-w-md mx-auto my-12 text-center space-y-4">
        <EmptyState
          icon={<ShoppingBagIcon size={24} />}
          title="No Items to Checkout"
          description="Your shopping bag is empty. Please add products from the collection before checking out."
          actionLabel="Go to Collection"
          onAction={() => {
            window.location.href = "/storefront";
          }}
        />
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
        <Link href="/storefront/cart" className="hover:text-stone-900 transition-colors">
          Shopping Bag
        </Link>
        <ChevronRightIcon size={12} />
        <span className="text-stone-900 font-semibold">Pre-Checkout Policy & Review</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Delivery Details & Simulated Payment (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Shipping Address (Realistic Demonstration) */}
          <div className="bg-white rounded-xl border border-stone-200 p-5 space-y-4 shadow-sm">
            <div className="flex items-center justify-between border-b border-stone-100 pb-3">
              <h2 className="font-serif text-base font-bold text-stone-900">
                1. Delivery Destination
              </h2>
              <span className="text-[11px] text-stone-600 font-mono">
                Persona ID #{selectedCustomer?.id}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="space-y-1">
                <label className="text-[11px] font-medium text-stone-600">
                  Recipient Name:
                </label>
                <input
                  type="text"
                  readOnly
                  value={selectedCustomer?.name || "Customer"}
                  className="w-full bg-stone-50 border border-stone-300 rounded px-3 py-2 text-stone-900 font-semibold focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-medium text-stone-600">
                  Email Address:
                </label>
                <input
                  type="email"
                  readOnly
                  value={selectedCustomer?.email || ""}
                  className="w-full bg-stone-50 border border-stone-300 rounded px-3 py-2 text-stone-700 font-mono focus:outline-none"
                />
              </div>

              <div className="sm:col-span-2 space-y-1">
                <label className="text-[11px] font-medium text-stone-600">
                  Delivery Address:
                </label>
                <input
                  type="text"
                  readOnly
                  value="B-402, Royal Palms Residency, Indiranagar, Bengaluru, 560038"
                  className="w-full bg-stone-50 border border-stone-300 rounded px-3 py-2 text-stone-700 focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Simulated Payment Method Options */}
          <div className="bg-white rounded-xl border border-stone-200 p-5 space-y-4 shadow-sm">
            <div className="flex items-center justify-between border-b border-stone-100 pb-3">
              <h2 className="font-serif text-base font-bold text-stone-900">
                2. Payment Method
              </h2>
              <span className="text-[10px] font-mono font-bold uppercase bg-amber-100 text-amber-900 px-2 py-0.5 rounded">
                Simulated Sandbox
              </span>
            </div>

            <div className="space-y-2.5">
              {[
                { id: "upi", name: "Instant UPI (Google Pay / PhonePe / Paytm)", desc: "Zero gateway fees with instant transaction authorization" },
                { id: "card", name: "Credit / Debit Card", desc: "Visa, MasterCard, Rupay, Amex (Simulated test card)" },
                { id: "netbanking", name: "Net Banking", desc: "All major Indian scheduled banks supported" },
              ].map((m) => (
                <label
                  key={m.id}
                  className={`flex items-start gap-3 p-3.5 rounded-lg border cursor-pointer transition-all ${
                    paymentMethod === m.id
                      ? "bg-amber-50/60 border-amber-400 ring-1 ring-amber-400"
                      : "bg-stone-50/60 border-stone-200 hover:border-stone-300"
                  }`}
                >
                  <input
                    type="radio"
                    name="payment_method"
                    value={m.id}
                    checked={paymentMethod === m.id}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="mt-0.5 text-stone-900 focus:ring-amber-500 cursor-pointer"
                  />
                  <div className="space-y-0.5 text-xs">
                    <span className="font-semibold text-stone-900 block">
                      {m.name}
                    </span>
                    <span className="text-[11px] text-stone-600 block">
                      {m.desc}
                    </span>
                  </div>
                </label>
              ))}
            </div>

            <p className="text-[11px] text-stone-600 pt-1 leading-relaxed">
              🔒 <strong>Demo Sandbox:</strong> No live banking or Razorpay credentials required. Completing purchase will simulate order placement and record the assessed policy in the merchant ledger.
            </p>
          </div>
        </div>

        {/* Right Column: Pre-Checkout Policy Card + Order Summary (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Customer-Facing Return Policy Card */}
          <div className="bg-white rounded-xl border border-stone-200 p-5 space-y-3 shadow-sm">
            <div className="flex items-center justify-between border-b border-stone-100 pb-2.5">
              <span className="font-serif text-sm font-bold text-stone-900">
                Order Return Policy
              </span>
              <span className="text-[10px] text-emerald-800 font-bold uppercase tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Verified at Checkout
              </span>
            </div>

            {isAssessing ? (
              <div className="py-4">
                <LoadingState rows={2} />
              </div>
            ) : assessmentError ? (
              <div className="p-3 bg-red-50 text-red-800 text-xs rounded-lg border border-red-200">
                {assessmentError}
              </div>
            ) : assessment ? (
              <CustomerPolicyCard policy={assessment.final_policy} />
            ) : (
              <div className="text-xs text-stone-600">Standard returns apply.</div>
            )}
          </div>

          {/* Order Review List & Complete Purchase */}
          <div className="bg-white rounded-xl border border-stone-200 p-5 space-y-4 shadow-sm">
            <h3 className="font-serif text-sm font-bold text-stone-900 border-b border-stone-100 pb-2.5">
              Order Items ({cart.reduce((c, i) => c + i.quantity, 0)})
            </h3>

            <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1 divide-y divide-stone-100">
              {cart.map((item) => (
                <div
                  key={`${item.product_id}-${item.size}`}
                  className="pt-2 flex items-center justify-between text-xs"
                >
                  <div className="space-y-0.5 max-w-[200px]">
                    <span className="font-medium text-stone-900 truncate block">
                      {item.name}
                    </span>
                    <span className="text-[11px] text-stone-600 font-mono block">
                      Size: {item.size} • Qty: {item.quantity}
                    </span>
                  </div>
                  <span className="font-mono font-bold text-stone-900">
                    ₹{(item.price * item.quantity).toLocaleString("en-IN")}
                  </span>
                </div>
              ))}
            </div>

            <div className="border-t border-stone-200 pt-3 space-y-1.5 text-xs text-stone-600">
              <div className="flex items-center justify-between">
                <span>Items Subtotal</span>
                <span className="font-mono text-stone-900 font-medium">
                  ₹{cartTotal.toLocaleString("en-IN")}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Shipping</span>
                <span className="text-emerald-700 font-semibold text-[11px] uppercase">
                  FREE
                </span>
              </div>
              <div className="border-t border-stone-100 pt-2 flex items-baseline justify-between text-sm font-bold text-stone-900">
                <span>Total Amount</span>
                <span className="font-mono text-lg text-stone-900">
                  ₹{cartTotal.toLocaleString("en-IN")}
                </span>
              </div>
            </div>

            {/* Complete Purchase Button */}
            <button
              type="button"
              disabled={isAssessing || isSubmitting}
              onClick={handleCompletePurchase}
              className="w-full py-3.5 px-4 rounded-lg bg-stone-900 hover:bg-stone-800 disabled:bg-stone-400 text-white text-xs font-semibold uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-md cursor-pointer disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <span>Confirming Order...</span>
              ) : (
                <>
                  <CheckCircleIcon size={16} />
                  <span>Complete Purchase (Simulated)</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
