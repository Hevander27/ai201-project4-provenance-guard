"""Provenance Guard — Flask API.

Endpoints (the contract every other file implements against):

  POST /submit   accepts {"text": ..., "creator_id": ...}
                 -> runs signal 1 + signal 2 -> combines -> labels -> logs
                 -> returns {content_id, attribution, confidence, label}
                 rate-limited.

  POST /appeal   accepts {"content_id": ..., "creator_reasoning": ...}
                 -> sets status "under_review", logs alongside the original
                 -> returns confirmation.

  GET  /log      returns the most recent audit entries as JSON (for grading
                 visibility; in production this would require auth).

The full pipeline runs end-to-end: two detection signals -> combined confidence
-> attribution + transparency label -> audit log, plus the appeal workflow and
per-IP rate limiting.
"""

import uuid

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from audit import find_latest, log_event, read_log
from labels import make_label
from scoring import attribution, combine
from signals import llm_signal, stylometric_signal

app = Flask(__name__)

# Flask-Limiter >= 3.x requires storage_uri. memory:// resets on restart — fine
# for this project. get_remote_address keys the limit per client IP.
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/")
def home():
    return "Provenance Guard is running."


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")  # limits justified in README
def submit():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text:
        return jsonify({"error": "Missing required field 'text'."}), 400

    content_id = str(uuid.uuid4())

    # --- Detection pipeline ---------------------------------------------------
    s1 = llm_signal(text)             # Signal 1: LLM-as-judge (Groq)
    s2 = stylometric_signal(text)     # Signal 2: stylometric heuristics
    confidence = combine(s1["score"], s2["score"])
    attr = attribution(confidence)
    label = make_label(attr, confidence)

    # --- Audit log ------------------------------------------------------------
    log_event({
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attr,
        "confidence": confidence,
        "llm_score": s1["score"],
        "stylometric_score": s2["score"],
        "signals": ["llm_judge", "stylometric"],
        "status": "classified",
    })

    return jsonify({
        "content_id": content_id,
        "attribution": attr,
        "confidence": confidence,
        "label": label,
    })


@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json(silent=True) or {}
    content_id = data.get("content_id")
    reasoning = data.get("creator_reasoning")

    if not content_id:
        return jsonify({"error": "Missing required field 'content_id'."}), 400

    # Attach the original decision to the appeal record for the reviewer.
    original = find_latest(content_id)

    log_event({
        "content_id": content_id,
        "status": "under_review",
        "appeal_reasoning": reasoning,
        "original_attribution": (original or {}).get("attribution"),
        "original_confidence": (original or {}).get("confidence"),
    })

    return jsonify({
        "content_id": content_id,
        "status": "under_review",
        "message": "Your appeal was received and is under review.",
    })


@app.route("/log", methods=["GET"])
def view_log():
    return jsonify({"entries": read_log()})


if __name__ == "__main__":
    # debug=True auto-reloads on save while you build.
    app.run(port=5000, debug=True)
