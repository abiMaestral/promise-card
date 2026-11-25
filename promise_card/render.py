"""Render a Card as a single self-contained HTML page (no external assets)."""
from __future__ import annotations

import html

from .schema import QUESTIONS, Card, State

LABEL = {
    State.stated: ("Stated", "#1b6e3a", "#e3f3e8"),
    State.vague: ("Vague", "#8a5a00", "#fdf0d5"),
    State.contradictory: ("Contradictory", "#9b1c1c", "#fbe2e2"),
    State.not_stated: ("Not stated", "#555", "#ececec"),
    State.not_applicable: ("Not applicable", "#777", "#f5f5f5"),
}
TITLE = {
    "total_cost": "What you pay", "payment_timing": "When you pay", "promise": "What is promised",
    "conditions": "Conditions you must meet", "terms_can_change": "Can terms change later?",
    "if_not_placed": "If the promise is not met", "refuse_offer": "If you refuse an offer",
    "terms_elsewhere": "Terms kept elsewhere",
}
e = html.escape

CSS = """body{font:15px/1.5 system-ui,sans-serif;max-width:820px;margin:24px auto;padding:0 16px;color:#1d1d1d}
h1{font-size:22px;margin:0 0 4px}.sub{color:#666;font-size:13px;margin-bottom:18px}
.f{border:1px solid #ddd;border-radius:10px;padding:12px 14px;margin:10px 0}
.h{display:flex;justify-content:space-between;align-items:center;gap:8px}
.t{font-weight:600}.q{color:#666;font-size:12px}.b{font-size:12px;font-weight:600;padding:2px 8px;border-radius:99px;white-space:nowrap}
.v{margin:6px 0}.qt{border-left:3px solid #ccc;padding:2px 10px;margin:6px 0;color:#333;font-size:13px}
.src{font-size:11px;color:#888}.n{font-size:11px;color:#8a5a00}.note{background:#f7f7f7;padding:10px 14px;border-radius:8px;font-size:13px;color:#444}
table{border-collapse:collapse;font-size:12px;width:100%}td{border-top:1px solid #eee;padding:4px 6px;vertical-align:top}"""


def render(card: Card) -> str:
    srcs = {s.doc_id: s for s in card.sources}
    out = [f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Promise Card: {e(card.title)}</title>",
           f"<style>{CSS}</style></head><body>",
           f"<h1>{e(card.title)}</h1>",
           f"<div class='sub'>Promise type: <b>{e(card.promise_type.value.replace('_', ' '))}</b> · "
           f"{len(card.sources)} source(s) · schema v{card.schema_version}</div>",
           "<div class='note'>This card reports what the reviewed documents say, with exact quotes. "
           "It does not judge whether the offer is fair, legal or genuine.</div>"]
    for f in card.fields:
        lab, fg, bg = LABEL[f.state]
        out.append(f"<div class='f'><div class='h'><div><div class='t'>{TITLE[f.field.value]}</div>"
                   f"<div class='q'>{e(QUESTIONS[f.field])}</div></div>"
                   f"<span class='b' style='color:{fg};background:{bg}'>{lab}</span></div>")
        if f.value:
            out.append(f"<div class='v'>{e(f.value)}</div>")
        for q in f.quotes:
            s = srcs.get(q.doc_id)
            where = f"<a href='{e(s.url)}'>{e(q.doc_id)}</a>" if s and s.url else e(q.doc_id)
            date = f", checked {e(s.checked_on)}" if s and s.checked_on else ""
            out.append(f"<div class='qt'>“{e(q.text)}”<div class='src'>{where}{date}</div></div>")
        for n in f.notes:
            out.append(f"<div class='n'>checker: {e(n)}</div>")
        out.append("</div>")
    if card.contradictions:
        out.append("<h3>Contradictions between documents</h3><table>")
        for c in card.contradictions:
            out.append(f"<tr><td>{e(c.field.value)}</td><td>“{e(c.a.text)}” ({e(c.a.doc_id)})</td>"
                       f"<td>“{e(c.b.text)}” ({e(c.b.doc_id)})</td><td>{e(c.reason)}</td></tr>")
        out.append("</table>")
    flagged = [h for h in card.clause_hits]
    if flagged:
        out.append("<h3>Open-ended and deferred wording found</h3><table>")
        for h in flagged[:30]:
            out.append(f"<tr><td>{e(h.kind.replace('_', '-'))}</td><td>{e(h.phrase)}</td>"
                       f"<td>{e(h.sentence)}</td><td>{e(h.doc_id)}</td></tr>")
        out.append("</table>")
    if card.rejected_quotes:
        out.append(f"<p class='src'>{len(card.rejected_quotes)} quote(s) from the model were not found "
                   "in the sources and were removed.</p>")
    out.append("</body></html>")
    return "\n".join(out)
