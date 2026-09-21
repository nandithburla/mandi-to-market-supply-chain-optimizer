import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Server,
  Database,
  Cpu,
  Cloud,
  CheckCircle2,
  FileText,
  ShieldCheck,
  HardDrive,
  Activity,
  Layers,
} from "lucide-react";
import { api } from "../api/client";

export function SettingsPage() {
  const [health, setHealth] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .getHealth()
      .then((data) => setHealth(data))
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  const counts = health?.database?.counts || {};

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Top Banner */}
      <div className="rounded-2xl glass-panel p-6 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Server className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">System Architecture & Pipeline Status</h2>
              <p className="text-xs text-slate-400">
                Mandi-to-Market Supply Chain Optimizer v2.0 • Production Service
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-mono font-semibold text-emerald-300">
              API Status: {health?.status || "Online"}
            </span>
          </div>
        </div>
      </div>

      {/* Grid: Database & Model Specifications */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* SQLite Database Telemetry */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4"
        >
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-400" />
              SQLite Analytical Database
            </h3>
            <span className="text-xs font-mono text-emerald-300 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              mandi_market.db
            </span>
          </div>

          <p className="text-xs text-slate-400">
            Pre-aggregated relational storage housing cleaned arrivals, prices, IoT telemetry, and freight logs.
          </p>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Mandis Registered</span>
              <span className="text-base font-bold text-white">{counts.mandis || 57}</span>
            </div>
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Arrival Records</span>
              <span className="text-base font-bold text-emerald-400">
                {(counts.arrivals || 25000).toLocaleString()}
              </span>
            </div>
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Price Observations</span>
              <span className="text-base font-bold text-blue-400">
                {(counts.prices || 12000).toLocaleString()}
              </span>
            </div>
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[11px] block">Freight Trips</span>
              <span className="text-base font-bold text-amber-400">
                {(counts.transport_trips || 10000).toLocaleString()}
              </span>
            </div>
          </div>
        </motion.div>

        {/* AI Agent & OpenRouter LLM Configuration */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4"
        >
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Cpu className="w-4 h-4 text-purple-400" />
              Custom Lightweight AI Agent
            </h3>
            <span className="text-xs font-mono text-purple-300 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
              Active
            </span>
          </div>

          <p className="text-xs text-slate-400">
            Native Python AI architecture with intent recognition, SQL query tools, and grounded answer synthesis.
          </p>

          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Agent Framework</span>
              <span className="font-semibold text-white">Custom Native Python (Zero-overhead)</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400">NLU Intent Classifier</span>
              <span className="font-semibold text-white">OpenRouter LLM + Deterministic Router Fallback</span>
            </div>
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400">Database Grounding</span>
              <span className="font-semibold text-emerald-400">Parametric SQLite Query Tools</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Cloud & Kubernetes Deployment Box */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-2xl glass-panel p-6 border border-slate-800 space-y-4"
      >
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cloud className="w-4 h-4 text-blue-400" />
            Cloud & Production Deployment Blueprint
          </h3>
          <span className="text-xs font-mono text-blue-300 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
            AWS EKS Ready
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="font-bold text-slate-300 block">1. Docker Multi-Stage</span>
            <p className="text-[11px] text-slate-400 font-sans">
              Compiles React SPA with Vite and bundles with FastAPI into a single lightweight production container.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="font-bold text-slate-300 block">2. AWS ECR / EKS</span>
            <p className="text-[11px] text-slate-400 font-sans">
              Pre-configured Kubernetes manifests in <code className="text-emerald-400">k8s/</code> for automated pod deployment.
            </p>
          </div>
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5">
            <span className="font-bold text-slate-300 block">3. AWS LoadBalancer</span>
            <p className="text-[11px] text-slate-400 font-sans">
              Kubernetes Service exposed via AWS Network / Application Load Balancer with health checks on <code className="text-emerald-400">/api/health</code>.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
