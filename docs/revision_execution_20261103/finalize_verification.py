"""Record the checked revision; does not run or evaluate scientific campaigns."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RESEARCH = ROOT.parent / 'SGSMA26-Physics-Informed-AD'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    validation = read(ROOT / 'output/source/SOURCE_PACKAGE_VALIDATION.json')
    assert validation['status'] == 'PASS'
    assert validation['source_package_sha256'] == sha(ROOT / 'output/source/P07_Article_Supplement_Source.zip')
    protected = subprocess.run([sys.executable, '-B', 'scripts/verify_protected_figures.py', '--pdf', 'main.pdf'],
                               cwd=ROOT, capture_output=True, text=True, check=True)
    frozen_changes = subprocess.run(['git', 'diff', '--name-only', '--', 'generated/frozen/c01_20261029',
                                    'generated/frozen/ablation_a01_20261102', 'figures/frozen'],
                                   cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    assert not frozen_changes
    pdfs = {}
    for doc in ('main', 'supplement', 'historical_notes'):
        log = (ROOT / (doc + '.log')).read_text(errors='replace')
        assert not any(t in log for t in ('There were undefined references', 'There were multiply-defined labels',
                                          'Rerun to get cross-references right'))
        pdf = ROOT / (doc + '.pdf')
        pages = len(pymupdf.open(pdf))
        renders = [ROOT / 'tmp/pdfs/revision_20261103' / f'{doc}_{n:02}.png' for n in range(1, pages + 1)]
        assert all(p.is_file() for p in renders)
        pdfs[doc] = dict(pages=pages, sha256=sha(pdf), rendered_pages=len(renders),
                         render_sha256={p.name: sha(p) for p in renders})
    c02 = RESEARCH / 'experiments/PAPER_RECOVERY_C02/run'
    b01 = read(RESEARCH / 'experiments/PAPER_CALIBRATION_B01/run/PIPELINE_STAGE.json')
    result = dict(status='VERIFIED_DOCUMENT_REVISION_EMPIRICAL_VALIDATION_PENDING',
                  created_utc=datetime.now(timezone.utc).isoformat(), baseline=read(HERE / 'BASELINE_MANIFEST.json'),
                  protected_figures=json.loads(protected.stdout), frozen_C01_A01_figure_changes=[],
                  mathematical_checks=read(ROOT / 'generated/revision_math_20261103/checks.json')['summary'],
                  math_scope=read(ROOT / 'generated/revision_math_20261103/checks.json')['scope'],
                  math_portability=read(ROOT / 'generated/revision_math_20261103/PORTABILITY.json'),
                  comparator_lineage=read(HERE / 'COMPARATOR_LINEAGE_VERIFICATION.json'),
                  source_package_validation=validation, pdfs=pdfs,
                  visual_review=dict(main='All 16 pages via contacts; protected figures at final page size',
                                     supplement='All 19 pages via contacts; equations and A01 tables at final page size; body text overflows corrected',
                                     historical='All pages via contacts, changed equations and final pages at final page size; see HISTORICAL_VISUAL_QA.md',
                                     coauthor_brief='One page at final size',
                                     class_font_and_header_warnings='Retained template warnings; not described as a warning-free TeX build'),
                  campaign_snapshot=dict(B01=b01, C02=read(c02 / 'STATUS.json'),
                                         queue=read(c02 / 'QUEUE_STATUS.json') if (c02 / 'QUEUE_STATUS.json').exists() else None),
                  new_empirical_outcomes_in_article=0, submission_ready=False, pushed=False,
                  coauthor_or_journal_messages_sent=False, raw0002_opened=False)
    save(HERE / 'FINAL_VERIFICATION.json', result)
    manifest_path = ROOT / 'docs/editorial_closure/FINAL_MANIFEST.json'
    previous = read(manifest_path)
    paths = {entry['path'] for entry in previous['files']}
    paths.update(p.relative_to(ROOT).as_posix() for folder in (HERE, ROOT / 'generated/revision_math_20261103')
                 for p in folder.glob('*') if p.is_file() and p.suffix in ('.md', '.json', '.py'))
    paths.update(('generated/comparator_lineage.json', 'scripts/build_comparator_lineage.py',
                  'scripts/verify_history_partition.py', 'supplement/implemented_filter_details.tex',
                  'supplement/ablation_a01.tex', 'output/source/SOURCE_PACKAGE_VALIDATION.json'))
    entries = [dict(path=n, sha256=sha(ROOT / n), bytes=(ROOT / n).stat().st_size)
               for n in sorted(paths) if (ROOT / n).is_file() and n != manifest_path.relative_to(ROOT).as_posix()]
    save(manifest_path, dict(status=result['status'], created_utc=result['created_utc'],
                             page_counts=dict(article=pdfs['main']['pages'], supplement=pdfs['supplement']['pages'],
                                              historical_notes=pdfs['historical_notes']['pages'], review_bundle=35, coauthor_brief=1),
                             checks=result['protected_figures'], source_package_validation=validation,
                             revision_verification='docs/revision_execution_20261103/FINAL_VERIFICATION.json',
                             author_declarations_open=True, scientific_comparison_gaps_open=True, files=entries))
    print(json.dumps(dict(status=result['status'], pages={k:v['pages'] for k,v in pdfs.items()},
                          source_inputs=validation['input_files'], files_hashed=len(entries)), indent=2))


if __name__ == '__main__':
    main()
