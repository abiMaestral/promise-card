"""OCR evidence screenshots into one text file per document.
  python tools/ocr_to_text.py L26 evidence/L26/L26a.png evidence/L26/L26b.png ...
Pages are joined in the order given. Check the output by eye: OCR can drop symbols (₹)."""
import subprocess, sys
from pathlib import Path
doc_id, files = sys.argv[1], sys.argv[2:]
parts = [subprocess.run(["tesseract", f, "-", "--psm", "6"], capture_output=True, text=True).stdout for f in files]
out = Path("data/sources") / f"{doc_id}.txt"
out.write_text("\n\n".join(parts), encoding="utf-8")
print(out, sum(len(p) for p in parts), "chars")
