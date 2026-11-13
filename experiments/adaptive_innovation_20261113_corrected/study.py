"""Frozen F01 operator diagnostic. Not the R11 history bank or a second plant."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from pathlib import Path
import argparse,hashlib,json,time,platform
import numpy as np
from scipy.linalg import cholesky,solve_triangular,eigh
from scipy.special import logsumexp
from scipy.sparse import csr_matrix
from scipy.stats import chi2

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'channel_information_20261112'
OUT=HERE/'run'
ARMS=('fixed','adaptive','guarded')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def load():
    p=json.loads((HERE/'protocol.json').read_text())
    assert sha(BASE/'input_snapshot.npz')==p['snapshot_sha256']
    with np.load(BASE/'input_snapshot.npz') as z:b={k:z[k] for k in z.files}
    return p,b

def unit_response(b,n,duration):
    """Null innovations of a unit load, using actual ON/stay/OFF operators."""
    T=csr_matrix(b['T'][0]);J=b['J'][0];K=b['K0']
    assert np.all(b['group'][:46]==0) and np.max(abs(b['g'][:46]))==0
    x=np.zeros((376,9));out=np.empty((n,9,47))
    for k in range(n):
        if k==0:op=2+5*np.arange(9)
        elif k<duration:op=1+5*np.arange(9)
        elif k==duration:op=3+5*np.arange(9)
        else:op=np.zeros(9,dtype=int)
        e=J@x+b['v'][op].T
        out[k]=e.T
        x=T@x+b['u'][op].T-K@e
    return out

def prepare(p,b):
    S=(b['S']+b['S'].T)/2;W=solve_triangular(cholesky(S,lower=True),np.eye(47),lower=True)
    eig,U=eigh(W@np.diag(np.diag(S))@W.T)
    assert eig.min()>0
    transform=U.T@W
    step=unit_response(b,3600,3601)@transform.T
    long=unit_response(b,3600,1200)@transform.T
    short=unit_response(b,3600,300)@transform.T
    prototypes=step[np.array(p['prototype_ages_reports'])].transpose(1,0,2).reshape(-1,47)
    # Compare the algebraic innovations recursion against explicit state and
    # null-filter propagation, including ON/OFF and instrument memory.
    T=csr_matrix(b['T'][0]);J=b['J'][0];K=b['K0'];x=np.zeros((376,9));m=x.copy();err=0.
    for k in range(90):
        op=2+5*np.arange(9) if k==0 else 1+5*np.arange(9) if k<30 else 3+5*np.arange(9) if k==30 else np.zeros(9,int)
        y=J@x+b['v'][op].T;e=y-J@m
        if k==0:direct=[]
        direct.append(e.T);x=T@x+b['u'][op].T;m=T@m+K@e
    err=float(np.max(abs(np.array(direct)-unit_response(b,90,30))))
    assert err<1e-7
    write(OUT/'OPERATOR_CHECK.json',{'explicit_vs_innovation_recursion_max_error':err,'scope':'nominal load operators, not whole R11 observer equivalence','dimensions':[376,47],'sources':9})
    return eig,prototypes,long,short

def noise_schedule(n,kind,i):
    t=np.arange(n)/30.;a=np.zeros(n)
    if kind=='normal':
        mode=i%3
        if mode==1:a[t>=120]=2.;a[t>=360]=.5
        if mode==2:a=np.clip((t-60)/180,0,1)*2.;a[t>=420]=.5
    else:
        if i%3==1:a[t>=12]=2.
        if i%3==2:a[t>=12]=.5;a[t>=65]=2.
    return a

def observations(p,eig,long,short,split,kind,i):
    seed=p['seeds'][split]+(10000 if kind=='event' else 0)+i
    n=(600 if kind=='normal' else 120)*30
    alpha=noise_schedule(n,kind,i)
    rng=np.random.default_rng(seed);z=rng.normal(size=(n,47))*np.sqrt(1+alpha[:,None]*eig)
    events=[]
    if kind=='event':
        source=i%9;other=(source+4)%9;sign=1 if (i//9)%2==0 else -1
        amp=(.0005 if i<18 else .002)*sign
        for onset,duration,c,response,a in [(30,40,source,long,amp),(80,10,other,short,-amp)]:
            k=onset*30;z[k:]+=a*response[:n-k,c]
            events.append({'on':onset,'off':onset+duration,'source':c,'amplitude':a})
    return z,alpha,events

def infer(z,eig,proto,p):
    """Causal per-report age-mixture score, no temporal history posterior.

    All three arms use the same source/age/severity likelihood. Only the
    observation covariance coefficient and admission gate differ.
    """
    n=len(z);alpha=np.zeros(3);quiet=0;cooldown=0
    scores=np.empty((3,n));source=np.empty((3,n),np.int8);estimated=np.empty((3,n));admit=np.zeros((3,n),bool);lp=np.empty((3,n))
    v=p['severity_prior_sd']**2;eta=p['learning_rate'];b2=eig@eig
    for k,y in enumerate(z):
        var=1+alpha[:,None]*eig
        iv=1/var
        q=(proto*proto)@iv.T
        u=proto@(iv*y).T
        bf=.5*(v*u*u/(1+v*q)-np.log1p(v*q))
        by_source=logsumexp(bf.reshape(9,-1,3),axis=1)-np.log(len(proto)//9)
        logbf=logsumexp(by_source,axis=0)-np.log(9)
        normal_mass=1/(1+np.exp(np.clip(logbf+p['prior_log_odds'],-700,700)))
        scores[:,k]=logbf;source[:,k]=np.argmax(by_source,axis=0);estimated[:,k]=alpha
        lp[:,k]=-.5*(47*np.log(2*np.pi)+np.log(var).sum(axis=1)+(y*y*iv).sum(axis=1))+np.logaddexp(np.log(.99),np.log(.01)+logbf)
        raw=float((eig@(y*y-1))/b2)
        enabled=(k>=p['startup_reports'])
        gate=enabled and quiet>=p['quiet_reports'] and cooldown==0
        admit[1,k]=enabled;admit[2,k]=gate
        if enabled:alpha[1]=np.clip((1-eta)*alpha[1]+eta*raw,0,p['alpha_upper'])
        if gate:alpha[2]=np.clip((1-eta)*alpha[2]+eta*raw,0,p['alpha_upper'])
        # This report can affect eligibility only for later reports.
        if normal_mass[2]>=p['quiet_mass']:
            quiet+=1;cooldown=max(0,cooldown-1)
        else:quiet=0;cooldown=p['cooldown_reports']
    return {'score':scores,'source':source,'alpha':estimated,'admit':admit,'log_predictive':lp}

def alarms(score,source,h,p):
    rows=[];count=0;next_allowed=p['startup_reports']
    for k in range(p['startup_reports'],len(score)):
        if k<next_allowed:continue
        count=count+1 if score[k]>=h else 0
        if count>=p['confirmation_reports']:
            rows.append((k/30,int(source[k])));count=0;next_allowed=k+p['refractory_reports']
    return rows

def metrics(pred,truth,alpha,p,thresholds):
    rows=[];start=p['startup_reports'];duration=pred['score'].shape[1]/30
    for arm,h in enumerate(thresholds):
        published=alarms(pred['score'][arm],pred['source'][arm],h,p) if h is not None else []
        hit=np.zeros(len(truth),bool);extra=0
        for t,c in published:
            eligible=[j for j,e in enumerate(truth) if e['on']<=t<e['off'] and e['source']==c and not hit[j]]
            if eligible:hit[eligible[0]]=True
            else:extra+=1
        rows.append({'arm':ARMS[arm],'feasible':h is not None,'hits':int(hit.sum()),'events':len(truth),'alarms':len(published),'extras':extra,
          'hours':(duration-start/30)/3600,'noise_rmse':float(np.sqrt(np.mean((pred['alpha'][arm,start:]-alpha[start:])**2))),
          'mean_log_predictive':float(np.mean(pred['log_predictive'][arm,start:])),
          'admission_fraction':float(np.mean(pred['admit'][arm,start:]))})
    return rows

def bootstrap_diff(a,b,seed):
    rng=np.random.default_rng(seed);d=np.asarray(a)-np.asarray(b)
    vals=np.mean(d[rng.integers(0,len(d),size=(10000,len(d)))],axis=1)
    return {'difference':float(d.mean()),'ci95':np.quantile(vals,[.025,.975]).tolist(),'parents':len(d)}

def run_stream(p,b):
    eig,proto,long,short=prepare(p,b)
    # Prefix invariance is checked before either cohort is generated.
    rng=np.random.default_rng(7101);toy=rng.normal(size=(420,47))
    a=infer(toy,eig,proto,p);c=infer(toy[:389],eig,proto,p)
    assert all(np.array_equal(a[key][...,:389],c[key]) for key in a)
    grid=p['threshold_grid'];cal_counts=np.zeros((3,len(grid)),int);cal_hours=0.;seals={};records=[]
    for split in ('CAL','TEST'):
        if split=='TEST':
            # This seal exists before creating any TEST stream.
            selection={'protocol_sha256':sha(HERE/'protocol.json'),'code_sha256':sha(Path(__file__)),'normal_hours':cal_hours,'counts':cal_counts.tolist(),'thresholds':thresholds}
            write(OUT/'CAL_SELECTION.json',selection)
            (OUT/'TEST_STARTED.json').write_text(json.dumps({'cal_selection_sha256':sha(OUT/'CAL_SELECTION.json')}))
        for kind in ('normal','event'):
            # Event CAL is unnecessary: no tuning using labeled events.
            if split=='CAL' and kind=='event':continue
            for i in range(p['parents_per_kind']):
                start=time.perf_counter();z,alpha,truth=observations(p,eig,long,short,split,kind,i)
                ident=f'{split}_{kind}_{i:03d}';seals[ident]=hashlib.sha256(z.tobytes()).hexdigest()
                pred=infer(z,eig,proto,p)
                if split=='CAL':
                    for arm in range(3):
                        for j,h in enumerate(grid):cal_counts[arm,j]+=len(alarms(pred['score'][arm],pred['source'][arm],h,p))
                    cal_hours+=(len(z)-p['startup_reports'])/30/3600
                else:
                    rows=metrics(pred,truth,alpha,p,thresholds)
                    for row in rows:row.update(parent=ident,kind=kind)
                    records.extend(rows)
                # Compact evidence sufficient to re-evaluate publication counts.
                np.savez_compressed(OUT/(ident+'.npz'),score=pred['score'],source=pred['source'],alpha=pred['alpha'],admit=pred['admit'])
                if i<2 and split=='TEST':
                    np.savez_compressed(OUT/(ident+'_trace.npz'),**pred,true_alpha=alpha,observed_norm=np.linalg.norm(z,axis=1))
                print(f'{ident} completed {time.perf_counter()-start:.1f}s',flush=True)
        if split=='CAL':
            thresholds=[]
            for counts in cal_counts:
                feasible=np.flatnonzero(counts/cal_hours<=p['far_budget_per_hour'])
                thresholds.append(grid[int(feasible[0])] if len(feasible) else None)
    write(OUT/'INPUT_HASHES.json',seals);write(OUT/'PARENT_METRICS.json',records)
    summaries={}
    for arm in ARMS:
        ns=[r for r in records if r['arm']==arm and r['kind']=='normal'];es=[r for r in records if r['arm']==arm and r['kind']=='event']
        hours=sum(r['hours'] for r in ns);n=sum(r['alarms'] for r in ns)
        summaries[arm]={'threshold':thresholds[ARMS.index(arm)],'normal_alarms':n,'normal_hours':hours,'normal_far':n/hours,'poisson_upper95_per_hour':float(.5*chi2.ppf(.95,2*(n+1))/hours),
          'timely_joint_hits':sum(r['hits'] for r in es),'events':sum(r['events'] for r in es),'extra_alarms':sum(r['extras'] for r in es),
          'event_hours':sum(r['hours'] for r in es),'normal_noise_rmse':float(np.mean([r['noise_rmse'] for r in ns])),
          'normal_mean_log_predictive':float(np.mean([r['mean_log_predictive'] for r in ns])),
          'normal_admission_fraction':float(np.mean([r['admission_fraction'] for r in ns]))}
    contrasts={}
    for a,bname in [('adaptive','fixed'),('guarded','fixed'),('guarded','adaptive')]:
        A=[r['hits']/r['events'] for r in records if r['arm']==a and r['kind']=='event'];B=[r['hits']/r['events'] for r in records if r['arm']==bname and r['kind']=='event']
        contrasts[a+'-'+bname]=bootstrap_diff(A,B,p['seeds']['bootstrap'])
    write(OUT/'STREAM_RESULTS.json',{'scope':'F01 linear-operator per-report diagnostic, not R11, nonlinear transfer or TVE-calibrated PMU simulation','arms':summaries,'paired_timely_contrasts':contrasts,'prefix_invariance':True})

def run_covariance(p,b):
    """Known-onset, known-amplitude source diagnostic; no detector FAR claim."""
    S=(b['S']+b['S'].T)/2;W=solve_triangular(cholesky(S,lower=True),np.eye(47),lower=True)
    horizon=15
    step=unit_response(b,1201,1202)@W.T
    recovery=unit_response(b,1230,1200)@W.T
    target=step[:horizon].transpose(1,0,2).reshape(9,-1)
    U=recovery[1215:1230].transpose(1,0,2).reshape(9,-1)*p['recovery_amplitude_sd']
    rows=[];rng=np.random.default_rng(p['seeds']['covariance']);dim=47*horizon
    for i in range(p['covariance_parents']):
        source=i%9;prior=(source+1+(i//9)%8)%9
        amp=(.0005 if (i//9)%2==0 else .002)*(1 if (i//18)%2==0 else -1)
        means=amp*target;u=U[prior];c=u@u;latent=rng.normal();noise=rng.normal(size=dim)
        y=means[source]+u*latent+noise
        residual=y[None,:]-means
        fixed=np.sum(residual**2,axis=1)
        carry=fixed-(residual@u)**2/(1+c)
        for arm,dist,logdet in [('mean_only',fixed,0.),('mean_covariance',carry,np.log1p(c))]:
            rows.append({'parent':i,'source':source,'prior_source':prior,'arm':arm,'correct':int(np.argmin(dist)==source),'nis_covered':int(dist[source]<=chi2.ppf(.95,dim)),
                'true_source_log_density':float(-.5*(dim*np.log(2*np.pi)+logdet+dist[source]))})
    write(OUT/'COVARIANCE_PARENTS.json',rows)
    summary={arm:{'correct':sum(r['correct'] for r in rows if r['arm']==arm),'parents':p['covariance_parents'],
      'nis95_coverage':float(np.mean([r['nis_covered'] for r in rows if r['arm']==arm])),
      'mean_true_source_log_density':float(np.mean([r['true_source_log_density'] for r in rows if r['arm']==arm]))} for arm in ['mean_only','mean_covariance']}
    a=[r['correct'] for r in rows if r['arm']=='mean_covariance'];bb=[r['correct'] for r in rows if r['arm']=='mean_only']
    write(OUT/'COVARIANCE_RESULTS.json',{'scope':'known onset, amplitude and recovery mean; Gaussian inherited severity uncertainty; correct nominal linear model','arms':summary,'paired_correctness':bootstrap_diff(a,bb,p['seeds']['bootstrap'])})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true');args=parser.parse_args();OUT.mkdir(exist_ok=True)
    if args.freeze:
        assert not (OUT/'EXECUTION_FREEZE.json').exists()
        p={'scope':'independent nominal linear-operator diagnostic, no C03 observations or runtime writes',
          'snapshot_sha256':sha(BASE/'input_snapshot.npz'),'parents_per_kind':36,'covariance_parents':360,
          'seeds':{'CAL':13123000,'TEST':13124000,'bootstrap':13125000,'covariance':13126000},
          'prototype_ages_reports':[0,2,14,29,59,119,299,899],'severity_prior_sd':.01,
          'startup_reports':360,'learning_rate':1/900,'alpha_upper':8.,'quiet_reports':15,'quiet_mass':.99,'cooldown_reports':60,
          'prior_log_odds':float(np.log(.01/.99)),'confirmation_reports':6,'refractory_reports':150,
          'threshold_grid':[0.,1.,2.,3.,4.,5.,6.,8.,10.,12.,16.,24.,32.,48.,64.],
          'far_budget_per_hour':1.,'recovery_amplitude_sd':.002,
          'noise_contract':'nominal innovations plus alpha times diagonal innovation covariance; not physical independent PMU TVE',
          'endpoint':'timely correct load source under per-report likelihood scan; no family or OFF estimator'}
        write(HERE/'protocol.json',p)
        write(OUT/'EXECUTION_FREEZE.json',{'protocol_sha256':sha(HERE/'protocol.json'),'code_sha256':sha(Path(__file__)),'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
        print('Protocol and code frozen before data generation');return
    p,b=load();freeze=json.loads((OUT/'EXECUTION_FREEZE.json').read_text());assert freeze['protocol_sha256']==sha(HERE/'protocol.json') and freeze['code_sha256']==sha(Path(__file__))
    assert not (OUT/'COMPLETE.json').exists(),'Run is already sealed'
    run_covariance(p,b);run_stream(p,b)
    seal={f.name:sha(f) for f in OUT.glob('*') if f.is_file()}
    write(OUT/'COMPLETE.json',{'status':'COMPLETE','files':seal,'python':platform.python_version(),'numpy':np.__version__})
    print('COMPLETE',flush=True)
if __name__=='__main__':main()
