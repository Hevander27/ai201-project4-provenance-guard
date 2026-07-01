"""Confidence scoring: combine the two signals into one calibrated number,
then map that number to a coarse attribution category.

`confidence` == P(AI-generated), in [0.0, 1.0]. The weighting method and the
thresholds are DESIGN DECISIONS (Milestones 2 & 4) — the values live in
config.py and are justified in planning.md / README.
"""

from config import (
    AI_THRESHOLD,
    HUMAN_THRESHOLD,
    LLM_WEIGHT,
    STYLOMETRIC_WEIGHT,
)


def combine(llm_score: float, stylometric_score: float) -> float:
    """Fold both signal scores into a single confidence in [0,1].

    PLACEHOLDER method: normalized weighted average. Revisit in Milestone 4 —
    e.g. you might weight the LLM more, or damp the combined score toward 0.5
    when the two signals strongly disagree (honest uncertainty).
    """
    total = LLM_WEIGHT + STYLOMETRIC_WEIGHT
    combined = (LLM_WEIGHT * llm_score + STYLOMETRIC_WEIGHT * stylometric_score) / total
    return round(max(0.0, min(1.0, combined)), 3)


def attribution(confidence: float) -> str:
    """Map a confidence score to one of three categories.

    Returns "likely_ai" | "uncertain" | "likely_human".
    """
    if confidence >= AI_THRESHOLD:
        return "likely_ai"
    if confidence <= HUMAN_THRESHOLD:
        return "likely_human"
    return "uncertain"
