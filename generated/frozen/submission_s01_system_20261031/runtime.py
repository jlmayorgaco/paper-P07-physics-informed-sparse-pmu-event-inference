"""One causal publication stream from sealed physical/source and cyber components.

This composes existing predictions. It neither reruns nor changes a detector.
Completed intervals never change the current missing-PMU state.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import heapq
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'protocol/SYSTEM_COMPOSITION_PLAN.json'
OUTPUT = ROOT / 'run/system_composition_v1'
HYBRID = ROOT / 'run/ml_raw_segmented'
CYBER = ROOT / 'run/cyber_composition_v2'
PREFIX = ROOT / 'run/raw_physical_prefix/RESULT.json'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def check_clock(message, used_key='last_report_used_s'):
    emitted = float(message['emitted_s'])
    used = float(message[used_key])
    if not math.isfinite(emitted) or not math.isfinite(used) or used < 0 or used > emitted:
        raise ValueError('Invalid causal component clock')
    return emitted


def completed_window(physical, integrity):
    """Join explicitly selected planes, never using a broad dictionary update."""
    for key in ('window_index', 'window_start_s', 'window_end_s', 'legacy_event', 'available'):
        if physical[key] != integrity[key]:
            raise ValueError('Incompatible window components: ' + key)
    if physical['window_start_s'] >= physical['window_end_s']:
        raise ValueError('Invalid interval')
    if integrity.get('interval_diagnosis') is not True or integrity.get('asserts_current_ongoing_corruption') is not False:
        raise ValueError('Integrity diagnosis must concern a completed interval')
    pt = check_clock(physical)
    it = check_clock(integrity)
    # A received final sample can precede the nominal half-open boundary.
    if max(pt, it) > physical['window_end_s'] + 1e-7:
        raise ValueError('Component emission outside the completed-window contract')
    return dict(
        kind='completed_window', scope='observed_interval', window_index=physical['window_index'],
        window_start_s=physical['window_start_s'], window_end_s=physical['window_end_s'],
        emitted_s=max(pt, it), last_report_used_s=max(physical['last_report_used_s'], integrity['last_report_used_s']),
        available=physical['available'],
        physical=dict(event=physical['physical_event'], source=physical['physical_source'],
                      source_route=physical['source_route'], component_emitted_s=pt,
                      last_report_used_s=physical['last_report_used_s'],
                      fallback_reason=physical['fallback_reason'],
                      hybrid_source_changed=physical['hybrid_source_changed'],
                      eligible_diagnosis_ids=copy.deepcopy(physical['eligible_diagnosis_ids']),
                      ml_status_report_counts=copy.deepcopy(physical['ml_status_report_counts']),
                      selected_ml_diagnosis=copy.deepcopy(physical.get('selected_ml_diagnosis'))),
        integrity=dict(status=integrity['integrity_status'], sources=copy.deepcopy(integrity['integrity_sources']),
                       diagnoses=copy.deepcopy(integrity['integrity_diagnoses']), component_emitted_s=it,
                       last_report_used_s=integrity['last_report_used_s']),
        legacy_export=dict(event=physical['legacy_event'], location=physical['legacy_location'],
                           original_location=physical['zip_original_location'],
                           original_top3=copy.deepcopy(physical['legacy_top3'])),
        changes_current_availability=False, asserts_current_ongoing_corruption=False,
        asserts_physical_restoration=False, malicious_intent_inferred=False)


def availability_message(original):
    message = copy.deepcopy(original)
    message['last_report_used_s'] = message.pop('last_report_s')
    check_clock(message)
    if message['plane'] != 'integrity' or message['kind'] not in ('alarm', 'diagnosis', 'restoration', 'superseded', 'right_censored'):
        raise ValueError('Invalid availability message')
    message.update(scope='current_report_availability', origin='CYBER_V2',
                   stream='availability', malicious_intent_inferred=False)
    if message['kind'] == 'diagnosis' and message['family'] != 'missing':
        raise ValueError('Only missingness is persistent in this interface')
    return message


def ordered_stream(availability, windows, statuses):
    """Merge monotone input streams without using a later diagnosis to revise one."""
    streams = [availability, windows, statuses]
    for stream in streams:
        times = [check_clock(message) for message in stream]
        if any(a > b for a, b in zip(times, times[1:])):
            raise ValueError('Input stream is not chronological')
    tagged = [[(m['emitted_s'], stream_id, ordinal, m) for ordinal, m in enumerate(stream)]
              for stream_id, stream in enumerate(streams)]
    return [dict(item[3], publication_index=index)
            for index, item in enumerate(heapq.merge(*tagged))]


class AvailabilityState:
    """Example consumer: completed-window evidence cannot reopen a missing episode."""
    def __init__(self):
        self.missing = ()
        self.episode = None
        self.last_emitted = -math.inf

    def apply(self, message):
        emitted = check_clock(message)
        if emitted < self.last_emitted:
            raise ValueError('Consumer messages must be chronological')
        self.last_emitted = emitted
        if message['scope'] == 'current_report_availability':
            kind = message['kind']
            if kind == 'alarm':
                self.episode = message['episode']
            elif message['episode'] != self.episode:
                raise ValueError('Availability episode mismatch')
            elif kind == 'diagnosis':
                if message['family'] != 'missing':
                    raise ValueError('Unsupported persistent integrity diagnosis')
                self.missing = tuple(message['source'])
            elif kind in ('restoration', 'superseded'):
                self.missing = ()
                self.episode = None
            elif kind != 'right_censored':
                raise ValueError('Unsupported availability transition')
        elif message['scope'] in ('observed_interval', 'current_component_availability'):
            if message['changes_current_availability'] is not False:
                raise ValueError('Non-availability message tries to change current missingness')
        else:
            raise ValueError('Unknown publication scope')
        return self.missing


def input_files():
    paths = [HYBRID/'PREDICTIONS_SEAL.json', CYBER/'PREDICTIONS_SEAL.json', PREFIX]
    for folder in (HYBRID, CYBER):
        seal = read(folder/'PREDICTIONS_SEAL.json')
        for name, fingerprint in seal['files'].items():
            path = (folder/name).resolve()
            if not path.is_relative_to(folder.resolve()) or sha(path) != fingerprint:
                raise ValueError('Component seal mismatch: ' + name)
            paths.append(path)
    return paths


def freeze_plan():
    if PLAN.exists():
        raise FileExistsError(PLAN)
    files = input_files()
    save(PLAN, dict(id='S01_UNIFIED_PUBLICATION_V1',
        status='FROZEN_BEFORE_COMPOSITION_AFTER_COMPONENT_EVALUATION',
        component_results_already_known=True, new_performance_selection=False,
        runtime_sha256=sha(Path(__file__)), input_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in files},
        physical_plane='Unmodified sealed ZIP/SHORT hybrid completed windows',
        integrity_plane='Cyber V2 interval diagnoses plus its immediate missingness messages',
        current_state='Only current-report availability messages can update missingness; completed windows never reopen it',
        corruption='Interval assertion only; no backdating, forward filling or invented restoration',
        physical_inference='R11 unavailable under the frozen startup gate; do not relabel ML as R11',
        missing_and_startup='Retain every report and unavailable ML status; never encode unavailable as E0',
        clock='Merged delivery uses maximum component emission; each original component emission remains explicit',
        evaluation='Post-seal exact projections to existing components, not a newly optimized global score',
        truth_used=False, raw0002_access=False, c01_access=False))
    print('SYSTEM_PLAN_FROZEN', sha(PLAN), flush=True)


def install_boundary(allowed):
    allowed = {p.resolve() for p in allowed}
    seen = set()
    def audit(event, args):
        if event != 'open' or not isinstance(args[0], (str, bytes)):
            return
        path = Path(args[0]).resolve()
        if not path.is_relative_to(ROOT.parents[1]):
            return
        if path not in allowed and not path.is_relative_to(OUTPUT):
            raise PermissionError('System publication read boundary rejected: ' + str(path))
        seen.add(path.as_posix())
    sys.addaudithook(audit)
    return seen


def run():
    import numpy as np
    if OUTPUT.exists():
        raise FileExistsError('Use a new successor instead of overwriting system publication')
    plan = read(PLAN)
    allowed = [ROOT/name for name in plan['input_sha256']] + [PLAN, Path(__file__)]
    reads = install_boundary(allowed)
    if sha(Path(__file__)) != plan['runtime_sha256']:
        raise ValueError('Frozen runtime changed')
    for name, expected in plan['input_sha256'].items():
        if sha(ROOT/name) != expected:
            raise ValueError('Frozen component changed: ' + name)
    hybrid = read(HYBRID/'hybrid_predictions.json')
    cyber = read(CYBER/'prediction.json')
    ml = read(HYBRID/'prediction.json')
    prefix = read(PREFIX)
    if prefix['available'] is not False or not all(x['truth_read'] is False for x in (hybrid, cyber, ml)):
        raise ValueError('Unexpected component scope')
    if hybrid['zip_prediction_sha256'] != cyber['legacy_predictions_sha256']:
        raise ValueError('Components do not share the same sealed ZIP replay')
    physical_windows = hybrid['windows']
    cyber_windows = cyber['window_diagnoses']
    if len(physical_windows) != len(cyber_windows) or len(physical_windows) != 180:
        raise ValueError('Incomplete common-window collection')
    windows = [completed_window(p, c) for p, c in zip(physical_windows, cyber_windows)]
    with np.load(CYBER/'availability.npz', allow_pickle=False) as z:
        at = z['time_s'].copy(); missing = z['missing_pmu'].copy(); pmus = z['pmus'].copy()
    with np.load(HYBRID/'prediction.npz', allow_pickle=False) as z:
        mt = z['time_s'].copy(); status = z['status'].copy(); public = z['source_label'].copy()
    if at.shape != mt.shape or not np.allclose(at, mt, atol=1e-7, rtol=0):
        raise ValueError('Report clocks disagree')
    if missing.shape != (len(at), len(pmus)) or status.shape != at.shape:
        raise ValueError('Report coverage differs')
    if not np.array_equal(public[status != 2], np.full(np.count_nonzero(status != 2), -1)):
        raise ValueError('Unavailable ML reports were converted to normal')
    changes = np.r_[0, np.flatnonzero(status[1:] != status[:-1]) + 1]
    statuses = [dict(kind='component_status', component='SEGMENT_INITIALIZED_SIM_ET_SHORT',
                     scope='current_component_availability', report_index=int(k),
                     status_code=int(status[k]), status=ml['status_codes'][str(int(status[k]))],
                     emitted_s=float(max(at[k], mt[k])), last_report_used_s=float(max(at[k], mt[k])),
                     source_component_emitted_s=float(mt[k]), changes_current_availability=False)
                for k in changes]
    availability = [availability_message(m) for m in cyber['availability_messages']]
    messages = ordered_stream(availability, windows, statuses)
    OUTPUT.mkdir(parents=True)
    np.savez_compressed(OUTPUT/'report_status.npz', availability_time_s=at, ml_time_s=mt,
                        missing_pmu=missing, pmus=pmus, ml_status=status, ml_source_label=public)
    save(OUTPUT/'prediction.json', dict(method='S01_COMPOSED_PHYSICAL_AND_INTEGRITY_PUBLICATION',
        messages=messages, completed_windows=windows, truth_read=False, component_inference_reexecuted=False,
        new_independent_performance_result=False, reports=len(at), windows=len(windows),
        physical_filter=dict(method='R11', available=False, reason=prefix, evidence_sha256=sha(PREFIX)),
        component_lineage=plan['input_sha256'], protocol_sha256=sha(PLAN), runtime_sha256=sha(Path(__file__)),
        malicious_intent_inferred=False, persistent_corruption_inferred=False,
        component_performance_changed=False))
    save(OUTPUT/'READ_AUDIT.json', dict(paths=sorted(reads), truth_read=False, evaluation_read=False))
    save(OUTPUT/'PREDICTIONS_SEAL.json', dict(files={name:sha(OUTPUT/name) for name in
        ['prediction.json','report_status.npz','READ_AUDIT.json']}, protocol_sha256=sha(PLAN), truth_read=False))
    print('SYSTEM_PUBLICATION_SEALED', len(messages), 'messages', len(windows), 'windows', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['freeze-plan', 'run'])
    {'freeze-plan':freeze_plan, 'run':run}[parser.parse_args().action]()
