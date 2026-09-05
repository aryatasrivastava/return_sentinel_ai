"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import {
  StorefrontProduct,
  StorefrontCustomer,
  getStorefrontCustomers,
} from "@/lib/api/storefront";

export interface StorefrontCartItem {
  product_id: number;
  name: string;
  sku: string;
  category: string | null;
  price: number;
  size: string;
  quantity: number;
}

interface StorefrontContextType {
  customers: StorefrontCustomer[];
  selectedCustomer: StorefrontCustomer | null;
  setSelectedCustomer: (customer: StorefrontCustomer) => void;
  cart: StorefrontCartItem[];
  addToCart: (product: StorefrontProduct, size: string, quantity?: number) => void;
  updateQuantity: (product_id: number, size: string, quantity: number) => void;
  removeFromCart: (product_id: number, size: string) => void;
  clearCart: () => void;
  cartTotal: number;
  cartCount: number;
  getItemQuantity: (product_id: number, size: string) => number;
  isLoadingCustomers: boolean;
}

const StorefrontContext = createContext<StorefrontContextType | undefined>(undefined);

export function StorefrontProvider({ children }: { children: React.ReactNode }) {
  const [customers, setCustomers] = useState<StorefrontCustomer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<StorefrontCustomer | null>(null);
  const [cart, setCart] = useState<StorefrontCartItem[]>([]);
  const [isLoadingCustomers, setIsLoadingCustomers] = useState(true);

  // Load seeded customers on mount
  useEffect(() => {
    async function loadCustomers() {
      try {
        const data = await getStorefrontCustomers();
        setCustomers(data);
        if (data.length > 0) {
          // Default to Customer #19 (Ananya Sharma) or first in list
          const defaultCust = data.find((c) => c.id === 19) || data[0];
          setSelectedCustomer(defaultCust);
        }
      } catch (err) {
        console.error("Failed to load storefront demo customers:", err);
      } finally {
        setIsLoadingCustomers(false);
      }
    }
    loadCustomers();
  }, []);

  const addToCart = useCallback(
    (product: StorefrontProduct, size: string, quantity: number = 1) => {
      setCart((prev) => {
        const existingIndex = prev.findIndex(
          (item) => item.product_id === product.id && item.size === size
        );
        if (existingIndex > -1) {
          const updated = [...prev];
          updated[existingIndex].quantity += quantity;
          return updated;
        } else {
          return [
            ...prev,
            {
              product_id: product.id,
              name: product.name,
              sku: product.sku,
              category: product.category,
              price: product.price,
              size,
              quantity,
            },
          ];
        }
      });
    },
    []
  );

  const updateQuantity = useCallback(
    (product_id: number, size: string, quantity: number) => {
      setCart((prev) => {
        if (quantity <= 0) {
          return prev.filter(
            (item) => !(item.product_id === product_id && item.size === size)
          );
        }
        return prev.map((item) =>
          item.product_id === product_id && item.size === size
            ? { ...item, quantity }
            : item
        );
      });
    },
    []
  );

  const removeFromCart = useCallback((product_id: number, size: string) => {
    setCart((prev) =>
      prev.filter(
        (item) => !(item.product_id === product_id && item.size === size)
      )
    );
  }, []);

  const clearCart = useCallback(() => {
    setCart([]);
  }, []);

  const cartTotal = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  const cartCount = cart.reduce((count, item) => count + item.quantity, 0);

  const getItemQuantity = useCallback(
    (product_id: number, size: string) => {
      const item = cart.find(
        (i) => i.product_id === product_id && i.size === size
      );
      return item ? item.quantity : 0;
    },
    [cart]
  );

  return (
    <StorefrontContext.Provider
      value={{
        customers,
        selectedCustomer,
        setSelectedCustomer,
        cart,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        cartTotal,
        cartCount,
        getItemQuantity,
        isLoadingCustomers,
      }}
    >
      {children}
    </StorefrontContext.Provider>
  );
}

export function useStorefront() {
  const context = useContext(StorefrontContext);
  if (!context) {
    throw new Error("useStorefront must be used within a StorefrontProvider");
  }
  return context;
}
