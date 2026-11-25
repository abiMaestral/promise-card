# Labelling instructions (same as the human labeller's guide v1.0, offer references removed)

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
3. **Do two passages disagree?** Yes → `contradictory`. Give both quotes.
4. **Is a key part undefined or open-ended?** Yes → `vague`.
5. Otherwise → `stated`.

### What counts as vague (examples)

- An undefined yardstick: "based on performance", "successful completion", "tangible career benefits".
- A window given only as an example: "(e.g., 7 days from batch start)".
- An amount that exists but isn't given: "a one-time administrative registration fee… is mandatory" with no figure.
- "typically", "usually": salary floor "typically" Rs 3 LPA.

### Not vague

- Several clear tiers: "Non Tech … Rs. 1499 … Tech … Rs 9999" → `stated`.
- A harsh but clear term: "strictly non-refundable once enrollment is confirmed" → `stated`.
  The card records clarity, not fairness.

