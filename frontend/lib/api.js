async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

const postJson = (path, body) =>
  request(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

export const api = {
  health: () => request("/health"),
  ask: (question, sessionId) => postJson("/chat", { question, session_id: sessionId }),
  feedback: (messageId, rating) => postJson("/feedback", { message_id: messageId, rating }),
  history: () => request("/history"),
  stats: () => request("/stats"),
  schema: () => request("/schema"),
  glossary: () => request("/glossary"),
  evalReport: () => request("/eval/report"),
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/upload", { method: "POST", body: form });
  },
};

export const formatNumber = (v) =>
  typeof v === "number" ? v.toLocaleString("en-IN", { maximumFractionDigits: 2 }) : v ?? "—";

export const formatCost = (v) => `$${(v || 0).toFixed(4)}`;

export const formatMs = (ms) => (ms >= 1000 ? `${(ms / 1000).toFixed(1)} s` : `${ms || 0} ms`);
