import os
import sys
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from hybrid_search import hybrid_retrieve

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────
# LLM Initialization
# ─────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.environ.get("GOOGLE_API_KEY"),
    temperature=0.0,
)


# ─────────────────────────────────────────────
# Agent 2 — Retrieval Tool
# ─────────────────────────────────────────────
@tool
def retrieve_educational_content(query: str, top_k: int = 5) -> list:
    """
    Use this tool to search the educational curriculum corpus for math concepts.
    Performs hybrid retrieval combining BM25 (Elasticsearch) and dense semantic
    search (FAISS) via Reciprocal Rank Fusion to return the most relevant
    curriculum-aligned chunks.

    Args:
        query:  The user's search query or question about a math topic.
        top_k:  Number of top results to return (default 5).

    Returns:
        A list of the top matching document chunks with their content and metadata.
    """
    docs = hybrid_retrieve(query, top_k=top_k)
    # Serialize to plain dicts so the agent can read the output
    return [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in docs
    ]


# ─────────────────────────────────────────────
# Agent 1 — Query Understanding
# ─────────────────────────────────────────────

class QueryIntent(BaseModel):
    """Structured schema for a parsed student query."""
    intent: str = Field(
        description=(
            "The type of student query. One of: "
            "'factoid' (single-fact lookups like definitions), "
            "'concept' (conceptual understanding requests), "
            "'problem-solving' (step-by-step worked examples), "
            "or 'discovery' (open-ended exploration)."
        )
    )
    keywords: list[str] = Field(
        description="A list of key mathematical terms or concepts extracted from the query."
    )


_intent_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        (
            "You are an educational query analyser for a secondary-school mathematics AI tutor. "
            "Your job is to classify the student's question and extract the key mathematical terms. "
            "Respond ONLY with the structured output — no extra commentary."
        ),
    ),
    ("human", "Analyse this student query:\n\n{user_input}"),
])

# Chain: prompt → Gemini with structured output enforced via Pydantic schema
_intent_chain = _intent_prompt | llm.with_structured_output(QueryIntent)


def analyze_query(user_input: str) -> dict:
    """
    Agent 1 — Query Understanding.

    Takes a raw student question, sends it to Gemini with a structured output
    schema, and returns a dictionary containing:
      - intent   : one of factoid | concept | problem-solving | discovery
      - keywords : list of extracted mathematical terms
    """
    result: QueryIntent = _intent_chain.invoke({"user_input": user_input})
    return {"intent": result.intent, "keywords": result.keywords}


# ─────────────────────────────────────────────
# Main — End-to-end test
# ─────────────────────────────────────────────
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    test_query = "what is  Multi-Agent LLM Orchestration"
    print(f"Test Query: '{test_query}'\n")
    print("=" * 60)

    # --- Agent 1: Understand the query ---
    print("\n[Agent 1 — Query Understanding]")
    intent_result = analyze_query(test_query)
    print(f"  Intent  : {intent_result['intent']}")
    print(f"  Keywords: {intent_result['keywords']}")

    # --- Agent 2: Retrieve relevant content ---
    print("\n[Agent 2 — Retrieval Tool]")
    retrieval_results = retrieve_educational_content.invoke(
        {"query": test_query, "top_k": 3}
    )

    print(f"\nTop {len(retrieval_results)} Retrieved Chunks:")
    for i, chunk in enumerate(retrieval_results):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"  Source : {chunk['metadata'].get('source', 'N/A')}  |  "
              f"Page: {chunk['metadata'].get('page', 'N/A')}")
        print(f"  Content: {chunk['page_content']}")

    print("\n" + "=" * 60)
    print("Pipeline complete.")
