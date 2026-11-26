# Findings (draft, 25 Nov 2026)

*Author: Abishikth Ebenezer. Provider names are withheld in this public version; offers are referred to by ID
(P = pilot, L = lead, FA/FB = documents shared by two friends, with consent and names removed).*

## 1. What was studied

25 paid offers that promise some outcome (a job, an internship, interviews, a salary floor, or a refund)
in exchange for a fee, collected 20–24 Nov 2026 from provider pages, provider PDFs, public uploads and
two letters received by friends. Each was saved as evidence on the day it was read and hand-labelled on
eight questions a candidate should be able to answer **before paying**. Each answer got one of five states
(stated / vague / contradictory / not stated / not applicable), with the exact supporting quote.
303 of the 311 label quotes are found word for word in the saved evidence; the 5 fields whose quote
is not in the saved copy are reported separately in the evaluation.

## 2. Most of what a candidate needs to know is not clearly written down

| Question | Stated | Vague | Contradictory | Not stated | N/A |
|---|---|---|---|---|---|
| Q1 How much will I pay in total? | 6 | 17 | 2 | 0 | 0 |
| Q2 When is each payment due? | 9 | 7 | 0 | 9 | 0 |
| Q3 What exactly is promised? | 14 | 7 | 3 | 1 | 0 |
| Q4 What must I do to qualify? | 1 | 22 | 0 | 2 | 0 |
| Q5 Can terms change later? | 11 say yes | 0 | 0 | 14 | 0 |
| Q6 What if I am not placed? | 9 | 8 | 0 | 8 | 0 |
| Q7 Can I refuse an offer without losing money? | 8 | 0 | 0 | 12 | 5 |
| Q8 Are terms kept elsewhere? | 19 say yes | 0 | 0 | 6 | 0 |

- **Total cost is clear in 6 of 25**, and 4 of those 6 are small-fee internships (₹350–₹9,999).
  For the larger programmes the fee is mentioned but its amount is not on the page that makes the promise.
- **Qualifying conditions are fully defined in 1 of 25.** The rest depend on undefined yardsticks
  ("active participation", "exceptional performance", "successful completion", "a minimum number of points")
  or on instructions "communicated separately".
- **19 of 25 point to terms the candidate has not been shown**: an agreement signed after a test,
  a policy "shared upon successful enrolment and verification", an offer email, a separate placement policy,
  login details sent after payment.
- **11 of 25 reserve the right to change the terms**, several "without prior notice", one where
  "continued use … constitutes acceptance".

## 3. "Guarantee" is one word for at least eight different commitments

Main promise type across the 25 offers: refund if not placed (9), placement assistance only (5),
job offer (3), a number of interviews (2), an internship (2), a stipend (2), an "aim" (1), none on the page (1).
The same word covers "you will appear for the interviews and will get the job" (L26) and
"shall not be interpreted or deemed as a placement guarantee" (L01b) **from the same provider**.

Definitions narrow the promise in ways a headline does not show:
- two refund policies count a job the candidate finds **through their own applications**, anywhere in the world,
  as the provider's placement (L07, L08);
- a market slowdown cancels the refund in one (L07) and postpones the deadline indefinitely in another (L08);
- one refund is triggered by the absence of "tangible career benefits", never defined (L11);
- one "guarantee" adds ₹1,00,000 to the price of the same course page's "assistance" package (L13b).

## 4. Contradictions inside one offer

- Fee table vs FAQ give different drop-off fee schedules on one page (P01).
- "completely FREE OF COST for job seekers" vs a Pay-After-Placement fee on the same page (P08b).
- "Maximum 10 interviews" vs a refund if fewer than 10 are received (L06).
- "placed in a WEEK" vs "30 days Training" for tech roles (L22).
- A monthly in-hand salary of ₹23,000 vs a stipend paid only "upon successful completion of the assigned project" (FB).
- Across two documents of one provider: 60% vs 50% minimum grade, 4 LPA vs 3 LPA CTC limit,
  refund-if-no-offer vs refund-if-fewer-than-10-interviews (L05 vs L06).

## 5. Shared templates across brands

Sentence-level comparison (`tools/compare_pairs.py`):
- two internship FAQs under different brands share 7 near-identical sentences, including
  "The fee is fully reinvested in your development." (L19, L20); the same ₹350 buys 1 month in one and 3 months in the other;
- two ed-tech refund policies share 14 near-identical sentences (L07, L08);
- friend B's letter has the same salary table as a 2026 news report about a letter under a different company name,
  and links to four further brand domains; friend A's invitation PDF is titled with a third company's name in its metadata.

## 6. The evidence does not stay put

Of about 30 terms pages checked between 21 and 24 Nov, **8 changed or disappeared** within days
(404s, redirects to a homepage, a closed form, a site taken down) and 2 more were behind login walls.
One page that was labelled on 24 Nov could only be saved after its URL was corrected; collapsed FAQ
sections did not print. A candidate who does not save the page has no record of what they agreed to,
and neither of the two friends who paid had kept one.

