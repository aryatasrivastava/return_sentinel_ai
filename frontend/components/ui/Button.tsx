import React from "react";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
}

export function Button({
  variant = "primary",
  size = "md",
  children,
  icon,
  iconPosition = "left",
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles =
    "inline-flex items-center justify-center font-medium rounded-[6px] transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] disabled:opacity-50 disabled:cursor-not-allowed select-none";

  const sizeStyles = {
    sm: "text-xs px-2.5 py-1.5 gap-1.5",
    md: "text-sm px-3.5 py-2 gap-2",
    lg: "text-base px-4 py-2.5 gap-2.5",
  };

  const variantStyles = {
    primary:
      "bg-[var(--accent)] text-white hover:bg-[#324187] active:bg-[#2a3774] shadow-none",
    secondary:
      "bg-[var(--surface-sunken)] text-[var(--ink-900)] border border-[var(--border)] hover:bg-[#e5e8ef] active:bg-[#dbe0e9]",
    outline:
      "bg-[var(--surface)] border border-[var(--border)] text-[var(--ink-900)] hover:bg-[var(--surface-sunken)] active:bg-[#e5e8ef]",
    ghost:
      "bg-transparent text-[var(--ink-600)] hover:text-[var(--ink-900)] hover:bg-[var(--surface-sunken)] active:bg-[#e5e8ef]",
    danger:
      "bg-[var(--danger)] text-white hover:bg-[#9f3832] active:bg-[#8d312b]",
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {icon && iconPosition === "left" && <span className="shrink-0">{icon}</span>}
      <span>{children}</span>
      {icon && iconPosition === "right" && <span className="shrink-0">{icon}</span>}
    </button>
  );
}
