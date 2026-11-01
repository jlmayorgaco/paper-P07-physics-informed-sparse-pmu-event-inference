"""Import the sealed retrospective source-only RAW hybrid comparison."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01'
FROZEN = ROOT / 'generated/frozen/submission_s01_raw_hybrid_20261031'


def main():
    files = {
        'comparison.json': 'run/ml_raw_segmented/PHYSICAL_METADATA_COMPARISON.json',
        'prediction_seal.json': 'run/ml_raw_segmented/PREDICTIONS_SEAL.json',
        'hybrid_predictions.json': 'run/ml_raw_segmented/hybrid_predictions.json',
        'checks.json': 'run/ml_raw_segmented/CHECKS.json',
        'read_audit.json': 'run/ml_raw_segmented/READ_AUDIT.json',
        'inference_plan.json': 'protocol/ML_RAW_HYBRID_PLAN.json',
        'evaluation_protocol.json': 'evaluation/PHYSICAL_METADATA_COMPARISON_PROTOCOL.json',
        'protocol_freeze.json': 'evaluation/PHYSICAL_METADATA_PROTOCOL_FREEZE.json',
        'metadata_audit.json': 'evaluation/RAW_PHYSICAL_METADATA_AUDIT.json',
        'validation.json': 'evaluation/PHYSICAL_METADATA_VALIDATION.json',
        'evaluation.py': 'evaluation/score_physical_metadata.py',
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
    result = json.loads((FROZEN / 'comparison.json').read_text(encoding='utf-8'))
    assert result['prior_artifacts_unchanged'] and not result['model_or_routing_changed_by_evaluation']
    assert result['routing']['class_changes'] == 0
    values = {}
    for prefix, method in [('RawZIP', 'native'), ('RawHybrid', 'hybrid')]:
        row = result['results']['methods'][method]
        values[prefix + 'Joint'] = row['joint_any']['correct']
        values[prefix + 'Total'] = row['joint_any']['total']
    paired = result['results']['paired_positive']
    values.update(RawHybridGains=paired['gain'], RawHybridLosses=paired['loss'],
                  RawHybridRoutes=result['routing']['ML_selected'],
                  RawHybridFallbacks=result['routing']['windows'] - result['routing']['ML_selected'],
                  RawHybridSegments=len(result['segments']['segments']))
    macros = '% Generated from the metadata-based RAW comparison; not an official score.\n'
    macros += ''.join('\\newcommand{\\' + key + '}{' + str(value) + '}\n' for key, value in values.items())
    (ROOT / 'generated/submission_s01_raw_macros.tex').write_text(macros, encoding='utf-8')
    table = r'''% Generated from sealed predictions; all positive windows retained.
\begin{table}[t]\centering
\caption{Retrospective RAW family-and-source correctness on every physical-positive window, using the archived source metadata and current event-code support. Multiple windows from a sustained annotation are not independent actions.}
\label{tab:raw-source-hybrid}
\small\setlength{\tabcolsep}{5pt}
\begin{tabular}{lrr}\hline
Family & Submitted ZIP & Source hybrid\\\hline
'''
    for key, label in [('fault', 'Fault'), ('line_outage', 'Line'), ('generation_change', 'Generation'), ('load_change', 'Load')]:
        row = result['results']['per_family'][key]
        table += f"{label} & {row['native_joint']}/{row['positive_windows']} & {row['hybrid_joint']}/{row['positive_windows']} " + r'\\' + '\n'
    table += f"Total & {values['RawZIPJoint']}/{values['RawZIPTotal']} & {values['RawHybridJoint']}/{values['RawHybridTotal']} " + r'\\' + '\n'
    table += '\\hline\\end{tabular}\n\\end{table}\n'
    (ROOT / 'tables/generated/raw_source_hybrid.tex').write_text(table, encoding='utf-8')
    print(json.dumps(dict(imported_files=len(files), paired=paired, C01_accessed=False)))


if __name__ == '__main__':
    main()
