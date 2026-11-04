"""30-fps classifier decisions and a fixed causal episode interface."""
import json,time,argparse
import numpy as np,joblib
from pathlib import Path
from threadpoolctl import threadpool_limits
from bootstrap import ROOT,DATA,METHOD,save,sha
from causal_features import streams,features,raw_without_dae

class EpisodeAdapter:
 def __init__(self,names,assets,persistence):
  self.names=names;self.assets={a['id']:a for a in assets};self.n=persistence;self.number=0;self.current=0;self.run_label=0;self.run=0;self.events=[];self.last=None
 def decision(self,kind,k,label,scores):
  name=self.names[label];family=self.assets[name]['family'];ix=[j for j,s in enumerate(self.names) if s in self.assets and self.assets[s]['family']==family];rank=sorted(ix,key=lambda j:-scores[j]);t=k/30
  return dict(kind=kind,episode=self.number,emitted_s=t,last_report_used_s=t,alarm_s=self.alarm_s,family=family,source=name,top3=[self.names[j] for j in rank[:3]],onset_s=(k-self.run+1)/30,off_s=float('nan'),amplitude=float('nan'),amplitude_sd=float('nan'),duration_s=float('nan'),duration_sd_s=float('nan'),support=float(scores[label]),score_interpretation='Uncalibrated tree vote, not calibrated probability')
 def process(self,k,label,scores):
  self.run=self.run+1 if label==self.run_label else 1;self.run_label=label
  if k<360 or self.run<self.n:return self.current
  if self.current and label!=self.current:
   e=dict(self.last,kind='restoration' if label==0 else 'superseded',emitted_s=k/30,last_report_used_s=k/30,physical_restoration_confirmed=label==0)
   if label==0:e.update(off_s=(k-self.run+1)/30,duration_s=(k-self.run+1)/30-self.last['onset_s'])
   self.events.append(e);self.current=0
  if label and not self.current:
   self.number+=1;self.current=label;self.alarm_s=k/30;self.last=self.decision('alarm',k,label,scores);self.events.append(self.last);self.last=self.decision('diagnosis',k,label,scores);self.events.append(self.last)
  return self.current
 def finalize(self,k):
  if self.current:self.events.append(dict(self.last,kind='right_censored',emitted_s=k/30,last_report_used_s=k/30,physical_restoration_confirmed=False))

def predict(data):
 records=json.loads((data/'INPUTS.json').read_text());assets=json.loads((METHOD/'model/assets.json').read_text());models={m:joblib.load(ROOT/'models'/f'ET_CAUSAL_{m}.joblib') for m in ['RAW','INNOV']}
 for r in records:
  rid=r['id'];dest=data/'predictions'/rid
  if all((dest/('ET_'+m)/'prediction.json').exists() for m in models):continue
  started=time.perf_counter();obs=data/'observed'/f'{rid}.npz';cache=METHOD/'development/cache'/r['sha256']
  issue=None
  try:
   with threadpool_limits(limits=1):t,z=streams(obs,cache)
  except Exception as e:
   issue=repr(e)
   with threadpool_limits(limits=1):t,raw=raw_without_dae(obs)
   z={'RAW':raw}
  for mode,bundle in models.items():
   if mode not in z:
    for suffix in ['', '_FRAME']:
     out=dest/('ET_'+mode+suffix);out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'prediction.npz',time_s=t,source_label=np.full(len(t),-1,int),raw_source_label=np.full(len(t),-1,int))
     save(out/'prediction.json',dict(events=[],commits=[],truth_read=False,available=False,numerical_failure=issue,class_names=bundle['names'],observation_sha256=sha(obs)))
    continue
   X=features(z[mode]);model=bundle['model'];names=bundle['names'];scores=np.zeros((len(t),len(names)));scores[:360,0]=1.
   with threadpool_limits(limits=1):scores[360:,model.classes_]=model.predict_proba(X[360:])
   raw=np.argmax(scores,axis=1)
   for suffix,n in [('',6),('_FRAME',1)]:
    arm='ET_'+mode+suffix;out=dest/arm
    if (out/'prediction.json').exists():continue
    adapter=EpisodeAdapter(names,assets,n);public=np.zeros(len(t),int)
    for k in range(len(t)):public[k]=adapter.process(k,int(raw[k]),scores[k])
    adapter.finalize(len(t)-1);out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'prediction.npz',time_s=t,source_label=public,raw_source_label=raw,class_scores=scores)
    save(out/'prediction.json',dict(events=adapter.events,commits=[],truth_read=False,observation_sha256=sha(obs),class_names=names,adapter_confirmation_reports=n,cadence_fps=30,last_reference_report_s=float(t[299]),input_kind=mode,model_sha256=sha(ROOT/'models'/f'ET_CAUSAL_{mode}.joblib'),runtime_s=time.perf_counter()-started,causal=True,probabilities_calibrated=False))
   print('CAUSAL_ML_COMPLETE',rid,mode,flush=True)
if __name__=='__main__':
 import sys
 ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,default=DATA);a=ap.parse_args();reads=set()
 def audit(event,args):
  if event=='open' and isinstance(args[0],(str,bytes)):
   s=Path(args[0]).resolve().as_posix().lower()
   if 'raw000' in s or '/truth_private/' in s or '/workspace/runs/' in s:raise PermissionError(s)
   if 'sgsma26-physics-informed-ad' in s:reads.add(str(args[0]))
 sys.addaudithook(audit);predict(a.data);save(ROOT/'checks/CAUSAL_ML_READS.json',dict(paths=sorted(reads),truth_read=False))
