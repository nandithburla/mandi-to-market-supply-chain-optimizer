import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  CloudSun,
  Thermometer,
  CloudRain,
  Droplets,
  Activity,
  TrendingUp,
  Info,
} from "lucide-react";
import {
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ComposedChart,
  Bar,
} from "recharts";
import { KpiCard } from "../components/KpiCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { ErrorMessage } from "../components/ErrorMessage";

const formatNumber = (num) =>
  num !== undefined && num !== null
    ? new Intl.NumberFormat("en-IN").format(Math.round(num))
    : "—";

export function WeatherPage({ data, isLoading, error, onRetry }) {
  const [selectedMetric, setSelectedMetric] = useState("rainfall"); // "rainfall" | "temperature" | "humidity"

  if (isLoading && !data) return <LoadingSkeleton cards={4} charts={2} />;
  if (error) return <ErrorMessage message={error} onRetry={onRetry} />;
  if (!data) return null;

  const { kpis = {}, correlations = {}, daily_trend = [] } = data;

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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Avg Temperature"
          value={kpis.avg_temperature_c !== null ? `${kpis.avg_temperature_c}` : "—"}
          suffix="°C"
          subtext="Statewide sensor aggregate"
          icon={Thermometer}
          colorScheme="amber"
          helpText="Daily mean temperature recorded across IoT weather sensors."
        />
        <KpiCard
          title="Total Rainfall"
          value={formatNumber(kpis.total_rainfall_mm)}
          suffix="mm"
          subtext="Cumulative precipitation"
          icon={CloudRain}
          colorScheme="blue"
          helpText="Sum of all rainfall measurements recorded over the analysis period."
        />
        <KpiCard
          title="Avg Relative Humidity"
          value={kpis.avg_humidity_pct !== null ? `${kpis.avg_humidity_pct}%` : "—"}
          subtext="Moisture saturation"
          icon={Droplets}
          colorScheme="emerald"
          helpText="Average atmospheric relative humidity percentage."
        />
        <KpiCard
          title="Sensor Records"
          value={formatNumber(kpis.sensor_reading_count)}
          subtext="IoT telemetry events"
          icon={Activity}
          colorScheme="purple"
          helpText="Total number of cleaned IoT weather observation points."
        />
      </div>

      {/* Pearson Correlation Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-2xl glass-panel p-4 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium">Rainfall ↔ Arrivals Corr</span>
            <div className="text-xl font-bold font-mono text-white mt-1">
              {correlations.rainfall_vs_arrivals !== null ? correlations.rainfall_vs_arrivals : "—"}
            </div>
          </div>
          <div
            className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
              Math.abs(correlations.rainfall_vs_arrivals || 0) > 0.3
                ? "bg-emerald-500/20 text-emerald-300"
                : "bg-slate-800 text-slate-400"
            }`}
          >
            {Math.abs(correlations.rainfall_vs_arrivals || 0) > 0.3 ? "Moderate Impact" : "Low Direct Impact"}
          </div>
        </div>

        <div className="rounded-2xl glass-panel p-4 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium">Temperature ↔ Arrivals Corr</span>
            <div className="text-xl font-bold font-mono text-white mt-1">
              {correlations.temperature_vs_arrivals !== null ? correlations.temperature_vs_arrivals : "—"}
            </div>
          </div>
          <div
            className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
              Math.abs(correlations.temperature_vs_arrivals || 0) > 0.3
                ? "bg-emerald-500/20 text-emerald-300"
                : "bg-slate-800 text-slate-400"
            }`}
          >
            {Math.abs(correlations.temperature_vs_arrivals || 0) > 0.3 ? "Moderate Impact" : "Low Direct Impact"}
          </div>
        </div>

        <div className="rounded-2xl glass-panel p-4 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-400 font-medium">Humidity ↔ Arrivals Corr</span>
            <div className="text-xl font-bold font-mono text-white mt-1">
              {correlations.humidity_vs_arrivals !== null ? correlations.humidity_vs_arrivals : "—"}
            </div>
          </div>
          <div
            className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
              Math.abs(correlations.humidity_vs_arrivals || 0) > 0.3
                ? "bg-emerald-500/20 text-emerald-300"
                : "bg-slate-800 text-slate-400"
            }`}
          >
            {Math.abs(correlations.humidity_vs_arrivals || 0) > 0.3 ? "Moderate Impact" : "Low Direct Impact"}
          </div>
        </div>
      </div>

      {/* Dual Axis Composed Chart: Weather Metric & Arrivals */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <CloudSun className="w-4 h-4 text-emerald-400" />
              Daily Weather & Market Supply Dynamics
            </h3>
            <p className="text-xs text-slate-400">Comparing meteorological patterns against daily arrivals volume</p>
          </div>

          {/* Metric Selector Buttons */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setSelectedMetric("rainfall")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                selectedMetric === "rainfall"
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Rainfall (mm)
            </button>
            <button
              onClick={() => setSelectedMetric("temperature")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                selectedMetric === "temperature"
                  ? "bg-amber-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Temperature (°C)
            </button>
            <button
              onClick={() => setSelectedMetric("humidity")}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                selectedMetric === "humidity"
                  ? "bg-emerald-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Humidity (%)
            </button>
          </div>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={daily_trend} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 10 }} />
              <YAxis
                yAxisId="left"
                stroke="#10b981"
                tick={{ fontSize: 10 }}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                name="Arrivals (Qtl)"
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke={
                  selectedMetric === "rainfall"
                    ? "#3b82f6"
                    : selectedMetric === "temperature"
                    ? "#f59e0b"
                    : "#14b8a6"
                }
                tick={{ fontSize: 10 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
              <Bar
                yAxisId="left"
                dataKey="arrivals"
                name="Daily Arrivals (Qtl)"
                fill="#10b981"
                opacity={0.6}
                radius={[4, 4, 0, 0]}
              />
              {selectedMetric === "rainfall" && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="total_rainfall_mm"
                  name="Rainfall (mm)"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                />
              )}
              {selectedMetric === "temperature" && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="avg_temperature_c"
                  name="Temperature (°C)"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={false}
                />
              )}
              {selectedMetric === "humidity" && (
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="avg_humidity_pct"
                  name="Humidity (%)"
                  stroke="#14b8a6"
                  strokeWidth={2}
                  dot={false}
                />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Explanatory Dataset Limitations & Methodology Alert */}
      <div className="rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900/80 to-slate-900/80 border border-blue-500/20 p-5 flex items-start gap-4 shadow-glass">
        <div className="w-10 h-10 rounded-xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 flex-shrink-0">
          <Info className="w-5 h-5" />
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-bold text-sm text-white">Meteorological Methodology Note</h4>
          <p className="text-slate-300 leading-relaxed">
            In this agricultural dataset, weather sensor telemetry is aggregated at the state daily level. Significant rainfall events often induce 24-48 hour logistical transit delays before arriving produce surges at grain markets.
          </p>
        </div>
      </div>
    </div>
  );
}
