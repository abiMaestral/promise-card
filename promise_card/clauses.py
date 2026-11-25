"""Rule-based flags for open-ended and deferred clauses.

The phrase list is frozen with the schema (v1.0). Each pattern was seen in at least one
verified source during Days 1-2; the comment names it. Changes go in docs/rules_changelog.md.
"""
from __future__ import annotations

import re

from .schema import ClauseHit, SourceDoc

# (label, regex) - open-ended: the provider keeps room to change or add terms
OPEN_ENDED = [
    ("from time to time", r"from time to time"),                       # FB letter, L15 s2.2
    ("may be amended/modified", r"\bmay (?:be )?(?:amend|modif|revis|chang|updat)\w*"),
    ("subject to change", r"subject to (?:change|revision|modification)"),  # FA
    ("as may be communicated", r"as may be (?:communicated|notified|decided|informed)"),  # P13
    ("additional conditions", r"(?:any )?additional (?:conditions|terms|criteria)"),  # pilot row 12
    ("sole discretion", r"(?:sole|absolute) discretion"),
    ("subject to T&C", r"subject to (?:the )?(?:t\s*&\s*c|terms and conditions|terms & conditions)"),  # L08
    ("e.g. / such as (in a term)", r"\(e\.g\.,?[^)]*\)"),                # L14 "(e.g., 7 days ...)"
    ("typically/usually", r"\b(?:typically|usually|generally)\b"),     # P01 "typically Rs 3 LPA"
    ("continued use = acceptance", r"continued use[^.]{0,80}accept"),   # L15 s2.2
    # undefined yardsticks: the term depends on a judgement the document never defines
    ("based on performance", r"based on (?:your )?(?:performance|merit|evaluation)"),  # L20
    ("successful completion", r"successful(?:ly)? complet\w*"),          # FB, L19, pilot row 2
]

# deferred: relevant terms live in a document the reader has not been shown
DEFERRED = [
    ("shared upon/after enrolment", r"shared[^.]{0,40}(?:upon|after|on)[^.]{0,30}(?:enrol|enroll|registration|verification|payment)"),  # L09
    ("in the offer email/letter", r"(?:in|via) the (?:offer|enrol\w*|admission) (?:email|letter|mail)"),  # L12
    ("separate policy/agreement", r"(?:separate|our|the) (?:placement|refund|isa|income share)? ?(?:policy|agreement)(?! below)"),
    ("agreement to be signed", r"(?:sign|execute)\w* (?:an?|the) (?:agreement|isa|contract)"),  # P01, L26 ISA
    ("refer to / as per", r"\b(?:refer to|as per) (?:the |our )?(?:terms|policy|agreement|document|guidelines)"),
    ("will be shared later", r"will be (?:shared|provided|communicated|sent) (?:later|separately|after|upon|on)"),
]

_OPEN = [(l, re.compile(p, re.IGNORECASE)) for l, p in OPEN_ENDED]
_DEF = [(l, re.compile(p, re.IGNORECASE)) for l, p in DEFERRED]
_SENT = re.compile(r"(?<=[.!?])\s+|\n{1,}")


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(text) if s and s.strip()]


def scan_text(text: str) -> list[tuple[str, str]]:
    """Return (kind, label) for each pattern found in a piece of text (e.g. a quote)."""
    hits = []
    for kind, pats in (("open_ended", _OPEN), ("deferred", _DEF)):
        for label, rx in pats:
            if rx.search(text):
                hits.append((kind, label))
    return hits


def scan_docs(docs: list[SourceDoc]) -> list[ClauseHit]:
    out: list[ClauseHit] = []
    for d in docs:
        for s in sentences(d.text):
            for kind, label in scan_text(s):
                out.append(ClauseHit(kind=kind, phrase=label, doc_id=d.doc_id, sentence=s[:400]))
    return out
