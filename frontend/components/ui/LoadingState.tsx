import React from "react";

export function SkeletonBlock({
  className = "",
}: {
  className?: string;
}) {
  return (
    <div
      className={`bg-[var(--surface-sunken)] rounded-[6px] animate-pulse ${className}`}
    />
  );
}

export function LoadingState({
  rows = 4,
  className = "",
}: {
  rows?: number;
  className?: string;
}) {
  return (
    <div
      className={`w-full bg-[var(--surface)] border border-[var(--border)] rounded-[8px] p-6 space-y-4 ${className}`}
    >
      <div className="flex items-center justify-between pb-4 border-b border-[var(--border)]">
        <SkeletonBlock className="h-6 w-48" />
        <SkeletonBlock className="h-8 w-24" />
      </div>

      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex items-center gap-4">
            <SkeletonBlock className="h-5 w-24" />
            <SkeletonBlock className="h-5 flex-1" />
            <SkeletonBlock className="h-5 w-28" />
            <SkeletonBlock className="h-5 w-20" />
          </div>
        ))}
      </div>
    </div>
  );
}
