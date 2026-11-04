"""Package the exact local inputs recorded by the article/supplement builds.

The package is for review until scientific and authorship gates are closed.
System TeX inputs and unrelated experiment data are deliberately not bundled.
"""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TRANSIENT = {'.aux', '.out', '.toc', '.lof', '.lot', '.fls', '.log', '.blg', '.fdb_latexmk'}


def main():
    sources = set()
    for document in ('main', 'supplement'):
        recorder = ROOT / (document + '.fls')
        if not recorder.exists():
            raise FileNotFoundError(f'Build {document} with pdflatex -recorder first')
        for line in recorder.read_text(encoding='utf-8', errors='replace').splitlines():
            if not line.startswith('INPUT '):
                continue
            path = Path(line[6:].strip('"'))
            path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
            if path.is_relative_to(ROOT) and path.suffix.lower() not in TRANSIENT:
                if not path.is_file():
                    raise FileNotFoundError(path)
                sources.add(path)
    for name in ('references.bib', 'IEEEtran.bst'):
        path = ROOT / name
        if path.exists():
            sources.add(path)
    manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}
    instructions = '''P07 article and supplement source snapshot

Compile main.tex and supplement.tex separately with pdfLaTeX, BibTeX and two
further pdfLaTeX passes. IEEEtran.bst may be supplied by your TeX distribution.
All local files actually read by these builds are included with their paths.
The PDF copies are supplied separately in output/pdf in the working repository.

This is a review snapshot, not a certificate of submission readiness. The
independent confirmatory campaign and final author metadata/biographies remain
subject to the current repository status. No external submission is performed.
Historical Technical Notes are preserved as a separate repository document.
'''
    destination = ROOT / 'output/source/P07_Article_Supplement_Source.zip'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in manifest:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 31, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / name).read_bytes())
        archive.writestr('README_BUILD.txt', instructions)
        archive.writestr('SOURCE_MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive integrity failure')
        for name, expected in manifest.items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise ValueError('Archive source mismatch: ' + name)
    result = dict(file=str(destination), files=len(manifest), bytes=destination.stat().st_size,
                  sha256=hashlib.sha256(destination.read_bytes()).hexdigest(), submission_ready=False)
    (destination.parent / 'SOURCE_PACKAGE.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
