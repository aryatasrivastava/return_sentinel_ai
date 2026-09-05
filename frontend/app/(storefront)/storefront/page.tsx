"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useStorefront } from "@/lib/storefront/StorefrontContext";
import { getStorefrontProducts, StorefrontProduct } from "@/lib/api/storefront";
import { LoadingState } from "@/components/ui/LoadingState";
import { EmptyState } from "@/components/ui/EmptyState";
import {
  ShoppingBagIcon,
  CheckCircleIcon,
  FilterIcon,
  XIcon,
  ArrowRightIcon,
} from "@/components/ui/Icons";

const AVAILABLE_SIZES = ["S", "M", "L", "XL", "XXL"];

// Color themes based on product category for clean visual differentiation
function getCategoryColor(category?: string | null): { bg: string; text: string; badge: string } {
  switch (category) {
    case "Ethnic Occasionwear":
      return { bg: "from-amber-900/10 to-amber-700/5", text: "text-amber-900", badge: "bg-amber-100 text-amber-900" };
    case "Bridal & Festive":
      return { bg: "from-rose-900/10 to-rose-700/5", text: "text-rose-900", badge: "bg-rose-100 text-rose-900" };
    case "Formalwear":
      return { bg: "from-sky-900/10 to-sky-700/5", text: "text-sky-900", badge: "bg-sky-100 text-sky-900" };
    default:
      return { bg: "from-stone-900/10 to-stone-700/5", text: "text-stone-900", badge: "bg-stone-200 text-stone-900" };
  }
}

