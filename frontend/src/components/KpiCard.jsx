import React from "react";
import { motion } from "framer-motion";
import { HelpCircle, TrendingUp, TrendingDown, Minus } from "lucide-react";

export function KpiCard({
  title,
  value,
  prefix = "",
  suffix = "",
  subtext,
  icon: Icon,
  trend, // { value: "+12%", positive: true/false }
  helpText,
  colorScheme = "emerald", // "emerald" | "amber" | "blue" | "red" | "purple"
}) {
  const colorMaps = {
    emerald: {
      bg: "from-emerald-500/10 to-transparent",
      border: "hover:border-emerald-500/40",
      iconBg: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
      glow: "group-hover:shadow-glow-emerald",
      valueColor: "text-white",
    },
    amber: {
      bg: "from-amber-500/10 to-transparent",
      border: "hover:border-amber-500/40",
      iconBg: "bg-amber-500/20 text-amber-400 border-amber-500/30",
      glow: "group-hover:shadow-[0_0_20px_-5px_rgba(245,158,11,0.3)]",
      valueColor: "text-white",
    },
    blue: {
      bg: "from-blue-500/10 to-transparent",
      border: "hover:border-blue-500/40",
      iconBg: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      glow: "group-hover:shadow-[0_0_20px_-5px_rgba(59,130,246,0.3)]",
      valueColor: "text-white",
    },
    red: {
      bg: "from-rose-500/10 to-transparent",
      border: "hover:border-rose-500/40",
      iconBg: "bg-rose-500/20 text-rose-400 border-rose-500/30",
      glow: "group-hover:shadow-[0_0_20px_-5px_rgba(244,63,94,0.3)]",
      valueColor: "text-white",
    },
    purple: {
      bg: "from-purple-500/10 to-transparent",
      border: "hover:border-purple-500/40",
      iconBg: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      glow: "group-hover:shadow-[0_0_20px_-5px_rgba(168,85,247,0.3)]",
      valueColor: "text-white",
    },
  };

  const scheme = colorMaps[colorScheme] || colorMaps.emerald;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`relative overflow-hidden rounded-2xl glass-panel p-5 transition-all duration-300 border border-slate-800/80 group ${scheme.border} ${scheme.glow}`}
    >
      {/* Subtle Gradient Backdrop */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${scheme.bg} opacity-50 pointer-events-none`}
      />

      <div className="relative z-10 flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              {title}
            </span>
            {helpText && (
              <span className="cursor-help text-slate-500 hover:text-slate-300 transition-colors" title={helpText}>
                <HelpCircle className="w-3.5 h-3.5" />
              </span>
            )}
          </div>
          <div className="flex items-baseline gap-1 pt-1">
            {prefix && <span className="text-lg font-bold text-slate-300">{prefix}</span>}
            <span className={`text-2xl sm:text-3xl font-extrabold tracking-tight ${scheme.valueColor}`}>
              {value !== undefined && value !== null ? value : "—"}
            </span>
            {suffix && <span className="text-sm font-semibold text-slate-400">{suffix}</span>}
          </div>
        </div>

        {Icon && (
          <div
            className={`w-11 h-11 rounded-xl flex items-center justify-center border transition-transform duration-300 group-hover:scale-110 flex-shrink-0 ${scheme.iconBg}`}
          >
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      {(subtext || trend) && (
        <div className="relative z-10 mt-3 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
          {subtext && <span className="truncate">{subtext}</span>}
          {trend && (
            <span
              className={`inline-flex items-center gap-0.5 font-semibold ${
                trend.positive
                  ? "text-emerald-400"
                  : trend.positive === false
                  ? "text-rose-400"
                  : "text-slate-400"
              }`}
            >
              {trend.positive === true && <TrendingUp className="w-3 h-3" />}
              {trend.positive === false && <TrendingDown className="w-3 h-3" />}
              {trend.positive === null && <Minus className="w-3 h-3" />}
              {trend.value}
            </span>
          )}
        </div>
      )}
    </motion.div>
  );
}
