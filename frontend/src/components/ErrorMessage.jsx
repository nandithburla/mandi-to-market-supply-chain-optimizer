import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export function ErrorMessage({ message, onRetry }) {
  return (
    <div className="rounded-2xl bg-rose-950/40 border border-rose-800/60 p-6 text-center space-y-3 max-w-lg mx-auto my-8">
      <div className="w-12 h-12 rounded-full bg-rose-900/50 border border-rose-700/50 flex items-center justify-center mx-auto text-rose-400">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-base font-bold text-white">Data Fetch Error</h3>
      <p className="text-xs text-rose-300/90">{message || "Failed to load analytical metrics from backend."}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-rose-700 hover:bg-rose-600 text-white transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
}
