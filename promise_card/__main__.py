"""CLI.

  python -m promise_card build  --offer L22 [--backend cached|gemini|anthropic] [--model NAME]
  python -m promise_card build  --all --backend gemini
  python -m promise_card eval   --labels data/labels.csv

Offers are listed in data/offers.csv (one row per source document):
  offer_id,title,doc_id,source_file,url,evidence_type,checked_on
source_file is a .txt under data/sources/ (make it with tools/pdf_to_text.py).
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from .evaluate import compare, load_labels
from .extract import extract
from .pipeline import build_card
from .render import render
from .schema import Card, SourceDoc

DATA = Path("data")


def load_offers(path: Path = DATA / "offers.csv") -> dict[str, tuple[str, list[SourceDoc]]]:
    offers: dict[str, tuple[str, list[SourceDoc]]] = {}
    groups: dict[str, list[dict]] = defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            groups[r["offer_id"]].append(r)
    for oid, rows in groups.items():
        docs = [SourceDoc(doc_id=r["doc_id"], url=r.get("url", ""), evidence_type=r.get("evidence_type", ""),
                          checked_on=r.get("checked_on", ""),
                          text=(DATA / "sources" / r["source_file"]).read_text(encoding="utf-8"))
                for r in rows if (DATA / "sources" / r["source_file"]).exists()]
        if docs:
            offers[oid] = (rows[0]["title"], docs)
    return offers


def main() -> None:
    ap = argparse.ArgumentParser(prog="promise_card")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--offer")
    b.add_argument("--all", action="store_true")
    b.add_argument("--backend", default="cached")
    b.add_argument("--model")
    b.add_argument("--prompt", default="v1", choices=["v1", "guide"])
    b.add_argument("--run", default="", help="name of a run folder; keeps runs apart, e.g. run2a")
    ev = sub.add_parser("eval")
    ev.add_argument("--labels", default=str(DATA / "labels.csv"))
    ev.add_argument("--run", default="")
    a = ap.parse_args()

    offers = load_offers()
    ext_dir = DATA / "extractions" / a.run if a.run else DATA / "extractions"
    out = DATA / "cards" / a.run if a.run else DATA / "cards"
    out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "build":
        ids = list(offers) if a.all else [a.offer]
        if a.backend != "cached" and a.all:     # resume: skip offers already extracted
            done = [o for o in ids if (ext_dir / f"{o}.json").exists()
                    and "_backend" in (ext_dir / f"{o}.json").read_text(encoding="utf-8")]
            if done:
                print(f"skipping {len(done)} already extracted: {', '.join(done)}")
            ids = [o for o in ids if o not in done]
        for oid in ids:
            title, docs = offers[oid]
            try:
                ext = extract(oid, docs, a.backend, a.model, ext_dir, a.prompt)
            except Exception as exc:  # noqa: BLE001  keep going; report at the end
                print(f"{oid}: FAILED ({exc})")
                continue
            card = build_card(oid, title, docs, ext)
            (out / f"{oid}.json").write_text(card.model_dump_json(indent=2), encoding="utf-8")
            (out / f"{oid}.html").write_text(render(card), encoding="utf-8")
            states = ", ".join(f"{f.field.value}={f.state.value}" for f in card.fields)
            print(f"{oid}: {states}; rejected quotes={len(card.rejected_quotes)}")
    else:
        cards = {p.stem: Card.model_validate_json(p.read_text(encoding="utf-8")) for p in out.glob("*.json")}
        gp = DATA / "evidence_gaps.json"
        gaps = set(json.loads(gp.read_text())) if gp.exists() else set()
        print(json.dumps(compare(cards, load_labels(Path(a.labels)), gaps), indent=2))


if __name__ == "__main__":
    main()
