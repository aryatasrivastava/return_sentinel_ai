"use client";

import React, { useState, useEffect, useCallback } from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { Card, CardHeader } from "@/components/ui/Card";
import { PolicyBadge } from "@/components/policies/PolicyBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { LoadingState } from "@/components/ui/LoadingState";
import { Button } from "@/components/ui/Button";
import {
  ShieldCheckIcon,
  PolicyIcon,
  CheckCircleIcon,
  AlertOctagonIcon,
  SaveIcon,
  RefreshCwIcon,
} from "@/components/ui/Icons";
import {
  getPolicyConfig,
  updatePolicyConfig,
  PolicyConfigResponse,
} from "@/lib/api/policyConfig";
import { PolicyType } from "@/lib/types";

const ALL_POLICIES: { type: PolicyType; name: string; description: string }[] = [
  {
    type: "STANDARD_RETURN",
    name: "Standard Return",
    description: "Standard refund policy with zero customer friction",
  },
  {
    type: "EXCHANGE_FIRST",
    name: "Exchange First",
    description: "Prioritizes instant replacement/size swap before cash refund",
  },
  {
    type: "STORE_CREDIT",
    name: "Store Credit",
    description: "Restricts cash outflow to non-expiring store credit bonus",
  },
  {
    type: "RESTOCKING_FEE",
    name: "Restocking Fee",
    description: "Deducts a refurbishment fee on high-risk liquidation returns",
  },
];

const RISK_BANDS = [
  {
    key: "low" as const,
    label: "LOW RISK",
    badgeClass: "bg-[var(--success-soft)] text-[var(--success)] border-[#bfe7db]",
    description: "Standard shoppers with low historical return volume and no bracketing",
  },
  {
    key: "medium" as const,
    label: "MEDIUM RISK",
    badgeClass: "bg-[var(--warning-soft)] text-[var(--warning)] border-[#f2debf]",
    description: "Borderline orders, category-specific return histories, or mild bracketing",
  },
  {
    key: "high" as const,
    label: "HIGH RISK",
    badgeClass: "bg-[var(--danger-soft)] text-[var(--danger)] border-[#f5c6c2]",
    description: "Serial returners, severe multi-size bracketing, or heavy wardrobing indicators",
  },
];

