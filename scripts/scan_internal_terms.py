"""Editorial guard: list code, paths and internal campaign identifiers in the
LaTeX sources that reach the compiled article and supplement.

Usage: python scripts/scan_internal_terms.py [main|supplement]
Exit code 1 if anything is found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    r"\\nolinkurl", r"\\texttt", r"\\path\{", r"\.py\b", r"\.jl\b", r"\.ps1\b", r"\.npz\b",
    r"\b(?:GATE|GATES)\b", r"\b(?:F01|F21|H0\d|H\d{3}|R\d{2}[A-Z]?|X0\d|A0\d|B0\d|C0\d|S0\d|E\d|N0\d|P1\d)\b",
    r"\bSIM\d{4}\b", r"\bM0\d\b", r"\bRAW000[2-9]\b", r"\b[a-z]{3,}(?:\\?_[a-z]{3,})+\b", r"\bPENDING\b",
]
SKIP_INPUTS = {"preamble", "metadata", "author_biographies"}


def sources(doc: str) -> list[Path]:
    text = (ROOT / f"{doc}.tex").read_text(encoding="utf-8")
    text = "\n".join(l.split("%")[0] for l in text.splitlines())
    out = []
    for name in re.findall(r"\\input\{([^}]+)\}", text):
        if name in SKIP_INPUTS or name.startswith("generated/") and not name.startswith("generated/") is False:
            pass
        p = ROOT / (name if name.endswith(".tex") else name + ".tex")
        if p.exists() and name not in SKIP_INPUTS:
            out.append(p)
    return out


def main() -> int:
    doc = sys.argv[1] if len(sys.argv) > 1 else "main"
    rx = re.compile("|".join(PATTERNS))
    hits = 0
    for path in sources(doc):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("%")[0] if not line.lstrip().startswith("\\newcommand") else ""
            # labels and refs are invisible in the PDF
            code = re.sub(r"\\(?:label|ref|eqref|cite|input|includegraphics(?:\[[^]]*\])?|IfFileExists)\{[^}]*\}", "", code)
            for m in rx.finditer(code):
                hits += 1
                print(f"{path.relative_to(ROOT)}:{n}: {m.group(0)} | {code.strip()[:110]}")
    print(f"{hits} hits")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
