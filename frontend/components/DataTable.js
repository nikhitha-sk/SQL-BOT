import { formatNumber } from "@/lib/api";

export default function DataTable({ columns, rows, max = 200 }) {
  if (!rows.length) return <p className="py-6 text-center text-sm text-ink-500">No rows returned.</p>;
  return (
    <div className="scrollbar-thin max-h-80 overflow-auto rounded-xl border border-slate-200">
      <table className="w-full text-left text-sm">
        <thead className="sticky top-0 bg-slate-50 text-xs uppercase tracking-wide text-ink-500">
          <tr>
            {columns.map((c) => (
              <th key={c} className="whitespace-nowrap px-4 py-2.5 font-semibold">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.slice(0, max).map((row, i) => (
            <tr key={i} className="hover:bg-slate-50">
              {row.map((v, j) => (
                <td key={j} className={`whitespace-nowrap px-4 py-2 ${typeof v === "number" ? "text-right tabular-nums" : ""}`}>
                  {formatNumber(v)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > max && (
        <p className="border-t border-slate-100 bg-slate-50 px-4 py-2 text-xs text-ink-500">
          Showing first {max} of {rows.length} rows.
        </p>
      )}
    </div>
  );
}
