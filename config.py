"""Central configuration for Provenance Guard.

Mirrors the RepairSafe reference `config.py` pattern (dotenv + Groq model
constant), extended with the confidence thresholds and signal weights that
Project 4 needs. The values below are the design decisions from planning.md
(the reasoning lives there and in the README).
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- Groq (Detection Signal 1) -------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"  # free tier, same as Projects 1-3

# --- Audit log -----------------------------------------------------------------
LOG_FILE = "logs/audit.jsonl"

# --- Confidence model ----------------------------------------------------------
# Convention: `confidence` == P(content is AI-generated), in [0.0, 1.0].
#   0.0 -> certainly human   |   1.0 -> certainly AI
#
# "Protect humans" stance (planning.md, Milestone 2): a false positive (calling
# a human's work "AI") is the costly error, so the AI threshold is demanding and
# the uncertain band is wide. Borderline formal-human text lands in "uncertain"
# rather than being accused.
AI_THRESHOLD = 0.75     # confidence >= this  -> "likely_ai"
HUMAN_THRESHOLD = 0.40  # confidence <= this  -> "likely_human"
#                          in between          -> "uncertain"

# Signal weights for combining the two signals (planning.md, Milestone 4).
# The LLM signal is the stronger holistic detector; stylometrics is an
# independent structural cross-check.
LLM_WEIGHT = 0.6
STYLOMETRIC_WEIGHT = 0.4

# Statuses a piece of content can hold in the audit trail.
VALID_STATUSES = {"classified", "under_review"}
