import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Package,
  TrendingUp,
  Building2,
  Sprout,
  Search,
  ArrowUpDown,
  Download,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import { KpiCard } from "../components/KpiCard";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { ErrorMessage } from "../components/ErrorMessage";

const formatNumber = (num) =>
  num !== undefined && num !== null
    ? new Intl.NumberFormat("en-IN").format(Math.round(num))
    : "—";

export function ArrivalsPage({ data, isLoading, error, onRetry }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState("total_arrivals");
  const [sortAsc, setSortAsc] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  if (isLoading && !data) return <LoadingSkeleton cards={4} charts={2} />;
  if (error) return <ErrorMessage message={error} onRetry={onRetry} />;
  if (!data) return null;

  const { kpis = {}, top_mandis = [], crop_breakdown = [], mandi_table = [] } = data;

  // Filter and sort mandi table
  const filteredMandis = mandi_table.filter(
    (m) =>
      m.mandi_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.district.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.state.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedMandis = [...filteredMandis].sort((a, b) => {
    let valA = a[sortField];
    let valB = b[sortField];
    if (valA === null || valA === undefined) valA = -Infinity;
    if (valB === null || valB === undefined) valB = -Infinity;
    if (valA < valB) return sortAsc ? -1 : 1;
    if (valA > valB) return sortAsc ? 1 : -1;
    return 0;
  });

  const totalPages = Math.ceil(sortedMandis.length / pageSize) || 1;
  const paginatedMandis = sortedMandis.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const exportCsv = () => {
    const headers = ["Mandi ID,Mandi Name,District,State,Total Arrivals (Qtl),Active Days,Avg Daily (Qtl),Avg Price (₹),MSP Gap %,Risk Score,Risk Category\n"];
    const rows = mandi_table.map((m) =>
      `"${m.mandi_id}","${m.mandi_name}","${m.district}","${m.state}",${m.total_arrivals},${m.active_days},${m.avg_daily_arrivals},${m.avg_modal_price || ""},${m.avg_msp_gap_pct || ""},${m.risk_score || ""},"${m.risk_category}"\n`
    );
    const blob = new Blob([headers.concat(rows).join("")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mandi_arrivals_summary_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Total Arrivals"
          value={formatNumber(kpis.total_arrivals_quintal)}
          suffix="Qtl"
          subtext="Volume across state mandis"
          icon={Package}
          colorScheme="emerald"
        />
        <KpiCard
          title="Arrival Growth Rate"
          value={kpis.growth_rate_pct !== null ? `${kpis.growth_rate_pct}%` : "—"}
          subtext="First vs Second Half trend"
          icon={TrendingUp}
          trend={{
            value: `${kpis.growth_rate_pct > 0 ? "+" : ""}${kpis.growth_rate_pct || 0}%`,
            positive: kpis.growth_rate_pct >= 0,
          }}
          colorScheme={kpis.growth_rate_pct >= 0 ? "emerald" : "amber"}
        />
        <KpiCard
          title="Active Mandis"
          value={kpis.active_mandis || 0}
          subtext="Reporting active trade"
          icon={Building2}
          colorScheme="blue"
        />
        <KpiCard
          title="Commodity Crops"
          value={kpis.active_crops || 0}
          subtext="Distinct crops traded"
          icon={Sprout}
          colorScheme="purple"
        />
      </div>

      {/* Top 15 Mandis and Crop Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top 15 Mandis Chart */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Building2 className="w-4 h-4 text-emerald-400" />
                Top 15 Mandis by Arrival Volume
              </h3>
              <p className="text-xs text-slate-400">Total produce handled in Quintals</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={top_mandis} margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="mandi_name" stroke="#94a3b8" tick={{ fontSize: 10 }} width={120} />
                <Tooltip
                  formatter={(val) => [`${val.toLocaleString("en-IN")} Qtl`, "Arrivals"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Bar dataKey="total_arrivals" fill="#10b981" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Crop Breakdown Table */}
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
                  <Sprout className="w-4 h-4 text-teal-400" />
                  Crop-wise Arrival Share
                </h3>
                <p className="text-xs text-slate-400">Total volume and market penetration</p>
              </div>
            </div>

            <div className="overflow-x-auto max-h-72">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-2">Crop</th>
                    <th className="pb-2 text-right">Volume (Qtl)</th>
                    <th className="pb-2 text-right">Mandis</th>
                    <th className="pb-2 text-right">Share %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {crop_breakdown.map((c, i) => (
                    <tr key={i} className="hover:bg-slate-850/50 transition-colors">
                      <td className="py-2.5 font-medium text-white">{c.crop}</td>
                      <td className="py-2.5 text-right font-mono text-emerald-400">
                        {c.total_arrivals.toLocaleString("en-IN")}
                      </td>
                      <td className="py-2.5 text-right font-mono text-slate-300">{c.mandi_count}</td>
                      <td className="py-2.5 text-right font-mono text-slate-300">
                        <div className="flex items-center justify-end gap-2">
                          <div className="w-12 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                            <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${c.percentage}%` }} />
                          </div>
                          <span>{c.percentage}%</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Comprehensive Mandi Performance Table */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-sm font-bold text-white">Mandi Trading Master Directory</h3>
            <p className="text-xs text-slate-400">Detailed performance metrics across all active mandis</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search mandi, district, state..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setCurrentPage(1);
                }}
                className="pl-9 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none w-56 sm:w-64"
              />
            </div>
            <button
              onClick={exportCsv}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold bg-slate-950/50">
                <th className="py-3 px-3 cursor-pointer" onClick={() => handleSort("mandi_name")}>
                  <div className="flex items-center gap-1">
                    <span>Mandi</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-3 cursor-pointer" onClick={() => handleSort("district")}>
                  <div className="flex items-center gap-1">
                    <span>District / State</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-3 text-right cursor-pointer" onClick={() => handleSort("total_arrivals")}>
                  <div className="flex items-center justify-end gap-1">
                    <span>Total Arrivals (Qtl)</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-3 text-right cursor-pointer" onClick={() => handleSort("avg_daily_arrivals")}>
                  <div className="flex items-center justify-end gap-1">
                    <span>Avg Daily (Qtl)</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-3 text-right cursor-pointer" onClick={() => handleSort("avg_modal_price")}>
                  <div className="flex items-center justify-end gap-1">
                    <span>Avg Price (₹)</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-3 px-3 text-right cursor-pointer" onClick={() => handleSort("risk_score")}>
                  <div className="flex items-center justify-end gap-1">
                    <span>Risk Score</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {paginatedMandis.map((m) => (
                <tr key={m.mandi_id} className="hover:bg-slate-850/50 transition-colors">
                  <td className="py-3 px-3 font-semibold text-white">
                    <div>{m.mandi_name}</div>
                    <div className="text-[10px] text-slate-500 font-mono">{m.mandi_id}</div>
                  </td>
                  <td className="py-3 px-3 text-slate-300">
                    <div>{m.district}</div>
                    <div className="text-[10px] text-slate-500">{m.state}</div>
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-emerald-400 font-semibold">
                    {m.total_arrivals.toLocaleString("en-IN")}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-slate-300">
                    {m.avg_daily_arrivals.toLocaleString("en-IN")}
                  </td>
                  <td className="py-3 px-3 text-right font-mono text-amber-300">
                    {m.avg_modal_price ? `₹${m.avg_modal_price.toLocaleString("en-IN")}` : "—"}
                  </td>
                  <td className="py-3 px-3 text-right">
                    {m.risk_score !== null ? (
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                          m.risk_category === "Critical"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                            : m.risk_category === "High"
                            ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                            : m.risk_category === "Medium"
                            ? "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30"
                            : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        }`}
                      >
                        {m.risk_score} • {m.risk_category}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-xs text-slate-400">
          <div>
            Showing {(currentPage - 1) * pageSize + 1} to{" "}
            {Math.min(currentPage * pageSize, sortedMandis.length)} of {sortedMandis.length} mandis
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="font-mono text-slate-300">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
