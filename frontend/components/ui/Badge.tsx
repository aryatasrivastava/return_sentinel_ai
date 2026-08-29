import React from "react";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "neutral" | "accent" | "success" | "warning" | "danger";
  size?: "sm" | "md";
  icon?: React.ReactNode;
  children: React.ReactNode;
}

export function Badge({
  variant = "neutral",
  size = "md",
  icon,
  children,
  className = "",
  ...props
}: BadgeProps) {
  const baseStyles =
    "inline-flex items-center font-medium border select-none transition-colors";

  const sizeStyles = {
    sm: "text-[11px] px-1.5 py-0.5 rounded-[4px] gap-1 leading-tight",
    md: "text-xs px-2 py-0.5 rounded-[6px] gap-1.5 leading-snug",
  };

  const variantStyles = {
    neutral:
      "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--ink-600)]",
    accent:
      "bg-[var(--accent-soft)] border-[#d0d7f3] text-[var(--accent)]",
    success:
      "bg-[var(--success-soft)] border-[#bfe7db] text-[var(--success)]",
    warning:
      "bg-[var(--warning-soft)] border-[#f2debf] text-[var(--warning)]",
    danger:
      "bg-[var(--danger-soft)] border-[#f5c6c2] text-[var(--danger)]",
  };

  return (
    <span
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{children}</span>
    </span>
  );
}
