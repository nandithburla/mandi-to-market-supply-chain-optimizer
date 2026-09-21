import React from "react";
import {
  LayoutDashboard,
  TrendingUp,
  Coins,
  CloudSun,
  Truck,
  ShieldAlert,
  Sparkles,
  Settings2,
  ChevronRight,
  Database,
  Layers,
} from "lucide-react";

export const NAV_ITEMS = [
  { id: "overview", label: "Executive Overview", icon: LayoutDashboard, badge: null },
  { id: "arrivals", label: "Arrivals & Mandis", icon: TrendingUp, badge: null },
  { id: "prices", label: "Prices & MSP Monitor", icon: Coins, badge: null },
  { id: "weather", label: "Weather Dynamics", icon: CloudSun, badge: null },
  { id: "transport", label: "Transport & Logistics", icon: Truck, badge: null },
  { id: "risk", label: "Risk & Forecasting", icon: ShieldAlert, badge: "AI ML" },
  { id: "assistant", label: "AI Agri Assistant", icon: Sparkles, badge: "Live" },
  { id: "settings", label: "System & Pipeline", icon: Settings2, badge: null },
];

export function Sidebar({ activeTab, setActiveTab, isCollapsed, setIsCollapsed }) {
  return (
    <aside
      className={`fixed top-0 left-0 h-screen z-40 bg-slate-950/90 backdrop-blur-xl border-r border-slate-800/80 transition-all duration-300 flex flex-col justify-between ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="flex items-center gap-3 px-5 py-6 border-b border-slate-800/60">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-700 to-emerald-500 flex items-center justify-center text-xl shadow-glow-emerald flex-shrink-0">
            🌾
          </div>
          {!isCollapsed && (
            <div className="overflow-hidden">
              <h1 className="font-bold text-base tracking-tight text-white flex items-center gap-1.5 font-sans">
                Mandi-to-Market
              </h1>
              <p className="text-[11px] font-medium text-emerald-400/90 uppercase tracking-wider">
                Supply Chain Optimizer
              </p>
            </div>
          )}
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1.5 mt-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3.5 px-3.5 py-3 rounded-xl text-sm font-medium transition-all duration-200 group relative ${
                  isActive
                    ? "bg-gradient-to-r from-emerald-600/20 to-emerald-500/10 text-emerald-300 border border-emerald-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent"
                } ${isCollapsed ? "justify-center" : ""}`}
              >
                <Icon
                  className={`w-5 h-5 flex-shrink-0 transition-transform duration-200 group-hover:scale-110 ${
                    isActive ? "text-emerald-400" : "text-slate-400 group-hover:text-emerald-400"
                  }`}
                />
                {!isCollapsed && (
                  <span className="flex-1 text-left truncate">{item.label}</span>
                )}
                {!isCollapsed && item.badge && (
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      item.badge === "Live"
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 animate-pulse"
                        : "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
                {isActive && (
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-emerald-500 rounded-l-full" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/60">
        {!isCollapsed ? (
          <div className="bg-slate-900/90 rounded-xl p-3 border border-slate-800/80">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>State Agri Board v2.0</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <Database className="w-3 h-3 text-emerald-400" />
              SQLite Analytical DB • 57 Mandis
            </p>
          </div>
        ) : (
          <div className="flex justify-center">
            <span className="w-3 h-3 rounded-full bg-emerald-400" title="Connected" />
          </div>
        )}
      </div>
    </aside>
  );
}
