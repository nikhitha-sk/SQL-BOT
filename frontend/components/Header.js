"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Database } from "lucide-react";
import { api } from "@/lib/api";

const NAV = [
  { href: "/", label: "Chat" },
  { href: "/history", label: "History" },
  { href: "/data", label: "Data" },
  { href: "/evaluation", label: "Evaluation" },
];

export default function Header() {
  const path = usePathname();
  const [online, setOnline] = useState(null);

  useEffect(() => {
    api.health().then(() => setOnline(true)).catch(() => setOnline(false));
  }, []);

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-sm">
            <Database size={18} />
          </span>
          <span className="leading-tight">
            <span className="block text-base font-semibold text-ink-900">AskSQL</span>
            <span className="block text-[11px] font-medium uppercase tracking-wider text-ink-500">Business Data Assistant</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-lg px-3.5 py-2 text-sm font-medium transition ${
                path === item.href ? "bg-brand-50 text-brand-700" : "text-ink-700 hover:bg-slate-100"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <span
          className={`badge ${
            online === null ? "bg-slate-100 text-ink-500" : online ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"
          }`}
        >
          <span className={`h-1.5 w-1.5 rounded-full ${online ? "bg-emerald-500" : online === false ? "bg-red-500" : "bg-slate-400"}`} />
          {online === null ? "Connecting" : online ? "API online" : "API offline"}
        </span>
      </div>
      <nav className="flex gap-1 overflow-x-auto px-4 pb-2 md:hidden">
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${path === item.href ? "bg-brand-50 text-brand-700" : "text-ink-700"}`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
