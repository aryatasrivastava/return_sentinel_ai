"use client";

import React, { useState } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import {
  SettingsIcon,
  ShieldCheckIcon,
  CheckCircleIcon,
} from "@/components/ui/Icons";

export default function SettingsPage() {
  const [savedNotification, setSavedNotification] = useState(false);

  const [settings, setSettings] = useState({
    storeName: "Acme Luxury Apparel",
    storeUrl: "https://acmeluxury.in",
    currency: "INR (₹)",
    categoryFocus: "Apparel & Occasionwear",
    webhookUrl: "https://api.acmeluxury.in/webhooks/returnsentinel",
    lowRiskThreshold: 35,
    highRiskThreshold: 75,
    confidenceThreshold: 85,
    restockingFeePercent: 15,
    standardReturnDays: 14,
    emailAlerts: true,
    dailyDigest: true,
    webhookDispatch: true,
  });

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedNotification(true);
    setTimeout(() => setSavedNotification(false), 3000);
  };

  return (
    <PageContainer>
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-[var(--surface)] border border-[var(--border)] rounded-[8px] p-4">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <SettingsIcon size={18} className="text-[var(--accent)]" />
            <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
              Store & Model Configuration
            </h2>
          </div>
          <p className="text-xs text-[var(--ink-600)]">
            Configure risk tolerance thresholds, policy engine parameters, and integrations
          </p>
        </div>

        {savedNotification && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[6px] bg-[var(--success-soft)] text-[var(--success)] border border-[#bfe7db] text-xs font-medium animate-fadeIn">
            <CheckCircleIcon size={14} />
            Settings saved successfully (Mock Local State)
          </div>
        )}
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Section 1: Merchant Profile */}
        <Card>
          <CardHeader
            title="Merchant Profile"
            subtitle="Store identity and catalog domain settings"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--ink-900)]">
                Merchant / Store Name
              </label>
              <input
                type="text"
                value={settings.storeName}
                onChange={(e) =>
                  setSettings({ ...settings, storeName: e.target.value })
                }
                className="w-full px-3 py-2 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] text-xs text-[var(--ink-900)] focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring)]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--ink-900)]">
                Primary Storefront URL
              </label>
              <input
                type="text"
                value={settings.storeUrl}
                onChange={(e) =>
                  setSettings({ ...settings, storeUrl: e.target.value })
                }
                className="w-full px-3 py-2 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] text-xs text-[var(--ink-900)] focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring)]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--ink-900)]">
                Catalog Category Focus
              </label>
              <select
                value={settings.categoryFocus}
                onChange={(e) =>
                  setSettings({ ...settings, categoryFocus: e.target.value })
                }
                className="w-full px-3 py-2 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] text-xs text-[var(--ink-900)] focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring)]"
              >
                <option>Apparel & Occasionwear</option>
                <option>Footwear & Accessories</option>
                <option>Jewellery & Luxury Goods</option>
                <option>Electronics & Gadgets</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--ink-900)]">
                Operating Currency
              </label>
              <input
                type="text"
                disabled
                value={settings.currency}
                className="w-full px-3 py-2 bg-[var(--surface-sunken)]/60 border border-[var(--border)] rounded-[6px] text-xs text-[var(--ink-600)] cursor-not-allowed"
              />
            </div>
          </div>
        </Card>

        {/* Section 2: Risk Sensitivity & Model Thresholds */}
        <Card>
          <CardHeader
            title="Risk Sensitivity & Thresholds"
            subtitle="Control model scoring boundaries for policy enforcement"
          />

          <div className="space-y-5">
            {/* Low Risk Threshold Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-[var(--ink-900)]">
                  Low Risk Ceiling (Standard Return Pass-Through)
                </span>
                <span className="font-mono font-semibold text-[var(--success)] tabular-nums">
                  ≤ {settings.lowRiskThreshold} / 100
                </span>
              </div>
              <input
                type="range"
                min="10"
                max="50"
                value={settings.lowRiskThreshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    lowRiskThreshold: Number(e.target.value),
                  })
                }
                className="w-full accent-[var(--accent)] cursor-pointer"
              />
              <p className="text-[11px] text-[var(--ink-400)]">
                Orders with risk score below this value are granted full 14-day standard return windows automatically.
              </p>
            </div>

            {/* High Risk Trigger Threshold Slider */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-[var(--ink-900)]">
                  High Risk Trigger Threshold (Store Credit & Restocking Fee)
                </span>
                <span className="font-mono font-semibold text-[var(--danger)] tabular-nums">
                  ≥ {settings.highRiskThreshold} / 100
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="90"
                value={settings.highRiskThreshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    highRiskThreshold: Number(e.target.value),
                  })
                }
                className="w-full accent-[var(--accent)] cursor-pointer"
              />
              <p className="text-[11px] text-[var(--ink-400)]">
                Orders meeting or exceeding this threshold trigger defensive policies (Restocking fee / Store credit only).
              </p>
            </div>

            {/* Confidence Router Threshold */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-[var(--ink-900)]">
                  Autonomous Policy Confidence Cutoff
                </span>
                <span className="font-mono font-semibold text-[var(--accent)] tabular-nums">
                  {settings.confidenceThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="70"
                max="95"
                value={settings.confidenceThreshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    confidenceThreshold: Number(e.target.value),
                  })
                }
                className="w-full accent-[var(--accent)] cursor-pointer"
              />
              <p className="text-[11px] text-[var(--ink-400)]">
                If model certainty falls below {settings.confidenceThreshold}%, decision is routed for secondary verification instead of automatic policy mutation.
              </p>
            </div>
          </div>
        </Card>

        {/* Section 3: Return Policy Configuration */}
        <Card>
          <CardHeader
            title="Return Policy Parameters"
            subtitle="Configure fee percentages and exchange guarantees"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--ink-900)]">
                Standard Return Window (Days)
              </label>
              <input
                type="number"
                value={settings.standardReturnDays}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    standardReturnDays: Number(e.target.value),
                  })
                }
                className="w-full px-3 py-2 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] text-xs font-mono text-[var(--ink-900)] focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring)]"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[var(--ink-900)]">
                High-Risk Restocking Fee Percentage (%)
              </label>
              <input
                type="number"
                value={settings.restockingFeePercent}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    restockingFeePercent: Number(e.target.value),
                  })
                }
                className="w-full px-3 py-2 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] text-xs font-mono text-[var(--ink-900)] focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring)]"
              />
            </div>

            <div className="md:col-span-2 space-y-1.5">
              <label className="text-xs font-medium text-[var(--ink-900)]">
                Webhook Dispatch Endpoint (Order Intercept Events)
              </label>
              <input
                type="text"
                value={settings.webhookUrl}
                onChange={(e) =>
                  setSettings({ ...settings, webhookUrl: e.target.value })
                }
                className="w-full px-3 py-2 bg-[var(--surface-sunken)] border border-[var(--border)] rounded-[6px] text-xs font-mono text-[var(--ink-900)] focus:outline-none focus:ring-2 focus:ring-[var(--focus-ring)]"
              />
            </div>
          </div>
        </Card>

        {/* Section 4: Notification Preferences */}
        <Card>
          <CardHeader
            title="Notification Preferences"
            subtitle="Alert channels for high-threat intercepts and daily audit digests"
          />

          <div className="space-y-3">
            {[
              {
                id: "emailAlerts",
                label: "Instant High-Risk Email Alerts",
                desc: "Send instant notification to merchant fraud team when an order score exceeds 85/100.",
                checked: settings.emailAlerts,
              },
              {
                id: "dailyDigest",
                label: "Daily Audit & Margin Protection Digest",
                desc: "Receive daily summary at 08:00 AM detailing prevented margin loss and policy distribution.",
                checked: settings.dailyDigest,
              },
              {
                id: "webhookDispatch",
                label: "Real-Time Webhook Policy Dispatch",
                desc: "Emit event payload to merchant OMS/ERP on checkout policy attachment.",
                checked: settings.webhookDispatch,
              },
            ].map((item) => (
              <label
                key={item.id}
                className="flex items-start gap-3 p-3 rounded-[6px] bg-[var(--surface-sunken)] border border-[var(--border)] cursor-pointer hover:bg-[#e6e9f2] transition-colors"
              >
                <input
                  type="checkbox"
                  checked={item.checked}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      [item.id]: e.target.checked,
                    })
                  }
                  className="mt-0.5 accent-[var(--accent)] h-4 w-4 rounded-[4px]"
                />
                <div className="space-y-0.5 select-none">
                  <span className="text-xs font-semibold text-[var(--ink-900)] block">
                    {item.label}
                  </span>
                  <span className="text-xs text-[var(--ink-600)] block">
                    {item.desc}
                  </span>
                </div>
              </label>
            ))}
          </div>
        </Card>

        {/* Submit Action Button */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            type="submit"
            variant="primary"
            size="md"
            icon={<ShieldCheckIcon size={16} />}
          >
            Save Configuration
          </Button>
        </div>
      </form>
    </PageContainer>
  );
}
