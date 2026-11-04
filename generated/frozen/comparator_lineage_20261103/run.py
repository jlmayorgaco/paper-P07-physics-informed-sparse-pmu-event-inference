"""Predeclared two-arm development comparison, no SIM0019 access or plant fit."""
import json,sys,time,os
from pathlib import Path
import numpy as np,pandas as pd,joblib
from scipy.stats import median_abs_deviation
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import confusion_matrix,f1_score
from threadpoolctl import threadpool_limits
from bootstrap import ROOT,REPO,METHOD,save,sha
from causal_features import Observations,FIELDS,features
from causal_ml import EpisodeAdapter
from evaluate_holdout import match_events,m02_alarms
PARENTS=['M03_R04_RECOVERY_OBSERVER','M03_R05_HYPOTHESIS_REPAIR','M03_R06_MODE_CONFIRMATION','M03_R07_SEQUENTIAL_DIAGNOSIS','M03_R08_SINGLE_CLOCK_BOUNDARIES']
CAMP=['SIM0014_RECOVERY_OBSERVER_HOLDOUT','SIM0015_HYPOTHESIS_REPAIR_HOLDOUT','SIM0016_MODE_CONFIRMATION_HOLDOUT','SIM0017_DIAGNOSIS_HOLDOUT','SIM0018_BOUNDARY_HOLDOUT']
SOURCES={}
def record(p):
 p=Path(p).resolve();assert p.is_relative_to(REPO) and 'raw0002' not in str(p).lower() and 'SIM0019' not in str(p)
 SOURCES[p.relative_to(REPO).as_posix()]=sha(p);return p

def raw_stream(obs,cache):
 with np.load(record(obs)) as z:t=z['time_s'].copy();data={f:z[f].copy() for f in FIELDS}
 fit=json.loads(record(cache/'fit.json').read_text());empirical=Observations(METHOD,np.zeros(48));pos=0
 for f,keep in enumerate(empirical.keep):
  empirical.base[f]=np.asarray(fit['empirical_baseline'][pos:pos+len(keep)]).copy();pos+=len(keep)
 x=np.array([empirical.process(float(tt),{f:v[k] for f,v in data.items()}) for k,tt in enumerate(t)])
 center=np.median(x[30:300],axis=0);scale=np.maximum(median_abs_deviation(x[30:300],axis=0,scale='normal'),1e-6)
 return t,(x-center)/scale

def short_features(x):
 d=pd.DataFrame(x);parts=[np.asarray(x)]
 for w in [3,8,15]:
  mean=d.rolling(w,min_periods=w).mean();parts.extend([mean.to_numpy(),d.rolling(w,min_periods=w).std(ddof=0).to_numpy(),(mean-mean.shift(w)).to_numpy(),(d-d.shift(w)).to_numpy()])
 a=np.concatenate(parts,axis=1).astype(np.float32);assert a.shape[1]==611 and np.isfinite(a[360:]).all();return a

