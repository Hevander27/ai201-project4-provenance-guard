# Provenance Guard — Planning

> Skeleton only. Milestones 1 & 2 are where you fill this in — the five design
> questions below drive every implementation decision. Vague answers here
> produce vague code later.

## Overview

_1–2 paragraph architecture narrative: the path a single piece of text takes
from POST /submit → signal 1 → signal 2 → confidence scoring → transparency
label → audit log → response. (Milestone 1.)_

## Architecture

```
TODO (Milestone 1): ASCII diagram of the two flows.

Submission flow:
  POST /submit --(raw text)--> [Signal 1: LLM judge] --(P_ai)--\
                          \--> [Signal 2: stylometric] --(P_ai)-> [combine] --(confidence)-->
                                          [attribution + label] --> [audit log] --> JSON response

Appeal flow:
  POST /appeal --(content_id, reasoning)--> [status = under_review] --> [audit log] --> JSON response
```

_2–3 sentence narrative describing the submission and appeal flows._

## Detection Signals

_Q1. Your 2+ signals: what each measures, output shape (0–1 score), and how you
combine them. What can each signal NOT capture (its blind spot)?_

- **Signal 1 — LLM-as-judge (Groq):**
- **Signal 2 — Stylometric heuristics:**
- **Combination:**

## Uncertainty Representation

_Q2. What does confidence 0.6 mean to your system? How do raw signal outputs map
to a calibrated score? What thresholds separate likely_ai / uncertain /
likely_human? (These become AI_THRESHOLD / HUMAN_THRESHOLD in config.py.)_

## Transparency Label Design

_Q3. The exact verbatim text of all three variants. Write them here first._

| Variant | Condition | Exact label text |
| --- | --- | --- |
| High-confidence AI | `confidence >= AI_THRESHOLD` | _TODO_ |
| High-confidence human | `confidence <= HUMAN_THRESHOLD` | _TODO_ |
| Uncertain | in between | _TODO_ |

## Appeals Workflow

_Q4. Who can appeal, what they provide, what the system does (status change +
what gets logged), and what a reviewer sees in the appeal queue._

## Anticipated Edge Cases

_Q5. At least two SPECIFIC failure scenarios (not "inaccurate detection") —
e.g. a repetitive, simple-vocabulary poem the stylometrics may misread as AI._

1.
2.

## AI Tool Plan

_For M3, M4, M5: which spec sections + the diagram you'll hand the AI tool, what
you'll ask it to generate, and how you'll verify the output._

- **M3 (submission endpoint + signal 1):**
- **M4 (signal 2 + confidence scoring):**
- **M5 (production layer: labels, appeals, rate limiting, audit log):**
