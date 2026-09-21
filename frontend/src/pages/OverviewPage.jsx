import React from "react";
import { motion } from "framer-motion";
import {
  Package,
  IndianRupee,
  Coins,
  AlertOctagon,
  ShieldAlert,
  Building2,
  Sprout,
  TrendingUp,
} from "lucide-react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { KpiCard } from "../components/KpiCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { ErrorMessage } from "../components/ErrorMessage";

const formatNumber = (num) =>
  num !== undefined && num !== null
    ? new Intl.NumberFormat("en-IN").format(Math.round(num))
    : "—";

const formatCurrency = (num) =>
  num !== undefined && num !== null
    ? "₹" + new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(num)
    : "—";

export function OverviewPage({ data, isLoading, error, onRetry }) {
  if (isLoading && !data) return <LoadingSkeleton cards={5} charts={4} />;
  if (error) return <ErrorMessage message={error} onRetry={onRetry} />;
  if (!data) return null;

  const { kpis = {}, daily_arrivals_trend = [], price_vs_msp_trend = [], top_mandis = [], crop_distribution = [] } =
    data;

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
      {/* 5 Key Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          title="Total Arrivals"
          value={formatNumber(kpis.total_arrivals_quintal)}
          suffix="Qtl"
          subtext={`Across ${kpis.active_mandis || 0} Mandis`}
          icon={Package}
          colorScheme="emerald"
          helpText="Sum of arrival quantities (Quintals) across selected Mandis and crops."
        />
        <KpiCard
          title="Est. Market Value"
          value={formatCurrency(kpis.total_market_value)}
          subtext="Quantity x Modal Price"
          icon={IndianRupee}
          colorScheme="blue"
          helpText="Total transaction turnover calculated on matched daily price and arrival records."
        />
        <KpiCard
          title="Avg Modal Price"
          value={kpis.avg_modal_price ? `₹${formatNumber(kpis.avg_modal_price)}` : "—"}
          suffix="/Qtl"
          subtext="Wholesale benchmark"
          icon={Coins}
          colorScheme="amber"
          helpText="Weighted average wholesale modal price per Quintal."
        />
        <KpiCard
          title="% Below MSP"
          value={kpis.pct_below_msp !== null ? `${kpis.pct_below_msp}%` : "—"}
          subtext="Distress-sale share"
          icon={AlertOctagon}
          colorScheme={kpis.pct_below_msp > 30 ? "red" : "amber"}
          helpText="Percentage of price observations trading below official Minimum Support Price."
        />
        <KpiCard
          title="Avg Risk Score"
          value={kpis.avg_risk_score !== null ? `${kpis.avg_risk_score}` : "—"}
          suffix="/100"
          subtext="Statewide supply index"
          icon={ShieldAlert}
          colorScheme={kpis.avg_risk_score > 60 ? "red" : "emerald"}
          helpText="Composite 0-100 score combining MSP pressure (35%), price volatility (25%), arrival anomalies (20%), and weather (20%)."
        />
      </div>

      {/* Grid: Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Arrivals Trend */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                Daily Arrivals Trend (Quintals)
              </h3>
              <p className="text-xs text-slate-400">Total volume arriving across state grain markets</p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
              Daily Aggregate
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={daily_arrivals_trend} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorArrivals" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `${v / 1000}k`} />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="arrivals"
                  name="Arrivals (Qtl)"
                  stroke="#10b981"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorArrivals)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Modal Price vs MSP Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Coins className="w-4 h-4 text-amber-400" />
                Modal Price vs MSP (₹ / Quintal)
              </h3>
              <p className="text-xs text-slate-400">Comparing market prices against the government MSP floor</p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="flex items-center gap-1.5 text-blue-400">
                <span className="w-2.5 h-0.5 bg-blue-400"></span> Modal Price
              </span>
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-2.5 h-0.5 border-t border-dashed border-rose-400"></span> MSP Floor
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={price_vs_msp_trend} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${v}`} />
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
                  name="MSP Benchmark (₹)"
                  stroke="#ef4444"
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Grid: Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 10 Mandis Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Building2 className="w-4 h-4 text-emerald-400" />
                Top 10 Mandis by Arrival Volume
              </h3>
              <p className="text-xs text-slate-400">Highest volume trading hubs across all crops</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={top_mandis}
                margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="mandi_name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="arrivals" name="Arrivals (Qtl)" fill="#10b981" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Crop Volume Breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sprout className="w-4 h-4 text-teal-400" />
                Crop Volume Share & Distribution
              </h3>
              <p className="text-xs text-slate-400">Arrival quantity by agricultural commodity</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={crop_distribution} margin={{ top: 10, right: 10, left: -10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="crop" stroke="#94a3b8" tick={{ fontSize: 10, angle: -30, textAnchor: "end" }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="arrivals" name="Arrivals (Qtl)" fill="#14b8a6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Strategic Board Insights Box */}
      <div className="rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-slate-900/80 border border-emerald-500/20 p-5 flex items-start gap-4 shadow-glass">
        <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 flex-shrink-0">
          🌾
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-bold text-sm text-white">Board Intelligence Note</h4>
          <p className="text-slate-300 leading-relaxed">
            Arrivals and wholesale prices are monitored synchronously so the State Agriculture Board can instantly detect whether periods of peak commodity influx coincide with market prices sliding toward or below MSP.
          </p>
        </div>
      </div>
    </div>
  );
}
