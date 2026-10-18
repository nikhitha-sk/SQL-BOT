"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

const KEYWORDS = /\b(SELECT|FROM|WHERE|GROUP BY|ORDER BY|LIMIT|JOIN|LEFT|INNER|ON|AS|AND|OR|IN|NOT|WITH|HAVING|DESC|ASC|SUM|COUNT|AVG|ROUND|MIN|MAX|DISTINCT|CASE|WHEN|THEN|ELSE|END|STRFTIME|DATE|UNION|ALL)\b/gi;

function highlight(sql) {
  const escaped = sql.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return escaped
    .replace(/('[^']*')/g, '<span class="text-emerald-300">$1</span>')
    .replace(KEYWORDS, (k) => `<span class="text-sky-300 font-semibold">${k.toUpperCase()}</span>`);
}

export default function SqlView({ sql }) {
  const [copied, setCopied] = useState(false);
  const pretty = sql.replace(/\s+(FROM|WHERE|GROUP BY|ORDER BY|LIMIT|JOIN|LEFT JOIN|HAVING)\s/gi, "\n$1 ");

  const copy = async () => {
    await navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="relative rounded-xl bg-ink-900">
      <button onClick={copy} className="absolute right-3 top-3 rounded-md bg-white/10 p-1.5 text-slate-300 hover:bg-white/20" title="Copy SQL">
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </button>
      <pre className="whitespace-pre-wrap break-words p-4 pr-12 font-mono text-[13px] leading-relaxed text-slate-100">
        <code dangerouslySetInnerHTML={{ __html: highlight(pretty) }} />
      </pre>
    </div>
  );
}