## 7. Errors in reading these documents are easy to make

When the 17 pilot rows were first extracted with an LLM (Claude) and then checked by eye against the
live sources, 6 of the 13 checkable rows had errors: an inferred loan, a misread cheque schedule,
an unsupported "first salary" claim, a wrong refund rule, terms mixed from different pages, and a
condition read as a deadline. Lead summaries had four more (a wrong version date, a truncated URL,
"money back" for "full refund", and a claim not found on the page). This is the motivation for the
card's rule that **every field must carry a quote that code can find in the source**.

## 8. How well can a model fill in the card?

Run 1, 25 Nov 2026: Gemini 3.5 Flash-Lite (24 offers; one offer fell back to Gemini 3 Flash Preview
when the first model was overloaded), temperature 0, one call per offer, the same prompt for all.
200 field decisions (25 offers × 8 questions) compared with the hand labels.

| | Accuracy | Cohen's κ |
|---|---|---|
| Model alone | 66.0% | 0.49 |
| Model + code checks (rules v1.0, as frozen) | 64.5% | 0.48 |
| Model + code checks (rules v1.0.1, one bug fixed) | **68.5%** | **0.54** |
| v1.0.1, fields whose label quote is in the saved evidence (195) | 69.7% | |
| Run 2 (26 Nov): same model, prompt + the full labelling guide, rules v1.0.1 | 64.5% | 0.48 |

- **Quotes**: 187 quotes returned; **11 (5.9%) were not in the source** and were removed by the checker.
  Without the checker, about 1 in 17 quotes shown to a reader would have been invented or altered.
- **The checks were wrong in one way, and it was found by the evaluation.** As frozen, the rule
  "open-ended wording makes a stated answer vague" also fired on *Can terms change later?*, where
  "we may modify these Terms from time to time" **is** the clear answer (the labelling guide said so).
  It cost 7 correct answers there and 1 on *terms kept elsewhere*. v1.0.1 limits the rule to the other six
  questions; nothing else changed. Both scores are shown.
- **Where the checks helped**: turning the model's "stated" into "vague" when its own quote contained
  "based on performance", "successful completion" or similar was right 7 times out of 8 it fired
  (promise 68% → 84%, conditions 28% → 36%).
- **The model calls vague terms clear.** The commonest error is *vague → stated* (21 of 200):
  the model accepts "100% Guaranteed Placement" or "subject to the terms and conditions" as an answer.
  Next is *vague → not stated* (11): when a fee is mentioned but no amount is given, the model says the
  cost is not stated rather than vague.
- **Contradictions were not found (0 of 5).** All five are inside one document (a fee table vs an FAQ,
  "maximum 10" vs a refund below 10, "placed in a week" vs 30-day training, salary vs stipend). The model
  never used the contradictory state, and the code check only compares amounts across documents.
  This is the clearest gap.
- **Weakest question**: *What must I do to qualify?* (36%). **Strongest**: *Can terms change later?* (92%),
  *What is promised?* (84%), *Are terms kept elsewhere?* (84%).

**How hard is the task for a person?** Ten offers (80 decisions) were re-labelled on 25 Nov by the same
labeller, from the evidence, without looking at the first labels. Agreement with the first pass was
**81% (κ 0.72, substantial)**; on the same 80 decisions the model + checks scored 67.5% (κ 0.52). So the
model reaches about five-sixths of the labeller's own consistency. Seven of the 15 changes between the two
human passes were between *stated* and *vague*, the same boundary where the model makes most of its errors:
deciding when "100% job assistance" or "full refund as per our policy" is a clear answer is genuinely hard,
which is one more reason the card shows the quote next to every verdict.

**Giving the model my labelling rules did not help.** Run 2 added the full labelling guide (the same
decision order and examples I labelled with) to the prompt, with the same model and checks. Agreement
fell from 68.5% to 64.5%. The model became *more* willing to call terms clear (vague → stated: 21 → 24)
and to call vague terms missing (vague → not stated: 11 → 17), and it still found no contradictions.
More rules made the prompt longer without fixing the judgement. A run with a larger model was planned
but every attempt hit "model overloaded" errors on the free tier, so it is not reported.

What this means for the card: a model can draft it, and the quote check makes every shown quote real,
but about 3 answers in 10 still need a human look, mostly where the model is more confident than the
document. A card that marks *vague* as *stated* would reassure a candidate exactly where it should warn.

## Limitations

25 offers, one labeller (the 10-offer re-label measures consistency, not agreement between different people);
offers were found by search and from two friends, so they are not a random sample;
pages were captured on one or two days; image text was read with OCR and corrected by eye;
the card reports clarity of terms, not whether an offer is fair, legal or genuine.
