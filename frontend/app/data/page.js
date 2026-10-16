"use client";

import { useEffect, useState } from "react";
import { BookOpen, Table2 } from "lucide-react";
import PageHeader from "@/components/PageHeader";
import { api } from "@/lib/api";

export default function DataPage() {
  const [tables, setTables] = useState([]);
  const [glossary, setGlossary] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.schema(), api.glossary()])
      .then(([s, g]) => {
        setTables(s);
        setGlossary(g);
      })
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <PageHeader title="Data catalog" subtitle="Tables the chatbot is allowed to query, and the business terms it understands." />
      {error && <p className="card mb-6 p-5 text-sm text-red-600">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2">
        {tables.map((t) => (
          <div key={t.name} className="card p-5">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 text-brand-600"><Table2 size={17} /></span>
                <div>
                  <p className="font-mono text-sm font-semibold text-ink-900">{t.name}</p>
                  <p className="text-xs text-ink-500">{t.rows.toLocaleString("en-IN")} rows</p>
                </div>
              </div>
              {t.uploaded && <span className="badge bg-violet-50 text-violet-700">Uploaded CSV</span>}
            </div>
            <p className="mt-3 text-sm text-ink-700">{t.description}</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {t.columns.map((c) => (
                <span key={c} className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-xs text-ink-700">{c}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <h2 className="mb-4 mt-10 flex items-center gap-2 text-lg font-semibold text-ink-900"><BookOpen size={18} /> Business glossary</h2>
      <div className="card divide-y divide-slate-100">
        {glossary.map((g) => (
          <div key={g.term} className="grid gap-1 px-5 py-3.5 sm:grid-cols-[220px_1fr]">
            <p className="text-sm font-semibold capitalize text-ink-900">{g.term}</p>
            <p className="text-sm text-ink-700">{g.meaning}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
