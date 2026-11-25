# Rules changelog

## v1.0 — 23 Nov 2026 (frozen before labelling)
- Eight fields mapped one-to-one to the eight evaluation questions; five states.
- Code may only make a field less certain: invented quote → removed; stated + open-ended
  wording in its own quote → vague; different amounts across documents → contradictory.
- Open-ended patterns: from time to time; may be amended/modified; subject to change;
  as may be communicated; additional conditions; sole discretion; subject to T&C;
  "(e.g., …)"; typically/usually; continued use = acceptance; based on performance;
  successful completion. Each was seen in a verified source during Days 1–2.
- Deferred patterns: shared upon/after enrolment; in the offer email/letter; separate
  policy/agreement; agreement to be signed; refer to/as per terms; will be shared later.
- Tiers inside one document are not contradictions (L22: Rs 1499 non-tech / Rs 9999 tech).

## v1.0.1 — 25 Nov 2026 (bug fix found in run 1; results reported for both versions)
- The open-ended-wording rule (stated → vague) no longer applies to `terms_can_change` and
  `terms_elsewhere`. For those two fields the flagged wording is the answer itself, as the labelling
  guide (v1.0, frozen 23 Nov) already said ("If the page says so → stated"). In run 1 the rule wrongly
  downgraded 8 correct answers (7 terms_can_change, 1 terms_elsewhere).
- No other rule, prompt or label was changed. Both v1.0 and v1.0.1 scores are reported.