def main():
 assert not (ROOT/'PILOT_FREEZE.json').exists(), 'Create a successor to rerun frozen development'
 cfg=json.loads((ROOT/'PROTOCOL.json').read_text());save(ROOT/'RUNNING.json',dict(stage='extract',started=time.time()));assets=json.loads(record(METHOD/'model/assets.json').read_text());names=['E0']+[a['id'] for a in assets];meta=[]
 for camp,parent in zip(CAMP,PARENTS):
  data=REPO/camp;cases={c['id']:c for c in json.loads(record(data/'truth_private/cases.json').read_text())};records=json.loads(record(data/'truth_private/replays.json').read_text())
  for r in records:
   key=camp+'/'+r['id'];dest=ROOT/'features'/camp/(r['id']+'.npz');obs=data/'observed'/f'{r["id"]}.npz';cache=METHOD.parents[1]/parent/'runtime/development/cache'/r['sha256'];c=cases[r['physical_id']]
   record(obs);record(cache/'fit.json')
   if not dest.exists():
    with threadpool_limits(limits=1):t,x=raw_stream(obs,cache);base=features(x);short=short_features(x)
    y=np.zeros(len(t),int)
    for e in c['events']:y[(t>=e['onset_s'])&(t<e['off_s'])]=names.index(e['source'])
    dest.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(dest,time_s=t,base=base,short=short,y=y)
   meta.append(dict(campaign=camp,record=r['id'],parent=camp+'/'+r['physical_id'],feature=str(dest.relative_to(ROOT)),events=c['events'],duration_s=c['duration_s'],noise=r['noise_std_factor']))
   print('EXTRACTED',key,flush=True)
 save(ROOT/'FEATURE_MANIFEST.json',dict(records=meta,files=SOURCES,names=names,protocol_sha256=sha(ROOT/'PROTOCOL.json')))
 train=[r for r in meta if r['campaign'] in cfg['train_campaigns']];val=[r for r in meta if r['campaign']==cfg['validation_campaign']];assert not set(r['parent'] for r in train)&set(r['parent'] for r in val)
 rows=[];events=[];extras=[];cms={};timings=[]
 for variant in ['BASELINE','SHORT']:
  model_path=ROOT/'models'/(variant+'.joblib');parts=[];labels=[]
  for r in train:
   with np.load(ROOT/r['feature']) as a:
    take=np.arange(360,len(a['y']),3);x=a['base'][take];parts.append(x if variant=='BASELINE' else np.concatenate([x,a['short'][take]],axis=1));labels.append(a['y'][take])
  X=np.concatenate(parts);y=np.concatenate(labels);del parts,labels;assert len(np.unique(y))==19
  if model_path.exists():bundle=joblib.load(model_path);model=bundle['model']
  else:
   save(ROOT/'RUNNING.json',dict(stage='fit',variant=variant,rows=len(y),features=X.shape[1]));start=time.perf_counter();model=ExtraTreesClassifier(n_estimators=400,min_samples_leaf=2,max_features='sqrt',class_weight='balanced',random_state=2601026,n_jobs=2)
   with threadpool_limits(limits=1):model.fit(X,y)
   model.set_params(n_jobs=1);model_path.parent.mkdir(parents=True,exist_ok=True);joblib.dump(dict(model=model,names=names,mode=variant),model_path,compress=3);timings.append(dict(variant=variant,rows=len(y),features=X.shape[1],fit_seconds=time.perf_counter()-start));print('TRAINED',variant,timings[-1],flush=True)
  del X,y
  cm=np.zeros((19,19),int)
  for r in val:
   with np.load(ROOT/r['feature']) as a:t=a['time_s'];y=a['y'];X=a['base'] if variant=='BASELINE' else np.concatenate([a['base'],a['short']],axis=1)
   scores=np.zeros((len(t),19));scores[:360,0]=1
   with threadpool_limits(limits=1):scores[360:,model.classes_]=model.predict_proba(X[360:])
   raw=np.argmax(scores,axis=1);adapter=EpisodeAdapter(names,assets,6);public=np.array([adapter.process(k,int(raw[k]),scores[k]) for k in range(len(t))]);adapter.finalize(len(t)-1)
   out=ROOT/'predictions'/r['record']/variant;out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'prediction.npz',time_s=t,true_source=y,raw_source=raw,public_source=public,scores=scores);save(out/'prediction.json',dict(events=adapter.events,truth_read_by_runner=True,truth_used_as_model_input=False,supervised_development_validation=True))
   e,f=match_events(r['events'],m02_alarms(dict(events=adapter.events)),r['duration_s'],variant,r['record'],r['parent'])
   for z in e:z['joint_before_off']=bool(z['joint_top1'] and z['emitted_s']<z['off_s'])
   events.extend(e);extras.extend(f);recordcm=confusion_matrix(y,public,labels=range(19));cm+=recordcm
   rows.append(dict(method=variant,record=r['record'],parent=r['parent'],normal_control=not r['events'],normal_exposure_s=max(0,r['duration_s']-12) if not r['events'] else 0,events=len(e),before_off=sum(z['joint_before_off'] for z in e),extras=len(f),open_eof=sum(z['kind']=='right_censored' for z in adapter.events),detection_f1=f1_score(y!=0,public!=0,zero_division=0),source_accuracy=float(np.mean(y==public)),cm=json.dumps(recordcm.tolist())))
   print('EVALUATED',variant,r['record'],flush=True)
  cms[variant]=cm
 d=pd.DataFrame(rows);ee=pd.DataFrame(events);ff=pd.DataFrame(extras,columns=['method','record','parent','alarm_s','pred_event','pred_source','kind','normal_control']);summary=[]
 families=np.array([0]+[4 if a['family']=='load' else 2 for a in assets])
 for method,cm in cms.items():
  er=ee[ee.method==method];fr=ff[ff.method==method];rr=d[d.method==method];tp=cm[1:,1:].sum();fp=cm[0,1:].sum();fn=cm[1:,0].sum();familycm=np.zeros((3,3),int);classes=[0,2,4]
  for i in range(19):
   for j in range(19):familycm[classes.index(families[i]),classes.index(families[j])]+=cm[i,j]
  diag=np.diag(familycm);den=familycm.sum(0)+familycm.sum(1);f1=np.divide(2*diag,den,out=np.zeros(3,float),where=den>0)
  summary.append(dict(method=method,events=len(er),joint_before_off=int(er.joint_before_off.sum()),load_before_off=int(er[er.family=='load'].joint_before_off.sum()),line_before_off=int(er[er.family=='line'].joint_before_off.sum()),detection_f1=float(2*tp/(2*tp+fp+fn)),macro_family_f1=float(f1.mean()),load_family_f1=float(f1[2]),extras=int((~fr.normal_control).sum()),normal_FA=int(fr.normal_control.sum()),normal_exposure_s=float(rr.normal_exposure_s.sum()),open_eof=int(rr.open_eof.sum())))
  pd.DataFrame(cm,index=names,columns=names).to_csv(ROOT/(method+'_CONFUSION.csv'))
 for name,a in [('RECORDS',d),('EVENTS',ee),('EXTRAS',ff),('SUMMARY',pd.DataFrame(summary))]:a.to_csv(ROOT/(name+'.csv'),index=False)
 save(ROOT/'TRAINING_TIMING.json',timings);save(ROOT/'COMPLETE.json',dict(success=True,parents_train=len(set(r['parent'] for r in train)),parents_validation=len(set(r['parent'] for r in val)),validation_records=len(val),test_access=False,config_sha256=sha(ROOT/'PROTOCOL.json'),models=[dict(variant=m,sha256=sha(ROOT/'models'/(m+'.joblib'))) for m in cms],scope='Historical development only; not new physical holdout or independent test of R08'))
 print(pd.DataFrame(summary).to_string(index=False),flush=True)
if __name__=='__main__':main()
