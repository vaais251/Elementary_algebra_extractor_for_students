"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

const ConceptGraph = dynamic(() => import("./components/ConceptGraph"), {
  ssr: false,
});

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
        {data.answer?.trim() === "Insufficient evidence" ? (
          <div className="flex items-start gap-3 rounded-xl bg-slate-800/50 border border-slate-700/50 px-4 py-3">
            <span className="text-slate-500 text-lg leading-none mt-0.5">ℹ️</span>
            <p className="text-slate-400 italic text-[0.95rem]">
              Insufficient evidence — the tutor could not find enough
              curriculum-backed material to answer this question.
            </p>
          </div>
        ) : (
          <p className="text-slate-200 leading-relaxed whitespace-pre-wrap text-[0.95rem]">
            {data.answer}
          </p>
        )}

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
  const [error, setError] = useState<string | null>(null);
  const [bypassWarning, setBypassWarning] = useState(false);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setBypassWarning(false);

    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      if (!res.ok) {
        throw new Error(`Server responded with status ${res.status}`);
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError("Failed to connect to the tutoring server. Please try again.");
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
          disabled={loading}
          placeholder="e.g. Solve 2x + 5 = 13"
          className="w-full rounded-xl bg-slate-800/60 border border-white/10 px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/60 transition disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="mt-4 w-full rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-3 font-semibold tracking-wide transition-all duration-200 shadow-lg shadow-indigo-600/20"
        >
          {loading ? "Thinking..." : "Ask EduMaestro"}
        </button>
      </form>

      {/* ── Loading Skeleton ── */}
      {loading && (
        <div className="w-full max-w-2xl mt-8 backdrop-blur-lg bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl animate-pulse">
          <div className="flex items-center gap-3 mb-5">
            <span className="w-5 h-5 rounded-full border-2 border-indigo-400/40 border-t-indigo-400 animate-spin"></span>
            <span className="text-sm text-slate-400">
              Consulting the multi-agent tutor…
            </span>
          </div>
          <div className="space-y-3">
            <div className="h-3 rounded-full bg-slate-700/50 w-1/3"></div>
            <div className="h-3 rounded-full bg-slate-700/50 w-full"></div>
            <div className="h-3 rounded-full bg-slate-700/50 w-11/12"></div>
            <div className="h-3 rounded-full bg-slate-700/50 w-4/5"></div>
          </div>
        </div>
      )}

      {/* ── Error Banner ── */}
      {error && (
        <div
          role="alert"
          className="w-full max-w-2xl mt-8 rounded-2xl bg-red-500/10 border border-red-500/40 px-5 py-4 flex items-start gap-3 shadow-xl shadow-red-500/5"
        >
          <span className="text-xl leading-none mt-0.5">⚠️</span>
          <p className="text-red-300 font-medium text-sm">{error}</p>
        </div>
      )}

      {/* ── Answer Panel ── */}
      {result !== null && <AnswerPanel data={result} />}

      {/* ── Hallucination Gate & Quiz Panel ── */}
      {result && !result.error && result.quiz && result.quiz.length > 0 && (
        <>
          {result.hallucination_warning && !bypassWarning ? (
            <div className="w-full max-w-2xl mt-6 border border-red-500 bg-red-500/10 rounded-2xl p-6 shadow-xl flex flex-col items-center gap-4 text-center">
              <p className="text-red-400 font-semibold">
                Warning: Generated quiz may contain hallucinations.
              </p>
              <button
                type="button"
                onClick={() => setBypassWarning(true)}
                className="rounded-xl bg-red-600 hover:bg-red-500 px-6 py-2.5 font-semibold text-sm transition-all duration-200 text-white"
              >
                Acknowledge Warning &amp; Show Quiz
              </button>
            </div>
          ) : (
            <QuizPanel quizData={result.quiz} />
          )}
        </>
      )}

      {/* ── Learning Path (Curriculum Planner) ── */}
      {result && !result.error && result.learning_path && (
        <LearningPathPanel path={result.learning_path} />
      )}

      {/* ── Concept Graph ── */}
      {result && !result.error && <ConceptGraph />}
    </main>
  );
}

