import React from "react";
import { AlertOctagonIcon, SearchIcon } from "./Icons";
import { Button } from "./Button";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  variant?: "default" | "danger";
  className?: string;
}

export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  variant = "default",
  className = "",
}: EmptyStateProps) {
  const isDanger = variant === "danger";

  return (
    <div
      className={`flex flex-col items-center justify-center p-10 text-center rounded-[8px] border ${
        isDanger
          ? "bg-[var(--danger-soft)] border-[#f5c6c2]"
          : "bg-[var(--surface)] border-[var(--border)]"
      } ${className}`}
    >
      <div
        className={`w-12 h-12 rounded-[8px] flex items-center justify-center mb-3.5 ${
          isDanger
            ? "bg-white text-[var(--danger)] shadow-sm"
            : "bg-[var(--surface-sunken)] text-[var(--ink-400)]"
        }`}
      >
        {icon ? (
          icon
        ) : isDanger ? (
          <AlertOctagonIcon size={24} />
        ) : (
          <SearchIcon size={24} />
        )}
      </div>

      <h3
        className={`text-[1.125rem] leading-[1.5rem] font-semibold mb-1 ${
          isDanger ? "text-[var(--danger)]" : "text-[var(--ink-900)]"
        }`}
      >
        {title}
      </h3>

      <p className="text-xs text-[var(--ink-600)] max-w-sm mb-4 leading-relaxed">
        {description}
      </p>

      {actionLabel && onAction && (
        <Button
          variant={isDanger ? "danger" : "secondary"}
          size="sm"
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
