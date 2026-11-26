"""Isolated signature experiment. Only infer() is the PMU-only worker."""
from pathlib import Path
import argparse,csv,hashlib,importlib.util,json,math,sys
import numpy as np
from scipy.integrate import quad
from scipy.special import logsumexp,ndtr
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent
FIELDS=['voltage_magnitude','voltage_angle','current_magnitude','current_angle','frequency','rocof']
KEEP=[np.arange(8),np.arange(8),np.arange(8),np.arange(7),np.arange(8),np.arange(8)]
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE/'runtime/reference'))
from pmu_operator import report,wrap_deg
from noise import NoiseStream,apply_noise
spec=importlib.util.spec_from_file_location('x02_fixed_instrument',HERE/'runtime/instrument_parent.py')
instrument=importlib.util.module_from_spec(spec);spec.loader.exec_module(instrument)

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 def enc(v):return v.tolist() if isinstance(v,np.ndarray) else v.item() if isinstance(v,np.generic) else str(v)
 p.write_text(json.dumps(x,indent=2,default=enc,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csvwrite(p,rows):
 if not rows:return
 with Path(p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

class CoordinateMap:
 def __init__(self):
  self.cfg=read(HERE/'runtime/reference/reporting_config.json');self.noise=read(HERE/'runtime/reference/stochastic_model.json')
  self.filters=[instrument.ColoredInstrument(self.noise['families'][f],k) for f,k in zip(FIELDS,KEEP)]
 def coordinates(self,t,y,noisy=False):
  out=[]
  for f,keep in zip(FIELDS,KEEP):
   a=np.asarray(y[f],float)[:,keep].copy();s=self.noise['families'][f]
   if noisy:a-=np.asarray(s['normalization_center'])[keep]
   if 'angle' in f:
    a=wrap_deg(a-self.cfg['common_phase_slope_deg_s']*t[:,None])
    a=np.rad2deg(np.unwrap(np.deg2rad(a),axis=0))
   if f in ['frequency','rocof']:a[:4]=0.
   assert np.all(np.isfinite(a)),f
   out.append(a/s['normalization_scale'])
  return np.concatenate(out,axis=1)
 def whiten(self,y):
  result=[];start=0
  for filt,keep in zip(self.filters,KEEP):
   n=len(keep);a=y[:,start:start+n];result.append(filt.whiten(a[None,:,:])[0]);start+=n
  return np.concatenate(result,axis=1)

def export():
 import pandas as pd
 plan=read(HERE/'protocol/PLAN.json');design=read(HERE/'truth_private/cases.json');cm=CoordinateMap()
 mapping=pd.read_csv(HERE/'runtime/reference/terminal_mapping.csv');kv=pd.read_csv(HERE/'runtime/reference/data/bus.csv').base_kv.to_numpy()
 coords={};public=[];statuses=[]
 for case in design:
  folder=HERE/'engine/events/diagnostics'/case['id'];status=folder/'status.json'
  if not status.exists():
   statuses.append(dict(id=case['id'],available=False,reason='physical_rejection'));continue
  s=read(status);assert s['continuity_and_frozen_plant_pass'] and s['trajectory_solves']==1 and s['dynamic_state_resets']==0
  assert s['reports']==301 and s['non_input_parameter_change']==0
  v=pd.read_csv(folder/'voltage_all_pu.csv');i=pd.read_csv(folder/'native_terminal_current_pu.csv');t=v.time_s.to_numpy()
  va=v.iloc[:,1:].to_numpy().reshape(len(t),39,2);ia=i.iloc[:,1:].to_numpy().reshape(len(t),8,2)
  z=report(t,va[:,:,0]+1j*va[:,:,1],ia[:,:,0]+1j*ia[:,:,1],mapping,kv,cm.cfg)
  det=dict(voltage_magnitude=abs(z['voltage_pu'])*345e3/np.sqrt(3),current_magnitude=abs(z['current_A']),voltage_angle=np.angle(z['voltage_pu'],deg=True),current_angle=np.angle(z['current_A'],deg=True),frequency=z['frequency_hz'],rocof=z['rocof_hz_s'])
  xy=cm.coordinates(t,det);coords[case['id']]=xy
  np.savez_compressed(HERE/'engine'/f"{case['id']}_det.npz",time_s=t,y=xy)
  if case['split']=='test':
   for seed in plan['noise_seeds']:
    rid=f"R{len(public)+1:04d}";stream=NoiseStream(cm.noise,seed);noisy=apply_noise(det,stream.generate(len(t)));y=cm.coordinates(t,noisy,True)
    path=HERE/'observations'/f'{rid}.npz';np.savez_compressed(path,time_s=t,y=y)
    public.append(dict(id=rid,path=str(path.relative_to(HERE)),sha256=sha(path)))
  jumps=pd.read_csv(folder/'event_continuity.csv')
  statuses.append(dict(id=case['id'],available=True,maximum_dynamic_jump=float(jumps.max_differential_jump.max()),maximum_algebraic_residual=s['max_algebraic_residual']))
 write(HERE/'results/PHYSICAL_STATUS.json',statuses)
 # Model construction reads only declared dictionary runs.
 train=[c for c in design if c['split']!='test']
 assert all(c['id'] in coords for c in train),'A rejected dictionary trajectory blocks the candidate.'
 lookup={(c['eta'],c['source'],c['amplitude']):coords[c['id']] for c in train}
 h=plan['event_fd_step'];d=plan['context_fd_step'];dh=plan['half_context_fd_step'];buses=plan['buses']
 normal={eta:lookup[eta,None,0.] for eta in plan['context_dictionary']}
 def tangent(eta,b,h=h):return (lookup[eta,b,h]-lookup[eta,b,-h])/(2*h)
 D=np.array([tangent(0.,b) for b in buses]);Q=np.array([(lookup[0.,b,h]+lookup[0.,b,-h]-2*normal[0.])/(2*h*h) for b in buses])
 E=np.array([(tangent(d,b)-tangent(-d,b))/(2*d) for b in buses]);Eh=np.array([(tangent(dh,b)-tangent(-dh,b))/(2*dh) for b in buses])
 N=np.mean((normal[d]-normal[-d])/(2*d),axis=0)
 np.savez_compressed(HERE/'model/dictionary.npz',time_s=t,base=normal[0.],D=D,Q=Q,E=E,N=N,buses=buses)
 write(HERE/'model/TRAINING.json',dict(training_ids=[c['id'] for c in train],labels_known_for_dictionary=True,test_cases_used=False,known_onset_s=3.,known_off_s=6.,parent='F01'))
 checks=[]
 for j,b in enumerate(buses):
  norm=np.linalg.norm(cm.whiten(E[j])[90:]);checks.append(dict(bus=b,check='context_step_halving',relative_difference=float(np.linalg.norm(cm.whiten(Eh[j]-E[j])[90:])/max(norm,1e-12))))
 for b in [3,16]:
  hh=plan['half_event_fd_step'];ep=(tangent(dh,b,hh)-tangent(-dh,b,hh))/(2*dh);j=buses.index(b)
  checks.append(dict(bus=b,check='event_step_halving',relative_difference=float(np.linalg.norm(cm.whiten(ep-Eh[j])[90:])/max(np.linalg.norm(cm.whiten(Eh[j])[90:]),1e-12))))
 csvwrite(HERE/'results/DERIVATIVE_CHECKS.csv',checks)
 write(HERE/'observations/RECORDS.json',public)
 private=[];k=0
 for c in design:
  if c['split']!='test' or c['id'] not in coords:continue
  for seed in plan['noise_seeds']:
   private.append(dict(record=public[k]['id'],physical_case=c['id'],source=c['source'],amplitude=c['amplitude'],eta=c['eta'],seed=seed));k+=1
 write(HERE/'truth_private/records.json',private)
 write(HERE/'model/MANIFEST.json',dict(dictionary_sha256=sha(HERE/'model/dictionary.npz'),no_test_responses_used=True,physical_cases=len(statuses),rejected=sum(not s['available'] for s in statuses)))
 print('EXPORTED',len(public),'observed records; dictionary contains no test response.')

def integral(rD,rQ,DD,DQ,QQ,rr,sd,bounds):
 """Proper bounded Gaussian amplitude integral; all stationary points split quad."""
 lo,hi=bounds;prec=1/sd**2
 co=np.array([2*QQ,3*DQ,DD-2*rQ+prec,-rD])
 roots=np.roots(np.trim_zeros(co,'f'));stationary=[float(r.real) for r in roots if abs(r.imag)<1e-7 and lo<r.real<hi]
 def shape(a):return a*rD+a*a*(rQ-.5*DD-.5*prec)-a**3*DQ-.5*a**4*QQ
 candidates=[lo,hi]+stationary;mode=max(candidates,key=shape);peak=shape(mode)
 points=[lo,hi]+stationary
 for a in stationary:
  curvature=DD-2*rQ+prec+6*DQ*a+6*QQ*a*a
  if curvature>0:
   width=1/math.sqrt(curvature)
   points += [a+k*width for k in [-12,-6,-2,-1,1,2,6,12] if lo<a+k*width<hi]
 points=sorted(set(points))
 def moment(power):
  return sum(quad(lambda a:a**power*math.exp(min(0.,shape(a)-peak)),a,b,epsabs=1e-12,epsrel=1e-8,limit=100)[0] for a,b in zip(points[:-1],points[1:]))
 z=moment(0);assert z>0
 mean=moment(1)/z;variance=max(0.,moment(2)/z-mean*mean)
 prior_norm=sd*math.sqrt(2*math.pi)*(ndtr(hi/sd)-ndtr(lo/sd))
 return -.5*rr+peak+math.log(z/prior_norm),mean,math.sqrt(variance)

def fit_context(cm,y,base,N,plan):
 prefix=np.arange(len(y))<round(plan['prefix_end_s']*30);prefix[:21]=False
 residual=y-base;n=np.tile(N,(len(y),1));wn=cm.whiten(n)[prefix];wr=cm.whiten(residual)[prefix]
 eta=float(np.clip(np.sum(wn*wr)/max(np.sum(wn*wn),1e-20),-.1,.1))
 offset=np.mean(residual[prefix],axis=0)
 return eta,offset

def infer():
 def guard(event,args):
  if event=='open' and isinstance(args[0],(str,bytes)):
   value=str(args[0]).replace('\\','/').lower()
   if any(x in value for x in ['/truth_private/','/engine/','raw000']):raise PermissionError(value)
 sys.addaudithook(guard)
 plan=read(HERE/'protocol/PLAN.json');cm=CoordinateMap();records=read(HERE/'observations/RECORDS.json');m=np.load(HERE/'model/dictionary.npz');base=m['base'];buses=m['buses'].tolist()
 score=(m['time_s']>=plan['score_start_s'])&(m['time_s']<=plan['score_end_s'])
 numerical_checks()
 for k,record in enumerate(records):
  path=HERE/record['path'];assert sha(path)==record['sha256'];z=np.load(path);y=z['y'];eta,offset=fit_context(cm,y,base,m['N'],plan);results={}
  for arm in plan['comparators']:
   correction=np.zeros(47) if arm=='nominal' else offset
   residual=cm.whiten(y-base-correction)[score].ravel();rr=float(residual@residual)
   evid=[-.5*rr];means=[];sds=[]
   for j in range(len(buses)):
    d=m['D'][j]+(eta*m['E'][j] if arm=='conditioned' else 0.)
    d=cm.whiten(d)[score].ravel();q=cm.whiten(m['Q'][j])[score].ravel()
    logz,mean,sd=integral(float(residual@d),float(residual@q),float(d@d),float(d@q),float(q@q),rr,plan['amplitude_prior_sd'],plan['amplitude_bounds'])
    evid.append(logz);means.append(mean);sds.append(sd)
   logs=np.array(evid)+np.log(np.r_[.5,np.full(len(buses),.5/len(buses))]);mass=np.exp(logs-logsumexp(logs));rank=np.argsort(-mass[1:]);winner=int(np.argmax(mass))
   results[arm]=dict(source=None if winner==0 else buses[winner-1],source_rank=[buses[j] for j in rank],mass=mass,amplitude_mean=means,amplitude_sd=sds,eta_estimated=eta,log_evidence=evid)
  write(HERE/'predictions'/f"{record['id']}.json",dict(record=record['id'],observation_sha256=record['sha256'],last_report_used_s=10.,true_onset_not_inferred=True,true_source_read=False,true_context_read=False,outputs=results))
  if k%12==0:print('INFER_PROGRESS',k+1,len(records),flush=True)
 write(HERE/'predictions/READ_BOUNDARY.json',dict(truth_private_read=False,engine_read=False,only_PMU_observations_and_public_model=True,records=len(records)))

def numerical_checks():
 # Independent analytic Gaussian check in a nonzero linear case.
 rr=5.;rD=.8;DD=2.;sd=.05
 logz,mean,sdev=integral(rD,0.,DD,0.,0.,rr,sd,[-.15,.15])
 v=1/(DD+1/sd**2);mu=v*rD
 expected=-.5*rr+.5*math.log(v/sd**2)+.5*mu**2/v+math.log((ndtr((.15-mu)/math.sqrt(v))-ndtr((-.15-mu)/math.sqrt(v)))/(ndtr(.15/sd)-ndtr(-.15/sd)))
 null=integral(0.,0.,0.,0.,0.,rr,sd,[-.15,.15])[0]
 assert abs(logz-expected)<1e-9 and abs(null+.5*rr)<1e-9
 write(HERE/'results/INTEGRAL_CHECK.json',dict(linear_error=abs(logz-expected),no_information_error=abs(null+.5*rr),passed=True))

def evaluate():
 plan=read(HERE/'protocol/PLAN.json');truth=read(HERE/'truth_private/records.json');cases=read(HERE/'truth_private/cases.json');cm=CoordinateMap();m=np.load(HERE/'model/dictionary.npz');score=m['time_s']>=3.;rows=[];fidelity=[]
 for record in truth:
  pred=read(HERE/'predictions'/f"{record['record']}.json")
  for arm,p in pred['outputs'].items():
   source=record['source'];index=0 if source is None else 1+plan['buses'].index(source)
   amp=None if source is None else p['amplitude_mean'][index-1]
   rows.append(dict(record=record['record'],physical_case=record['physical_case'],source=source,eta=record['eta'],amplitude=record['amplitude'],seed=record['seed'],method=arm,predicted_source=p['source'],joint_correct=int(p['source']==source),source_top1=int(source is not None and p['source_rank'][0]==source),source_top3=int(source is not None and source in p['source_rank'][:3]),log_loss=-math.log(max(p['mass'][index],1e-300)),amplitude_error=None if amp is None else amp-record['amplitude'],eta_error=p['eta_estimated']-record['eta']))
 for c in cases:
  if c['split']!='test' or c['source'] is None:continue
  cp=HERE/'engine'/f"{c['id']}_det.npz"
  control=next(v for v in cases if v['split']=='test' and v['eta']==c['eta'] and v['source'] is None)
  if not cp.exists() or not (HERE/'engine'/f"{control['id']}_det.npz").exists():continue
  true=np.load(cp)['y'];base_context=np.load(HERE/'engine'/f"{control['id']}_det.npz")['y'];increment=true-base_context;eta,offset=fit_context(cm,true,m['base'],m['N'],plan);j=plan['buses'].index(c['source']);a=c['amplitude']
  reference=cm.whiten(increment)[score];den=max(float(np.linalg.norm(reference)),1e-12)
  for arm in plan['comparators']:
   effect=a*(m['D'][j]+(eta*m['E'][j] if arm=='conditioned' else 0.))+a*a*m['Q'][j]
   correction=np.zeros(47) if arm=='nominal' else offset
   fidelity.append(dict(physical_case=c['id'],source=c['source'],eta=c['eta'],amplitude=a,method=arm,eta_estimated=eta,relative_incremental_error=float(np.linalg.norm(cm.whiten(effect-increment)[score])/den),absolute_whitened_error=float(np.linalg.norm(cm.whiten(m['base']+correction+effect-true)[score])),true_incremental_norm=den))
 csvwrite(HERE/'results/PER_RECORD.csv',rows);csvwrite(HERE/'results/FIDELITY.csv',fidelity)
 summary=[]
 for arm in plan['comparators']:
  event=[r for r in rows if r['method']==arm and r['source'] is not None];norm=[r for r in rows if r['method']==arm and r['source'] is None];f=[r for r in fidelity if r['method']==arm]
  summary.append(dict(method=arm,event_records=len(event),joint_correct=sum(r['joint_correct'] for r in event),conditional_source_correct=sum(r['source_top1'] for r in event),source_top3=sum(r['source_top3'] for r in event),normal_records=len(norm),normal_selected_event=sum(not r['joint_correct'] for r in norm),mean_event_log_loss=float(np.mean([r['log_loss'] for r in event])),median_incremental_error=float(np.median([r['relative_incremental_error'] for r in f])),median_absolute_error=float(np.median([r['absolute_whitened_error'] for r in f]))))
 csvwrite(HERE/'results/SUMMARY.csv',summary)
 rng=np.random.default_rng(plan['bootstrap_seed']);intervals=[];ids=sorted({r['physical_case'] for r in fidelity})
 for metric,data in [('relative_incremental_error',fidelity),('joint_correct',rows),('log_loss',rows)]:
  differences=[]
  for cid in ids:
   values={arm:np.mean([r[metric] for r in data if r['physical_case']==cid and r['method']==arm]) for arm in ['recentered','conditioned']}
   differences.append(values['conditioned']-values['recentered'])
  differences=np.array(differences);boot=np.mean(differences[rng.integers(0,len(ids),(plan['bootstrap_repetitions'],len(ids)))],axis=1)
  intervals.append(dict(metric=metric,contrast='conditioned_minus_recentered',estimate=float(np.mean(differences)),lower95=float(np.quantile(boot,.025)),upper95=float(np.quantile(boot,.975)),physical_cases=len(ids)))
 csvwrite(HERE/'results/PAIRED_INTERVALS.csv',intervals)
 write(HERE/'results/EVALUATION_AUDIT.json',dict(intended_physical=plan['test_physical_trajectories'],intended_event_physical=plan['test_physical_events'],available_event_physical=len(ids),intended_observed=plan['test_physical_trajectories']*len(plan['noise_seeds']),available_observed=len(truth),noise_seeds=3,methods_fixed=True,known_onset_and_restoration=True,C01_changed=False,RAW0002_opened=False))
 print(json.dumps(summary,indent=2))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['export','infer','evaluate']);args=parser.parse_args()
 with threadpool_limits(limits=1):globals()[args.mode]()
