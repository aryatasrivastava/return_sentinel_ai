import React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "sunken" | "flat";
  noPadding?: boolean;
}

export function Card({
  variant = "default",
  noPadding = false,
  children,
  className = "",
  ...props
}: CardProps) {
  const bgStyles = {
    default: "bg-[var(--surface)] border border-[var(--border)]",
    sunken: "bg-[var(--surface-sunken)] border border-[var(--border)]",
    flat: "bg-[var(--surface)] border-0",
  };

  return (
    <div
      className={`rounded-[8px] overflow-hidden ${bgStyles[variant]} ${
        noPadding ? "" : "p-5"
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export interface CardHeaderProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  badge?: React.ReactNode;
  className?: string;
}

export function CardHeader({
  title,
  subtitle,
  action,
  badge,
  className = "",
}: CardHeaderProps) {
  return (
    <div
      className={`flex items-start justify-between gap-4 pb-4 mb-4 border-b border-[var(--border)] ${className}`}
    >
      <div className="space-y-0.5 min-w-0">
        <div className="flex items-center gap-2">
          <h2 className="text-[1.125rem] leading-[1.5rem] font-semibold text-[var(--ink-900)] tracking-tight">
            {title}
          </h2>
          {badge}
        </div>
        {subtitle && (
          <p className="text-xs text-[var(--ink-600)] leading-relaxed">
            {subtitle}
          </p>
        )}
      </div>
      {action && <div className="shrink-0 flex items-center gap-2">{action}</div>}
    </div>
  );
}
