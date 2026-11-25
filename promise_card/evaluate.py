"""Compare cards with hand labels.

Labels file (CSV, one row per offer) has columns <field>_state for each of the eight
fields, e.g. total_cost_state, plus promise_type. Rows with an empty offer_id or with
in_eval != "yes" are skipped.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .schema import Card, FieldName, State

STATES = [s.value for s in State]


def load_labels(path: Path) -> dict[str, dict[str, str]]:
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("offer_id") and r.get("in_eval", "yes").strip().lower() == "yes":
                rows[r["offer_id"]] = r
    return rows


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def compare(cards: dict[str, Card], labels: dict[str, dict[str, str]], gaps: set[str] | None = None) -> dict:
    """gaps: 'OFFER.field' keys whose hand-label quote is not in the saved evidence (data/evidence_gaps.json).
    They are scored, and also reported separately, because the model cannot see that text."""
    gaps = gaps or set()
    clean_pairs: list[tuple[str, str]] = []
    pairs_by_field: dict[str, list[tuple[str, str]]] = {f.value: [] for f in FieldName}
    confusion: Counter = Counter()
    ptype = []
    quotes_total = quotes_ok = 0
    for oid, lab in labels.items():
        card = cards.get(oid)
        if not card:
            continue
        for f in FieldName:
            gold = (lab.get(f"{f.value}_state") or "").strip()
            if gold not in STATES:
                continue
            pred = card.field(f).state.value
            pairs_by_field[f.value].append((gold, pred))
            if f"{oid}.{f.value}" not in gaps:
                clean_pairs.append((gold, pred))
            confusion[(gold, pred)] += 1
        if lab.get("promise_type"):
            ptype.append((lab["promise_type"].strip(), card.promise_type.value))
        quotes_ok += sum(len(fr.quotes) for fr in card.fields)
        quotes_total += sum(len(fr.quotes) for fr in card.fields) + len(card.rejected_quotes)
    all_pairs = [p for ps in pairs_by_field.values() for p in ps]
    return {
        "offers": len({o for o in labels if o in cards}),
        "field_decisions": len(all_pairs),
        "state_accuracy": sum(a == b for a, b in all_pairs) / len(all_pairs) if all_pairs else None,
        "state_kappa": kappa(all_pairs),
        "state_accuracy_evidence_complete": (sum(a == b for a, b in clean_pairs) / len(clean_pairs)) if clean_pairs else None,
        "fields_excluded_for_evidence_gaps": len(all_pairs) - len(clean_pairs),
        "per_field_accuracy": {k: (sum(a == b for a, b in v) / len(v) if v else None)
                               for k, v in pairs_by_field.items()},
        "promise_type_accuracy": (sum(a == b for a, b in ptype) / len(ptype)) if ptype else None,
        "quote_fidelity": quotes_ok / quotes_total if quotes_total else None,
        "confusion": {f"{g} -> {p}": n for (g, p), n in sorted(confusion.items())},
    }
