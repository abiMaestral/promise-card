"""A quote is kept only if it really appears in the source it claims to come from.

Matching ignores case, whitespace runs, curly vs straight quotes, dash variants and the
"Rs"/"Rs."/"₹"/"INR" currency spellings. Nothing else is forgiven: a paraphrase fails.
"""
from __future__ import annotations

import re

_MAP = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "−": "-", " ": " ", "…": "...",
})
_CURRENCY = re.compile(r"(₹|\brs\.?|\binr\b)\s*", re.IGNORECASE)


def norm(text: str) -> str:
    text = text.translate(_MAP).lower()
    text = _CURRENCY.sub("rs ", text)
    text = re.sub(r"[*_`]", "", text)        # markdown emphasis copied from pages
    text = re.sub(r"(?<=\w)-(?=\w)", "", text)   # "High-performing" vs PDF's "Highperforming"
    text = re.sub(r"\s*/\s*", "/", text)      # "fees / Enrolment" vs "fees/ Enrolment"
    return re.sub(r"\s+", " ", text).strip()


def _piece_in(piece: str, text_n: str) -> bool:
    q = norm(piece).strip(" .\"'")
    return len(q) >= 4 and q in text_n


def quote_in(quote: str, text: str) -> bool:
    """A quote may be one passage, or table cells joined with " | " (copied from a table).
    For table quotes every cell of 4+ characters must be in the source; short cells
    like "No" or "Rs 99" are skipped because they would match almost anything."""
    text_n = norm(text)
    if "|" not in quote:
        return _piece_in(quote, text_n)
    cells = [c for c in quote.split("|") if len(norm(c).strip(" .\"'")) >= 4]
    return bool(cells) and all(_piece_in(c, text_n) for c in cells)
