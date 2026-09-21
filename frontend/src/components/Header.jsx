import React, { useState, useEffect } from "react";
import {
  Filter,
  RefreshCw,
  Sparkles,
  Server,
  Calendar,
  Clock,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

export function Header({
  activeTab,
  navItems,
  onRefresh,
  isLoading,
  showFilters,
  setShowFilters,
  onOpenAssistant,
  health,
}) {
  const [currentTime, setCurrentTime] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleDateString("en-IN", {
          timeZone: "Asia/Kolkata",
          day: "numeric",
          month: "short",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const currentItem = navItems.find((item) => item.id === activeTab) || navItems[0];

  const pageDescriptions = {
    overview: "Real-time state agriculture overview tracking arrivals, prices, MSP compliance, and risk across Mandis.",
    arrivals: "In-depth arrival volumes, daily crop supply distributions, and Mandi trading performance.",
    prices: "Wholesale modal price monitoring, Minimum Support Price (MSP) comparison, and distress-sale detection.",
    weather: "IoT weather sensor analysis evaluating temperature, rainfall, and humidity correlation with crop arrivals.",
    transport: "Logistics tracking transit hours, warehouse destination delays, and supply chain bottleneck analysis.",
    risk: "Automated risk ranking, IQR anomaly detection, 14-day Holt's forecasting, and K-Means clustering.",
    assistant: "Ask natural-language questions to query real Mandi arrivals, MSP prices, transport delays, and weather.",
    settings: "System architecture, SQLite database statistics, ETL pipeline verification, and model parameters.",
  };

  return (
    <header className="sticky top-0 z-30 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800/80 px-6 py-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Title & Description */}
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              {currentItem.label}
            </h1>
            <span className="hidden sm:inline-flex items-center gap-1 text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              Live Data
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl line-clamp-1">
            {pageDescriptions[activeTab] || ""}
          </p>
        </div>

        {/* Action Controls & Health */}
        <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
          {/* Live IST Clock */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-xs font-mono">
            <Clock className="w-3.5 h-3.5 text-emerald-400" />
            <span>{currentTime || "IST Live"}</span>
          </div>

          {/* Filter Toggle Button (hide on assistant/settings) */}
          {activeTab !== "assistant" && activeTab !== "settings" && (
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all ${
                showFilters
                  ? "bg-emerald-600 text-white shadow-glow-emerald"
                  : "bg-slate-900 text-slate-300 hover:bg-slate-800 border border-slate-700/80"
              }`}
            >
              <Filter className="w-3.5 h-3.5" />
              <span>Filters</span>
            </button>
          )}

          {/* Quick Refresh */}
          <button
            onClick={onRefresh}
            disabled={isLoading}
            title="Refresh analytical cache"
            className="p-2 rounded-xl bg-slate-900 text-slate-300 hover:bg-slate-800 hover:text-white border border-slate-700/80 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin text-emerald-400" : ""}`} />
          </button>

          {/* Quick AI Assistant Launcher (if not already on assistant page) */}
          {activeTab !== "assistant" && (
            <button
              onClick={onOpenAssistant}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:from-emerald-500 hover:to-teal-500 shadow-glow-emerald transition-all"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Ask AI</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
