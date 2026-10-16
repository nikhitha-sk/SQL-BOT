"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Terminal, XCircle } from "lucide-react";
import PageHeader, { StatCard } from "@/components/PageHeader";
import { api, formatCost, formatMs } from "@/lib/api";

function LevelBars({ byLevel }) {
  return (
    <div className="space-y-3">
      {Object.entries(byLevel).map(([level, pct]) => (
        <div key={level}>
          <div className="mb-1 flex justify-between text-sm">
            <span className="capitalize text-ink-700">{level}</span>
            <span className="font-medium tabular-nums">{pct}%</span>
          </div>
          <div className="h-2 rounded-full bg-slate-100">
            <div className="h-2 rounded-full bg-brand-600" style={{ width: `${pct}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function EvaluationPage() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    api.evalReport().then(setReport).catch((e) => setError(e.message));
  }, []);

  const main = report?.rag || report?.basic;
  const cases = main ? (showAll ? main.cases : main.cases.filter((c) => !c.passed)) : [];

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <PageHeader title="Evaluation" subtitle="Accuracy on a fixed set of 40 test questions (easy, medium and hard)." />

      {error && (
        <div className="card p-6">
          <p className="font-medium text-ink-900">No evaluation report yet</p>
          <p className="mt-1 text-sm text-ink-500">Run the evaluation from the backend folder, then refresh this page:</p>
          <pre className="mt-3 flex items-center gap-2 rounded-lg bg-ink-900 p-3 font-mono text-sm text-slate-100">
            <Terminal size={14} /> python -m eval.run_eval
          </pre>
        </div>
      )}

      {main && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Accuracy (RAG)" value={report.rag ? `${report.rag.accuracy}%` : "—"} hint={report.rag && `${report.rag.passed} of ${report.rag.total} correct`} accent />
            <StatCard label="Accuracy (basic prompt)" value={report.basic ? `${report.basic.accuracy}%` : "—"} hint={report.basic ? `${report.basic.passed} of ${report.basic.total} correct` : "Run with --mode basic"} />
            <StatCard label="Avg time / question" value={formatMs(main.avg_time_ms)} />
            <StatCard label="Avg cost / question" value={formatCost(main.avg_cost_usd)} hint={`Last run ${main.run_at}`} />
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-[320px_1fr]">
            <div className="card h-fit p-5">
              <p className="mb-4 text-sm font-semibold text-ink-900">Accuracy by difficulty</p>
              <LevelBars byLevel={main.by_level} />
            </div>

            <div className="card overflow-hidden">
              <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
                <p className="text-sm font-semibold text-ink-900">{showAll ? "All cases" : "Failed cases"}</p>
                <button onClick={() => setShowAll(!showAll)} className="text-sm font-medium text-brand-600 hover:text-brand-700">
                  {showAll ? "Show failed only" : "Show all"}
                </button>
              </div>
              <div className="scrollbar-thin max-h-[560px] divide-y divide-slate-100 overflow-auto">
                {cases.length === 0 && <p className="px-5 py-10 text-center text-sm text-ink-500">No failed cases. 🎉</p>}
                {cases.map((c) => (
                  <details key={c.question} className="group px-5 py-3">
                    <summary className="flex cursor-pointer list-none items-center gap-3">
                      {c.passed ? <CheckCircle2 size={16} className="shrink-0 text-emerald-500" /> : <XCircle size={16} className="shrink-0 text-red-500" />}
                      <span className="flex-1 text-sm text-ink-900">{c.question}</span>
                      <span className="badge bg-slate-100 capitalize text-ink-500">{c.level}</span>
                    </summary>
                    <div className="mt-3 grid gap-3 md:grid-cols-2">
                      <div>
                        <p className="mb-1 text-xs font-semibold uppercase text-ink-500">Expected SQL</p>
                        <pre className="scrollbar-thin overflow-x-auto rounded-lg bg-slate-100 p-3 font-mono text-xs">{c.expected_sql}</pre>
                      </div>
                      <div>
                        <p className="mb-1 text-xs font-semibold uppercase text-ink-500">Generated SQL</p>
                        <pre className="scrollbar-thin overflow-x-auto rounded-lg bg-slate-100 p-3 font-mono text-xs">{c.generated_sql || c.error || "—"}</pre>
                      </div>
                    </div>
                  </details>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
