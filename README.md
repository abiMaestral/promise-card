# Placement Promise Card

**Abishikth Ebenezer** · built for the ATRISI Amplify Builder Challenge · November 2026

Paid placement, internship and "job guarantee" offers in India describe what they promise in very different
ways, and much of what a candidate needs to know is vague, missing, contradictory, or kept in a document
shown only after payment. This project asks:

> **Can a candidate see, before paying, what a placement offer actually commits to, and can a language
> model be trusted to show it?**

A **Promise Card** answers eight questions about an offer (what you pay, when, what is promised, the
conditions, whether terms can change, what happens if you are not placed, whether you can refuse an offer,
and whether terms are kept elsewhere). Each answer is marked **stated, vague, contradictory, not stated** or
**not applicable**, with an exact quote. The card never judges whether an offer is fair, legal or genuine.

**Live site:** https://abiMaestral.github.io/promise-card/ (the `docs/` folder, served by GitHub Pages)

- **Check an offer:** paste any offer's terms. With no key, the page finds amounts, open-ended wording and
  pointers to hidden documents, in your browser. With your own free Gemini key, it drafts the full card, and
  every quote the AI returns is checked against your text before it is shown.
- **23 real offers:** AI-drafted cards for 23 of the offers I collected (provider names hidden), with a toggle
  to compare each answer with my hand label.
- **How well it works:** the numbers below.

## Results (25 offers, 200 decisions)

| | Agreement with hand labels | Cohen's κ |
|---|---|---|
| Hand labeller vs own re-labels (10 offers, 80 decisions) | 81.0% | 0.72 |
| Model alone (Gemini 3.5 Flash-Lite) | 66.0% | 0.49 |
| Model + code checks, rules v1.0 as frozen | 64.5% | 0.48 |
| Model + code checks, rules v1.0.1 (one bug fixed) | **68.5%** | **0.54** |
| Run 2: same, plus my full labelling guide in the prompt | 64.5% | 0.48 |

- **11 of 187 model quotes (5.9%) were not in the source**; the quote check removed all of them.
- The model's main error is calling **vague** terms **stated** (21 of 200), the same boundary where the
  human re-labels disagreed most.
- **Giving the model my labelling rules made it worse** (68.5% → 64.5%): it called even more vague terms clear.
- **0 of 5 contradictions** were found: all five are inside a single document, and the code only compares
  amounts across documents. This is the main gap.
- From the hand labels alone: total cost can be worked out for **6 of 25** offers; qualifying conditions are
  fully defined in **1 of 25**; **19 of 25** point to terms the candidate has not seen; **11 of 25** reserve
  the right to change terms; and **8 of ~30** terms pages changed or vanished within days of being read.

Full write-up: [`docs/findings_draft.md`](docs/findings_draft.md). The bug found during evaluation and its fix:
[`docs/rules_changelog.md`](docs/rules_changelog.md).

## How it works

```
saved evidence (PDF / screenshot)  →  text (pdftotext, OCR corrected by eye)
  → LLM extraction: 8 fields, each with a state and verbatim quotes        promise_card/extract.py
  → quote check: a quote not found in its source is removed;               promise_card/quote_check.py
      an answer left without evidence becomes "not stated"
  → clause rules: open-ended wording ("based on performance",              promise_card/clauses.py
      "may be amended", "(e.g., 7 days)") turns "stated" into "vague"
  → cross-document check: different amounts for one field → contradictory  promise_card/contradictions.py
  → card (HTML)                                                            promise_card/render.py
  → evaluation against hand labels                                         promise_card/evaluate.py
```

Code may only make an answer **less** certain than the model claimed, never more.

## Method in brief

1. **Collect** (20–23 Nov): 17 pilot offers and 29 leads from provider pages, provider PDFs, public uploads and
   reports; two letters from friends. Each source verified by eye against the live page; 25 offers that take a
   fee *and* promise an outcome were kept for evaluation.
2. **Freeze** the schema, the five states, the clause phrase list and a labelling guide (23 Nov), before any
   model output was seen.
3. **Hand-label** all 25 offers from the saved evidence (24 Nov). 303 of 311 label quotes are found word for
   word in the saved evidence; the 5 fields whose quote is not are scored separately.
4. **Run** the model once per offer, temperature 0, same prompt (25 Nov).
5. **Evaluate**: accuracy and κ per field, a confusion table, quote fidelity, the effect of each check, and a
   blind re-label of 10 random offers to measure the labeller's own consistency.

## Reproduce

```bash
pip install -r requirements.txt
python -m pytest -q
python -m promise_card build --all --backend gemini --model gemini-3.5-flash-lite   # needs GEMINI_API_KEY
python -m promise_card eval --labels data/labels.csv
python tools/analyse_run.py runs/<run>
python tools/build_demo.py runs/<run>/cards_v1.0.1      # rebuilds docs/index.html
```

The evidence, source texts, labels and model outputs contain provider and private documents, so they are not
in this repository (see `.gitignore`); the scores are in `runs/run1_2026-11-25/`.

## Limitations

25 offers and one labeller; offers found by search and through friends, not sampled at random; pages
captured on one or two days; one model run; image text read by OCR and corrected by eye. The card measures
how clearly terms are written, not whether an offer is fair, legal or genuine.
