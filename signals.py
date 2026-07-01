"""Detection signals for Provenance Guard.

Two INDEPENDENT signals, each returning P(AI-generated) in [0.0, 1.0]:

  Signal 1 - llm_signal()          Groq LLM-as-judge. Semantic/holistic read of
                                   whether the text sounds human or AI. This is
                                   the same LLM-as-judge pattern as RepairSafe's
                                   classify_safety_tier(), re-aimed at attribution.
                                   -> Milestone 3

  Signal 2 - stylometric_signal()  Pure-Python structural statistics (sentence
                                   length variance, vocabulary diversity,
                                   punctuation density). No API call. AI prose
                                   tends to be more uniform; human prose varies.
                                   -> Milestone 4

The DESIGN DECISIONS (the judge prompt + its output format, which metrics to
use and how to fold them into one score) belong in planning.md first. The
`TODO`s below mark exactly where those decisions plug in. Everything else --
the Groq call, graceful fallback, metric math -- is ready to run.
"""

from __future__ import annotations

import re
import statistics

from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL

# Lazy-safe client: if there's no key yet, the app still runs and the signal
# returns a neutral 0.5 instead of crashing on import.
_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# =============================================================================
# Signal 1 — LLM-as-judge (Groq)                                    [Milestone 3]
# =============================================================================

def llm_signal(text: str) -> dict:
    """Ask the LLM how likely `text` is AI-generated.

    Returns {"score": float in [0,1] (P(AI)), "reason": str}.
    """
    if _client is None:
        return {"score": 0.5, "reason": "No GROQ_API_KEY set; neutral fallback."}

    # TODO (M3): design this prompt + a parseable output format in planning.md.
    # Reference pattern: RepairSafe's classify_safety_tier() asked for a tier +
    # reason and parsed them out. Here, ask for a probability + reason instead.
    system_prompt = (
        "PLACEHOLDER — write your AI-detection judge prompt in planning.md, "
        "then paste it here. It should make the model output a probability that "
        "the text is AI-generated, plus a one-line reason, in a format you parse."
    )

    try:
        resp = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0,
        )
        raw = resp.choices[0].message.content.strip()
        score, reason = _parse_llm_output(raw)
        return {"score": score, "reason": reason}
    except Exception as exc:  # network / parse / auth — fail to neutral, never crash
        return {"score": 0.5, "reason": f"LLM error, neutral fallback: {exc}"}


def _parse_llm_output(raw: str) -> tuple[float, str]:
    """Pull a 0..1 probability and a reason out of the model's reply.

    TODO (M3): tighten this to match the exact output format you design. This
    placeholder just grabs the first decimal it finds and clamps it to [0,1].
    """
    match = re.search(r"(\d*\.\d+|\d+)", raw)
    score = float(match.group(1)) if match else 0.5
    score = max(0.0, min(1.0, score))
    return score, raw


# =============================================================================
# Signal 2 — Stylometric heuristics (pure Python)                   [Milestone 4]
# =============================================================================

def stylometric_signal(text: str) -> dict:
    """Structural statistics of the text. No API call.

    Returns {"score": float in [0,1] (P(AI)), "metrics": {...}}.
    The raw metrics are computed for you; how you MAP them to a single score is
    the Milestone 4 design decision.
    """
    metrics = compute_metrics(text)

    # TODO (M4): combine `metrics` into one P(AI) score per planning.md.
    # Intuition to encode: LOW sentence-length variance + LOW type-token ratio
    # (repetitive, uniform) leans AI; high variance / rich vocabulary leans human.
    score = 0.5  # PLACEHOLDER
    return {"score": score, "metrics": metrics}


def compute_metrics(text: str) -> dict:
    """Compute a few interpretable stylometric features (starting set)."""
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_lengths = [len(re.findall(r"\b\w+\b", s)) for s in sentences]

    word_count = len(words)
    unique_words = len(set(words))

    return {
        "word_count": word_count,
        "sentence_count": len(sentences),
        # Vocabulary diversity: unique / total. Lower can indicate repetition.
        "type_token_ratio": round(unique_words / word_count, 3) if word_count else 0.0,
        # Burstiness: humans mix short and long sentences; AI is often uniform.
        "sentence_length_variance": (
            round(statistics.pvariance(sentence_lengths), 3)
            if len(sentence_lengths) > 1 else 0.0
        ),
        "avg_sentence_length": (
            round(statistics.mean(sentence_lengths), 2) if sentence_lengths else 0.0
        ),
        # Punctuation density: variety/rate of punctuation per word.
        "punctuation_density": (
            round(len(re.findall(r"[,;:\-—()\"']", text)) / word_count, 3)
            if word_count else 0.0
        ),
    }
