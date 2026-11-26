"""Final editorial guard on the compiled PDFs (text layer, including figure text).

Lists code, paths, internal campaign identifiers and archive jargon.
Usage: python scripts/scan_pdf_text.py main.pdf supplement.pdf
"""
from __future__ import annotations

import re
import sys

import pymupdf

PATTERN = re.compile(
    r"[\w./-]+\.(?:py|jl|json|csv|npz|ps1)\b"
    r"|\b(?:GATES?|F01|F21|H0\d|H\d{3}|R1\d|X0\d|A0\d|B0\d|C0\d|S0\d|N0\d|SIM\d{4}|M0\d|RAW000[2-9])\b"
    r"|\b[a-z]{3,}_[a-z_]{3,}\b|\bfrozen\b|\barchived\b|\bsealed\b|Chen2016|PENDING")
ALLOWED = {"Representative signatures from the archived RAW0001"}


def main() -> int:
    total = 0
    for path in sys.argv[1:]:
        with pymupdf.open(path) as doc:
            for i, page in enumerate(doc):
                text = " ".join(page.get_text().split())
                for m in PATTERN.finditer(text):
                    ctx = text[max(0, m.start() - 60): m.end() + 30]
                    if any(a in text[max(0, m.start() - 60): m.end() + 60] for a in ALLOWED):
                        continue
                    total += 1
                    print(f"{path} p{i + 1}: {m.group(0)} | {ctx}".encode("ascii", "replace").decode())
    print(f"{total} hits")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
