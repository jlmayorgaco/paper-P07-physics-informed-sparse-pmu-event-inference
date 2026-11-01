"""Read-only scope checks on the frozen runtime and already-open RAW0001.

Does not train, score a detector, open C01 results, or access RAW0002.
"""
from pathlib import Path
import ast
import hashlib
import json
import math

import numpy as np
import pandas as pd

PAPER = Path(__file__).resolve().parents[3]
RESEARCH = PAPER.parent / 'SGSMA26-Physics-Informed-AD'
RUNTIME = RESEARCH / 'experiments/PAPER_CONFIRMATORY_C01/run/runtime'


def main():
    source = RUNTIME / 'core_v6.py'
    # Execute only the existing observation class, without loading bank files
    # or any campaign observations. __init__ is deliberately not invoked.
    tree = ast.parse(source.read_text(encoding='utf-8'))
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Observations')
    fields = ['voltage_magnitude','voltage_angle','current_magnitude','current_angle','frequency','rocof']
    namespace = {'np': np, 'FIELDS': fields, 'wrap': lambda x: (x + 180) % 360 - 180}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
    cls = namespace['Observations']
    obj = cls.__new__(cls)
    obj.keep = [np.arange(8)] * 3 + [np.arange(7)] + [np.arange(8)] * 2
    obj.centers = [np.zeros(len(k)) for k in obj.keep]
    obj.base = [np.zeros(len(k)) for k in obj.keep]
    obj.scales = [1.0] * 6
    obj.cfg = {'common_phase_slope_deg_s': 0.0}
    obj.phase = {}
    obj.filters = [type('IdentityFilter', (), {'process': lambda self, x: x})() for _ in fields]
    report = {f: np.zeros(8) for f in fields}
    report['voltage_magnitude'][0] = np.nan
    try:
        obj.process(20.0, report)
        raise AssertionError('Expected frozen post-startup missing-data rejection')
    except ValueError as exc:
        missing_error = str(exc)

    records = []
    for path in sorted((RESEARCH / 'data/RAW0001').glob('*.csv')):
        frame = pd.read_csv(path, usecols=['Event','DATA_PRESENT'])
        records.append({'file': path.name, 'rows': len(frame),
                        'event_counts': {str(k): int(v) for k,v in frame.Event.value_counts(dropna=False).items()},
                        'data_present_counts': {str(k): int(v) for k,v in frame.DATA_PRESENT.value_counts(dropna=False).items()}})
    assert len(records) == 8
    assets_path = RESEARCH / 'experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/physics/source_runtime/model/assets.json'
    assets = json.loads(assets_path.read_text())
    output = {
        'scope': 'Availability and catalog checks only; these are NOT inference performance scores.',
        'runtime_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'missing_after_startup': {'input': 'one missing voltage magnitude at t=20s', 'outcome': missing_error},
        'admitted_catalog': assets,
        'raw0001_label_inventory': records,
        'illustrative_poisson_zero_alarm_upper95_per_hour_for_204s': -math.log(.05)/(204/3600),
        'poisson_caveat': 'Planning illustration assuming independent homogeneous Poisson exposure. H04 repeated conditions and colored noise do not establish this assumption.',
        'no_model_trained': True, 'no_detector_scored_on_raw': True,
        'c01_partial_results_read': False, 'raw0002_read': False,
    }
    destination = Path(__file__).with_suffix('.json')
    destination.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
