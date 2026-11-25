"""Turn saved evidence PDFs (browser "Save as PDF") into plain text for the pipeline.

  python tools/pdf_to_text.py evidence/L05/L05_2026-11-22.pdf L05

Browser print adds a header (date/time, page title) and footer (URL, "3/12") on every page.
Those lines are removed so that sentences split across a page break can still be matched.
Nothing else is changed.
"""
import re, subprocess, sys
from pathlib import Path


def clean(text: str) -> str:
    lines = text.replace("\f", "\n").split("\n")
    title = next((l.strip() for l in lines if l.strip() and not re.match(r"^\d{1,2}/\d{1,2}/\d{2},", l.strip())), "")
    out = []
    for l in lines:
        s = l.strip()
        if re.match(r"^\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2} [AP]M$", s):   # print header date
            continue
        if re.match(r"^\d+/\d+$", s):                                      # page counter
            continue
        if re.match(r"^(https?://|file:///)\S", s.replace(" ", "")) and len(s.split()) <= 12 and "." in s:
            continue                                                       # print footer URL
        if title and s == title:
            continue
        out.append(l)
    return "\n".join(out)


if __name__ == "__main__":
    pdf, doc_id = sys.argv[1], sys.argv[2]
    raw = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
    out = Path("data/sources") / f"{doc_id}.txt"
    out.write_text(clean(raw), encoding="utf-8")
    print(out, len(out.read_text(encoding="utf-8")), "chars")
