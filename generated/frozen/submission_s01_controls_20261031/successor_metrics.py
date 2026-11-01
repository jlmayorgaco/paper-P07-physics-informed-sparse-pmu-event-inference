"""Pure, data-independent successor metrics. No filesystem or model imports.

Times describe emitted messages, never backdated estimated onset. Source labels
are canonical adapter inputs; this module does not guess a legacy ontology.
"""
from collections import defaultdict
from math import isfinite


class ContractError(ValueError):
    """Input cannot be scored without violating the declared evaluation contract."""


KINDS = ('alarm', 'diagnosis', 'restoration', 'withdrawn', 'superseded', 'right_censored')
PLANES = ('physical', 'integrity')
TERMINAL = ('restoration', 'withdrawn', 'superseded', 'right_censored')


def _time(value, name):
    if isinstance(value, bool):
        raise ContractError(f'{name} must be a finite number')
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f'{name} must be a finite number') from exc
    if not isfinite(value) or value < 0:
        raise ContractError(f'{name} must be finite and nonnegative')
    return value


def _label(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f'{name} must be a nonempty canonical string')
    return value


def _plane(value):
    if value not in PLANES:
        raise ContractError(f'plane must be one of {PLANES}')
    return value


def _sources(value):
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple)) or not value:
        raise ContractError('source must be a string or nonempty canonical source list')
    labels = tuple(sorted(_label(v, 'source') for v in value))
    if len(labels) != len(set(labels)):
        raise ContractError('duplicate source in source set')
    return labels


def target(value):
    """Hashable compositional target: (plane, family, exact source set)."""
    return (_plane(value.get('plane', 'physical')),
            _label(value.get('family'), 'family'), _sources(value.get('source')))


def _target_json(value):
    return dict(plane=value[0], family=value[1], source=list(value[2]))