export default function PoliciesPage() {
  const [config, setConfig] = useState<PolicyConfigResponse | null>(null);
  const [lowRisk, setLowRisk] = useState<PolicyType[]>([]);
  const [mediumRisk, setMediumRisk] = useState<PolicyType[]>([]);
  const [highRisk, setHighRisk] = useState<PolicyType[]>([]);
  const [fallback, setFallback] = useState<PolicyType>("EXCHANGE_FIRST");

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  const fetchConfig = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getPolicyConfig();
      setConfig(data);
      setLowRisk(data.low_risk_allowed || []);
      setMediumRisk(data.medium_risk_allowed || []);
      setHighRisk(data.high_risk_allowed || []);
      setFallback(data.low_confidence_fallback || "EXCHANGE_FIRST");
    } catch (err: any) {
      setError(err.message || "Failed to load policy configuration from backend.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  // Handle matrix checkbox toggle
  const togglePolicy = (
    band: "low" | "medium" | "high",
    policy: PolicyType
  ) => {
    setSaveSuccess(false);
    setValidationError(null);

    const updateList = (prev: PolicyType[]) =>
      prev.includes(policy)
        ? prev.filter((p) => p !== policy)
        : [...prev, policy];

    if (band === "low") setLowRisk(updateList);
    if (band === "medium") setMediumRisk(updateList);
    if (band === "high") setHighRisk(updateList);
  };

  // Client-side validation
  const validate = (): boolean => {
    if (lowRisk.length === 0) {
      setValidationError("Low Risk tier must have at least one allowed policy enabled.");
      return false;
    }
    if (mediumRisk.length === 0) {
      setValidationError("Medium Risk tier must have at least one allowed policy enabled.");
      return false;
    }
    if (highRisk.length === 0) {
      setValidationError("High Risk tier must have at least one allowed policy enabled.");
      return false;
    }
    setValidationError(null);
    return true;
  };

  const handleSave = async () => {
    if (!validate()) return;

    setIsSaving(true);
    setError(null);
    setSaveSuccess(false);

    try {
      const updated = await updatePolicyConfig({
        low_risk_allowed: lowRisk,
        medium_risk_allowed: mediumRisk,
        high_risk_allowed: highRisk,
        low_confidence_fallback: fallback,
      });

      setConfig(updated);
      setLowRisk(updated.low_risk_allowed);
      setMediumRisk(updated.medium_risk_allowed);
      setHighRisk(updated.high_risk_allowed);
      setFallback(updated.low_confidence_fallback);
      setSaveSuccess(true);
    } catch (err: any) {
      setError(err.message || "Failed to save policy configuration.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <PageContainer>
        <LoadingState rows={6} />
      </PageContainer>
    );
  }

  if (error && !config) {
    return (
      <PageContainer>
        <EmptyState
          variant="danger"
          title="Policy Config Unavailable"
          description={error}
          actionLabel="Retry"
          onAction={fetchConfig}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* Top Banner / Summary */}
      <Card className="bg-[var(--surface)] p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <PolicyIcon size={20} className="text-[var(--accent)]" />
              <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)]">
                Merchant Return Policy Matrix Editor
              </h2>
            </div>
            <p className="text-xs text-[var(--ink-600)] max-w-2xl leading-relaxed">
              Configure which defensive return policies the AI Policy Agent is allowed to recommend for each risk band. All selections are strictly validated and enforced in real time by the Policy Engine.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <div className="px-3 py-1.5 rounded-[6px] bg-[var(--success-soft)] border border-[#bfe7db] text-xs font-medium text-[var(--success)] flex items-center gap-1.5">
              <ShieldCheckIcon size={14} />
              Policy Engine: Enforcing Live Matrix
            </div>
          </div>
        </div>
      </Card>

      {/* Save Success Banner */}
      {saveSuccess && (
        <div className="p-4 rounded-[6px] bg-[var(--success-soft)] border border-[#bfe7db] flex items-center justify-between text-xs text-[var(--success)]">
          <div className="flex items-center gap-2 font-medium">
            <CheckCircleIcon size={16} />
            <span>Policy matrix configuration successfully saved and persisted to database!</span>
          </div>
          {config?.updated_at && (
            <span className="font-mono text-[11px] text-[var(--ink-600)]">
              Updated: {new Date(config.updated_at).toLocaleTimeString("en-IN")}
            </span>
          )}
        </div>
      )}

      {/* Validation Error Banner */}
      {(validationError || error) && (
        <div className="p-4 rounded-[6px] bg-[var(--danger-soft)] border border-[#f5c6c2] flex items-center gap-2 text-xs text-[var(--danger)]">
          <AlertOctagonIcon size={16} className="shrink-0" />
          <span>{validationError || error}</span>
        </div>
      )}

      {/* Policy Allowed-Set Matrix (3 Risk Bands x 4 Policy Columns) */}
      <Card>
        <CardHeader
          title="Allowed Return Policies by Threat Tier"
          subtitle="Select at least one permitted policy per risk tier"
          badge={
            <span className="font-mono text-xs bg-[var(--surface-sunken)] border border-[var(--border)] px-2 py-0.5 rounded-[4px] text-[var(--ink-600)]">
              3 Risk Tiers • 4 Policies
            </span>
          }
        />

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[var(--border)] bg-[var(--surface-sunken)]">
                <th className="p-3.5 font-semibold text-[var(--ink-900)] w-1/4">
                  Risk Tier
                </th>
                {ALL_POLICIES.map((p) => (
                  <th key={p.type} className="p-3.5 font-semibold text-[var(--ink-900)] text-center">
                    <div className="flex flex-col items-center gap-1">
                      <PolicyBadge policy={p.type} size="sm" />
                      <span className="text-[10px] text-[var(--ink-400)] font-normal max-w-[120px] text-center">
                        {p.name}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {RISK_BANDS.map((band) => {
                const currentAllowed =
                  band.key === "low"
                    ? lowRisk
                    : band.key === "medium"
                    ? mediumRisk
                    : highRisk;

                const hasNoneSelected = currentAllowed.length === 0;

                return (
                  <tr
                    key={band.key}
                    className={`transition-colors ${
                      hasNoneSelected ? "bg-[var(--danger-soft)]/20" : "hover:bg-[var(--surface-sunken)]/50"
                    }`}
                  >
                    <td className="p-3.5 align-middle">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded-[4px] font-mono text-[10px] font-bold border uppercase tracking-wider ${band.badgeClass}`}
                          >
                            {band.label}
                          </span>
                          {hasNoneSelected && (
                            <span className="text-[10px] font-semibold text-[var(--danger)]">
                              (Required: select &ge; 1)
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-[var(--ink-400)]">
                          {band.description}
                        </p>
                      </div>
                    </td>

                    {ALL_POLICIES.map((p) => {
                      const isChecked = currentAllowed.includes(p.type);
                      return (
                        <td key={p.type} className="p-3.5 text-center align-middle">
                          <label className="inline-flex items-center justify-center cursor-pointer p-2 rounded-[6px] hover:bg-white transition-colors">
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => togglePolicy(band.key, p.type)}
                              className="w-4 h-4 rounded border-[var(--border)] text-[var(--accent)] focus:ring-[var(--focus-ring)] cursor-pointer"
                            />
                          </label>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Low Confidence Fallback Selector */}
      <Card>
        <CardHeader
          title="Low-Confidence Safety Fallback Policy"
          subtitle="Applied when model prediction confidence is too low (<50%) to ensure fair customer treatment"
        />

        <div className="space-y-4">
          <p className="text-xs text-[var(--ink-600)] leading-relaxed">
            When customer behavior or catalog telemetry is insufficient to produce a high-confidence prediction, ReturnSentinel bypasses aggressive risk bands and safely falls back to this merchant-designated policy.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
            {ALL_POLICIES.map((p) => {
              const isSelected = fallback === p.type;
              return (
                <div
                  key={p.type}
                  onClick={() => {
                    setSaveSuccess(false);
                    setFallback(p.type);
                  }}
                  className={`p-3.5 rounded-[6px] border cursor-pointer transition-all space-y-2 ${
                    isSelected
                      ? "bg-[var(--accent-soft)] border-[var(--accent)] ring-2 ring-[var(--focus-ring)]"
                      : "bg-[var(--surface-sunken)] border-[var(--border)] hover:border-[var(--ink-400)]"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <PolicyBadge policy={p.type} size="sm" />
                    <input
                      type="radio"
                      name="fallback_policy"
                      checked={isSelected}
                      onChange={() => setFallback(p.type)}
                      className="cursor-pointer"
                    />
                  </div>
                  <p className="text-[11px] text-[var(--ink-600)]">
                    {p.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </Card>

      {/* Action Footer: Save & Re-fetch Buttons */}
      <div className="flex items-center justify-between pt-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={fetchConfig}
          disabled={isLoading || isSaving}
          className="flex items-center gap-1.5"
        >
          <RefreshCwIcon size={14} className={isLoading ? "animate-spin" : ""} />
          Discard Changes / Reload
        </Button>

        <Button
          variant="primary"
          size="md"
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-2"
        >
          <SaveIcon size={16} />
          {isSaving ? "Saving Configuration..." : "Save Policy Configuration"}
        </Button>
      </div>
    </PageContainer>
  );
}
