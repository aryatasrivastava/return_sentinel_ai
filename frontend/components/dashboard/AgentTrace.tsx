"use client";

import React, { useState } from "react";
import { AgentStep } from "@/lib/types";
import { Card, CardHeader } from "../ui/Card";
import { CpuIcon, TerminalIcon, GitBranchIcon, ShieldCheckIcon } from "../ui/Icons";

export interface AgentTraceProps {
  steps: AgentStep[];
  title?: string;
  subtitle?: string;
  orderId?: string;
  interactive?: boolean;
  className?: string;
}

export function AgentTrace({
  steps,
  title = "Agent Decision Trace",
  subtitle = "Live deterministic execution graph & tool verification stream",
  orderId = "ORD-9421",
  interactive = true,
  className = "",
}: AgentTraceProps) {
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({
    step_2: true, // open first tool payload by default
    step_3: false,
    step_5: true, // open ML prediction
  });

  const toggleStep = (id: string) => {
    if (!interactive) return;
    setExpandedSteps((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  // Render the distinct node icon marker for each step type
  const renderNodeMarker = (step: AgentStep) => {
    switch (step.type) {
      case "agent":
        // Filled indigo circle
        return (
          <div
            className="w-7 h-7 rounded-full bg-[var(--accent)] text-white flex items-center justify-center shadow-sm shrink-0 ring-4 ring-white z-10"
            title="Agent Decision Node"
          >
            <CpuIcon size={13} className="text-white" />
          </div>
        );

      case "tool":
        // Slate square marker
        return (
          <div
            className="w-7 h-7 rounded-[4px] bg-[var(--ink-900)] text-white flex items-center justify-center shadow-sm shrink-0 ring-4 ring-white z-10"
            title="Tool Execution Node"
          >
            <TerminalIcon size={12} className="text-white" />
          </div>
        );

      case "ml":
        // Amber diamond marker
        return (
          <div
            className="w-7 h-7 bg-[var(--warning)] text-white flex items-center justify-center shadow-sm shrink-0 rotate-45 ring-4 ring-white z-10 rounded-[2px]"
            title="ML Model Inference Node"
          >
            <span className="-rotate-45 font-mono text-[10px] font-bold">ML</span>
          </div>
        );

      case "routing":
        // Routing decision node / fork
        return (
          <div
            className="w-7 h-7 rounded-full bg-[var(--accent-soft)] border-2 border-[var(--accent)] text-[var(--accent)] flex items-center justify-center shadow-sm shrink-0 ring-4 ring-white z-10"
            title="Confidence Router Branch"
          >
            <GitBranchIcon size={13} className="text-[var(--accent)]" />
          </div>
        );

      case "policy":
        // Final policy node -> Green pill / badge marker
        return (
          <div
            className="w-7 h-7 rounded-[6px] bg-[var(--success)] text-white flex items-center justify-center shadow-sm shrink-0 ring-4 ring-white z-10"
            title="Final Policy Action Node"
          >
            <ShieldCheckIcon size={14} className="text-white" />
          </div>
        );

      default:
        return (
          <div className="w-6 h-6 rounded-full bg-[var(--ink-400)] text-white flex items-center justify-center ring-4 ring-white z-10" />
        );
    }
  };

  return (
    <Card className={`overflow-hidden ${className}`}>
      <CardHeader
        title={title}
        subtitle={subtitle}
        badge={
          <span className="font-mono text-xs bg-[var(--surface-sunken)] border border-[var(--border)] px-2 py-0.5 rounded-[4px] text-[var(--ink-600)] tabular-nums">
            Order: {orderId}
          </span>
        }
      />

      {/* Vertical Connected Timeline Container */}
      <div className="relative pl-2 pr-1 py-2">
        <div className="space-y-6 relative">
          {steps.map((step, idx) => {
            const isLast = idx === steps.length - 1;
            const isExpanded = !!expandedSteps[step.id];
            const isCompleted = step.status === "complete";

            return (
              <div key={step.id} className="relative flex items-start gap-4 group">
                {/* Connecting Line Segment */}
                {!isLast && (
                  <div
                    className={`absolute left-[13px] top-7 w-[2px] h-[calc(100%+24px)] ${
                      step.type === "routing"
                        ? "border-l-2 border-dashed border-[var(--accent)]"
                        : isCompleted
                        ? "bg-[var(--border)]"
                        : "border-l-2 border-dashed border-[var(--border)]"
                    }`}
                  />
                )}

                {/* Node Marker */}
                <div className="shrink-0 pt-0.5">
                  {renderNodeMarker(step)}
                </div>

                {/* Step Content Card */}
                <div
                  onClick={() => toggleStep(step.id)}
                  className={`flex-1 rounded-[6px] border transition-all duration-150 p-3.5 ${
                    step.type === "policy"
                      ? "bg-[var(--success-soft)] border-[#bfe7db]"
                      : step.type === "ml"
                      ? "bg-[var(--warning-soft)]/30 border-[#f2debf]"
                      : "bg-[var(--surface)] border-[var(--border)] hover:border-[var(--ink-400)]"
                  } ${interactive ? "cursor-pointer" : ""}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      {/* Step Type Pill */}
                      <span className="text-[10px] uppercase font-semibold tracking-wider text-[var(--ink-400)]">
                        {step.type === "tool"
                          ? "Tool Invocation"
                          : step.type === "ml"
                          ? "Inference"
                          : step.type === "routing"
                          ? "Router Branch"
                          : step.type === "policy"
                          ? "Policy Resolution"
                          : "Agent Decision"}
                      </span>

                      {step.durationMs && (
                        <span className="font-mono text-[10px] text-[var(--ink-400)] tabular-nums">
                          • {step.durationMs}ms
                        </span>
                      )}
                    </div>

                    {step.timestamp && (
                      <span className="font-mono text-[11px] text-[var(--ink-400)] tabular-nums">
                        {step.timestamp}
                      </span>
                    )}
                  </div>

                  {/* Step Label */}
                  <div className="text-sm font-medium text-[var(--ink-900)] mb-1">
                    {step.type === "tool" ? (
                      <code className="font-mono text-xs bg-[var(--surface-sunken)] border border-[var(--border)] px-1.5 py-0.5 rounded-[4px] text-[var(--ink-900)]">
                        {step.label}
                      </code>
                    ) : step.type === "ml" ? (
                      <span className="font-mono text-sm font-semibold text-[var(--warning)]">
                        {step.label}
                      </span>
                    ) : step.type === "policy" ? (
                      <span className="font-semibold text-[var(--success)] inline-flex items-center gap-1.5">
                        <span className="font-mono bg-white px-2 py-0.5 rounded-[4px] border border-[#bfe7db] shadow-none">
                          {step.label}
                        </span>
                      </span>
                    ) : (
                      <span>{step.label}</span>
                    )}
                  </div>

                  {/* Step Detail Explanation */}
                  {step.detail && (
                    <p className="text-xs text-[var(--ink-600)] leading-relaxed">
                      {step.detail}
                    </p>
                  )}

                  {/* Expandable JSON / Tool Output Payload */}
                  {step.output && (
                    <div className="mt-2 pt-2 border-t border-[var(--border)]/60">
                      <div className="flex items-center justify-between text-[11px] text-[var(--ink-400)] mb-1">
                        <span>Payload Output:</span>
                        <span className="text-[10px] underline">
                          {isExpanded ? "Hide payload" : "Show payload"}
                        </span>
                      </div>

                      {isExpanded && (
                        <pre className="font-mono text-[11px] bg-[var(--surface-sunken)] text-[var(--ink-900)] p-2.5 rounded-[4px] overflow-x-auto border border-[var(--border)] leading-relaxed">
                          {(() => {
                            try {
                              return JSON.stringify(
                                JSON.parse(step.output),
                                null,
                                2
                              );
                            } catch {
                              return step.output;
                            }
                          })()}
                        </pre>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
