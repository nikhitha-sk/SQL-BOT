export default function PageHeader({ title, subtitle, children }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-ink-500">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

export function StatCard({ label, value, hint, accent = false }) {
  return (
    <div className={`card p-5 ${accent ? "bg-gradient-to-br from-brand-600 to-brand-800 text-white" : ""}`}>
      <p className={`text-xs font-semibold uppercase tracking-wider ${accent ? "text-brand-100" : "text-ink-500"}`}>{label}</p>
      <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
      {hint && <p className={`mt-1 text-xs ${accent ? "text-brand-100" : "text-ink-500"}`}>{hint}</p>}
    </div>
  );
}
