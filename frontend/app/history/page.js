"use client";

import { Fragment, useEffect, useState } from "react";
import { RefreshCw, ThumbsDown, ThumbsUp } from "lucide-react";
import PageHeader, { StatCard } from "@/components/PageHeader";
import { api, formatCost, formatMs } from "@/lib/api";

export default function HistoryPage() {
  const [rows, setRows] = useState(null);
  const [stats, setStats] = useState(null);
  const [open, setOpen] = useState(null);
  const [error, setError] = useState("");

  const load = () => {
    setError("");
    Promise.all([api.history(), api.stats()])
      .then(([h, s]) => {
        setRows(h);
        setStats(s);
      })
      .catch((e) => setError(e.message));
  };
  useEffect(load, []);

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <PageHeader title="Query history" subtitle="Every question, the SQL that ran, time, tokens and cost (audit log).">
        <button onClick={load} className="btn-ghost"><RefreshCw size={15} /> Refresh</button>
      </PageHeader>

      {stats && (
        <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Questions asked" value={stats.questions} accent />
          <StatCard label="Success rate" value={`${Math.round(stats.success_rate * 100)}%`} />
          <StatCard label="Avg response time" value={formatMs(Math.round(stats.avg_time_ms))} />
          <StatCard label="Total LLM cost" value={formatCost(stats.total_cost_usd)} hint={`${stats.good_queries} approved example queries`} />
        </div>
      )}

      {error && <p className="card p-5 text-sm text-red-600">{error}</p>}

      {rows && (
        <div className="card overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-ink-500">
              <tr>
                <th className="px-5 py-3 font-semibold">Question</th>
                <th className="hidden px-5 py-3 font-semibold md:table-cell">Chart</th>
                <th className="px-5 py-3 font-semibold">Status</th>
                <th className="hidden px-5 py-3 text-right font-semibold sm:table-cell">Time</th>
                <th className="hidden px-5 py-3 text-right font-semibold sm:table-cell">Cost</th>
                <th className="px-5 py-3 text-center font-semibold">Rating</th>
                <th className="hidden px-5 py-3 font-semibold lg:table-cell">Asked at</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.length === 0 && (
                <tr><td colSpan={7} className="px-5 py-10 text-center text-ink-500">No questions yet. Ask something on the Chat page.</td></tr>
              )}
              {rows.map((r) => (
                <Fragment key={r.id}>
                  <tr onClick={() => setOpen(open === r.id ? null : r.id)} className="cursor-pointer hover:bg-slate-50">
                    <td className="max-w-md truncate px-5 py-3 font-medium text-ink-900">{r.question}</td>
                    <td className="hidden px-5 py-3 capitalize text-ink-700 md:table-cell">{r.chart}</td>
                    <td className="px-5 py-3">
                      <span className={`badge ${r.success ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                        {r.success ? "Success" : "Blocked / failed"}
                      </span>
                    </td>
                    <td className="hidden px-5 py-3 text-right tabular-nums text-ink-700 sm:table-cell">{formatMs(r.time_ms)}</td>
                    <td className="hidden px-5 py-3 text-right tabular-nums text-ink-700 sm:table-cell">{formatCost(r.cost_usd)}</td>
                    <td className="px-5 py-3 text-center">
                      {r.rating === 1 ? <ThumbsUp size={15} className="inline text-emerald-600" /> : r.rating === -1 ? <ThumbsDown size={15} className="inline text-red-500" /> : <span className="text-slate-300">—</span>}
                    </td>
                    <td className="hidden whitespace-nowrap px-5 py-3 text-ink-500 lg:table-cell">{r.created_at}</td>
                  </tr>
                  {open === r.id && (
                    <tr className="bg-slate-50">
                      <td colSpan={7} className="px-5 py-3">
                        <pre className="scrollbar-thin overflow-x-auto rounded-lg bg-ink-900 p-3 font-mono text-xs text-slate-100">{r.sql || "No SQL was run."}</pre>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
