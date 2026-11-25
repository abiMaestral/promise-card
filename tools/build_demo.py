"""Build the public site: one self-contained page (try-it tool + anonymised cards + results).

  python tools/build_demo.py runs/run1_2026-11-25/cards_v1.0.1 -> docs/index.html (GitHub Pages)

Provider names, URLs, e-mails and phone numbers are replaced in every quote. Friends' documents
(FA, FB) are left out of the public page.
"""
import csv, html, json, re, sys
from pathlib import Path

CARDS = Path(sys.argv[1])
EXCLUDE = {"FA", "FB"}
TITLES = {
 "P01": "Pay-after-placement business analytics course", "P05": "Placement consultancy terms (fee = one month's salary)",
 "P06": "Placement-guarantee training programme", "P07b": "AI internship tracks (free / paid)",
 "P08b": "Pay-after-placement job consultancy", "P09": "Placement agency terms and fee policy",
 "P13": "Engineering course with placement protection", "L01b": "IT certification provider: terms of use",
 "L05": "Full-stack course: money-back guarantee", "L06": "Full-stack course FAQ (same provider as L05)",
 "L07": "Digital-marketing course: guaranteed placement policy", "L08": "Job-guarantee programme policy",
 "L09": "Data-science institute: placement guarantee", "L10": "Training academy: terms and conditions",
 "L11": "Course provider: refund policy", "L12": "Marketing course: salary floor or 60% refund (blog)",
 "L13b": "Cloud course: placement-guarantee package", "L14": "Skills platform: refund policy",
 "L15": "University placement-assistance terms", "L19": "Internship FAQ, brand A",
 "L20": "Internship FAQ, brand B", "L22": "Training-cum-guaranteed internship form",
 "L26": "DevOps pay-after-placement programme document",
}
BRANDS = "|".join(l.strip() for l in Path("data/private_brands.txt").read_text(encoding="utf-8").splitlines() if l.strip())  # private, not in git
RX = [(re.compile(r"https?://\S+|www\.\S+", re.I), "[link]"), (re.compile(r"\S+@\S+\.\w+"), "[email]"),
      (re.compile(r"\+?\d[\d -]{8,}\d"), "[phone]"), (re.compile(r"\b(?:" + BRANDS + r")\b", re.I), "[Provider]")]


def red(t: str) -> str:
    for rx, rep in RX:
        t = rx.sub(rep, t)
    return t


labels = {r["offer_id"]: r for r in csv.DictReader(open("data/labels.csv", encoding="utf-8"))}
data = []
for p in sorted(CARDS.glob("*.json")):
    c = json.loads(p.read_text(encoding="utf-8"))
    oid = c["offer_id"]
    if oid in EXCLUDE:
        continue
    data.append({
        "id": oid, "title": TITLES[oid], "ptype": c["promise_type"],
        "rejected": len(c["rejected_quotes"]),
        "fields": [{"f": f["field"], "s": f["state"], "v": red(f["value"]),
                    "q": [red(q["text"]) for q in f["quotes"]],
                    "n": f["notes"], "h": labels[oid][f["field"] + "_state"]} for f in c["fields"]],
    })
order = {"P": 0, "L": 1}
data.sort(key=lambda d: (order[d["id"][0]], d["id"]))
RESULTS = [["Me, re-labelling 10 offers a day later (80 answers)", "81.0%", "0.72"],
           ["AI alone (Gemini 3.5 Flash-Lite)", "66.0%", "0.49"],
           ["AI + code checks (rules as first frozen)", "64.5%", "0.48"],
           ["AI + code checks (one bug fixed)", "68.5%", "0.54"]]
extra = Path("runs/extra_results.json")
if extra.exists():
    RESULTS += json.loads(extra.read_text(encoding="utf-8"))
guide = Path("promise_card/guide_for_model.md").read_text(encoding="utf-8")
sample = Path("tests/fixtures/L20.txt").read_text(encoding="utf-8")
sample = "\n".join(re.sub(r"^[^\w(\[\"]+", "", l) for l in sample.splitlines() if not l.startswith("#"))  # drop OCR icon glyphs
page = (Path("site/template.html").read_text(encoding="utf-8")
        .replace("/*DATA*/[]", json.dumps(data, ensure_ascii=False))
        .replace("/*RESULTS*/[]", json.dumps(RESULTS, ensure_ascii=False))
        .replace('/*SAMPLE*/""', json.dumps("Sample: a real internship FAQ, name hidden.\n\n" + sample, ensure_ascii=False))
        .replace('/*GUIDE*/""', json.dumps(guide, ensure_ascii=False)))
Path("docs/index.html").write_text(page, encoding="utf-8")
Path("docs/.nojekyll").write_text("")
leak = re.findall(r"\b(?:" + BRANDS + r")\b", page, re.I)
print(f"{len(data)} cards written; brand names left in page: {len(leak)}")
