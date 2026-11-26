"""Convert archived full-record alarm-rate intervals to monitored-time units.

No predictions, matches, bootstrap draws or frozen files are modified.
Exact rescaling is permitted only when each paired parent has the same
full and monitored duration, as verified below for this completed cohort.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'generated/frozen/c01_20261029'


def corrected_intervals():
    records=pd.read_csv(F/'RECORDS.csv')
    intervals=pd.read_csv(F/'PAIRED_INTERVALS.csv')
    corrections=[]
    for i,row in intervals.iterrows():
        if row['lane']!='continuous' or row['metric']!='extras_per_event_hour':continue
        subset=records[(records.lane=='continuous')&(records.events>0)&
                       (records.condition==row['condition'])&(records.noise==row['noise'])]
        left=subset[subset.method==row['method']].sort_values('parent')
        right=subset[subset.method==row['reference']].sort_values('parent')
        if len(left)!=18 or len(right)!=18 or not left.available.all() or not right.available.all():
            raise ValueError('Exposure conversion requires all 18 paired event parents')
        if list(left.parent)!=list(right.parent):raise ValueError('Unpaired parents')
        ratios=[]
        for group in (left,right):
            if not np.allclose(group.duration_s,120) or not np.allclose(group.monitored_s,108):
                raise ValueError('Nonconstant exposure requires a fresh descriptive aggregation')
            ratios.extend((group.duration_s/group.monitored_s).tolist())
        if not np.allclose(ratios,ratios[0]):raise ValueError('Cannot rescale unequal exposures')
        factor=float(ratios[0])
        for column in ('difference','lower95','upper95'):intervals.at[i,column]=float(row[column])*factor
        corrections.append(dict(condition=row['condition'],noise=float(row['noise']),
                                method=row['method'],reference=row['reference'],factor=factor,
                                full_exposure_s=float(left.duration_s.sum()),monitored_exposure_s=float(left.monitored_s.sum())))
    intervals.to_csv(ROOT/'generated/paired_monitored_intervals.csv',index=False)
    audit={'purpose':'Descriptive unit correction; original registered intervals remain unchanged.',
           'formula':'alarm count / sum(monitored_s); archived difference and CI multiplied by full/monitored exposure',
           'original_hashes':{name:hashlib.sha256((F/name).read_bytes()).hexdigest() for name in ('RECORDS.csv','PAIRED_INTERVALS.csv')},
           'rows':corrections,'predictions_matches_or_test_selection_changed':False}
    (ROOT/'generated/monitored_exposure_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    return intervals
