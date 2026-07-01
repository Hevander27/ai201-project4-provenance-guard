"""Transparency label generation.

The label is what a *reader* on the platform sees. It must state the attribution
result in plain language and make the confidence meaningful to a non-technical
person. There are exactly three variants.

DESIGN DECISION: the verbatim text of all three variants must appear in
planning.md AND the README (it's graded from there). Write it there first, then
paste the final wording into LABELS below so code and docs match.
"""

# Finalized label text (planning.md, Milestone 2 — "direct & concise" tone).
# `{ai}` = round(confidence * 100); `{human}` = 100 - {ai}. The percentage makes
# the confidence meaningful to a reader; the "likely_ai" wording says "signals
# of" rather than accusing, per the false-positive asymmetry.
LABELS = {
    "likely_ai": (
        "⚠️ Likely AI-generated ({ai}% confidence). "
        "This text shows strong signals of AI authorship."
    ),
    "likely_human": (
        "✅ Likely human-written ({human}% confidence). "
        "No strong signals of AI authorship were found."
    ),
    "uncertain": (
        "❓ Attribution uncertain ({ai}% estimated AI). "
        "Our signals are mixed, so this result is inconclusive."
    ),
}


def make_label(attribution: str, confidence: float) -> str:
    """Return the reader-facing label text for a given attribution.

    The confidence percentage is interpolated into the text so 0.51 and 0.95
    read differently to a non-technical reader.
    """
    ai_pct = round(confidence * 100)
    human_pct = 100 - ai_pct
    template = LABELS.get(attribution, LABELS["uncertain"])
    return template.format(ai=ai_pct, human=human_pct)
