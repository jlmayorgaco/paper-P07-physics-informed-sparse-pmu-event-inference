"""Read-only audit of C01 metric code using invented fixtures; no campaign data."""
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(r'C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD')
OUT = Path(__file__).with_name('methodology_metric_checks.json')
path = ROOT / 'experiments/PAPER_CONFIRMATORY_C01/execution/metrics.py'
spec = importlib.util.spec_from_file_location('audit_metrics', path)
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
truth = [dict(id='invented_event', family='line', source='LINE1-2', onset_s=10., off_s=15.)]
aa = [dict(episode=1, alarm_s=11., emitted_s=12., family='line', source='LINE1-2', top3=['LINE1-2'])]
matched, extras = metrics.match(truth, aa, 30.)
matched_ep = {v['episode'] for v in matched if v['detected']}
restorations = {1: dict(emitted_s=13.)}
early_closure = dict(
    true_off_s=15., restoration_emitted_s=13.,
    off_delay_s=restorations[1]['emitted_s']-truth[0]['off_s'],
    false_restorations_as_in_evaluate_line_48=sum(ep not in matched_ep for ep in restorations),
    observation='Premature restoration of a matched event is not counted by false_restorations.'
)
late_source = [dict(episode=1, alarm_s=11., emitted_s=19., family='line', source='LINE1-2')]
first_stop = metrics.first_stop(truth, late_source, 30.)
persistent_truth = [dict(id='invented_persistent', family='line', source='LINE1-2', onset_s=10., off_s=None)]
source_matrix = []
for alarm_source in ['LINE1-2', 'LINE2-3']:
    for diagnosis_source in ['LINE1-2', 'LINE2-3', None]:
        events = [dict(kind='alarm', episode=1, emitted_s=11., family='line', source=alarm_source)]
        if diagnosis_source is not None:
            events.append(dict(kind='diagnosis', episode=1, emitted_s=19., family='line', source=diagnosis_source))
        associated = metrics.alarms(dict(events=events))
        outcome = metrics.first_stop(persistent_truth, associated, 30.)
        source_matrix.append(dict(alarm_source=alarm_source, diagnosis_source=diagnosis_source,
                                 source_used_by_alarms=associated[0]['source'], outcome=outcome))
result = dict(
    scope='Synthetic metric checks only; C01 truth, predictions, observations and partial results not read.',
    premature_closure=early_closure,
    delayed_diagnosis_first_stop=first_stop,
    delayed_diagnosis_note='Alarm delay is 1 s but source is emitted after 9 s; restricted_correct_delay_s preserves the latter.',
    first_stop_source_matrix=source_matrix,
    illustrative_random_clone_split_leak_probability_six_clones=1-0.7**6-0.3**6,
    conditional_homogeneous_Poisson_zero_alarm_upper95_per_hour={
        'H04_204_seconds':-math.log(.05)*3600/204,
        'C01_one_stratum_12_times_588_seconds':-math.log(.05)*3600/(12*588)
    },
    zero_alarm_hours_required_for_point_one_per_hour_under_same_model=-math.log(.05)/.1,
    Poisson_caveat='Illustrations under an assumed homogeneous Poisson process; paired or correlated streams do not automatically satisfy it.'
)
def json_finite(value):
    if isinstance(value, dict):
        return {k: json_finite(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_finite(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value

result = json_finite(result)
OUT.write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
print(json.dumps(result, indent=2, allow_nan=False))
