"""Reproduce comparator provenance from frozen metadata, without inference.

Default execution is self-contained in P07. The optional one-time capture reads
the research repository and inspects the two serialized models only after their
SHA-256 values match both COMPLETE.json and the pre-C01 reference freeze.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'generated/frozen/comparator_lineage_20261103'
ML = 'experiments/E5_VALIDATION_PAPER/M03_R09_NUISANCE_DEV/ml'
REFERENCE = 'generated/frozen/continuous_20261029/C01/references/R11_FREEZE.json'
EXECUTION = 'generated/frozen/c01_20261029/EXECUTION_FREEZE.json'
SOURCES = {
    'COMPLETE.json': f'{ML}/COMPLETE.json',
    'PROTOCOL.json': f'{ML}/PROTOCOL.json',
    'infer.py': f'{ML}/infer.py',
    'run.py': f'{ML}/run.py',
    'causal_ml.py': f'{ML}/causal_ml.py',
    'common.py': 'experiments/PAPER_CONFIRMATORY_C01/execution/common.py',
    'worker.py': 'experiments/PAPER_CONFIRMATORY_C01/execution/worker.py',
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def capture(research):
    if SNAPSHOT.exists():
        raise FileExistsError('Snapshot already exists; preserve it and create a successor for changes.')
    frozen = {}
    for relative in (REFERENCE, EXECUTION):
        frozen.update({item['path']: item['sha256'] for item in read(ROOT / relative)['files']})
    data = {}
    provenance = []
    for name, relative in SOURCES.items():
        path = research / relative
        digest = sha(path)
        if relative in frozen:
            assert digest == frozen[relative], relative
        data[name] = path.read_bytes()
        provenance.append({'snapshot_file': name, 'source_path': relative,
                           'sha256': digest, 'checked_against_pre_C01_freeze': relative in frozen})
    complete = json.loads(data['COMPLETE.json'])
    assert sha(research / f'{ML}/PROTOCOL.json') == complete['config_sha256']
    expected = {item['variant']: item['sha256'] for item in complete['models']}
    # Hash validation precedes unpickling; no prediction or fitting is called.
    import joblib
    inspections = []
    for variant in ('BASELINE', 'SHORT'):
        relative = f'{ML}/models/{variant}.joblib'
        path = research / relative
        digest = sha(path)
        assert digest == expected[variant] == frozen[relative], relative
        bundle = joblib.load(path)
        model = bundle['model']
        inspections.append({
            'variant': variant, 'source_path': relative, 'sha256': digest,
            'class_name': type(model).__name__, 'features': int(model.n_features_in_),
            'trees': int(model.n_estimators), 'class_indices': model.classes_.tolist(),
            'class_names': list(bundle['names']),
            'model_parameters': {key: model.get_params()[key] for key in
                                 ('min_samples_leaf', 'max_features', 'class_weight', 'random_state')},
        })
        del bundle, model
    SNAPSHOT.mkdir(parents=True)
    for name, contents in data.items():
        (SNAPSHOT / name).write_bytes(contents)
    write(SNAPSHOT / 'MODEL_INSPECTION.json', {'scope': 'Verified serialization metadata only; no inference',
                                             'models': inspections})
    write(SNAPSHOT / 'MANIFEST.json', {
        'scope': 'Training lineage and artifact identity; no performance outcomes or campaign data',
        'sources': provenance,
        'reference_manifests': [{'path': p, 'sha256': sha(ROOT / p)} for p in (REFERENCE, EXECUTION)],
        'reference_entries': {path: frozen[path] for path in
                              [*SOURCES.values(), *[item['source_path'] for item in inspections]]
                              if path in frozen},
        'model_inspection_sha256': sha(SNAPSHOT / 'MODEL_INSPECTION.json'),
    })


def verify_models(research):
    """Optional local check; keep default regeneration independent of joblib."""
    import joblib
    import sklearn
    inspections = read(SNAPSHOT / 'MODEL_INSPECTION.json')['models']
    for item in inspections:
        path = research / item['source_path']
        assert sha(path) == item['sha256'], item['source_path']
        bundle = joblib.load(path)
        model = bundle['model']
        assert int(model.n_features_in_) == item['features']
        assert int(model.n_estimators) == item['trees']
        assert model.classes_.tolist() == item['class_indices']
        assert list(bundle['names']) == item['class_names']
        assert type(model).__name__ == item['class_name']
        assert {key: model.get_params()[key] for key in item['model_parameters']} == item['model_parameters']
        del bundle, model
    print(json.dumps({'local_serializations_match_snapshot': True,
                      'sklearn_version': sklearn.__version__, 'inference_called': False}))


def generate():
    manifest = read(SNAPSHOT / 'MANIFEST.json')
    for item in manifest['sources']:
        assert sha(SNAPSHOT / item['snapshot_file']) == item['sha256'], item['snapshot_file']
        if item['checked_against_pre_C01_freeze']:
            assert manifest['reference_entries'][item['source_path']] == item['sha256']
    assert sha(SNAPSHOT / 'MODEL_INSPECTION.json') == manifest['model_inspection_sha256']
    for item in manifest['reference_manifests']:
        if (ROOT / item['path']).exists():
            assert sha(ROOT / item['path']) == item['sha256'], item['path']
    complete, protocol = read(SNAPSHOT / 'COMPLETE.json'), read(SNAPSHOT / 'PROTOCOL.json')
    models = read(SNAPSHOT / 'MODEL_INSPECTION.json')['models']
    assert complete['success'] and not complete['test_access'] and not protocol['test_access_C01']
    assert sha(SNAPSHOT / 'PROTOCOL.json') == complete['config_sha256']
    assert (complete['parents_train'], complete['parents_validation'], complete['validation_records']) == (32, 8, 16)
    expected = {item['variant']: item['sha256'] for item in complete['models']}
    for model in models:
        assert model['sha256'] == expected[model['variant']]
        assert model['sha256'] == manifest['reference_entries'][model['source_path']]
        assert model['class_name'] == 'ExtraTreesClassifier' and model['trees'] == protocol['trees'] == 400
        assert model['class_indices'] == list(range(19)) and len(model['class_names']) == 19
        assert model['class_names'][0] == 'E0'
    assert models[0]['class_names'] == models[1]['class_names']
    assert [model['features'] for model in models] == [846, 1457]
    source = {name: (SNAPSHOT / name).read_text(encoding='utf-8') for name in
              ('infer.py', 'run.py', 'causal_ml.py', 'common.py', 'worker.py')}
    assert "ML=BASE/'M03_R09_NUISANCE_DEV/ml'" in source['common.py']
    assert "[('BASELINE','ET_REFERENCE'),('SHORT','ET_CANDIDATE')]" in source['worker.py']
    assert "for variant in ['BASELINE','SHORT']" in source['infer.py']
    assert 'raw=np.argmax(scores,axis=1)' in source['infer.py']
    assert 'EpisodeAdapter(names,assets,6)' in source['infer.py']
    assert 'if k<360 or self.run<self.n:return self.current' in source['causal_ml.py']
    assert "assert len(np.unique(y))==19" in source['run.py']
    output = {
        'scope': manifest['scope'],
        'training_parents': complete['parents_train'],
        'validation_parents': complete['parents_validation'],
        'validation_records': complete['validation_records'],
        'train_campaigns': protocol['train_campaigns'],
        'validation_campaign': protocol['validation_campaign'],
        'target': protocol['target'], 'test_access_during_training': False,
        'fitted_classes': models[0]['class_names'], 'models': models,
        'C01_mapping': {'ET_REFERENCE': 'BASELINE', 'ET_CANDIDATE': 'SHORT'},
        'publication': {'decision': 'argmax tree vote; six consecutive reports',
                        'first_decision_index_zero_based': protocol['first_decision'],
                        'prefix_reports': protocol['reference_reports'],
                        'independent_probability_trigger': False,
                        'votes_calibrated': False},
        'original_hackathon_serializations_loaded_by_C01': False,
        'provenance': {'snapshot': SNAPSHOT.relative_to(ROOT).as_posix(),
                       'snapshot_manifest_sha256': sha(SNAPSHOT / 'MANIFEST.json'),
                       'source_files': manifest['sources'],
                       'pre_C01_manifests': manifest['reference_manifests']},
    }
    write(ROOT / 'generated/comparator_lineage.json', output)
    # Reader-facing text: no code names, paths, hashes or internal campaign identifiers
    # (those remain in generated/comparator_lineage.json for the reproduction package).
    # Reader-facing text: no code names, paths, hashes or internal campaign identifiers
    # (those remain in generated/comparator_lineage.json for the reproduction package).
    rows = []
    for label, model in zip(('ExtraTrees', 'ExtraTrees short'), models):
        windows = '1, 5, 10 s' if label == 'ExtraTrees' else '1, 5, 10 s; 3, 8, 15 reports'
        rows.append(f"{label} & {model['features']} & {windows} & {model['trees']}" + '\\\\')
    table = [r'\begin{table}[t]\centering\small',
             r'\caption{Fitted ExtraTrees comparators used in the held-out streams. Both were trained for this study and are distinct from the original competition models.}',
             r'\label{tab:comparator-lineage}',
             r'\begin{tabular}{@{}lrlr@{}}\toprule',
             r'Comparator & Features & Windows & Trees\\\midrule',
             *rows, r'\bottomrule\end{tabular}', r'\end{table}', '',
             f"Both models were fitted on {complete['parents_train']} physical parents from four",
             'earlier development campaigns; validation used',
             f"{complete['parents_validation']} parents and {complete['validation_records']} observed records from a fifth campaign.",
             'All of these were development data for the comparator construction.',
             'The fitted label set contains normal operation and all 18 catalog',
             'sources. The training target is the active source; after restoration,',
             'including physical recovery, its label is normal. This is not a',
             'source-excluded transfer test.', '',
             'Each report selects the largest tree vote, and six consecutive',
             'reports of the same label drive the episode interface; there is no',
             'separate probability threshold. Tree votes are uncalibrated; the',
             '300-report prefix and the start of monitoring at report 360 are fixed.',
             'Model hashes, training metadata and the observed class set are kept',
             'in the reproducibility package.', '']
    destination = ROOT / 'tables/generated/comparator_lineage.tex'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text('\n'.join(table), encoding='utf-8')
    print(json.dumps({'models': len(models), 'train_parents': output['training_parents'],
                      'validation_parents': output['validation_parents'],
                      'source': output['provenance']['snapshot'],
                      'campaigns_run': False, 'predictions_read': False}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture-from', type=Path, help='One-time capture from the trusted research checkout')
    parser.add_argument('--verify-models-from', type=Path, help='Optional hash-first local serialization metadata check')
    arguments = parser.parse_args()
    if arguments.capture_from:
        capture(arguments.capture_from.resolve())
    generate()
    if arguments.verify_models_from:
        verify_models(arguments.verify_models_from.resolve())
