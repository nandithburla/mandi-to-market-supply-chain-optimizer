import React from "react";
import { motion } from "framer-motion";
import {
  Truck,
  Clock,
  Navigation,
  Warehouse,
  AlertTriangle,
  MapPin,
  TrendingDown,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
} from "recharts";
import { KpiCard } from "../components/KpiCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { ErrorMessage } from "../components/ErrorMessage";

const formatNumber = (num) =>
  num !== undefined && num !== null
    ? new Intl.NumberFormat("en-IN").format(Math.round(num))
    : "—";

export function TransportPage({ data, isLoading, error, onRetry }) {
  if (isLoading && !data) return <LoadingSkeleton cards={4} charts={2} />;
  if (error) return <ErrorMessage message={error} onRetry={onRetry} />;
  if (!data) return null;

  const { kpis = {}, warehouse_delays = [], routes = [] } = data;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Total Freight Trips"
          value={formatNumber(kpis.total_trips)}
          subtext="Recorded vehicle dispatches"
          icon={Truck}
          colorScheme="blue"
          helpText="Total number of valid Mandi-to-Warehouse logistics shipments."
        />
        <KpiCard
          title="Avg Transit Time"
          value={kpis.avg_transit_hours !== null ? `${kpis.avg_transit_hours}` : "—"}
          suffix="Hours"
          subtext="Mandi to warehouse door"
          icon={Clock}
          colorScheme="amber"
          helpText="Average transit duration per trip in hours."
        />
        <KpiCard
          title="Total Distance"
          value={formatNumber(kpis.total_distance_km)}
          suffix="km"
          subtext="Freight mileage"
          icon={Navigation}
          colorScheme="emerald"
          helpText="Cumulative distance traveled across all logistics routes in kilometers."
        />
        <KpiCard
          title="Active Warehouses"
          value={kpis.active_warehouses || 0}
          subtext="Destination receiving hubs"
          icon={Warehouse}
          colorScheme="purple"
          helpText="Distinct central warehouse storage hubs receiving produce."
        />
      </div>

      {/* Row 1: Warehouse Delays & Route Efficiency */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Warehouse Delay Rankings Bar Chart */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-amber-400" />
                Average Transit Time by Destination Warehouse
              </h3>
              <p className="text-xs text-slate-400">Longer transit times reveal logistical bottlenecks</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={warehouse_delays}
                margin={{ top: 5, right: 20, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${v} hrs`} />
                <YAxis type="category" dataKey="warehouse" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                <Tooltip
                  formatter={(val) => [`${val} Hours`, "Avg Transit Time"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Bar dataKey="avg_transit_hours" fill="#f59e0b" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Warehouse Volume & Transit Matrix */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Warehouse className="w-4 h-4 text-purple-400" />
                  Warehouse Logistics Operations Summary
                </h3>
                <p className="text-xs text-slate-400">Shipment volume, average distance, and transit performance</p>
              </div>
            </div>

            <div className="overflow-x-auto max-h-72">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2">Warehouse</th>
                    <th className="pb-2 text-right">Total Trips</th>
                    <th className="pb-2 text-right">Avg Dist (km)</th>
                    <th className="pb-2 text-right">Avg Transit (hrs)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {warehouse_delays.map((w, i) => (
                    <tr key={i} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-2.5 font-semibold text-white">{w.warehouse}</td>
                      <td className="py-2.5 text-right font-mono text-slate-300">
                        {w.total_trips.toLocaleString("en-IN")}
                      </td>
                      <td className="py-2.5 text-right font-mono text-slate-400">
                        {w.avg_distance_km ? `${w.avg_distance_km} km` : "—"}
                      </td>
                      <td className="py-2.5 text-right font-mono font-bold text-amber-400">
                        {w.avg_transit_hours} hrs
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Row 2: Mandi to Warehouse Supply Chain Corridors Table */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4"
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Navigation className="w-4 h-4 text-emerald-400" />
              Mandi-to-Warehouse Logistics Corridors
            </h3>
            <p className="text-xs text-slate-400">Primary supply chain routes ranked by transit duration</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold bg-slate-950/50">
                <th className="py-3 px-3">Origin Mandi</th>
                <th className="py-3 px-3">Destination Warehouse</th>
                <th className="py-3 px-3 text-right">Total Trips</th>
                <th className="py-3 px-3 text-right">Avg Distance (km)</th>
                <th className="py-3 px-3 text-right">Avg Transit (Hours)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {routes.map((r, i) => (
                <tr key={i} className="hover:bg-slate-850/50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-white">
                    <div>{r.mandi_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{r.mandi_id}</div>
                  </td>
                  <td className="py-3 px-3 text-slate-300 font-medium">{r.warehouse}</td>
                  <td className="py-3 px-3 text-right font-mono text-slate-300">{r.total_trips}</td>
                  <td className="py-3 px-3 text-right font-mono text-slate-400">
                    {r.avg_distance_km ? `${r.avg_distance_km} km` : "—"}
                  </td>
                  <td className="py-3 px-3 text-right font-mono font-bold text-amber-400">
                    {r.avg_transit_hours} hrs
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
