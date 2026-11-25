"""Find disagreements between quotes for the same field.

Deliberately narrow: two quotes for the same field contradict if they state different
amounts of the same kind (rupees, percent, LPA, days/months, counts of interviews).
Wording-level conflicts (e.g. "self-application counts" vs "excluded") are left to the
extractor's `contradictory` state, which must cite both quotes.
"""
from __future__ import annotations

import re
from itertools import combinations

from .schema import Contradiction, FieldResult, Quote

_NUM = r"(\d[\d,]*(?:\.\d+)?)"
KINDS = {
    "rupees": re.compile(r"(?:rs\.?|₹|inr)\s*" + _NUM + r"(?:\s*(lakh|lac|k)\b)?", re.I),
    "lpa": re.compile(_NUM + r"\s*(?:-|to)?\s*(?:\d[\d.]*)?\s*lpa", re.I),
    "percent": re.compile(_NUM + r"\s*%"),
    "duration": re.compile(_NUM + r"\s*(day|week|month|year)s?\b", re.I),
    "interviews": re.compile(_NUM + r"\s*interviews?", re.I),
}


def _val(num: str, unit: str | None = None) -> float:
    v = float(num.replace(",", ""))
    if unit:
        u = unit.lower()
        v *= {"lakh": 1e5, "lac": 1e5, "k": 1e3}.get(u, 1)
    return v


def amounts(text: str) -> dict[str, set[float]]:
    out: dict[str, set[float]] = {}
    for kind, rx in KINDS.items():
        for m in rx.finditer(text):
            if kind == "rupees":
                out.setdefault(kind, set()).add(_val(m.group(1), m.group(2)))
            elif kind == "duration":
                n, unit = _val(m.group(1)), m.group(2).lower()
                out.setdefault(f"duration_{unit}", set()).add(n)
            else:
                out.setdefault(kind, set()).add(_val(m.group(1)))
    return out


def find(field: FieldResult) -> list[Contradiction]:
    """Pairs of verified quotes, from different documents, for one field whose same-kind amounts are disjoint."""
    found = []
    qs = [q for q in field.quotes if q.verified]
    for a, b in combinations(qs, 2):
        if a.doc_id == b.doc_id:
            continue  # tiers in one document (e.g. Rs 1499 non-tech / Rs 9999 tech) are not conflicts
        aa, bb = amounts(a.text), amounts(b.text)
        for kind in set(aa) & set(bb):
            if aa[kind].isdisjoint(bb[kind]):
                found.append(Contradiction(field=field.field, a=a, b=b,
                                           reason=f"different {kind}: {sorted(aa[kind])} vs {sorted(bb[kind])}"))
                break
    return found
