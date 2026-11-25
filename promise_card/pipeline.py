"""Model output -> checked card. All state changes made by code are recorded in notes.

Order of checks (code can only make a field *less* certain, never more):
  1. quote_check: unverifiable quotes are removed (kept in card.rejected_quotes).
     If a stated/vague/contradictory field is left with no verified quote, it becomes
     not_stated with the note "model answer had no verifiable quote".
  2. clause flags: a "stated" field whose own quote contains an open-ended phrase -> vague.
  3. contradictions: verified quotes from different documents with different amounts of
     the same kind -> contradictory.
  4. terms_elsewhere: if no field answer exists but a deferred clause is found in the
     sources, the field becomes "stated" pointing at that sentence (this is a finding about
     the documents, so it is allowed to add information - it is still a verbatim sentence).
"""
from __future__ import annotations

from . import clauses, contradictions
from .quote_check import quote_in
from .schema import (Card, FieldName, FieldResult, PromiseType, Quote, SourceDoc, State)

_NEEDS_QUOTE = {State.stated, State.vague, State.contradictory}


def build_card(offer_id: str, title: str, docs: list[SourceDoc], extraction: dict) -> Card:
    texts = {d.doc_id: d.text for d in docs}
    rejected: list[Quote] = []
    fields: list[FieldResult] = []

    for raw in extraction["fields"]:
        try:
            name = FieldName(raw["field"])
        except ValueError:
            continue
        try:
            state = State(raw.get("state", "not_stated"))
        except ValueError:
            state = State.not_stated
        fr = FieldResult(field=name, state=state, value=raw.get("value", "") or "")
        if raw.get("_note"):
            fr.notes.append(raw["_note"])
        for q in raw.get("quotes", []) or []:
            quote = Quote(doc_id=q.get("doc_id", ""), text=q.get("text", ""))
            quote.verified = quote.doc_id in texts and quote_in(quote.text, texts[quote.doc_id])
            if quote.verified:
                fr.quotes.append(quote)
            else:
                rejected.append(quote)
                fr.notes.append(f"quote rejected (not found in {quote.doc_id or '?'})")
        # 1. no evidence left
        if fr.state in _NEEDS_QUOTE and not fr.quotes:
            fr.notes.append(f"model said {fr.state.value}; no verifiable quote -> not_stated")
            fr.state, fr.value = State.not_stated, ""
        if fr.state == State.contradictory and len(fr.quotes) < 2:
            fr.notes.append("contradictory needs two quotes; only one verified -> vague")
            fr.state = State.vague
        # 2. open-ended wording inside the field's own quote
        # Not for the two fields whose answer *is* such wording: "we may modify these terms" is a clear
        # yes to "can terms change?", and a pointer to another document is the answer to terms_elsewhere
        # (labelling guide v1.0). Applying the rule there was a bug in v1.0, fixed in v1.0.1.
        if fr.state == State.stated and name not in (FieldName.terms_can_change, FieldName.terms_elsewhere):
            hits = [label for q in fr.quotes for kind, label in clauses.scan_text(q.text)
                    if kind == "open_ended"]
            if hits:
                fr.notes.append(f"open-ended wording in quote ({', '.join(sorted(set(hits)))}) -> vague")
                fr.state = State.vague
        fields.append(fr)

    # 3. numeric contradictions across documents
    found = []
    for fr in fields:
        c = contradictions.find(fr)
        if c:
            found.extend(c)
            if fr.state != State.contradictory:
                fr.notes.append(f"code found contradiction: {c[0].reason} -> contradictory")
                fr.state = State.contradictory

    hits = clauses.scan_docs(docs)

    # 4. deferred terms found by rule
    te = next((f for f in fields if f.field == FieldName.terms_elsewhere), None)
    deferred = [h for h in hits if h.kind == "deferred"]
    if te is not None and te.state == State.not_stated and deferred:
        h = deferred[0]
        te.state = State.stated
        te.value = f"Source refers to terms elsewhere ({h.phrase})."
        te.quotes = [Quote(doc_id=h.doc_id, text=h.sentence, verified=True)]
        te.notes.append("set by deferred-clause rule")

    try:
        ptype = PromiseType(extraction.get("promise_type", "none"))
    except ValueError:
        ptype = PromiseType.none

    order = list(FieldName)
    fields.sort(key=lambda f: order.index(f.field))
    return Card(offer_id=offer_id, title=title, sources=docs, promise_type=ptype, fields=fields,
                clause_hits=hits, contradictions=found, rejected_quotes=rejected)
