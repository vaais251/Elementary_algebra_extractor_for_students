"use client";

import { useState } from "react";

/* ── Answer Panel Component ── */
const AnswerPanel = ({ data }: { data: any }) => {
  if (data.error) {
    return (
      <div className="w-full max-w-2xl mt-8 backdrop-blur-lg bg-red-500/10 border border-red-500/30 rounded-2xl p-6 shadow-xl">
        <p className="text-red-400 font-medium">❌ {data.error}</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mt-8 space-y-4">
      {/* ── Hallucination Warning ── */}
      {data.hallucination_warning && (
        <div className="rounded-2xl bg-red-500/15 border border-red-500/40 px-5 py-4 flex items-start gap-3 shadow-lg shadow-red-500/5">
          <span className="text-2xl leading-none mt-0.5">⚠️</span>
          <div>
            <p className="text-red-300 font-semibold text-sm">
              Warning: This answer may not be fully supported by the curriculum.
            </p>
            <p className="text-red-400/80 text-xs mt-1">
              Faithfulness Score: {(data.faithfulness_score * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* ── Tutor Response Card ── */}
      <div className="backdrop-blur-lg bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl shadow-indigo-500/5">
        <h2 className="text-sm font-semibold text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-indigo-400"></span>
          Tutor Response
        </h2>

        {/* Faithfulness badge (when NOT a hallucination) */}
        {!data.hallucination_warning && data.faithfulness_score != null && (
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 px-3 py-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span className="text-emerald-300 text-xs font-medium">
              Faithfulness: {(data.faithfulness_score * 100).toFixed(1)}%
            </span>
          </div>
        )}

        {/* Answer text */}
        <p className="text-slate-200 leading-relaxed whitespace-pre-wrap text-[0.95rem]">
          {data.answer}
        </p>

        {/* ── Citations ── */}
        {data.citations && data.citations.length > 0 && (
          <div className="mt-5 pt-4 border-t border-white/10">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
              Sources Used
            </h3>
            <div className="flex flex-wrap gap-2">
              {data.citations.map((cite: string, i: number) => (
                <span
                  key={i}
                  className="inline-block rounded-full bg-slate-700/60 border border-white/10 px-3 py-1 text-xs text-slate-300 font-mono"
                >
                  {cite}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/* ── Main Page ── */
export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: "Failed to reach backend." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white flex flex-col items-center px-4 py-16">
      {/* ── Heading ── */}
      <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
        EduMaestro Tutor
      </h1>
      <p className="text-slate-400 mb-10 text-center max-w-md">
        Ask any elementary algebra question and let the multi-agent system break
        it down for you.
      </p>

      {/* ── Query Panel ── */}
      <form
        onSubmit={handleAsk}
        className="w-full max-w-2xl backdrop-blur-lg bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl shadow-indigo-500/5 transition-all"
      >
        <label
          htmlFor="query-input"
          className="block text-sm font-medium text-slate-300 mb-2"
        >
          Your Question
        </label>
        <input
          id="query-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. Solve 2x + 5 = 13"
          className="w-full rounded-xl bg-slate-800/60 border border-white/10 px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 transition"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="mt-4 w-full rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-3 font-semibold tracking-wide transition-all duration-200 shadow-lg shadow-indigo-600/20"
        >
          {loading ? "Thinking..." : "Ask EduMaestro"}
        </button>
      </form>

      {/* ── Answer Panel ── */}
      {result !== null && <AnswerPanel data={result} />}
    </main>
  );
}

