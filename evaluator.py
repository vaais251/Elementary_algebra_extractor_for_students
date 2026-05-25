import re
import sys

# Force UTF-8 output so special characters render correctly on Windows terminals.
sys.stdout.reconfigure(encoding='utf-8')

# --- Faithfulness Evaluator ---
# Computes a token overlap score between a generated answer and retrieved
# evidence passages to surface potential hallucinations before serving a
# response to the student.

STOP_WORDS = {
    'the', 'is', 'in', 'and', 'to', 'a', 'of', 'it',
    'be', 'as', 'at', 'so', 'we', 'he', 'by', 'or',
    'an', 'if', 'me', 'my', 'do', 'on', 'no', 'up',
}


def _tokenize(text: str) -> set[str]:
    """Lowercase, strip punctuation, split into tokens, and remove stop words."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)   # remove all punctuation
    tokens = set(text.split())
    tokens -= STOP_WORDS                   # filter stop words in-place
    return tokens


def calculate_token_overlap(answer: str, evidence: str) -> float:
    """Calculate the faithfulness score of an answer against source evidence.

    The score is the fraction of unique, meaningful tokens in the answer that
    also appear in the evidence.  A high score (close to 1.0) indicates the
    answer is well-grounded in the retrieved passages; a low score is a signal
    of potential hallucination.

    Args:
        answer:   The AI-generated answer to evaluate.
        evidence: The retrieved source passage(s) used as ground truth.

    Returns:
        A float in [0.0, 1.0] representing the overlap ratio.
        Returns 0.0 if the answer contains no meaningful tokens.
    """
    answer_tokens = _tokenize(answer)
    evidence_tokens = _tokenize(evidence)

    # Guard against division by zero when the answer is empty / all stop words
    if not answer_tokens:
        return 0.0

    intersection = answer_tokens & evidence_tokens
    return len(intersection) / len(answer_tokens)


# ---------------------------------------------------------------------------
# Quick smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mock_evidence = (
        "The quadratic formula is x = (-b +/- sqrt(b^2 - 4ac)) / 2a."
    )

    mock_faithful_answer = (
        "To solve this, use the quadratic formula: x = (-b +/- sqrt(b^2 - 4ac)) / 2a."
    )

    mock_hallucinated_answer = (
        "Use the cubic equation formula derived by Newton to find the intercepts."
    )

    faithful_score = calculate_token_overlap(mock_faithful_answer, mock_evidence)
    hallucinated_score = calculate_token_overlap(mock_hallucinated_answer, mock_evidence)

    print("=" * 55)
    print("  EduMaestro — Faithfulness Evaluator (Day 11)")
    print("=" * 55)
    print(f"\n{'Evidence':>15}: {mock_evidence}")
    print()
    print(f"{'Faithful ans':>15}: {mock_faithful_answer}")
    print(f"{'Overlap score':>15}: {faithful_score:.2%}  [PASS]")  
    print()
    print(f"{'Hallucinated':>15}: {mock_hallucinated_answer}")
    print(f"{'Overlap score':>15}: {hallucinated_score:.2%}  [WARN]")
    print("=" * 55)
