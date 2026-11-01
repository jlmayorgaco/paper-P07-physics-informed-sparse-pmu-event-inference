"""Import the independently verified composition without creating new scores."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01'
FROZEN = ROOT / 'generated/frozen/submission_s01_system_20261031'


def main():
    files = {
        'validation.json': 'evaluation/SYSTEM_COMPOSITION_V1_VALIDATION.json',
        'plan.json': 'protocol/SYSTEM_COMPOSITION_PLAN.json',
        'prediction_seal.json': 'run/system_composition_v1/PREDICTIONS_SEAL.json',
        'read_audit.json': 'run/system_composition_v1/READ_AUDIT.json',
        'runtime.py': 'runtime/system_replay.py',
        'verifier.py': 'evaluation/verify_system_composition_v1.py',
    }
    data = {name: (SOURCE / path).read_bytes() for name, path in files.items()}
    result = json.loads(data['validation.json'])
    if result['status'] != 'PASS_EXACT_COMPONENT_EQUIVALENCE' or not result['prior_artifacts_unchanged']:
        raise ValueError('Unverified system composition')
    for name, key in [('plan.json','plan_sha256'), ('runtime.py','runtime_sha256'),
                      ('verifier.py','verifier_sha256'), ('prediction_seal.json','output_seal_sha256')]:
        if hashlib.sha256(data[name]).hexdigest() != result[key]:
            raise ValueError('Composition lineage changed: ' + name)
    if result['reconstructed_missing_disagreement_rows'] or result['reconstructed_ml_status_disagreement_rows']:
        raise ValueError('Composition changes report state')
    FROZEN.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, content in data.items():
        target = FROZEN / name
        if target.exists() and target.read_bytes() != content:
            raise ValueError('Frozen system import changed: ' + name)
        if not target.exists():
            target.write_bytes(content)
        manifest[name] = dict(source=str(SOURCE / files[name]), sha256=hashlib.sha256(content).hexdigest())
    (FROZEN / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    values = dict(SystemWindows=result['windows'], SystemReports=result['reports'],
                  SystemMessages=result['messages'])
    tex = '% Exact composition equivalence; these counts are not new performance results.\n'
    tex += ''.join('\\newcommand{\\' + name + '}{' + str(value) + '}\n' for name, value in values.items())
    (ROOT / 'generated/submission_s01_system_macros.tex').write_text(tex, encoding='utf-8')
    print(json.dumps(dict(imported_files=len(files), **values, new_performance_claim=False)))


if __name__ == '__main__':
    main()
