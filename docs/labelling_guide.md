# Labelling guide (schema v1.0, frozen 23 Nov 2026)

You are writing the answer key. The model is scored against these labels, so label
**before** you look at any model output, and label from the **saved PDF/screenshot**
in `evidence/`, not the live page (pages change; the saved copy is what the model sees).

## For each offer

1. Open the saved evidence for the offer (all documents listed in `doc_ids`).
2. For each of the eight fields, pick one state and paste the supporting quote.
3. Pick one `promise_type`.
4. Anything the schema can't express → `label_notes`. These notes become the rules changelog.

About 5–8 minutes per offer. 26 offers. Do it in two sittings; note the date in `labelled_on`.

## The eight fields

| Field | Question | Notes |
|---|---|---|
| total_cost | Q1 How much will I pay in total? | All payments: registration, fee, ISA/% of CTC, deposits. Several tiers in one doc = still `stated`. |
| payment_timing | Q2 When is each payment due? | "Before training", "after placement", EMIs. |
| promise | Q3 What exactly is guaranteed? | The outcome in the provider's words. |
| conditions | Q4 What must I do to qualify? | Attendance, scores, age, CIBIL, "must not decline". |
| terms_can_change | Q5 Can the provider add conditions or change terms later? | "may be amended", "subject to change", "continued use = acceptance". If the page says so → `stated` (quote it). |
| if_not_placed | Q6 What happens if I am not placed? | Refund, partial refund, extension, nothing. |
| refuse_offer | Q7 Can I refuse an offer without losing money? | Only `not_applicable` if no job/internship offer is promised at all. |
| terms_elsewhere | Q8 Are relevant terms on other pages or in documents not reviewed? | Agreement after enrolment, separate placement policy, offer email. If the docs point elsewhere → `stated`. |

## The five states — decide in this order

1. **Does the question apply?** No → `not_applicable`.
2. **Do the sources address it at all?** No → `not_stated`.
3. **Do two passages disagree?** Yes → `contradictory`. Paste both quotes separated by ` || `.
4. **Is a key part undefined or open-ended?** Yes → `vague`.
5. Otherwise → `stated`.

### What counts as vague (examples from our own sources)

- An undefined yardstick: "based on performance" (L20), "successful completion" (Friend B, L19), "tangible career benefits" (L11).
- A window given only as an example: "(e.g., 7 days from batch start)" (L14).
- An amount that exists but isn't given: "a one-time administrative registration fee… is mandatory" with no figure (Friend A).
- "typically", "usually": salary floor "typically" Rs 3 LPA (P01).

### Not vague

- Several clear tiers: "Non Tech … Rs. 1499 … Tech … Rs 9999" (L22) → `stated`.
- A harsh but clear term: "strictly non-refundable once enrollment is confirmed" (L14) → `stated`.
  The card records clarity, not fairness.

## Quotes

- Copy exactly from the saved document. Don't fix typos ("Inludes" stays).
- One sentence or less. If two parts are needed, separate with ` || `.
- `not_stated` / `not_applicable`: leave the quote empty.

## promise_type (pick the main one)

`job_offer` · `placement_or_refund` · `salary_floor` · `interview_count` · `internship` ·
`stipend_or_pay` · `assistance_only` · `aim` · `none`

If two apply, pick the one the provider leads with, and note the other in `label_notes`.

## Consistency check (Thursday)

On Thursday you re-label 10 offers chosen at random, without looking at your first labels.
The agreement between your two passes is the ceiling for what the model can be expected to reach.
