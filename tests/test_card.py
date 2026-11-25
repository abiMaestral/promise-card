"""Tests use two real offers (L20, L22; text as verified by eye on 23 Nov 2026) and
small synthetic snippets for the contradiction rule, marked as synthetic."""
import json
from pathlib import Path

from promise_card import clauses, contradictions
from promise_card.pipeline import build_card
from promise_card.quote_check import quote_in
from promise_card.render import render
from promise_card.schema import FieldName, FieldResult, Quote, SourceDoc, State

FIX = Path(__file__).parent / "fixtures"   # real offers L20, L22 (text verified 23-24 Nov), provider names redacted


def doc(oid):
    return SourceDoc(doc_id=oid, text=(FIX / f"{oid}.txt").read_text(encoding="utf-8"))


def card(oid):
    ext = json.loads((FIX / f"{oid}.json").read_text(encoding="utf-8"))
    return build_card(oid, oid, [doc(oid)], ext)


# quote check -------------------------------------------------------------
def test_quote_tolerates_currency_and_quotes_only():
    t = "Fee: Rs. 1499/-Only - 7 days training"
    assert quote_in("rs 1499/-only - 7 days training", t)
    assert quote_in("₹1499/-Only", t)
    assert not quote_in("Rs 1,499 only", t)          # a comma added = paraphrase -> rejected


def test_quote_too_short_rejected():
    assert not quote_in("Rs", "Rs 500")


# pipeline ----------------------------------------------------------------
def test_invented_quote_removed_and_field_downgraded():
    c = card("L22")
    f = c.field(FieldName.if_not_placed)
    assert f.state == State.not_stated and not f.quotes
    assert len(c.rejected_quotes) == 1


def test_open_ended_wording_turns_stated_into_vague():
    c = card("L20")
    assert c.field(FieldName.promise).state == State.vague      # "based on performance"
    assert any("open-ended" in n for n in c.field(FieldName.promise).notes)


def test_tiers_in_one_document_are_not_a_contradiction():
    assert card("L22").field(FieldName.total_cost).state == State.stated


def test_states_only_get_less_certain():
    c = card("L22")
    assert c.field(FieldName.promise).state == State.vague      # model said vague, stays vague


# contradictions (synthetic) ------------------------------------------------
def test_different_amounts_across_documents_flagged():
    f = FieldResult(field=FieldName.conditions, state=State.stated, quotes=[
        Quote(doc_id="A", text="minimum 60% in assessments", verified=True),
        Quote(doc_id="B", text="minimum 50% in assessments", verified=True)])
    assert contradictions.find(f)


def test_same_amount_across_documents_not_flagged():
    f = FieldResult(field=FieldName.total_cost, state=State.stated, quotes=[
        Quote(doc_id="A", text="Rs 1,595 to confirm", verified=True),
        Quote(doc_id="B", text="₹1595 internship fee", verified=True)])
    assert not contradictions.find(f)


def test_lakh_units():
    assert contradictions.amounts("Rs 1.2 lakh")["rupees"] == {120000.0}


# clause rules --------------------------------------------------------------
def test_clause_patterns_from_verified_sources():
    assert ("open_ended", "e.g. / such as (in a term)") in clauses.scan_text(
        "Requests must be raised within the defined window (e.g., 7 days from batch start)")
    assert ("open_ended", "from time to time") in clauses.scan_text("We may modify these Terms from time to time.")
    assert any(k == "deferred" for k, _ in clauses.scan_text(
        "The formal policy will be shared with you upon successful enrolment and verification."))


def test_render_has_quotes_and_disclaimer():
    h = render(card("L20"))
    assert "does not judge" in h and "INR 350" in h


def test_table_row_quote_checks_each_cell():
    page = "Elevate Unit fee (paid at the start of Unit 6)\n₹5,000\nNot stated as refundable"
    assert quote_in("Elevate Unit fee (paid at the start of Unit 6) | ₹5,000 | Not stated as refundable", page)
    assert not quote_in("Elevate Unit fee (paid at the start of Unit 6) | refundable on request", page)


def test_change_clause_is_a_clear_answer_for_terms_can_change():
    d = SourceDoc(doc_id="X", text="We may modify these Terms from time to time.")
    ext = {"promise_type": "none", "fields": [{"field": "terms_can_change", "state": "stated",
           "value": "Yes", "quotes": [{"doc_id": "X", "text": "We may modify these Terms from time to time."}]}]}
    assert build_card("X", "X", [d], ext).field(FieldName.terms_can_change).state == State.stated
