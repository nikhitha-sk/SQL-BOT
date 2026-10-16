"use client";

import { useState } from "react";
import { AlertTriangle, BarChart3, Code2, Coins, Gauge, RotateCw, ShieldAlert, Sparkles, Table2, ThumbsDown, ThumbsUp, Zap } from "lucide-react";
import ChartView from "./ChartView";
import DataTable from "./DataTable";
import SqlView from "./SqlView";
import { api, formatCost, formatMs } from "@/lib/api";

const CHART_NAMES = { number: "Number card", line: "Line chart", bar: "Bar chart", pie: "Pie chart", scatter: "Scatter plot", table: "Table" };

export default function AnswerCard({ answer }) {
  const hasChart = answer.chart.type !== "table";
  const [tab, setTab] = useState(hasChart ? "chart" : "table");
  const [rating, setRating] = useState(0);

  const rate = async (value) => {
    setRating(value);
    try {
      await api.feedback(answer.id, value);
    } catch {
      setRating(0);
    }
  };

  if (answer.status !== "ok") {
    const blocked = answer.status === "blocked";
    return (
      <div className={`card border-l-4 p-5 ${blocked ? "border-l-amber-400" : "border-l-red-400"}`}>
        <div className="flex items-start gap-3">
          {blocked ? <ShieldAlert className="mt-0.5 text-amber-500" size={20} /> : <AlertTriangle className="mt-0.5 text-red-500" size={20} />}
          <div className="min-w-0 flex-1">
            <p className="font-medium text-ink-900">{blocked ? "Request blocked" : "Something went wrong"}</p>
            <p className="mt-1 text-sm text-ink-700">{answer.error}</p>
            {answer.sql && <div className="mt-3"><SqlView sql={answer.sql} /></div>}
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    hasChart && { id: "chart", label: CHART_NAMES[answer.chart.type], icon: BarChart3 },
    { id: "table", label: `Table · ${answer.rows.length} rows`, icon: Table2 },
    { id: "sql", label: "SQL", icon: Code2 },
  ].filter(Boolean);

  return (
    <div className="card overflow-hidden">
      <div className="flex items-start gap-3 border-b border-slate-100 p-5">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
          <Sparkles size={16} />
        </span>
        <p className="pt-1 text-[15px] leading-relaxed text-ink-900">{answer.explanation}</p>
      </div>

      <div className="flex gap-1 border-b border-slate-100 px-4 pt-3">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`-mb-px flex items-center gap-1.5 border-b-2 px-3 pb-2.5 text-sm font-medium transition ${
              tab === t.id ? "border-brand-600 text-brand-700" : "border-transparent text-ink-500 hover:text-ink-900"
            }`}
          >
            <t.icon size={15} /> {t.label}
          </button>
        ))}
      </div>

      <div className="p-5">
        {tab === "chart" && <ChartView chart={answer.chart} columns={answer.columns} rows={answer.rows} />}
        {tab === "table" && <DataTable columns={answer.columns} rows={answer.rows} />}
        {tab === "sql" && <SqlView sql={answer.sql} />}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 bg-slate-50/60 px-5 py-3">
        <div className="flex flex-wrap items-center gap-2 text-xs text-ink-500">
          <span className="badge bg-white ring-1 ring-slate-200"><Gauge size={12} /> {formatMs(answer.time_ms)}</span>
          <span className="badge bg-white ring-1 ring-slate-200"><Coins size={12} /> {formatCost(answer.usage.cost_usd)} · {(answer.usage.input_tokens + answer.usage.output_tokens).toLocaleString()} tokens</span>
          {answer.attempts > 1 && <span className="badge bg-amber-50 text-amber-700"><RotateCw size={12} /> Auto-fixed in {answer.attempts} tries</span>}
          {answer.cached && <span className="badge bg-emerald-50 text-emerald-700"><Zap size={12} /> From cache</span>}
          {answer.context?.tables?.length > 0 && (
            <span className="hidden sm:inline" title="Context found by RAG">
              Context: {[...answer.context.tables.slice(0, 3), ...answer.context.glossary].join(", ")}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <span className="mr-1 text-xs text-ink-500">Helpful?</span>
          <button onClick={() => rate(1)} className={`rounded-md p-1.5 transition ${rating === 1 ? "bg-emerald-100 text-emerald-700" : "text-ink-500 hover:bg-slate-200"}`} title="Good answer — save as example">
            <ThumbsUp size={15} />
          </button>
          <button onClick={() => rate(-1)} className={`rounded-md p-1.5 transition ${rating === -1 ? "bg-red-100 text-red-700" : "text-ink-500 hover:bg-slate-200"}`} title="Bad answer">
            <ThumbsDown size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
