"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, FileUp, Loader2, MessageSquarePlus, ShieldCheck, Sparkles, TrendingUp, User } from "lucide-react";
import AnswerCard from "@/components/AnswerCard";
import { api } from "@/lib/api";

const SAMPLES = [
  { icon: "🏆", text: "Which product sold the most last month?" },
  { icon: "📈", text: "Show monthly revenue for this year" },
  { icon: "🥧", text: "What is the revenue share of each product category?" },
  { icon: "🗺️", text: "Total revenue by state" },
  { icon: "👥", text: "Who are the top 5 customers by revenue?" },
  { icon: "🛡️", text: "Delete all orders" },
];

const newSession = () => (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()));

export default function ChatPage() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [upload, setUpload] = useState(null);
  const endRef = useRef(null);
  const fileRef = useRef(null);

  useEffect(() => setSessionId(newSession()), []);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const ask = async (text) => {
    const question = (text ?? input).trim();
    if (!question || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setLoading(true);
    try {
      const answer = await api.ask(question, sessionId);
      setMessages((m) => [...m, { role: "bot", answer }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "bot", answer: { status: "error", error: e.message, chart: { type: "table" } } }]);
    } finally {
      setLoading(false);
    }
  };

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setUpload({ state: "loading", name: file.name });
    try {
      const res = await api.upload(file);
      setUpload({ state: "done", ...res });
    } catch (err) {
      setUpload({ state: "error", message: err.message });
    }
  };

  const reset = () => {
    setMessages([]);
    setSessionId(newSession());
  };

  return (
    <div className="mx-auto grid max-w-7xl gap-6 px-6 py-6 lg:grid-cols-[280px_1fr]">
      {/* Sidebar */}
      <aside className="hidden space-y-4 lg:block">
        <button onClick={reset} className="btn-primary w-full py-2.5">
          <MessageSquarePlus size={16} /> New chat
        </button>

        <div className="card p-4">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-ink-500">Try asking</p>
          <div className="space-y-1">
            {SAMPLES.map((s) => (
              <button key={s.text} onClick={() => ask(s.text)} className="w-full rounded-lg px-2.5 py-2 text-left text-sm text-ink-700 transition hover:bg-brand-50 hover:text-brand-700">
                <span className="mr-2">{s.icon}</span>{s.text}
              </button>
            ))}
          </div>
        </div>

        <div className="card p-4">
          <p className="mb-1 text-sm font-semibold text-ink-900">Bring your own data</p>
          <p className="mb-3 text-xs text-ink-500">Upload a CSV file and ask questions about it.</p>
          <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={onUpload} />
          <button onClick={() => fileRef.current?.click()} className="btn-ghost w-full" disabled={upload?.state === "loading"}>
            {upload?.state === "loading" ? <Loader2 size={16} className="animate-spin" /> : <FileUp size={16} />} Upload CSV
          </button>
          {upload?.state === "done" && (
            <p className="mt-2 text-xs text-emerald-700">
              Loaded <b>{upload.rows}</b> rows into table <code className="rounded bg-emerald-50 px-1">{upload.table}</code>
            </p>
          )}
          {upload?.state === "error" && <p className="mt-2 text-xs text-red-600">{upload.message}</p>}
        </div>

        <div className="rounded-2xl bg-gradient-to-br from-brand-600 to-brand-900 p-4 text-white">
          <ShieldCheck size={18} />
          <p className="mt-2 text-sm font-semibold">Safe by design</p>
          <p className="mt-1 text-xs leading-relaxed text-brand-100">
            Every query is checked: SELECT only, approved tables, row limit, timeout and a read-only connection.
          </p>
        </div>
      </aside>

      {/* Chat */}
      <section className="flex min-h-[calc(100vh-10rem)] flex-col">
        <div className="flex-1 space-y-6 pb-6">
          {messages.length === 0 && (
            <div className="pt-8 text-center sm:pt-14">
              <span className="badge bg-brand-50 text-brand-700 ring-1 ring-brand-100">
                <Sparkles size={12} /> Text-to-SQL · RAG · Auto charts
              </span>
              <h1 className="mx-auto mt-5 max-w-2xl text-4xl font-semibold tracking-tight text-ink-900 sm:text-5xl">
                Ask your business data <span className="bg-gradient-to-r from-brand-600 to-sky-500 bg-clip-text text-transparent">anything</span>
              </h1>
              <p className="mx-auto mt-4 max-w-xl text-ink-500">
                Type a question in plain English. AskSQL writes safe SQL, runs it, and shows you the answer as a chart, a table and the SQL used.
              </p>
              <div className="mx-auto mt-10 grid max-w-3xl gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {SAMPLES.slice(0, 6).map((s) => (
                  <button key={s.text} onClick={() => ask(s.text)} className="card group p-4 text-left transition hover:-translate-y-0.5 hover:border-brand-200">
                    <span className="text-xl">{s.icon}</span>
                    <p className="mt-2 text-sm font-medium text-ink-700 group-hover:text-brand-700">{s.text}</p>
                  </button>
                ))}
              </div>
              <div className="mx-auto mt-10 flex max-w-2xl flex-wrap justify-center gap-x-8 gap-y-2 text-xs text-ink-500">
                <span className="flex items-center gap-1.5"><TrendingUp size={14} /> Bar, line, pie and number charts</span>
                <span className="flex items-center gap-1.5"><ShieldCheck size={14} /> Read-only and validated</span>
                <span className="flex items-center gap-1.5"><MessageSquarePlus size={14} /> Follow-up questions</span>
              </div>
            </div>
          )}

          {messages.map((m, i) =>
            m.role === "user" ? (
              <div key={i} className="flex justify-end">
                <div className="flex max-w-[80%] items-start gap-2.5">
                  <p className="rounded-2xl rounded-tr-sm bg-brand-600 px-4 py-2.5 text-[15px] text-white shadow-sm">{m.text}</p>
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-ink-700"><User size={15} /></span>
                </div>
              </div>
            ) : (
              <AnswerCard key={i} answer={m.answer} />
            )
          )}

          {loading && (
            <div className="card flex items-center gap-3 p-5 text-sm text-ink-500">
              <Loader2 size={18} className="animate-spin text-brand-600" />
              Finding tables, writing SQL and running it…
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            ask();
          }}
          className="sticky bottom-4"
        >
          <div className="card flex items-end gap-2 p-2 pl-4 ring-brand-100 focus-within:ring-4">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  ask();
                }
              }}
              rows={1}
              maxLength={500}
              placeholder={messages.length ? "Ask a follow-up, e.g. “now only for Karnataka”" : "Ask a question about your data…"}
              className="max-h-40 flex-1 resize-none bg-transparent py-2.5 text-[15px] outline-none placeholder:text-slate-400"
            />
            <button type="submit" disabled={!input.trim() || loading} className="btn-primary h-10 w-10 rounded-xl p-0" title="Send">
              <ArrowUp size={18} />
            </button>
          </div>
          <p className="mt-2 text-center text-[11px] text-ink-500">AskSQL can make mistakes. Check the SQL tab to see exactly what was run.</p>
        </form>
      </section>
    </div>
  );
}
