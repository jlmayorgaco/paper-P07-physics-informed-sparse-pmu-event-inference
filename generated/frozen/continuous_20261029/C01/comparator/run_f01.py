"""PMU-only IO adapter; no truth, schedule, solver state or RAW inputs."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
import pandas as pd
from chen2016 import covariance_bank,PMUComparator

REPO=Path(__file__).resolve().parents[3]
MODEL=REPO/'experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/physics/source_runtime/model'
PMUS=[2,5,6,10,19,22,29,39]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build_bank():
    b=pd.read_csv(MODEL/'physics/reference/data/branch.csv')
    edges=[dict(f=int(r.src_bus)-1,t=int(r.dst_bus)-1,x=float(r.X),tap=float(r.r_src),id=f'LINE{int(r.src_bus)}-{int(r.dst_bus)}') for r in b.itertuples()]
    assets=json.loads((MODEL/'assets.json').read_text());credible=[]
    for a in assets:
        if a['family']!='line':continue
        i=next(i for i,e in enumerate(edges) if {e['f']+1,e['t']+1}=={a['i'],a['j']})
        edges[i]['id']=a['id'];credible.append(i)
    names,cov,audit=covariance_bank(39,edges,[p-1 for p in PMUS],0,credible)
    audit.pop('matrix_inverses')
    audit.update(branch_sha256=sha(MODEL/'physics/reference/data/branch.csv'),assets_sha256=sha(MODEL/'assets.json'),tap_rule='flat-voltage DC slope 1/(X*tap)',reference_bus_1based=1)
    return names,cov,audit

def run(obs,out):
    obs=Path(obs).resolve();out=Path(out).resolve()
    if out.exists():raise FileExistsError(out)
    if any(x in str(p).lower().replace('\\','/') for p in [obs,out] for x in ['raw000','/truth_private/','/engine/']):raise PermissionError('Restricted input/output')
    # Audit blocks accidental future imports/access to truth inside this process.
    def guard(event,args):
        if event=='open' and isinstance(args[0],(str,bytes)):
            s=str(args[0]).lower().replace('\\','/')
            if any(x in s for x in ['raw000','/truth_private/','/engine/']):raise PermissionError(s)
    sys.addaudithook(guard)
    names,C,audit=build_bank();model=PMUComparator(C,names)
    with np.load(obs,allow_pickle=False) as z:
        t=z['time_s'].copy();a=z['voltage_angle'].copy()
    if len(t)<300 or a.shape!=(len(t),8):raise ValueError('300-report prefix and 8 angle channels required')
    if not np.allclose(t,np.arange(len(t))/30,atol=1e-8,rtol=0):raise ValueError('30 fps timebase required')
    trace=[];decision=None
    for k,(tt,aa) in enumerate(zip(t,a)):
        d=model.process(tt,aa)
        if d is not None:decision=d
        if model.core is not None and k%2==1:trace.append([float(tt),*model.core.scores.tolist()])
    out.mkdir(parents=True)
    result=dict(method='CHEN2016_PERSISTENT_QCD_F01_ADAPTER',decision=decision,names=names,scale=model.scale,center_rad=model.center.tolist(),threshold=model.core.threshold,input_sha256=sha(obs),truth_read=False,raw_read=False,normal_prefix_reports=300,beta_seconds=3600,observation_rate_hz=15,reported_rate_hz=30,one_stopping_decision=True,restoration_supported=False,load_family_supported=False,audit=audit)
    (out/'prediction.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    pd.DataFrame(trace,columns=['time_s',*names[1:]]).to_csv(out/'scores.csv',index=False)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--observation',required=True);p.add_argument('--output',required=True);a=p.parse_args();print(json.dumps(run(a.observation,a.output),indent=2))
