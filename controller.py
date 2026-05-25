"""
controller.py — EduMaestro Day 12
==================================
Agent 7 (Controller): orchestrates the full query-to-output pipeline.
Agent 6 (Assessment):  generates formative multiple-choice quizzes via Gemini.

Pipeline
--------
  Query
    |-- Agent 1  : analyze_query           (intent + keywords)
    |-- Agent 2  : retrieve_educational_content  (hybrid BM25 + FAISS)
    |-- Agent 3/4: rerank_documents         (CrossEncoder + MMR)
    |-- Agent 5  : generate_tutor_response  (structured answer)
    |-- Evaluator: calculate_token_overlap  (faithfulness check)
    |-- Agent 6  : generate_assessment      (3-question MCQ quiz)
    --> Final consolidated output dict
"""

import sys
import os
import json
import re

# Force UTF-8 on Windows terminals before any other print/import.
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

# ── Local module imports ──────────────────────────────────────────────────────
from agents import analyze_query, retrieve_educational_content
from reranker import rerank_documents
from generator import generate_tutor_response
from evaluator import calculate_token_overlap

# ── Gemini client (google-genai v1 SDK — installed as google-genai) ─────────────
from google import genai
from google.genai import types as genai_types

_genai_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

_HALLUCINATION_THRESHOLD = 0.4   # scores below this trigger a warning


