"use client";

import { useEffect, useRef } from "react";
import { formatNumber } from "@/lib/api";

const COLORS = ["#2563eb", "#0ea5e9", "#14b8a6", "#f59e0b", "#8b5cf6", "#ef4444"];

function traces(chart, columns, rows) {
  const col = (name) => rows.map((r) => r[columns.indexOf(name)]);
  const x = col(chart.x);
  const y = col(chart.y);
  switch (chart.type) {
    case "line":
      return [{ type: "scatter", mode: "lines+markers", x, y, line: { color: COLORS[0], width: 3, shape: "spline" }, marker: { size: 6 }, fill: "tozeroy", fillcolor: "rgba(37,99,235,0.08)" }];
    case "bar":
      return [{ type: "bar", x, y, marker: { color: COLORS[0], cornerradius: 6 } }];
    case "pie":
      return [{ type: "pie", labels: x, values: y, hole: 0.55, marker: { colors: COLORS }, textinfo: "label+percent" }];
    case "scatter":
      return [{ type: "scatter", mode: "markers", x, y, marker: { color: COLORS[0], size: 9, opacity: 0.75 } }];
    default:
      return [];
  }
}

export default function ChartView({ chart, columns, rows }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!["line", "bar", "pie", "scatter"].includes(chart.type)) return;
    let Plotly;
    let cancelled = false;
    import("plotly.js-dist-min").then((mod) => {
      if (cancelled || !ref.current) return;
      Plotly = mod.default;
      Plotly.newPlot(
        ref.current,
        traces(chart, columns, rows),
        {
          margin: { t: 16, r: 16, b: 56, l: 64 },
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { family: "Inter, system-ui, sans-serif", color: "#334155", size: 12 },
          xaxis: { title: { text: chart.x }, gridcolor: "#f1f5f9", automargin: true },
          yaxis: { title: { text: chart.y }, gridcolor: "#e2e8f0", automargin: true },
          showlegend: chart.type === "pie",
          hoverlabel: { bgcolor: "#0f172a", font: { color: "#fff" } },
        },
        { displayModeBar: false, responsive: true }
      );
    });
    return () => {
      cancelled = true;
      if (Plotly && ref.current) Plotly.purge(ref.current);
    };
  }, [chart, columns, rows]);

  if (chart.type === "number") {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl bg-gradient-to-br from-brand-50 to-white py-10">
        <span className="text-xs font-semibold uppercase tracking-wider text-brand-700">{chart.label}</span>
        <span className="mt-2 text-5xl font-semibold tracking-tight text-ink-900">{formatNumber(rows[0][0])}</span>
      </div>
    );
  }
  return <div ref={ref} className="h-80 w-full" />;
}
