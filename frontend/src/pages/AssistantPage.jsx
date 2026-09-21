import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Send,
  Bot,
  User,
  RotateCcw,
  BarChart3,
  Table as TableIcon,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Database,
  ArrowRight,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { api } from "../api/client";

const SUGGESTIONS = [
  "Which mandis have the highest wheat arrivals?",
  "Which mandis have wheat prices below MSP?",
  "Show transport delays",
  "What is the average rainfall and temperature?",
  "Show maize arrivals across mandis",
  "Which mandis have the lowest prices for mustard?",
];

export function AssistantPage() {
  const [messages, setMessages] = useState([
    {
      id: "initial-1",
      sender: "bot",
      text: "Namaste! I am your AI Mandi-to-Market Supply Chain Assistant. Ask me anything about mandi arrivals, wholesale crop prices, MSP comparisons, transport logistics, or IoT weather telemetry.",
      intent: "greeting",
      data: null,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [expandedTables, setExpandedTables] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (queryText) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || isLoading) return;

    const userMessageId = `user-${Date.now()}`;
    const botMessageId = `bot-${Date.now()}`;

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        id: userMessageId,
        sender: "user",
        text: textToSend,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.queryAgent(textToSend);

      setMessages((prev) => [
        ...prev,
        {
          id: botMessageId,
          sender: "bot",
          text: response.answer || "I received data for your query.",
          intent: response.intent,
          data: response.data,
          chart: response.chart,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: botMessageId,
          sender: "bot",
          text: `⚠️ Error executing query: ${err.message || "Failed to contact AI agent"}`,
          intent: "error",
          data: null,
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTable = (msgId) => {
    setExpandedTables((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const renderMessageChart = (intent, data) => {
    if (!data || !Array.isArray(data) || data.length === 0) return null;

    if (intent === "arrivals") {
      return (
        <div className="mt-4 p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-emerald-400" />
              Mandi Arrivals Visualization
            </span>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="mandi" stroke="#94a3b8" tick={{ fontSize: 10, angle: -30, textAnchor: "end" }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(v) => [`${v.toLocaleString("en-IN")} Qtl`, "Total Arrivals"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Bar dataKey="total_arrivals_quintal" name="Arrivals (Qtl)" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    if (intent === "prices") {
      return (
        <div className="mt-4 p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-blue-400" />
              Price vs MSP Comparison
            </span>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="mandi" stroke="#94a3b8" tick={{ fontSize: 10, angle: -30, textAnchor: "end" }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `₹${v}`} />
                <Tooltip
                  formatter={(v, name) => [`₹${v.toLocaleString("en-IN")}`, name === "average_price" ? "Modal Price" : "MSP"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "5px" }} />
                <Bar dataKey="average_price" name="Modal Price" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="average_msp" name="MSP Floor" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    if (intent === "transport") {
      return (
        <div className="mt-4 p-4 rounded-xl bg-slate-950/80 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <BarChart3 className="w-3.5 h-3.5 text-amber-400" />
              Average Transit Time by Destination Warehouse
            </span>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="warehouse" stroke="#94a3b8" tick={{ fontSize: 10, angle: -30, textAnchor: "end" }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} tickFormatter={(v) => `${v} hrs`} />
                <Tooltip
                  formatter={(v) => [`${v} Hours`, "Avg Transit Time"]}
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                />
                <Bar dataKey="average_transit_hours" name="Transit Time (Hours)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      );
    }

    return null;
  };

  const renderDataTable = (data) => {
    if (!data) return null;

    if (Array.isArray(data) && data.length > 0) {
      const keys = Object.keys(data[0]);
      return (
        <div className="mt-3 overflow-x-auto rounded-xl bg-slate-950 border border-slate-800 p-2 max-h-60">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                {keys.map((k) => (
                  <th key={k} className="py-2 px-2 capitalize">
                    {k.replace(/_/g, " ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {data.map((row, i) => (
                <tr key={i} className="hover:bg-slate-900/50">
                  {keys.map((k) => (
                    <td key={k} className="py-1.5 px-2 font-mono text-slate-200">
                      {typeof row[k] === "number" ? row[k].toLocaleString("en-IN") : String(row[k])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    if (typeof data === "object") {
      return (
        <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-2 rounded-xl bg-slate-950 border border-slate-800 p-3 text-xs">
          {Object.entries(data).map(([k, v]) => (
            <div key={k} className="space-y-0.5">
              <span className="text-slate-400 capitalize">{k.replace(/_/g, " ")}</span>
              <div className="font-mono font-bold text-white text-sm">{String(v)}</div>
            </div>
          ))}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] max-w-5xl mx-auto">
      {/* Top Suggestions Bar */}
      <div className="mb-4">
        <div className="text-xs text-slate-400 font-semibold mb-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
          <span>Recommended Queries</span>
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => handleSend(s)}
              disabled={isLoading}
              className="flex-shrink-0 text-xs px-3 py-1.5 rounded-full bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-emerald-300 border border-slate-800 hover:border-emerald-500/30 transition-all flex items-center gap-1 group disabled:opacity-50"
            >
              <span>{s}</span>
              <ArrowRight className="w-3 h-3 text-slate-500 group-hover:text-emerald-400 transition-transform group-hover:translate-x-0.5" />
            </button>
          ))}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex items-start gap-3 ${msg.sender === "user" ? "flex-row-reverse" : ""}`}
            >
              {/* Avatar */}
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  msg.sender === "user"
                    ? "bg-emerald-600 text-white"
                    : "bg-slate-800 text-emerald-400 border border-slate-700"
                }`}
              >
                {msg.sender === "user" ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-2xl rounded-2xl p-4.5 space-y-2 text-sm shadow-glass ${
                  msg.sender === "user"
                    ? "bg-gradient-to-r from-emerald-600 to-teal-700 text-white rounded-tr-none"
                    : "bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-none"
                }`}
              >
                <div className="flex items-center justify-between gap-4 text-[11px] text-slate-400">
                  <span className="font-semibold text-slate-300">
                    {msg.sender === "user" ? "You" : "Agricultural AI Agent"}
                  </span>
                  <div className="flex items-center gap-2">
                    {msg.intent && msg.intent !== "greeting" && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 uppercase font-mono text-[10px]">
                        {msg.intent}
                      </span>
                    )}
                    <span>{msg.timestamp}</span>
                  </div>
                </div>

                {/* Body Text */}
                <div className="whitespace-pre-line leading-relaxed text-[13px] font-normal">
                  {msg.text}
                </div>

                {/* Intent Visual Chart */}
                {msg.sender === "bot" && renderMessageChart(msg.intent, msg.data)}

                {/* Raw Database Records Table Accordion */}
                {msg.sender === "bot" && msg.data && (
                  <div className="pt-2 border-t border-slate-800/80">
                    <button
                      onClick={() => toggleTable(msg.id)}
                      className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-medium"
                    >
                      <Database className="w-3.5 h-3.5" />
                      <span>{expandedTables[msg.id] ? "Hide SQLite Result Data" : "View SQLite Result Data"}</span>
                      {expandedTables[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>
                    {expandedTables[msg.id] && renderDataTable(msg.data)}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-800 text-emerald-400 border border-slate-700 flex items-center justify-center animate-pulse">
              <Bot className="w-5 h-5" />
            </div>
            <div className="rounded-2xl rounded-tl-none bg-slate-900 border border-slate-800 p-4 space-y-2">
              <div className="flex items-center gap-2 text-xs text-emerald-400 font-mono">
                <Sparkles className="w-3.5 h-3.5 animate-spin" />
                <span>AI Agent is querying agricultural database...</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce" />
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.2s]" />
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <div className="mt-4 relative">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 bg-slate-900/90 rounded-2xl border border-slate-700/80 p-2 shadow-2xl focus-within:border-emerald-500 transition-colors"
        >
          <input
            type="text"
            placeholder="Ask questions about mandi arrivals, crop prices, MSP, weather, or transport..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            className="flex-1 bg-transparent px-4 py-2.5 text-sm text-white placeholder:text-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-all shadow-glow-emerald disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
