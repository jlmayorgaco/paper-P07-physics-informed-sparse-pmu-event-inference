"""Post-hoc P07 closure audit. Evaluator joins truth AFTER all decisions are frozen.

Usage: python audit_p07_timeline.py --csv episode_timeline.csv --out timeline_audit.json

The CSV must contain one row per previous episode, with columns:
 record_id,episode_id,off_true,off_emitted,compress_time,next_on_true,
 number_histories_at_next_on,number_distinct_old_causes_at_next_on,
 trace_discarded_amplitude,trace_discarded_between.

Important: this file is NOT to be imported by the inference runtime, because
it includes evaluator truth fields. It is intentionally a separate script.
"""
import json,argparse
from pathlib import Path
import numpy as np
import pandas as pd
REQUIRED=['record_id','episode_id','off_true','off_emitted','compress_time',
          'next_on_true','number_histories_at_next_on','number_distinct_old_causes_at_next_on',
          'trace_discarded_amplitude','trace_discarded_between']

def audit(df):
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing:raise ValueError('Missing columns: '+str(missing))
    # A missing timestamp is unknown, never silently mapped to zero.
    eligible=df.dropna(subset=['next_on_true','compress_time']).copy()
    if len(eligible)==0:raise ValueError('No rows with known compression and next ON')
    eligible['compressed_before_next_on']=eligible['compress_time']<eligible['next_on_true']
    eligible['attributed_old_cause_still_distinct']=(eligible['number_distinct_old_causes_at_next_on']>1)
    eligible['time_before_next_on_sec']=eligible['next_on_true']-eligible['compress_time']
    out={
      'n_episodes_in_file':int(len(df)),
      'n_episodes_with_next_on_and_compress':int(len(eligible)),
      'n_compressed_before_next_on':int(eligible['compressed_before_next_on'].sum()),
      'fraction_compressed_before_next_on':float(eligible['compressed_before_next_on'].mean()),
      'n_with_multiple_old_causes_at_next_on':int(eligible['attributed_old_cause_still_distinct'].sum()),
      'fraction_multiple_old_causes_at_next_on':float(eligible['attributed_old_cause_still_distinct'].mean()),
      'median_time_before_next_on_sec':float(eligible['time_before_next_on_sec'].median()),
      'mean_trace_discarded_amp':float(eligible['trace_discarded_amplitude'].mean()),
      'mean_trace_discarded_between':float(eligible['trace_discarded_between'].mean()),
      'interpretation':('This audits old-cause representation at new ON. It does NOT by itself establish'
                        ' a causal benefit of history versus mixture uncertainty; pair with controlled B/C/D ablation.')
    }
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--csv',required=True);parser.add_argument('--out',required=True)
    a=parser.parse_args();stats=audit(pd.read_csv(a.csv));Path(a.out).write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))