/* ── Learning Path Panel Component ── */
const LearningPathPanel = ({
  path,
}: {
  path: { current: string; prerequisites: string[]; next_steps: string[] };
}) => {
  const Chip = ({ label, tone }: { label: string; tone: "amber" | "emerald" }) => {
    const styles =
      tone === "amber"
        ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
        : "bg-emerald-500/10 border-emerald-500/30 text-emerald-300";
    return (
      <span
        className={`inline-block rounded-full border px-3 py-1 text-xs font-medium ${styles}`}
      >
        {label}
      </span>
    );
  };

  return (
    <div className="w-full max-w-2xl mt-6 backdrop-blur-lg bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl shadow-cyan-500/5">
      <h2 className="text-sm font-semibold text-cyan-400 uppercase tracking-widest mb-1 flex items-center gap-2">
        <span className="inline-block w-2 h-2 rounded-full bg-cyan-400"></span>
        Learning Path
      </h2>
      <p className="text-slate-500 text-xs mb-5">
        The curriculum planner reasons over the prerequisite graph to suggest
        where to go before and after this topic.
      </p>

      <div className="space-y-4">
        {/* Prerequisites */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
            Before this, you should know
          </h3>
          {path.prerequisites.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {path.prerequisites.map((c) => (
                <Chip key={c} label={c} tone="amber" />
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-sm italic">
              This is a foundational concept — no prerequisites.
            </p>
          )}
        </div>

        {/* Current focus */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
            Current focus
          </h3>
          <span className="inline-block rounded-full bg-indigo-500/15 border border-indigo-500/40 px-3 py-1 text-sm font-semibold text-indigo-200">
            {path.current}
          </span>
        </div>

        {/* Next steps */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
            Recommended next
          </h3>
          {path.next_steps.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {path.next_steps.map((c) => (
                <Chip key={c} label={c} tone="emerald" />
              ))}
            </div>
          ) : (
            <p className="text-slate-400 text-sm italic">
              You&apos;ve reached the top of this learning track.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

/* ── Quiz Panel Component ── */
const QuizPanel = ({ quizData }: { quizData: any[] }) => {
  const [selectedAnswers, setSelectedAnswers] = useState<
    Record<number, string>
  >({});
  const [submitted, setSubmitted] = useState(false);

  if (!quizData || quizData.length === 0) return null;

  // Extract just the letter from an option string like "A. Some text"
  function getOptionLetter(option: string): string {
    return option.trim().charAt(0).toUpperCase();
  }

  const score = quizData.reduce((acc, q, idx) => {
    return acc + (selectedAnswers[idx] === q.answer ? 1 : 0);
  }, 0);

  return (
    <div className="w-full max-w-2xl mt-6 backdrop-blur-lg bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl shadow-purple-500/5">
      <h2 className="text-sm font-semibold text-purple-400 uppercase tracking-widest mb-5 flex items-center gap-2">
        <span className="inline-block w-2 h-2 rounded-full bg-purple-400"></span>
        Formative Quiz
      </h2>

      <div className="space-y-6">
        {quizData.map((q: any, qIdx: number) => {
          return (
            <div key={qIdx} className="space-y-3">
              <p className="text-slate-200 font-medium text-[0.95rem]">
                <span className="text-indigo-400 font-semibold mr-2">
                  Q{qIdx + 1}.
                </span>
                {q.question}
              </p>

              <div className="grid gap-2 pl-1">
                {q.options.map((option: string, oIdx: number) => {
                  const letter = getOptionLetter(option);
                  const isSelected = selectedAnswers[qIdx] === letter;
                  const isCorrect = q.answer === letter;

                  let optionStyle =
                    "border-white/10 bg-slate-800/40 hover:bg-slate-700/50";
                  if (submitted) {
                    if (isCorrect) {
                      optionStyle =
                        "border-emerald-500/50 bg-emerald-500/10 ring-1 ring-emerald-500/30 text-emerald-300";
                    } else if (isSelected && !isCorrect) {
                      optionStyle =
                        "border-red-500/50 bg-red-500/10 ring-1 ring-red-500/30 text-red-300";
                    } else {
                      optionStyle = "border-white/5 bg-slate-800/20 opacity-50";
                    }
                  } else if (isSelected) {
                    optionStyle =
                      "border-indigo-500/50 bg-indigo-500/10 ring-1 ring-indigo-500/30";
                  }

                  return (
                    <label
                      key={oIdx}
                      className={`flex items-center gap-3 w-full rounded-xl border px-4 py-2.5 text-sm transition-all duration-150 cursor-pointer ${optionStyle} ${
                        submitted ? "pointer-events-none" : ""
                      }`}
                    >
                      <input
                        type="radio"
                        name={`question-${qIdx}`}
                        value={letter}
                        checked={isSelected}
                        disabled={submitted}
                        onChange={() => {
                          if (!submitted) {
                            setSelectedAnswers((prev) => ({
                              ...prev,
                              [qIdx]: letter,
                            }));
                          }
                        }}
                        className="w-4 h-4 text-indigo-600 bg-slate-700 border-white/20 focus:ring-indigo-500 focus:ring-offset-slate-900"
                      />
                      <span className="text-slate-300">{option}</span>
                      {submitted && isCorrect && (
                        <span className="ml-auto text-emerald-400 text-xs font-semibold">
                          ✓ Correct
                        </span>
                      )}
                      {submitted && isSelected && !isCorrect && (
                        <span className="ml-auto text-red-400 text-xs font-semibold">
                          ✗ Incorrect
                        </span>
                      )}
                    </label>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 pt-4 border-t border-white/10">
        {!submitted ? (
          <button
            type="button"
            onClick={() => setSubmitted(true)}
            disabled={Object.keys(selectedAnswers).length < quizData.length}
            className="w-full rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-3 font-semibold tracking-wide transition-all duration-200 shadow-lg shadow-purple-600/20"
          >
            Submit Answers
          </button>
        ) : (
          <div className="text-center space-y-1">
            <p className="text-lg font-bold">
              You scored {score} out of {quizData.length}
            </p>
            <p className="text-slate-500 text-xs">
              {score === quizData.length
                ? "🎉 Perfect score!"
                : "Review the correct answers highlighted in green."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
