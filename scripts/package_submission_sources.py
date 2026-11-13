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
    for name in ('references.bib', 'IEEEtran.bst', 'scripts/build_comparator_lineage.py',
                 'generated/comparator_lineage.json', 'scripts/verify_history_partition.py', 'scripts/build_recovery_comparison.py',
                 'scripts/verify_recovery_distribution.py', 'generated/recovery_distribution_checks.json',
                 'scripts/build_channel_information_figure.py',
                 'scripts/build_channel_profile_figure.py',
                 'scripts/build_theory_figures.py', 'scripts/build_integrity_figure.py',
                 'scripts/build_recovery_overview.py', 'scripts/build_physics_measurement_chain.py',
                 'scripts/build_paper_method_figure.py', 'figures/paper_method/main.tex',
                 'figures/recovery_overview/main.tex', 'figures/physical_report/main.tex',
                 'generated/revision_math_20261103/checks.json',
                 'generated/revision_math_20261103/PORTABILITY.json'):
        path = ROOT / name
        if path.exists():
            sources.add(path)
    for folder in ('comparator_lineage_20261103', 'revision_math_kernel_20261103', 'recovery_c02_20261105'):
        sources.update(p for p in (ROOT / 'generated/frozen' / folder).glob('*') if p.is_file())
    # Compact inputs regenerate the theory/noise figures without simulation data.
    sources.update(p for p in (ROOT / 'generated/revision_20261104').glob('*')
                   if p.is_file() and p.suffix in {'.csv', '.json'})
    diagnostic = ROOT / 'experiments/channel_information_20261112'
    sources.update(p for p in diagnostic.glob('*')
                   if p.is_file() and p.suffix in {'.py', '.json', '.csv', '.md', '.npz'})
    for folder in ('channel_profile_20261112', 'hbg_verification_20261112'):
        sources.update(p for p in (ROOT / 'experiments' / folder).glob('*')
                       if p.is_file() and p.suffix in {'.py', '.json', '.csv', '.md', '.txt'})
    sources.add(ROOT / 'docs/HBG_REPRODUCTION_AUDIT_20261112.md')
    manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}
    instructions = '''P07 article and supplement source snapshot

Compile main.tex and supplement.tex separately with pdfLaTeX, BibTeX and two
further pdfLaTeX passes. IEEEtran.bst may be supplied by your TeX distribution.
All local files actually read by these builds are included with their paths.
Comparator provenance is independently regenerated, without models or PMU data,
with Python: python scripts/build_comparator_lineage.py.
The editable overview and physical/report diagrams are TikZ vector figures.
Regenerate them with python scripts/build_recovery_overview.py and
python scripts/build_physics_measurement_chain.py (pdfLaTeX and PyMuPDF required).
The current half-page Figure 1 is built by:
python scripts/build_paper_method_figure.py
Local mathematical checks use the bundled verified kernel:
python scripts/verify_history_partition.py (requires NumPy and SciPy).
Predictive sufficiency, mixture moments and deterministic post-processing have
small finite-enumeration checks: python scripts/verify_recovery_distribution.py.
These small checks do not rerun the nonlinear scientific campaigns.
The deterministic terminal-current diagnostic reproduces from its compact
operator snapshot, without the scientific repository or campaign files:
python experiments/channel_information_20261112/run_channel_diagnostic.py
python scripts/build_channel_information_figure.py
The bounded-rival severity successor uses the same nominal snapshot:
python experiments/channel_profile_20261112/run.py
python scripts/build_channel_profile_figure.py
Independent illustrative Gaussian/energy checks (not IEEE-39 outcomes):
python experiments/hbg_verification_20261112/verify_extended.py
See that experiment's README for dependencies and the fixed-mean scope.
The PDF copies are supplied separately in output/pdf in the working repository.

This is a review snapshot, not a certificate of submission readiness. C01 and
A01, B01 and C02 are complete frozen evidence. The successor mechanism and
transfer study, and final author declarations, remain subject
to the current repository status. No external submission is performed.
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
