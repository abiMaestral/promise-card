"""Error analysis of one extraction run against the hand labels.

  python tools/analyse_run.py runs/run1_2026-11-25  -> prints tables, writes <run>/analysis.json

Compares three things per field: the hand label, the model's raw state, and the state after the
code checks. That separates what the model got wrong from what the checks changed.
"""
import csv, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from promise_card.__main__ import load_offers
from promise_card.evaluate import kappa
from promise_card.pipeline import build_card
from promise_card.schema import FieldName

run = Path(sys.argv[1])
labels = {r["offer_id"]: r for r in csv.DictReader(open("data/labels.csv", encoding="utf-8")) if r["in_eval"] == "yes"}
gaps = set(json.loads(Path("data/evidence_gaps.json").read_text()))
offers = load_offers()
raw_p, fin_p, changes, rej, quotes = [], [], Counter(), 0, 0
per_field = {f.value: [] for f in FieldName}
rows = []
for oid, lab in labels.items():
    ext = json.loads((run / f"{oid}.json").read_text(encoding="utf-8"))
    title, docs = offers[oid]
    card = build_card(oid, title, docs, ext)
    raw = {f["field"]: f.get("state") for f in ext["fields"]}
    rej += len(card.rejected_quotes); quotes += len(card.rejected_quotes) + sum(len(f.quotes) for f in card.fields)
    for f in FieldName:
        g, r, c = lab[f"{f.value}_state"], raw.get(f.value, "not_stated"), card.field(f).state.value
        raw_p.append((g, r)); fin_p.append((g, c)); per_field[f.value].append((g, r, c))
        if r != c:
            changes[("helped" if c == g and r != g else "hurt" if r == g and c != g else "neutral", r, c)] += 1
        rows.append([oid, f.value, g, r, c, "gap" if f"{oid}.{f.value}" in gaps else ""])
acc = lambda p: sum(a == b for a, b in p) / len(p)
out = {
    "raw_model_accuracy": acc(raw_p), "raw_model_kappa": kappa(raw_p),
    "after_checks_accuracy": acc(fin_p), "after_checks_kappa": kappa(fin_p),
    "code_changes": {f"{k[0]}: {k[1]} -> {k[2]}": v for k, v in sorted(changes.items())},
    "quotes_total": quotes, "quotes_rejected": rej,
    "per_field": {k: {"raw": acc([(g, r) for g, r, _ in v]), "final": acc([(g, c) for g, _, c in v])} for k, v in per_field.items()},
    "label_distribution": dict(Counter(g for g, _ in fin_p)),
    "model_distribution_final": dict(Counter(c for _, c in fin_p)),
}
(run / "analysis.json").write_text(json.dumps(out, indent=2))
with open(run / "field_level.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["offer", "field", "label", "model_raw", "after_checks", "evidence_gap"]); w.writerows(rows)
print(json.dumps(out, indent=2))
