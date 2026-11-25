"""Frozen card schema (v1.0, 23 Nov 2026).

The same eight fields and five states are used by the hand labels, the extractor and the
evaluation, so that every number in the evaluation compares like with like.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FieldName(str, Enum):
    total_cost = "total_cost"            # Q1 How much will I pay in total?
    payment_timing = "payment_timing"    # Q2 When is each payment due?
    promise = "promise"                  # Q3 What exactly is guaranteed?
    conditions = "conditions"            # Q4 What must I do to qualify?
    terms_can_change = "terms_can_change"  # Q5 Can the provider add conditions / change terms later?
    if_not_placed = "if_not_placed"      # Q6 What happens if I am not placed?
    refuse_offer = "refuse_offer"        # Q7 Can I refuse an offer without losing money?
    terms_elsewhere = "terms_elsewhere"  # Q8 Are relevant terms on other pages or in documents not shown?


QUESTIONS = {
    FieldName.total_cost: "How much will I pay in total?",
    FieldName.payment_timing: "When is each payment due?",
    FieldName.promise: "What exactly is guaranteed?",
    FieldName.conditions: "What must I do to qualify?",
    FieldName.terms_can_change: "Can the provider add conditions or change terms later?",
    FieldName.if_not_placed: "What happens if I am not placed?",
    FieldName.refuse_offer: "Can I refuse an offer without losing money?",
    FieldName.terms_elsewhere: "Were relevant terms found on other pages, or deferred to a document not reviewed?",
}


class State(str, Enum):
    stated = "stated"                  # answered clearly, with a quote
    vague = "vague"                    # addressed, but key part undefined or open-ended
    contradictory = "contradictory"    # two quotes in the reviewed sources disagree
    not_stated = "not_stated"          # the reviewed sources do not address it
    not_applicable = "not_applicable"  # the question does not apply to this offer


class PromiseType(str, Enum):
    job_offer = "job_offer"                    # "100% job offer", "will get the job"
    placement_or_refund = "placement_or_refund"  # placed, else a (partial) refund
    salary_floor = "salary_floor"              # job at or above a stated CTC
    interview_count = "interview_count"        # N interviews, else refund
    internship = "internship"                  # guaranteed internship
    stipend_or_pay = "stipend_or_pay"          # pay/stipend during internship
    assistance_only = "assistance_only"        # "placement assistance", explicitly no guarantee
    aim = "aim"                                # "aims to provide"
    none = "none"                              # no outcome promised


class Quote(BaseModel):
    doc_id: str
    text: str
    verified: bool = False   # set by code (quote_check), never by the model


class FieldResult(BaseModel):
    field: FieldName
    state: State
    value: str = ""                      # short plain-words answer; "" if not_stated / not_applicable
    quotes: list[Quote] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)   # why code changed the state, etc.


class ClauseHit(BaseModel):
    kind: str        # "open_ended" | "deferred"
    phrase: str      # the matched pattern label
    doc_id: str
    sentence: str


class Contradiction(BaseModel):
    field: FieldName
    a: Quote
    b: Quote
    reason: str


class SourceDoc(BaseModel):
    doc_id: str
    url: str = ""
    evidence_type: str = ""
    checked_on: str = ""
    text: str


class Card(BaseModel):
    offer_id: str
    title: str
    sources: list[SourceDoc]
    promise_type: PromiseType
    fields: list[FieldResult]
    clause_hits: list[ClauseHit] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    rejected_quotes: list[Quote] = Field(default_factory=list)
    schema_version: str = "1.0"

    def field(self, name: FieldName) -> FieldResult:
        return next(f for f in self.fields if f.field == name)
