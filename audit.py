"""Structured audit log (JSON Lines).

Adapted directly from the RepairSafe reference `auditor.py`:
  - ISO-8601 UTC timestamps
  - creates the log directory if missing
  - one JSON object per line, append-only (works with Splunk/Datadog/etc.)
  - a one-line console summary so you can watch events in real time

Extended for Project 4 with `read_log()` (backing the GET /log endpoint) and a
`find_latest()` helper the appeals workflow uses to look up the original
decision for a content_id.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from config import LOG_FILE


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def log_event(entry: dict) -> None:
    """Append one structured record to the audit log.

    `entry` is a plain dict; a UTC `timestamp` is added if not already present.
    Every /submit classification and every /appeal should call this.
    """
    entry.setdefault("timestamp", _timestamp())

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    cid = str(entry.get("content_id", "?"))[:8]
    print(
        f"[LOGGED] status={entry.get('status', '?')} "
        f"| content_id={cid} "
        f"| confidence={entry.get('confidence', '-')}"
    )


def read_log(limit: int = 20) -> list:
    """Return the most recent `limit` entries, newest first (for GET /log)."""
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []
    entries = [json.loads(line) for line in lines if line.strip()]
    return list(reversed(entries[-limit:]))


def find_latest(content_id: str) -> dict | None:
    """Return the most recent log entry for a content_id, or None.

    Used by the appeals workflow to attach the original classification to the
    appeal record. (Append-only log: an "update" is a new entry, not an edit.)
    """
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None
    for line in reversed(lines):
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry.get("content_id") == content_id:
            return entry
    return None
