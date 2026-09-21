import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  ShieldAlert,
  AlertTriangle,
  TrendingUp,
  BrainCircuit,
  Sliders,
  Sparkles,
  Layers,
  ChevronDown,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  ZAxis,
  Legend,
  Cell,
} from "recharts";
import { KpiCard } from "../components/KpiCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { ErrorMessage } from "../components/ErrorMessage";

export function RiskPage({ data, isLoading, error, onCropChange, onRetry }) {
  const [showWeights, setShowWeights] = useState(false);

  if (isLoading && !data) return <LoadingSkeleton cards={4} charts={3} />;
  if (error) return <ErrorMessage message={error} onRetry={onRetry} />;
  if (!data) return null;

  const {
    risk_weights = {},
    risk_rankings = [],
    category_counts = {},
    selected_crop,
    available_crops = [],
    arrival_anomalies = [],
    price_anomalies = [],
    arrival_forecast = [],
    price_forecast = [],
    clusters = [],
  } = data;

  const top15Risk = risk_rankings.slice(0, 15);

  const categoryBarData = [
    { category: "Low", count: category_counts.Low || 0, color: "#10b981" },
    { category: "Medium", count: category_counts.Medium || 0, color: "#eab308" },
    { category: "High", count: category_counts.High || 0, color: "#f97316" },
    { category: "Critical", count: category_counts.Critical || 0, color: "#ef4444" },
  ];

  const clusterColorMap = ["#10b981", "#3b82f6", "#f59e0b", "#ec4899"];

  return (
    <div className="space-y-6">
      {/* Top Section: Risk Score Summary & Formula Weights */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Critical Risk Mandis"
          value={category_counts.Critical || 0}
          subtext="Score 81 - 100"
          icon={AlertTriangle}
          colorScheme="red"
          helpText="Mandis under severe compounded stress across prices, supply volatility, and weather."
        />
        <KpiCard
          title="High Risk Mandis"
          value={category_counts.High || 0}
          subtext="Score 61 - 80"
          icon={ShieldAlert}
          colorScheme="amber"
          helpText="Mandis with elevated price pressure or arrival volatility."
        />
        <KpiCard
          title="Medium Risk Mandis"
          value={category_counts.Medium || 0}
          subtext="Score 31 - 60"
          icon={TrendingUp}
          colorScheme="blue"
          helpText="Mandis with moderate fluctuations."
        />
        <KpiCard
          title="Low Risk Mandis"
          value={category_counts.Low || 0}
          subtext="Score 0 - 30"
          icon={Sparkles}
          colorScheme="emerald"
          helpText="Stable trading mandis adhering to MSP with predictable volumes."
        />
      </div>

      {/* Row 1: Top 15 Risk Mandis & Category Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top 15 Mandis by Risk Score */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                Mandi Risk Score Rankings (Top 15)
              </h3>
              <p className="text-xs text-slate-400">
                0-100 composite index calculated from live database features
              </p>
            </div>
            <button
              onClick={() => setShowWeights(!showWeights)}
              className="flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:text-emerald-300 transition-colors"
            >
              <Sliders className="w-3.5 h-3.5 text-emerald-400" />
              <span>Weights</span>
            </button>
          </div>

          {showWeights && (
            <div className="mb-4 p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-1">
              <span className="font-bold text-emerald-400">Score Formula Components:</span>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1 font-mono text-[11px]">
                <div>MSP Pressure: 35%</div>
                <div>Price Volatility: 25%</div>
                <div>Arrival Anomaly: 20%</div>
                <div>Weather Anomaly: 20%</div>
              </div>
            </div>
          )}

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={top15Risk} margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis type="category" dataKey="mandi_name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                <Tooltip
                  formatter={(val, name, item) => [
                    `${val}/100 (${item.payload.risk_category})`,
                    "Risk Score",
                  ]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Bar dataKey="risk_score" radius={[0, 6, 6, 0]}>
                  {top15Risk.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        entry.risk_category === "Critical"
                          ? "#ef4444"
                          : entry.risk_category === "High"
                          ? "#f97316"
                          : entry.risk_category === "Medium"
                          ? "#eab308"
                          : "#10b981"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Risk Category Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800 flex flex-col justify-between"
        >
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
              <Layers className="w-4 h-4 text-emerald-400" />
              Mandi Count by Risk Band
            </h3>
            <p className="text-xs text-slate-400 mb-4">Statewide mandi classification</p>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="category" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(val) => [`${val} Mandis`, "Count"]}
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {categoryBarData.map((entry, index) => (
                      <Cell key={`cat-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Low (0-30)</span>
              <span className="font-bold text-emerald-400">{category_counts.Low || 0} Mandis</span>
            </div>
            <div className="flex justify-between">
              <span>Medium (31-60)</span>
              <span className="font-bold text-yellow-400">{category_counts.Medium || 0} Mandis</span>
            </div>
            <div className="flex justify-between">
              <span>High (61-80)</span>
              <span className="font-bold text-amber-400">{category_counts.High || 0} Mandis</span>
            </div>
            <div className="flex justify-between">
              <span>Critical (81-100)</span>
              <span className="font-bold text-rose-400">{category_counts.Critical || 0} Mandis</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Row 2: Crop Selector for Anomaly & Forecasting */}
      <div className="flex items-center justify-between bg-slate-900/90 rounded-2xl p-4 border border-slate-800">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-emerald-400" />
          <div>
            <h4 className="text-sm font-bold text-white">Crop-Specific Predictive & Anomaly Models</h4>
            <p className="text-xs text-slate-400">Select commodity to evaluate anomalies and 14-day forecasts</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400">Crop:</label>
          <select
            value={selected_crop || ""}
            onChange={(e) => onCropChange && onCropChange(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-700 text-xs font-semibold text-emerald-300 focus:border-emerald-500 focus:outline-none"
          >
            {available_crops.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Row 3: Anomaly Timeseries (Arrivals & Prices) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Arrival Anomalies */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-emerald-400" />
                Arrival Volume Anomalies (IQR Method) — {selected_crop}
              </h3>
              <p className="text-xs text-slate-400">Flagging unexpected volume spikes or crashes</p>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={arrival_anomalies} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(val, name, item) => [
                    `${val.toLocaleString("en-IN")} Qtl ${item.payload.is_anomaly ? "⚠️ [ANOMALY]" : ""}`,
                    "Arrivals",
                  ]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Line
                  type="monotone"
                  dataKey="quantity"
                  name="Arrival Quantity"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={(props) => {
                    const { cx, cy, payload } = props;
                    if (payload.is_anomaly) {
                      return (
                        <circle
                          key={`dot-${payload.date}`}
                          cx={cx}
                          cy={cy}
                          r={6}
                          fill="#ef4444"
                          stroke="#ffffff"
                          strokeWidth={2}
                        />
                      );
                    }
                    return null;
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Price Anomalies */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Price Anomalies (IQR Method) — {selected_crop}
              </h3>
              <p className="text-xs text-slate-400">Flagging abnormal price surges or crashes</p>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={price_anomalies} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${v}`} />
                <Tooltip
                  formatter={(val, name, item) => [
                    `₹${val.toLocaleString("en-IN")} ${item.payload.is_anomaly ? "⚠️ [PRICE ANOMALY]" : ""}`,
                    "Modal Price",
                  ]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Line
                  type="monotone"
                  dataKey="modal_price"
                  name="Modal Price"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={(props) => {
                    const { cx, cy, payload } = props;
                    if (payload.is_anomaly) {
                      return (
                        <circle
                          key={`dot-p-${payload.date}`}
                          cx={cx}
                          cy={cy}
                          r={6}
                          fill="#ef4444"
                          stroke="#ffffff"
                          strokeWidth={2}
                        />
                      );
                    }
                    return null;
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Row 4: 14-Day Holt's Exponential Forecasting & Mandi Clustering */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 14-Day Arrivals Forecast */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-emerald-400" />
                14-Day Arrival Forecast (Holt's Exp Smoothing) — {selected_crop}
              </h3>
              <p className="text-xs text-slate-400">Historical trend combined with forward projection</p>
            </div>
            <span className="text-xs font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
              14 Days Ahead
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={arrival_forecast} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(val, name, item) => [
                    `${val.toLocaleString("en-IN")} Qtl ${item.payload.is_forecast ? "(Forecast)" : "(Historical)"}`,
                    "Arrivals",
                  ]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Mandi K-Means Clustering */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                Mandi Clustering (K-Means on Volume & Price)
              </h3>
              <p className="text-xs text-slate-400">Mandis in the same cluster share similar supply characteristics</p>
            </div>
            <span className="text-xs font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
              4 Clusters
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  type="number"
                  dataKey="total_arrivals"
                  name="Arrivals"
                  stroke="#64748b"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                  label={{ value: "Total Arrivals (Qtl)", position: "insideBottom", offset: -5, fill: "#94a3b8", fontSize: 10 }}
                />
                <YAxis
                  type="number"
                  dataKey="avg_modal_price"
                  name="Avg Price"
                  stroke="#64748b"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(v) => `₹${v}`}
                  label={{ value: "Avg Modal Price (₹)", angle: -90, position: "insideLeft", fill: "#94a3b8", fontSize: 10 }}
                />
                <Tooltip
                  formatter={(val, name, item) => [
                    `${item.payload.mandi_name}: ₹${item.payload.avg_modal_price} | ${item.payload.total_arrivals.toLocaleString("en-IN")} Qtl (Cluster ${item.payload.cluster})`,
                    "Mandi",
                  ]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                {Array.from(new Set(clusters.map((c) => c.cluster))).map((clusterId) => (
                  <Scatter
                    key={`cluster-${clusterId}`}
                    name={`Cluster ${clusterId}`}
                    data={clusters.filter((c) => c.cluster === clusterId)}
                    fill={clusterColorMap[clusterId % clusterColorMap.length]}
                  />
                ))}
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
