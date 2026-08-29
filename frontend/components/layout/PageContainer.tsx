import React from "react";

export function PageContainer({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`w-full max-w-[1280px] mx-auto px-4 sm:px-6 md:px-8 py-6 space-y-6 ${className}`}
    >
      {children}
    </div>
  );
}
