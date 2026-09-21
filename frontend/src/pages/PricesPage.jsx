import React from "react";
import { motion } from "framer-motion";
import {
  Coins,
  Scale,
  TrendingDown,
  TrendingUp,
  AlertOctagon,
  Building2,
  Sprout,
  ShieldCheck,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from "recharts";
import { KpiCard } from "../components/KpiCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { ErrorMessage } from "../components/ErrorMessage";

const formatNumber = (num) =>
  num !== undefined && num !== null
    ? new Intl.NumberFormat("en-IN").format(Math.round(num))
    : "—";

export function PricesPage({ data, isLoading, error, onRetry }) {
  if (isLoading && !data) return <LoadingSkeleton cards={4} charts={3} />;
  if (error) return <ErrorMessage message={error} onRetry={onRetry} />;
  if (!data) return null;

  const { kpis = {}, timeline = [], msp_gap_by_crop = [], mandis_below_msp = [] } = data;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/95 border border-slate-700/80 p-3 rounded-xl shadow-glass text-xs space-y-1">
          <p className="font-semibold text-slate-200">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="font-mono">
              {entry.name}: {typeof entry.value === "number" ? entry.value.toLocaleString("en-IN") : entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          title="Avg Modal Price"
          value={kpis.avg_modal_price ? `₹${formatNumber(kpis.avg_modal_price)}` : "—"}
          suffix="/Qtl"
          subtext="Wholesale market average"
          icon={Coins}
          colorScheme="blue"
          helpText="Average modal price across filtered wholesale records."
        />
        <KpiCard
          title="Avg MSP Floor"
          value={kpis.avg_msp ? `₹${formatNumber(kpis.avg_msp)}` : "—"}
          suffix="/Qtl"
          subtext="Government benchmark"
          icon={Scale}
          colorScheme="emerald"
          helpText="Average official Minimum Support Price for matched crop records."
        />
        <KpiCard
          title="Avg MSP Gap"
          value={kpis.avg_msp_gap !== null ? `₹${kpis.avg_msp_gap}` : "—"}
          subtext="Modal Price - MSP"
          icon={kpis.avg_msp_gap >= 0 ? TrendingUp : TrendingDown}
          trend={{
            value: `${kpis.avg_msp_gap >= 0 ? "+" : ""}₹${kpis.avg_msp_gap || 0}`,
            positive: kpis.avg_msp_gap >= 0,
          }}
          colorScheme={kpis.avg_msp_gap >= 0 ? "emerald" : "red"}
          helpText="Absolute price margin above or below MSP."
        />
        <KpiCard
          title="MSP Gap %"
          value={kpis.avg_msp_gap_pct !== null ? `${kpis.avg_msp_gap_pct}%` : "—"}
          subtext="Relative price delta"
          icon={Coins}
          colorScheme={kpis.avg_msp_gap_pct >= 0 ? "emerald" : "amber"}
          helpText="((Modal Price - MSP) / MSP) * 100."
        />
        <KpiCard
          title="% Below MSP"
          value={kpis.pct_below_msp !== null ? `${kpis.pct_below_msp}%` : "—"}
          subtext="Observations below floor"
          icon={AlertOctagon}
          colorScheme={kpis.pct_below_msp > 30 ? "red" : "emerald"}
          helpText="Percentage of observations where modal wholesale price fell below MSP."
        />
      </div>

      {/* Row 1: Modal Price vs MSP & MSP Gap by Crop */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Timeline Chart */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Coins className="w-4 h-4 text-blue-400" />
                Modal Price vs MSP Trend
              </h3>
              <p className="text-xs text-slate-400">Daily average modal price tracking alongside MSP floor</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeline} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${v}`} />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="modal_price"
                  name="Modal Price (₹)"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="msp"
                  name="MSP Floor (₹)"
                  stroke="#ef4444"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* MSP Gap % by Crop */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Scale className="w-4 h-4 text-emerald-400" />
                Average MSP Gap % by Crop
              </h3>
              <p className="text-xs text-slate-400">Crops below 0% represent active farmer price pressure</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={msp_gap_by_crop} margin={{ top: 10, right: 10, left: -10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="crop" stroke="#94a3b8" tick={{ fontSize: 10, angle: -30, textAnchor: "end" }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${v}%`} />
                <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
                <Tooltip
                  formatter={(val, name) => [`${val}%`, "MSP Gap %"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Bar dataKey="avg_gap_pct" name="MSP Gap %" radius={[4, 4, 0, 0]}>
                  {msp_gap_by_crop.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.avg_gap_pct >= 0 ? "#10b981" : "#ef4444"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Row 2: Top Mandis Below MSP & Detailed Breakdown Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Mandis Below MSP Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <AlertOctagon className="w-4 h-4 text-rose-400" />
                Top Mandis with Highest % Below MSP
              </h3>
              <p className="text-xs text-slate-400">Markets requiring immediate procurement intervention</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={mandis_below_msp}
                margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="mandi_name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                <Tooltip
                  formatter={(val) => [`${val}%`, "% Below MSP"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Bar dataKey="below_msp_pct" name="% Below MSP" fill="#f43f5e" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* MSP Crop Economics Table */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Sprout className="w-4 h-4 text-emerald-400" />
                  Crop Price vs MSP Reference Matrix
                </h3>
                <p className="text-xs text-slate-400">Summary across all monitored commodity prices</p>
              </div>
            </div>

            <div className="overflow-x-auto max-h-72">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2">Crop</th>
                    <th className="pb-2 text-right">Modal (₹)</th>
                    <th className="pb-2 text-right">MSP (₹)</th>
                    <th className="pb-2 text-right">Gap (₹)</th>
                    <th className="pb-2 text-right">Below MSP %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {msp_gap_by_crop.map((c, i) => (
                    <tr key={i} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-2.5 font-semibold text-white">{c.crop}</td>
                      <td className="py-2.5 text-right font-mono text-slate-200">
                        ₹{c.avg_modal_price.toLocaleString("en-IN")}
                      </td>
                      <td className="py-2.5 text-right font-mono text-slate-400">
                        ₹{c.avg_msp.toLocaleString("en-IN")}
                      </td>
                      <td
                        className={`py-2.5 text-right font-mono font-bold ${
                          c.avg_gap >= 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {c.avg_gap >= 0 ? "+" : ""}₹{c.avg_gap.toLocaleString("en-IN")}
                      </td>
                      <td className="py-2.5 text-right font-mono">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            c.below_msp_pct > 35
                              ? "bg-rose-500/20 text-rose-300"
                              : "bg-emerald-500/20 text-emerald-300"
                          }`}
                        >
                          {c.below_msp_pct}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Policy Insights Alert */}
      <div className="rounded-2xl bg-gradient-to-r from-amber-950/40 via-slate-900/80 to-slate-900/80 border border-amber-500/20 p-5 flex items-start gap-4 shadow-glass">
        <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 flex-shrink-0">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-bold text-sm text-white">Government MSP Protection Alert</h4>
          <p className="text-slate-300 leading-relaxed">
            Crops showing a persistently negative MSP Gap % signify that private buyers are acquiring produce below mandated support rates. Targeted state agency procurement centers should be prioritized for mandis flagged above 50% below-MSP observations.
          </p>
        </div>
      </div>
    </div>
  );
}
