import React from "react";

export function LoadingSkeleton({ cards = 4, charts = 2 }) {
  return (
    <div className="space-y-6 animate-pulse">
      {/* KPI Cards Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: cards }).map((_, i) => (
          <div
            key={i}
            className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5 space-y-3"
          >
            <div className="h-3 w-24 bg-slate-800 rounded-full" />
            <div className="h-8 w-36 bg-slate-700/60 rounded-lg" />
            <div className="h-2 w-full bg-slate-800/80 rounded-full pt-2" />
          </div>
        ))}
      </div>

      {/* Chart Panels Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Array.from({ length: charts }).map((_, i) => (
          <div
            key={i}
            className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-4 h-80 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between">
              <div className="h-4 w-48 bg-slate-800 rounded-full" />
              <div className="h-4 w-16 bg-slate-800 rounded-full" />
            </div>
            <div className="h-52 bg-slate-800/40 rounded-xl flex items-center justify-center text-slate-600 text-xs font-mono">
              Computing analytical trends...
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
