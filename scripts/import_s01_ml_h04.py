"""Import the observation-only replay of the frozen classifier on common H04."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01'
FROZEN = ROOT / 'generated/frozen/submission_s01_ml_h04_20261031'


def main():
    files = {
        'evaluation.json': 'run/ml_h04_v2/EVALUATION.json',
        'inference_complete.json': 'run/ml_h04_v2/INFERENCE_COMPLETE.json',
        'protocol.json': 'protocol/ML_H04_V2_PLAN.json',
        'results.md': 'run/ml_h04_v2/RESULTS.md',
        'v1_deviation.md': 'run/ml_h04/AUDIT_DEVIATION.md',
    }
    FROZEN.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, relative in files.items():
        source = SOURCE / relative
        data = source.read_bytes()
        target = FROZEN / name
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f'Frozen artifact changed: {name}')
        if not target.exists():
            target.write_bytes(data)
        manifest[name] = dict(source=str(source), sha256=hashlib.sha256(data).hexdigest())
    (FROZEN / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    evidence = json.loads((FROZEN / 'evaluation.json').read_text(encoding='utf-8'))
    assert not evidence['inference_truth_read'] and evidence['model_and_frozen_sources_unchanged']
    row = evidence['summary'][0]
    values = {'ETCommon' + suffix: row[key] for suffix, key in [
        ('Timely', 'timely_joint'), ('Total', 'intended_events'), ('Extras', 'extras'),
        ('Orphan', 'orphan_restorations'), ('Premature', 'premature_restorations'),
        ('Missing', 'restoration_missing'), ('Load', 'load_timely'), ('Line', 'line_timely')]}
    for family in ('load', 'line'):
        values['ETCommon' + family.title() + 'Total'] = sum(
            event['family'] == family for record in evidence['records'].values() for event in record['events'])
    macros = '% Generated from observation-only H04 V2, preserving V1 and exact parity evidence.\n'
    macros += ''.join('\\newcommand{\\' + key + '}{' + str(value) + '}\n' for key, value in values.items())
    (ROOT / 'generated/submission_s01_ml_h04_macros.tex').write_text(macros, encoding='utf-8')
    print(json.dumps(dict(files=len(files), timely=row['timely_joint'], extras=row['extras'])))


if __name__ == '__main__':
    main()
