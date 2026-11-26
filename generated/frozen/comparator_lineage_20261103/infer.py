"""Frozen RAW classifier wrapper for a new PMU trajectory; no truth access."""
import argparse,json,sys,time
from pathlib import Path
import numpy as np,joblib
from threadpoolctl import threadpool_limits
from bootstrap import ROOT,REPO,METHOD,save,sha
from run import raw_stream,short_features,features
from causal_ml import EpisodeAdapter

def predict(observation,cache,output):
 assets=json.loads((METHOD/'model/assets.json').read_text())
 started=time.perf_counter()
 with threadpool_limits(limits=1):t,x=raw_stream(observation,cache);base=features(x);short=short_features(x)
 preprocessing_seconds=time.perf_counter()-started
 for variant in ['BASELINE','SHORT']:
  modelpath=ROOT/'models'/(variant+'.joblib');bundle=joblib.load(modelpath);model=bundle['model'];model.set_params(n_jobs=1);names=bundle['names'];X=base if variant=='BASELINE' else np.concatenate([base,short],axis=1);scores=np.zeros((len(t),len(names)));scores[:360,0]=1
  started=time.perf_counter()
  with threadpool_limits(limits=1):scores[360:,model.classes_]=model.predict_proba(X[360:])
  raw=np.argmax(scores,axis=1);adapter=EpisodeAdapter(names,assets,6);public=np.array([adapter.process(k,int(raw[k]),scores[k]) for k in range(len(t))]);adapter.finalize(len(t)-1)
  dest=output/variant;dest.mkdir(parents=True,exist_ok=True);np.savez_compressed(dest/'prediction.npz',time_s=t,source_label=public,raw_source_label=raw,class_scores=scores)
  save(dest/'prediction.json',dict(events=adapter.events,commits=[],truth_read=False,available=True,causal=True,class_names=names,observation_sha256=sha(observation),prefix_fit_sha256=sha(cache/'fit.json'),model_sha256=sha(modelpath),adapter_confirmation_reports=6,cadence_fps=30,last_reference_report_s=float(t[299]),input_kind='RAW'+('_SHORT' if variant=='SHORT' else ''),preprocessing_seconds=preprocessing_seconds,prediction_and_publication_seconds=time.perf_counter()-started,probabilities_calibrated=False))
  print('PREDICTED',variant,observation.name,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--observation',type=Path,required=True);p.add_argument('--cache',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();reads=set()
 def audit(event,args):
  if event=='open' and isinstance(args[0],(str,bytes)):
   s=Path(args[0]).resolve().as_posix().lower()
   if 'raw000' in s or '/truth_private/' in s or '/new_pilot/engine/' in s:raise PermissionError(s)
   if 'sgsma26-physics-informed-ad' in s:reads.add(str(args[0]))
 sys.addaudithook(audit);predict(a.observation,a.cache,a.output);save(a.output/'READ_AUDIT.json',dict(truth_read=False,paths=sorted(reads)))
