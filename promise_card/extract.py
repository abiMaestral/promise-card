"""LLM extraction: source text in, one JSON answer per field out, each with verbatim quotes.

The model is only asked to *point at* text. Everything it says is then checked by code
(quote_check, clauses, contradictions) before it reaches the card.

Backends:
  gemini     - Google Gemini via google-genai (free tier works); env GEMINI_API_KEY
  anthropic  - Claude via anthropic SDK; env ANTHROPIC_API_KEY
  cached     - read a saved JSON from data/extractions/<offer_id>.json (no key needed;
               used by tests and the demo so results are reproducible)
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .schema import QUESTIONS, FieldName, PromiseType, SourceDoc, State

PROMPT = """You are filling in a "Placement Promise Card" for a paid training, internship or
placement offer. You do NOT judge whether the offer is good, bad, fair or fraudulent.
You only report what the documents below say, with exact quotes.

For each field, choose exactly one state:
- "stated": the documents answer the question clearly.
- "vague": the documents address it, but a key part is undefined or open-ended
  (e.g. "successful completion" never defined; "based on performance"; "e.g., 7 days";
  "as may be communicated"; amount "not mentioned" but a fee exists).
- "contradictory": two passages give different answers. Quote BOTH.
- "not_stated": the documents do not address it at all.
- "not_applicable": the question cannot apply (e.g. refuse_offer when no job offer is promised).

Fields and questions:
{fields}

Also classify the main promise as one of: {ptypes}.

Rules:
1. Every quote must be copied EXACTLY, character for character, from ONE document, and
   name that document's doc_id. Short quotes (one sentence or less) are best.
2. "stated", "vague" and "contradictory" need at least one quote. "not_stated" and
   "not_applicable" have no quotes.
3. "value" is a short plain-English answer (max 25 words) using only what is quoted.
   Never add facts, estimates or advice. Never infer an amount that is not written.
4. terms_elsewhere is about terms the documents say exist elsewhere (an agreement, a
   separate policy, an offer email, "shared after enrolment").

Return ONLY JSON in this shape:
{{"promise_type": "...",
  "fields": [{{"field": "total_cost", "state": "...", "value": "...",
              "quotes": [{{"doc_id": "...", "text": "..."}}]}}, ...]}}

Documents:
{docs}
"""


def build_prompt(docs: list[SourceDoc], prompt: str = "v1") -> str:
    """v1: the prompt used in run 1. guide: v1 plus the human labeller's guide (frozen 23 Nov),
    so the model gets the same decision rules the hand labels were made with."""
    fields = "\n".join(f"- {f.value}: {q}" for f, q in QUESTIONS.items())
    ptypes = ", ".join(p.value for p in PromiseType)
    body = "\n\n".join(f'<doc id="{d.doc_id}">\n{d.text}\n</doc>' for d in docs)
    text = PROMPT.format(fields=fields, ptypes=ptypes, docs=body)
    if prompt == "guide":
        guide = (Path(__file__).parent / "guide_for_model.md").read_text(encoding="utf-8")
        text = text.replace("Documents:\n", "Decision rules (follow these exactly):\n" + guide + "\nDocuments:\n", 1)
    return text


def parse_json(raw: str) -> dict:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("model returned no JSON")
    data = json.loads(m.group(0))
    seen = {f.get("field") for f in data.get("fields", [])}
    for f in FieldName:   # a missing field is recorded as not_stated, with a note
        if f.value not in seen:
            data.setdefault("fields", []).append(
                {"field": f.value, "state": State.not_stated.value, "value": "", "quotes": [],
                 "_note": "field missing from model output"})
    return data


def call_model(prompt: str, backend: str, model: str | None = None) -> str:
    if backend == "gemini":
        from google import genai  # pip install google-genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"],
                              http_options={"timeout": 180_000, "retry_options": {"attempts": 1}})
        r = client.models.generate_content(
            model=model or "gemini-3.5-flash-lite", contents=prompt,
            config={"temperature": 0, "response_mime_type": "application/json"})
        return r.text
    if backend == "anthropic":
        import anthropic  # pip install anthropic
        client = anthropic.Anthropic()
        r = client.messages.create(model=model or "claude-sonnet-5-5", max_tokens=4000,
                                   temperature=0, messages=[{"role": "user", "content": prompt}])
        return r.content[0].text
    raise ValueError(f"unknown backend {backend}")


def extract(offer_id: str, docs: list[SourceDoc], backend: str = "cached",
            model: str | None = None, cache_dir: Path = Path("data/extractions"), prompt: str = "v1") -> dict:
    path = cache_dir / f"{offer_id}.json"
    if backend == "cached":
        return json.loads(path.read_text(encoding="utf-8"))
    import time
    models = [m.strip() for m in (model or "").split(",") if m.strip()] or [None]
    raw, used, last = None, None, None
    for rnd in range(3):                       # up to 3 rounds over the model list
        for m in models:
            try:
                raw, used = call_model(build_prompt(docs, prompt), backend, m), m
                break
            except Exception as exc:           # noqa: BLE001
                last = exc
                msg = str(exc)
                if "404" in msg or "API key" in msg or "PERMISSION" in msg:
                    raise                      # will never succeed: stop now
                print(f"  {offer_id}: {m or 'default'} busy ({msg[:40]}...)")
        if raw is not None:
            break
        if rnd < 2:
            print(f"  {offer_id}: all models busy, waiting 60s")
            time.sleep(60)
    if raw is None:
        raise last
    model = used
    data = parse_json(raw)
    data["_backend"], data["_model"], data["_prompt"] = backend, model or "default", prompt
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