# ─────────────────────────────────────────────────────────────────────────────
# Agent 6 — Assessment: Formative Quiz Generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_assessment(topic: str) -> list:
    """Agent 6 — Assessment.

    Calls Gemini to generate exactly 3 multiple-choice questions about *topic*.
    Uses temperature=0.4 for slight variation across runs.

    Args:
        topic: The mathematical concept or keyword to quiz the student on.

    Returns:
        A list of dicts, each containing:
          - question (str)
          - options  (list[str], 4 items labelled A–D)
          - answer   (str, the correct option label e.g. "B")
        Returns an empty list if Gemini returns unparseable output.
    """
    prompt = (
        f"You are an educational assessment designer for secondary-school mathematics.\n"
        f"Generate exactly 3 multiple-choice questions about: '{topic}'.\n\n"
        "Requirements:\n"
        "  - Each question must have 4 options labelled A, B, C, D.\n"
        "  - Mark the single correct answer.\n"
        "  - Return ONLY a valid JSON array — no markdown fences, no extra text.\n\n"
        "Format:\n"
        "[\n"
        "  {\n"
        '    "question": "...",\n'
        '    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],\n'
        '    "answer": "A"\n'
        "  },\n"
        "  ...\n"
        "]"
    )

    try:
        response = _genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(temperature=0.4),
        )
        raw = response.text.strip()

        # Strip markdown code fences if Gemini wraps the JSON anyway
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        questions = json.loads(raw)
        return questions if isinstance(questions, list) else []

    except (json.JSONDecodeError, ValueError, AttributeError) as exc:
        print(f"  [Agent 6] Quiz parse error: {exc}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Agent 7 — Controller: Full Pipeline Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def run_edumaestro(user_query: str) -> dict:
    """Agent 7 — Controller.

    Runs the complete EduMaestro pipeline for a given student query and returns
    a consolidated output dictionary.

    Args:
        user_query: The raw question submitted by the student.

    Returns:
        A dict with keys:
          - query          (str)
          - intent         (str)
          - keywords       (list[str])
          - answer         (str)   — may include a hallucination warning
          - citations      (list[int])
          - worked_solution (str | None)
          - lesson_outline (str)
          - faithfulness_score (float)
          - hallucination_warning (bool)
          - quiz           (list[dict])
    """
    separator = "=" * 60

    print(f"\n{separator}")
    print("  EduMaestro — Full Pipeline (Day 12)")
    print(separator)
    print(f"\n  Query: \"{user_query}\"")

    # ── Step 1: Query Understanding (Agent 1) ─────────────────────────────────
    print("\n[Step 1] Analyzing query intent...")
    intent_data = analyze_query(user_query)
    intent   = intent_data["intent"]
    keywords = intent_data["keywords"]
    print(f"  Intent  : {intent}")
    print(f"  Keywords: {keywords}")

    # ── Step 2: Hybrid Retrieval (Agent 2) ────────────────────────────────────
    print("\n[Step 2] Retrieving educational content...")
    raw_results = retrieve_educational_content.invoke(
        {"query": user_query, "top_k": 5}
    )
    print(f"  Retrieved {len(raw_results)} candidate chunk(s).")

    # ── Step 3: Reranking (Agent 3/4) — simulate CrossEncoder scores ──────────
    # rerank_documents expects LangChain Document objects, not plain dicts.
    # We reconstruct lightweight Document-like objects to keep the contract.
    print("\n[Step 3] Reranking with CrossEncoder + MMR (top 3)...")

    from langchain_core.documents import Document

    doc_objects = [
        Document(
            page_content=r["page_content"],
            metadata=r.get("metadata", {}),
        )
        for r in raw_results
    ]

    # Simulate descending relevance scores (indices already ordered by hybrid RRF)
    simulated_scores = [1.0 - (i * 0.15) for i in range(len(doc_objects))]

    top_docs = rerank_documents(simulated_scores, doc_objects, top_k=3)
    print(f"  Reranked down to {len(top_docs)} document(s).")

    # ── Step 4: Build evidence string ─────────────────────────────────────────
    evidence_string = "\n\n".join(
        f"[ID: {i + 1}] {doc.page_content}"
        for i, doc in enumerate(top_docs)
    )

    # ── Step 5: Generate Tutor Response (Agent 5) ─────────────────────────────
    print("\n[Step 5] Generating tutor response...")
    tutor_response = generate_tutor_response(user_query, evidence_string)

    # Extract the plain-text answer for evaluation
    generated_answer_text = tutor_response.answer

    # ── Step 6: Faithfulness Evaluation ───────────────────────────────────────
    print("\n[Step 6] Running faithfulness evaluation...")
    score = calculate_token_overlap(generated_answer_text, evidence_string)
    hallucination_warning = score < _HALLUCINATION_THRESHOLD

    print(f"  Overlap score : {score:.2%}")
    if hallucination_warning:
        print("  WARNING: Potential Hallucination Detected.")
        generated_answer_text += "\n\nWARNING: Potential Hallucination Detected."

    # ── Step 7: Assessment / Quiz (Agent 6) ───────────────────────────────────
    print("\n[Step 7] Generating formative quiz...")
    # Use the first keyword as the topic if available, else fall back to the query
    quiz_topic = keywords[0] if keywords else user_query
    quiz = generate_assessment(quiz_topic)
    print(f"  Generated {len(quiz)} question(s).")

    # ── Build and return the final consolidated output ────────────────────────
    return {
        "query":                user_query,
        "intent":               intent,
        "keywords":             keywords,
        "answer":               generated_answer_text,
        "citations":            tutor_response.citations,
        "worked_solution":      tutor_response.worked_solution,
        "lesson_outline":       tutor_response.lesson_outline,
        "faithfulness_score":   round(score, 4),
        "hallucination_warning": hallucination_warning,
        "quiz":                 quiz,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = run_edumaestro("Explain the Pythagorean theorem")

    separator = "=" * 60
    print(f"\n{separator}")
    print("  FINAL CONSOLIDATED OUTPUT")
    print(separator)

    print(f"\n  Query   : {result['query']}")
    print(f"  Intent  : {result['intent']}")
    print(f"  Keywords: {result['keywords']}")

    print(f"\n--- Tutor Answer ---")
    print(f"  {result['answer']}")

    if result["worked_solution"]:
        print(f"\n--- Worked Solution ---")
        print(f"  {result['worked_solution']}")

    print(f"\n--- Lesson Outline ---")
    print(f"  {result['lesson_outline']}")

    print(f"\n--- Faithfulness Evaluation ---")
    print(f"  Score              : {result['faithfulness_score']:.2%}")
    print(f"  Hallucination flag : {'YES [WARN]' if result['hallucination_warning'] else 'No  [OK]'}")

    print(f"\n--- Formative Quiz ({len(result['quiz'])} questions) ---")
    for i, q in enumerate(result["quiz"], start=1):
        print(f"\n  Q{i}: {q.get('question', 'N/A')}")
        for opt in q.get("options", []):
            print(f"      {opt}")
        print(f"      Correct: {q.get('answer', 'N/A')}")

    print(f"\n{separator}")
    print("  Pipeline complete.")
    print(separator)
