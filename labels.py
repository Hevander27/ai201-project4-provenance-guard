"""Transparency label generation.

The label is what a *reader* on the platform sees. It must state the attribution
result in plain language and make the confidence meaningful to a non-technical
person. There are exactly three variants.

DESIGN DECISION: the verbatim text of all three variants must appear in
planning.md AND the README (it's graded from there). Write it there first, then
paste the final wording into LABELS below so code and docs match.
"""

# TODO (M2/M5): replace these PLACEHOLDERs with your finalized label text.
# Keep in mind the assignment's asymmetry hint: a false positive (calling a
# human's work "AI") is the costly error — the "likely_ai" wording should hedge
# accordingly rather than accuse.
LABELS = {
    "likely_ai": (
        "PLACEHOLDER — high-confidence AI label. Write the exact reader-facing "
        "text in planning.md, then paste it here."
    ),
    "likely_human": (
        "PLACEHOLDER — high-confidence human label."
    ),
    "uncertain": (
        "PLACEHOLDER — uncertain label. This should read differently from the "
        "two confident variants so 0.51 != 0.95 for the reader."
    ),
}


def make_label(attribution: str, confidence: float) -> str:
    """Return the reader-facing label text for a given attribution.

    `confidence` is available if you want to interpolate the percentage into the
    text (e.g. "we're about 82% confident ...") — a nice way to surface the
    number without exposing raw signal internals.
    """
    return LABELS.get(attribution, LABELS["uncertain"])