export default function StorefrontProductListingPage() {
  const { cart, addToCart, updateQuantity, getItemQuantity, cartCount } = useStorefront();
  const [products, setProducts] = useState<StorefrontProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected size per product card state: { [productId]: size }
  const [selectedSizes, setSelectedSizes] = useState<Record<number, string>>({});
  // Prominent Floating Toast State
  const [toastItem, setToastItem] = useState<{ name: string; size: string; price: number } | null>(null);

  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getStorefrontProducts();
        setProducts(data);
        // Initialize default size "M" for all products
        const initialSizes: Record<number, string> = {};
        data.forEach((p) => {
          initialSizes[p.id] = "M";
        });
        setSelectedSizes(initialSizes);
      } catch (err: any) {
        setError(err.message || "Failed to load product catalog.");
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  const handleSizeChange = (productId: number, size: string) => {
    setSelectedSizes((prev) => ({ ...prev, [productId]: size }));
  };

  const handleAddToCart = (product: StorefrontProduct) => {
    const size = selectedSizes[product.id] || "M";
    addToCart(product, size, 1);

    // Show prominent floating toast
    setToastItem({ name: product.name, size, price: product.price });
  };

  // Auto-dismiss toast after 4 seconds
  useEffect(() => {
    if (toastItem) {
      const timer = setTimeout(() => {
        setToastItem(null);
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [toastItem]);

  const categories = ["ALL", ...Array.from(new Set(products.map((p) => p.category).filter(Boolean)))];

  const filteredProducts =
    selectedCategory === "ALL"
      ? products
      : products.filter((p) => p.category === selectedCategory);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <LoadingState rows={6} />
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        variant="danger"
        title="Catalog Unavailable"
        description={error}
        actionLabel="Retry"
        onAction={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Header Banner */}
      <section className="bg-gradient-to-r from-stone-900 to-stone-800 text-white rounded-xl p-6 sm:p-8 shadow-sm">
        <div className="max-w-2xl space-y-3">
          <span className="text-amber-400 font-mono text-xs uppercase tracking-widest font-semibold">
            Spring / Festive Edition 2026
          </span>
          <h1 className="font-serif text-3xl sm:text-4xl font-bold tracking-tight text-stone-100">
            Artisanal Silks & Occasionwear
          </h1>
          <p className="text-stone-300 text-xs sm:text-sm leading-relaxed">
            Explore authentic handloom silks, bespoke sherwanis, and festive bridal couture. ReturnSentinel AI seamlessly personalizes your checkout policy in real-time.
          </p>
        </div>
      </section>

      {/* Interactive Testing Callout */}
      <div className="p-4 rounded-lg bg-amber-50/80 border border-amber-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-amber-900">
        <div className="space-y-0.5">
          <span className="font-bold flex items-center gap-1 text-amber-950">
            💡 ReturnSentinel Demo Tip: Test Size Bracketing
          </span>
          <p className="text-amber-800">
            Add the <strong>same item in 2 different sizes (e.g. Size M + Size L)</strong> to your bag, then visit checkout to see how ReturnSentinel detects bracketing signals and applies defensive policies!
          </p>
        </div>

        {cartCount > 0 && (
          <Link
            href="/storefront/cart"
            className="shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded bg-amber-600 hover:bg-amber-700 text-white font-medium transition-colors"
          >
            <ShoppingBagIcon size={14} />
            <span>View Bag ({cartCount})</span>
          </Link>
        )}
      </div>

      {/* Category Filter Navigation */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-stone-200">
        <FilterIcon size={14} className="text-stone-600 shrink-0 mr-1" />
        <span className="text-xs font-semibold text-stone-700 uppercase tracking-wider shrink-0 mr-2">
          Category:
        </span>
        {categories.map((cat) => (
          <button
            key={cat || "unknown"}
            onClick={() => setSelectedCategory(cat || "ALL")}
            className={`text-xs px-3 py-1.5 rounded-full font-medium transition-all shrink-0 cursor-pointer ${
              selectedCategory === cat
                ? "bg-stone-900 text-white shadow-sm"
                : "bg-stone-100 text-stone-600 hover:bg-stone-200 hover:text-stone-900"
            }`}
          >
            {cat === "ALL" ? "All Products" : cat}
          </button>
        ))}
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => {
          const theme = getCategoryColor(product.category);
          const currentSize = selectedSizes[product.id] || "M";
          const currentQty = getItemQuantity(product.id, currentSize);
          const productCartItems = cart.filter((item) => item.product_id === product.id);

          return (
            <div
              key={product.id}
              className="group bg-white rounded-xl border border-stone-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              {/* Product Visual Placeholder */}
              <div
                className={`h-48 bg-gradient-to-br ${theme.bg} p-6 flex flex-col justify-between border-b border-stone-100 relative`}
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider ${theme.badge}`}
                  >
                    {product.category || "Apparel"}
                  </span>
                  <span className="font-mono text-[10px] text-stone-600 font-medium">
                    {product.sku}
                  </span>
                </div>

                <div className="text-center my-auto">
                  <span className="font-serif text-lg font-semibold text-stone-800 line-clamp-2">
                    {product.name}
                  </span>
                </div>

                <div className="text-left">
                  <span className="text-[10px] text-stone-600 font-mono">
                    Product ID: #{product.id}
                  </span>
                </div>
              </div>

              {/* Product Details & Purchase Controls */}
              <div className="p-4 space-y-4">
                <div className="flex items-baseline justify-between">
                  <h3 className="font-serif text-sm font-bold text-stone-900 line-clamp-1">
                    {product.name}
                  </h3>
                  <span className="font-mono text-base font-bold text-stone-900 tabular-nums">
                    ₹{product.price.toLocaleString("en-IN")}
                  </span>
                </div>

                {/* Size Selection & Add to Cart / Stepper */}
                <div className="space-y-2.5 pt-2 border-t border-stone-100">
                  <div className="flex items-center justify-between gap-2">
                    <label
                      htmlFor={`size-${product.id}`}
                      className="text-xs font-medium text-stone-600"
                    >
                      Select Size:
                    </label>
                    <select
                      id={`size-${product.id}`}
                      value={currentSize}
                      onChange={(e) => handleSizeChange(product.id, e.target.value)}
                      className="bg-stone-50 border border-stone-300 text-xs rounded px-2.5 py-1 text-stone-900 font-semibold focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer"
                    >
                      {AVAILABLE_SIZES.map((sz) => {
                        const szQty = getItemQuantity(product.id, sz);
                        return (
                          <option key={sz} value={sz}>
                            Size {sz} {szQty > 0 ? `(${szQty} in bag)` : ""}
                          </option>
                        );
                      })}
                    </select>
                  </div>

                  {/* Multi-size indicator for this product if already in bag */}
                  {productCartItems.length > 0 && (
                    <div className="flex items-center flex-wrap gap-1.5 text-[11px] text-amber-900 bg-amber-50/80 px-2.5 py-1.5 rounded-lg border border-amber-200/70 font-mono">
                      <span className="font-sans font-semibold text-amber-950 text-[10px] uppercase tracking-wider">
                        In Bag:
                      </span>
                      {productCartItems.map((item) => (
                        <span
                          key={item.size}
                          className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            item.size === currentSize
                              ? "bg-amber-600 text-white shadow-xs ring-1 ring-amber-700"
                              : "bg-amber-100 text-amber-900"
                          }`}
                        >
                          Size {item.size} × {item.quantity}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Quantity Stepper (if selected size is already in cart) OR Add to Bag Button */}
                  {currentQty > 0 ? (
                    <div className="w-full py-1.5 px-2 rounded-lg bg-stone-900 text-white flex items-center justify-between shadow-sm border border-stone-800">
                      <button
                        type="button"
                        onClick={() => updateQuantity(product.id, currentSize, currentQty - 1)}
                        className="w-8 h-8 rounded-md bg-stone-800 hover:bg-stone-700 active:scale-95 text-stone-200 hover:text-white flex items-center justify-center font-bold text-base transition-all cursor-pointer border border-stone-700"
                        aria-label={`Decrease size ${currentSize} quantity`}
                        title={`Decrease size ${currentSize} quantity`}
                      >
                        −
                      </button>

                      <div className="flex items-center gap-1.5 text-xs">
                        <span className="text-stone-300 font-medium">Size {currentSize}:</span>
                        <span className="font-mono text-xs font-bold text-amber-400 bg-stone-800 px-2 py-0.5 rounded border border-amber-500/30 tabular-nums">
                          {currentQty} in Bag
                        </span>
                      </div>

                      <button
                        type="button"
                        onClick={() => updateQuantity(product.id, currentSize, currentQty + 1)}
                        className="w-8 h-8 rounded-md bg-stone-800 hover:bg-stone-700 active:scale-95 text-stone-200 hover:text-white flex items-center justify-center font-bold text-base transition-all cursor-pointer border border-stone-700"
                        aria-label={`Increase size ${currentSize} quantity`}
                        title={`Increase size ${currentSize} quantity`}
                      >
                        +
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleAddToCart(product)}
                      className="w-full py-2.5 px-4 rounded-lg text-xs font-semibold uppercase tracking-wider flex items-center justify-center gap-2 transition-all bg-stone-900 hover:bg-stone-800 active:scale-[0.99] text-white shadow-sm cursor-pointer"
                    >
                      <ShoppingBagIcon size={14} />
                      <span>Add Size {currentSize} to Bag</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Prominent Floating "Added to Bag" Notification Toast */}
      {toastItem && (
        <div className="fixed bottom-6 right-6 z-50 max-w-md w-full animate-in fade-in slide-in-from-bottom-5 duration-300">
          <div className="bg-stone-900 text-white p-4 rounded-xl shadow-2xl border border-stone-700 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-9 h-9 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center shrink-0">
                <CheckCircleIcon size={18} />
              </div>
              <div className="min-w-0 space-y-0.5">
                <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider block">
                  Added to Your Bag!
                </span>
                <p className="text-xs text-stone-200 truncate font-serif font-semibold">
                  {toastItem.name}
                </p>
                <div className="flex items-center gap-2 text-[11px] text-stone-400 font-mono">
                  <span>Size: {toastItem.size}</span>
                  <span>•</span>
                  <span>₹{toastItem.price.toLocaleString("en-IN")}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Link
                href="/storefront/cart"
                className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-stone-950 font-bold text-xs uppercase tracking-wider transition-colors flex items-center gap-1 shadow-sm"
              >
                <span>View Bag</span>
                <ArrowRightIcon size={12} />
              </Link>
              <button
                type="button"
                onClick={() => setToastItem(null)}
                className="p-1 text-stone-400 hover:text-white transition-colors"
                title="Dismiss"
              >
                <XIcon size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
