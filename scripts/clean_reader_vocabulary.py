"""Remove internal jargon from every LaTeX source that reaches the article or the
supplement (recursively through \\input).  Reader text must not contain code
names, paths, campaign identifiers or archive jargon.

Usage: python scripts/clean_reader_vocabulary.py [--apply]
Without --apply it only lists what would change.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Anchor phrase required by scripts/verify_protected_figures.py; leave untouched.
PROTECTED = "Representative signatures from the archived RAW0001"
WORDS = [
    (r"\bfrozen\b", "fixed"), (r"\bFrozen\b", "Fixed"),
    (r"\barchived\b", "stored"), (r"\bArchived\b", "Stored"),
    (r"\bsealed\b", "stored"), (r"\bSealed\b", "Stored"),
    (r"Chen2016", r"Chen \\emph{et al.}"),
]


def sources(doc: str) -> list[Path]:
    seen: list[Path] = []

    def walk(name: str) -> None:
        p = ROOT / (name if name.endswith(".tex") else name + ".tex")
        if not p.exists() or p in seen:
            return
        seen.append(p)
        for x in re.findall(r"\\input\{([^}]+)\}", p.read_text(encoding="utf-8")):
            walk(x)
    walk(doc)
    return seen


def clean_line(line: str) -> str:
    if line.lstrip().startswith("%") or PROTECTED in line:
        return line
    # do not touch labels, refs, file names or macro definitions
    parts = re.split(r"(\\(?:label|ref|eqref|cite|input|includegraphics(?:\[[^]]*\])?|IfFileExists|nolinkurl|url)\{[^}]*\})", line)
    for i in range(0, len(parts), 2):
        for pat, rep in WORDS:
            parts[i] = re.sub(pat, rep, parts[i])
    return "".join(parts)


def main() -> None:
    apply = "--apply" in sys.argv
    files = {p for d in ("main", "supplement") for p in sources(d)}
    for p in sorted(files):
        if p.name in ("main.tex", "supplement.tex", "preamble.tex"):
            pass
        old = p.read_text(encoding="utf-8").splitlines(keepends=True)
        new = [clean_line(l) for l in old]
        changed = [(i + 1, a.strip()[:100]) for i, (a, b) in enumerate(zip(old, new)) if a != b]
        if changed:
            print(p.relative_to(ROOT), len(changed))
            if apply:
                p.write_text("".join(new), encoding="utf-8")
    for d in ("main", "supplement"):
        for p in sources(d):
            t = p.read_text(encoding="utf-8")
            for k in ("H04", "RAW0001", "extras\\_per", "extras_per"):
                for m in re.finditer(re.escape(k), t):
                    ln = t[: m.start()].count("\n") + 1
                    print("CHECK", d, p.relative_to(ROOT), ln, t[m.start(): m.start() + 80].replace("\n", " "))


if __name__ == "__main__":
    main()