def _episode(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or str(value) == '':
        raise ContractError('episode must be a nonempty string or integer')
    return str(value)


def normalize_truth(events, horizon_s, unique_onsets=False):
    horizon = _time(horizon_s, 'horizon_s')
    if horizon == 0:
        raise ContractError('horizon_s must be positive')
    result, ids = [], set()
    for event in events:
        event_id = _label(event.get('id'), 'truth id')
        if event_id in ids:
            raise ContractError('truth ids must be globally unique')
        ids.add(event_id)
        onset = _time(event.get('onset_s'), 'onset_s')
        off = None if event.get('off_s') is None else _time(event['off_s'], 'off_s')
        if onset >= horizon or (off is not None and off <= onset):
            raise ContractError('truth requires onset < horizon and off > onset')
        result.append(dict(id=event_id, onset_s=onset, off_s=off, target=target(event)))
    result.sort(key=lambda e: (e['onset_s'], e['target'][0], e['id']))
    if unique_onsets:
        keys = [(e['target'][0], e['onset_s']) for e in result]
        if len(keys) != len(set(keys)):
            raise ContractError('simultaneous same-plane truth must be one exact-source-set event or use the window lane')
    return result


def normalize_messages(messages, horizon_s):
    """Sort and validate messages; no mutable state or caller mutation."""
    horizon = _time(horizon_s, 'horizon_s')
    result = []
    for message in messages:
        kind = message.get('kind')
        if kind not in KINDS:
            raise ContractError(f'unsupported message kind {kind!r}')
        emitted = _time(message.get('emitted_s'), 'emitted_s')
        last_report = _time(message.get('last_report_s', emitted), 'last_report_s')
        if emitted > horizon or last_report > emitted:
            raise ContractError('message exceeds horizon or uses a report after emission')
        row = dict(kind=kind, episode=_episode(message.get('episode')),
                   plane=_plane(message.get('plane', 'physical')),
                   emitted_s=emitted, last_report_s=last_report)
        if kind == 'diagnosis':
            row['target'] = target(message)
            row['top3'] = tuple(_sources(v) for v in message.get('top3', []))
            if len(row['top3']) > 3:
                raise ContractError('top3 contains more than three candidates')
        result.append(row)
    result.sort(key=lambda m: (m['emitted_s'], KINDS.index(m['kind']), m['plane'], m['episode']))
    by_episode = defaultdict(list)
    for row in result:
        by_episode[(row['plane'], row['episode'])].append(row)
    for rows in by_episode.values():
        alarms = [r for r in rows if r['kind'] == 'alarm']
        endings = [r for r in rows if r['kind'] in TERMINAL]
        diagnoses = [r for r in rows if r['kind'] == 'diagnosis']
        diagnosis_times = [d['emitted_s'] for d in diagnoses]
        if len(diagnosis_times) != len(set(diagnosis_times)):
            raise ContractError('multiple diagnoses at one timestamp need an explicit exact source set')
        if len(alarms) > 1 or len(endings) > 1:
            raise ContractError('episode must have at most one alarm and one terminal message')
        if diagnoses and not alarms:
            raise ContractError('diagnosis requires an alarm; use native_joint_messages for joint stops')
        if alarms:
            if any(r['emitted_s'] < alarms[0]['emitted_s'] for r in rows):
                raise ContractError('episode message precedes alarm')
            if endings and any(d['emitted_s'] > endings[0]['emitted_s'] for d in diagnoses):
                raise ContractError('diagnosis emitted after episode termination')
    return result


def _episodes(messages):
    grouped = defaultdict(list)
    for message in messages:
        grouped[(message['plane'], message['episode'])].append(message)
    result = []
    for (plane, episode), rows in grouped.items():
        first = lambda kind: next((r for r in rows if r['kind'] == kind), None)
        result.append(dict(plane=plane, episode=episode, alarm=first('alarm'),
                           diagnosis=first('diagnosis'), restoration=first('restoration'),
                           terminal=next((r for r in rows if r['kind'] in TERMINAL), None)))
    return sorted(result, key=lambda e: (e['alarm']['emitted_s'] if e['alarm'] else float('inf'), e['plane'], e['episode']))


def native_joint_messages(stops):
    """Explicitly expand a native alarm+source stop; never infer this from alarm.source."""
    output = []
    for stop in stops:
        target(stop)
        common = dict(episode=stop['episode'], plane=stop.get('plane', 'physical'),
                      emitted_s=stop['emitted_s'], last_report_s=stop.get('last_report_s', stop['emitted_s']))
        output.extend([dict(common, kind='alarm'),
                       dict(common, kind='diagnosis', family=stop['family'], source=stop['source'],
                            top3=stop.get('top3', []))])
    return output


def evaluate_continuous(truth, messages, horizon_s, available=True, association_cap_s=30.0):
    """C01 temporal association retained per plane; diagnosis/closure semantics clarified."""
    horizon = _time(horizon_s, 'horizon_s')
    cap = _time(association_cap_s, 'association_cap_s')
    if cap == 0:
        raise ContractError('association cap must be positive')
    events = normalize_truth(truth, horizon, unique_onsets=True)
    episodes = _episodes(normalize_messages(messages, horizon)) if available else []
    used, rows = set(), []
    for index, event in enumerate(events):
        plane, family, sources = event['target']
        next_on = next((e['onset_s'] for e in events[index + 1:] if e['target'][0] == plane), None)
        bounds = [event['onset_s'] + cap]
        if next_on is not None:
            bounds.append(next_on)
        exclusive_bound = min(bounds)
        candidates = [ep for ep in episodes if ep['alarm'] and (plane, ep['episode']) not in used
                      and ep['plane'] == plane and event['onset_s'] <= ep['alarm']['emitted_s'] < exclusive_bound]
        ep = candidates[0] if candidates else None
        if ep:
            used.add((plane, ep['episode']))
        alarm = ep['alarm'] if ep else None
        diagnosis = ep['diagnosis'] if ep else None
        restoration = ep['restoration'] if ep else None
        correct = bool(diagnosis and diagnosis['target'] == event['target'])
        deadline = event['off_s']
        timely = bool(correct and (diagnosis['emitted_s'] < deadline if deadline is not None else diagnosis['emitted_s'] <= horizon))
        off_observable = deadline is not None and deadline <= horizon
        restore_time = restoration['emitted_s'] if restoration else None
        premature = bool(restoration and (deadline is None or restore_time < deadline))
        off_delay = restore_time - deadline if restoration and deadline is not None else None
        missing = bool(available and off_observable and not restoration)
        rows.append(dict(event=event['id'], **_target_json(event['target']), available=bool(available),
                         detected=bool(alarm), episode=ep['episode'] if ep else None,
                         alarm_s=alarm['emitted_s'] if alarm else None,
                         alarm_delay_s=alarm['emitted_s'] - event['onset_s'] if alarm else None,
                         diagnosis_s=diagnosis['emitted_s'] if diagnosis else None,
                         diagnosis_delay_s=diagnosis['emitted_s'] - event['onset_s'] if diagnosis else None,
                         first_diagnosis_correct=correct, timely_joint=timely,
                         correct_source_known_at_alarm=bool(correct and diagnosis['emitted_s'] == alarm['emitted_s']),
                         top3=bool(diagnosis and diagnosis['target'][:2] == event['target'][:2] and sources in diagnosis['top3']),
                         diagnosis_censored=bool(available and not diagnosis), unavailable=not available,
                         restoration_s=restore_time, off_delay_s=off_delay, premature_restoration=premature,
                         restoration_at_or_after_next_onset=bool(restoration and next_on is not None and restore_time >= next_on),
                         restoration_missing=missing, restoration_truth_censored=bool(not off_observable),
                         episode_open_at_horizon=bool(ep and (ep['terminal'] is None or ep['terminal']['kind'] == 'right_censored')),
                         episode_terminal_kind=ep['terminal']['kind'] if ep and ep['terminal'] else None))
    extras = [dict(plane=ep['plane'], episode=ep['episode'], alarm_s=ep['alarm']['emitted_s'])
              for ep in episodes if ep['alarm'] and (ep['plane'], ep['episode']) not in used]
    orphan_restorations = [dict(plane=ep['plane'], episode=ep['episode'], restoration_s=ep['restoration']['emitted_s'])
                           for ep in episodes if ep['restoration'] and (ep['plane'], ep['episode']) not in used]
    by_plane = {plane: dict(intended_components=sum(r['plane'] == plane for r in rows),
                           timely_joint=sum(r['plane'] == plane and r['timely_joint'] for r in rows),
                           detected=sum(r['plane'] == plane and r['detected'] for r in rows),
                           extras=sum(e['plane'] == plane for e in extras)) for plane in PLANES}
    return dict(events=rows, extras=extras, orphan_restorations=orphan_restorations, by_plane=by_plane,
                summary=dict(intended_events=len(rows), detected=sum(r['detected'] for r in rows),
                             first_diagnosis_correct=sum(r['first_diagnosis_correct'] for r in rows),
                             timely_joint=sum(r['timely_joint'] for r in rows), extras=len(extras),
                             orphan_restorations=len(orphan_restorations),
                             premature_restorations=sum(r['premature_restoration'] for r in rows),
                             restoration_missing=sum(r['restoration_missing'] for r in rows),
                             unavailable_events=sum(r['unavailable'] for r in rows)))


def evaluate_persistent(event, messages, horizon_s, available=True):
    """Separate first alarm, its associated diagnosis and the first committed joint stop."""
    horizon = _time(horizon_s, 'horizon_s')
    truth = normalize_truth([event], horizon)[0]
    if truth['off_s'] is not None and truth['off_s'] <= horizon:
        raise ContractError('persistent lane requires no restoration within the observed horizon')
    plane = truth['target'][0]
    episodes = _episodes(normalize_messages(messages, horizon)) if available else []
    episodes = [ep for ep in episodes if ep['plane'] == plane and ep['alarm']]
    first = episodes[0] if episodes else None
    alarm = first['alarm'] if first else None
    associated = first['diagnosis'] if first else None
    diagnosed = [ep for ep in episodes if ep['diagnosis']]
    joint_ep = min(diagnosed, key=lambda ep: (ep['diagnosis']['emitted_s'], ep['episode'])) if diagnosed else None
    joint = joint_ep['diagnosis'] if joint_ep else None
    onset = truth['onset_s']
    pre_alarm = bool(alarm and alarm['emitted_s'] < onset)
    pre_joint = bool(joint and joint['emitted_s'] < onset)
    correct_associated = bool(associated and not pre_alarm and associated['target'] == truth['target'])
    # First joint stop is a distinct estimand; a previous unlocalized false alarm
    # remains visible and makes the stricter pipeline endpoint fail.
    correct_joint = bool(joint and not pre_joint and joint['target'] == truth['target'])
    strict_correct = bool(correct_joint and not pre_alarm)
    return dict(available=bool(available), unavailable=not available,
                first_alarm_s=alarm['emitted_s'] if alarm else None,
                first_alarm_episode=first['episode'] if first else None,
                prechange_alarm=pre_alarm, alarm_censored=bool(available and not alarm),
                alarm_delay_s=alarm['emitted_s'] - onset if alarm and not pre_alarm else None,
                associated_first_diagnosis_s=associated['emitted_s'] if associated else None,
                associated_first_diagnosis_correct=correct_associated,
                associated_diagnosis_censored=bool(available and not associated),
                source_correct_at_first_alarm=bool(correct_associated and associated['emitted_s'] == alarm['emitted_s']),
                first_joint_stop_s=joint['emitted_s'] if joint else None,
                first_joint_stop_episode=joint_ep['episode'] if joint_ep else None,
                first_joint_target=_target_json(joint['target']) if joint else None,
                prechange_joint_stop=pre_joint, joint_stop_censored=bool(available and not joint),
                first_joint_correct=correct_joint, first_joint_correct_without_prechange_alarm=strict_correct,
                joint_delay_s=joint['emitted_s'] - onset if joint and not pre_joint else None,
                restricted_correct_joint_delay_s=joint['emitted_s'] - onset if strict_correct else horizon - onset)


def normal_alarm_metrics(messages, horizon_s, monitoring_start_s, available=True, stop_mode='continue', plane=None):
    """Normal controls only. Native stop exposure is explicit, not a shared denominator."""
    horizon, start = _time(horizon_s, 'horizon_s'), _time(monitoring_start_s, 'monitoring_start_s')
    if start > horizon or stop_mode not in ('continue', 'first_alarm', 'first_joint_stop'):
        raise ContractError('invalid monitoring interval or stop_mode')
    if plane is not None:
        _plane(plane)
    normalized = normalize_messages(messages, horizon) if available else []
    if any(m['emitted_s'] < start and m['kind'] in ('alarm', 'diagnosis')
           and (plane is None or m['plane'] == plane) for m in normalized):
        raise ContractError('alarm/diagnosis before declared monitoring start; correct the exposure contract explicitly')
    eligible = [m for m in normalized if (plane is None or m['plane'] == plane) and m['emitted_s'] >= start]
    alarms = [m for m in eligible if m['kind'] == 'alarm']
    diagnostics = [ep['diagnosis'] for ep in _episodes(eligible) if ep['diagnosis']]
    stop_events = alarms if stop_mode == 'first_alarm' else diagnostics
    end = min(m['emitted_s'] for m in stop_events) if stop_mode != 'continue' and stop_events else horizon
    monitored = max(0.0, end - start) if available else 0.0
    count = sum(a['emitted_s'] <= end for a in alarms)
    return dict(available=bool(available), intended_normal_records=1, available_normal_records=int(bool(available)),
                planned_exposure_s=horizon-start, monitored_exposure_s=monitored,
                alarms=count, any_alarm=bool(alarms), alarm_rate_per_hour=count*3600/monitored if monitored > 0 else None,
                stop_mode=stop_mode, stop_s=end if available else None)


def make_windows(horizon_s, duration_s=30.0, start_s=0.0):
    horizon, width, start = _time(horizon_s, 'horizon_s'), _time(duration_s, 'duration_s'), _time(start_s, 'start_s')
    if width == 0 or start > horizon:
        raise ContractError('invalid window width or start')
    windows = []
    index = 0
    while start + index*width < horizon:
        left = start + index*width
        windows.append(dict(window_id=f'W{index:06d}', start_s=left, end_s=min(horizon, left+width)))
        index += 1
    return windows


def stream_window_predictions(messages, windows, horizon_s):
    """First diagnoses actually emitted in (start,end], without internal posterior voting."""
    episodes = _episodes(normalize_messages(messages, horizon_s))
    diagnostics = [ep['diagnosis'] for ep in episodes if ep['diagnosis']]
    return [dict(window_id=w['window_id'], emitted_s=w['end_s'],
                 targets=[_target_json(d['target']) for d in diagnostics
                          if (w['start_s'] < d['emitted_s'] <= w['end_s'])
                          or (index == 0 and d['emitted_s'] == w['start_s'])])
            for index, w in enumerate(windows)]


def evaluate_windows(truth, windows, predictions, horizon_s, available=True):
    """Window classification/set coverage, not within-window detection delay."""
    horizon = _time(horizon_s, 'horizon_s')
    events = normalize_truth(truth, horizon)
    by_id = {}
    for prediction in predictions:
        wid = _label(prediction.get('window_id'), 'window_id')
        if wid in by_id:
            raise ContractError('duplicate window prediction')
        by_id[wid] = prediction
    rows, seen, previous_end = [], set(), None
    for window in windows:
        wid = _label(window.get('window_id'), 'window_id')
        start, end = _time(window.get('start_s'), 'window start'), _time(window.get('end_s'), 'window end')
        if wid in seen or start >= end or end > horizon or (previous_end is not None and start < previous_end):
            raise ContractError('windows must have unique ids and be sorted, positive, nonoverlapping, within horizon')
        seen.add(wid); previous_end = end
        actual = {e['target'] for e in events if e['onset_s'] < end and (e['off_s'] is None or e['off_s'] > start)}
        prediction = by_id.get(wid)
        valid = bool(available and prediction is not None)
        predicted = set()
        emitted = None
        if valid:
            emitted = _time(prediction.get('emitted_s'), 'window prediction emission')
            if emitted < end:
                raise ContractError('complete-window decision emitted before window end')
            last_report = _time(prediction.get('last_report_s', end), 'last_report_s')
            if last_report > end or last_report > emitted:
                raise ContractError('window prediction uses reports beyond its assigned window')
            predicted = {target(t) for t in prediction.get('targets', [])}
        intersection = actual & predicted
        family_actual = {t[:2] for t in actual}; family_pred = {t[:2] for t in predicted}
        rows.append(dict(window_id=wid, start_s=start, end_s=end, emitted_s=emitted, available=valid,
                         true_targets=[_target_json(t) for t in sorted(actual)],
                         predicted_targets=[_target_json(t) for t in sorted(predicted)],
                         abnormal=bool(actual), predicted_abnormal=bool(predicted),
                         target_tp=len(intersection), target_fp=len(predicted-actual), target_fn=len(actual-predicted),
                         any_target_coverage=bool(actual and intersection),
                         any_family_coverage=bool(actual and family_actual & family_pred),
                         exact_set=bool(valid and actual == predicted),
                         binary_tp=int(bool(actual and predicted)), binary_fp=int(bool(not actual and predicted)),
                         binary_fn=int(bool(actual and not predicted)),
                         binary_tn=int(bool(valid and not actual and not predicted))))
    if set(by_id) - seen:
        raise ContractError('prediction references a window outside this contract')
    fields = ('target_tp', 'target_fp', 'target_fn', 'binary_tp', 'binary_fp', 'binary_fn', 'binary_tn')
    summary = {field: sum(r[field] for r in rows) for field in fields}
    summary.update(intended_windows=len(rows), available_windows=sum(r['available'] for r in rows),
                   abnormal_windows=sum(r['abnormal'] for r in rows),
                   exact_sets=sum(r['exact_set'] for r in rows),
                   abnormal_any_target_covered=sum(r['any_target_coverage'] for r in rows))
    return dict(windows=rows, summary=summary)
