"""Descriptive audit of sealed C01 tables, not a new evaluation or retuning."""
from pathlib import Path
import hashlib,json
import pandas as pd
HERE=Path(__file__).resolve().parent
PAPER=HERE.parents[1]
SCIENCE=PAPER.parent/'SGSMA26-Physics-Informed-AD'
RESULTS=SCIENCE/'experiments/PAPER_CONFIRMATORY_C01/run/results'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
s=pd.read_csv(RESULTS/'SUMMARY.csv');e=pd.read_csv(RESULTS/'EVENTS.csv');p=pd.read_csv(RESULTS/'PAIRED_INTERVALS.csv')
summary=s[s.lane=='continuous'].groupby('method')[['events','timely','joint','event_extras','false_restorations']].sum().to_dict('index')
restoration={}
for method,g in e[(e.lane=='continuous')&(e.method!='CHEN2016')].groupby('method'):
    x=g.off_delay_s.dropna()
    restoration[method]=dict(intended_event_realizations=len(g),matched_alarms=int(g.detected.sum()),associated_restorations_available=len(x),early_more_than_one_report=int((x < -1/30).sum()),minimum_signed_delay_s=float(x.min()),maximum_signed_delay_s=float(x.max()),no_associated_restoration=int(g.off_delay_s.isna().sum()))
files=[PAPER/'main.pdf',PAPER/'main.tex',PAPER/'sections/article_controlled_ablation.tex']+[RESULTS/n for n in ['SUMMARY.csv','EVENTS.csv','PAIRED_INTERVALS.csv','EVALUATION_AUDIT.json']]
out=dict(scope='Posthoc audit only. No C01 metric changes. Early restoration criterion chosen for this descriptive review: signed delay < -1/30 s. Replays are dependent; no significance claim.',hashes={str(f):sha(f) for f in files},continuous=summary,restoration=restoration,bootstrap_parents={str(k):list(map(int,v)) for k,v in p.groupby(['lane','metric']).parents.unique().to_dict().items()})
(HERE/'R2_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
