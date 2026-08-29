import React from "react";

export function TableContainer({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`w-full overflow-x-auto border border-[var(--border)] rounded-[8px] bg-[var(--surface)] ${className}`}
    >
      {children}
    </div>
  );
}

export function Table({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <table className={`w-full text-left border-collapse text-sm ${className}`}>
      {children}
    </table>
  );
}

export function TableHead({ children }: { children: React.ReactNode }) {
  return (
    <thead className="bg-[var(--surface-sunken)] border-b border-[var(--border)]">
      {children}
    </thead>
  );
}

export function TableHeaderCell({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <th
      className={`px-4 py-3 text-[0.75rem] leading-[1rem] font-medium text-[var(--ink-400)] uppercase tracking-wider select-none ${className}`}
    >
      {children}
    </th>
  );
}

export function TableBody({ children }: { children: React.ReactNode }) {
  return <tbody className="divide-y divide-[var(--border)]">{children}</tbody>;
}

export function TableRow({
  children,
  className = "",
  onClick,
}: {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}) {
  return (
    <tr
      onClick={onClick}
      className={`transition-colors duration-100 hover:bg-[var(--surface-sunken)] ${
        onClick ? "cursor-pointer" : ""
      } ${className}`}
    >
      {children}
    </tr>
  );
}

export function TableCell({
  children,
  className = "",
  mono = false,
}: {
  children: React.ReactNode;
  className?: string;
  mono?: boolean;
}) {
  return (
    <td
      className={`px-4 py-3.5 text-[0.875rem] leading-[1.25rem] text-[var(--ink-900)] ${
        mono
          ? "font-mono text-[0.8125rem] leading-[1.125rem] tabular-nums"
          : ""
      } ${className}`}
    >
      {children}
    </td>
  );
}
