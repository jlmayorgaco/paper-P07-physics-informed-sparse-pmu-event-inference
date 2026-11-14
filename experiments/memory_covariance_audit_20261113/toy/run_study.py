"""Matched-calibration Monte Carlo: mean vs Gaussian vs state mixture vs labeled.

Important scope: 3 dynamic swing nodes + grounded reference; fixed linear
post-restoration mode; one new load with known onset; not IEEE39.
"""
from __future__ import annotations
import argparse, json, hashlib, csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import logsumexp
from experiment import setup, simulate, posterior, METHODS

SCENARIOS = [
    dict(name='nominal_colored', horizon_s=.65,noise_scale=1.0,spread=1.,temporal_rho=.90,history_kind='two_sources'),
    dict(name='short_evidence', horizon_s=.35,noise_scale=1.0,spread=1.,temporal_rho=.90,history_kind='two_sources'),
    dict(name='noisy_colored', horizon_s=.65,noise_scale=1.4,spread=.8,temporal_rho=.97,history_kind='two_sources'),
    dict(name='signed_recovery', horizon_s=.65,noise_scale=1.0,spread=1.,temporal_rho=.95,history_kind='signed_load'),
]


def run_scenario(params,n_test,n_cal,seed,alpha=.05,n_boot=1500):
    sc=params.copy();name=sc.pop('name')
    g=setup(**sc)
    Ycal,_,_,_=simulate(g,n_cal,seed+123,force_class=0)
    Ytest,ctest,htest,atest=simulate(g,n_test,seed)
    idx_event=(ctest!=0); idx_null=(ctest==0)
    out=dict(scenario=name, assumptions={k:v for k,v in sc.items()},n_test=n_test,n_cal=n_cal,
             alpha=alpha, methods={}, C_D_max_diff=0., old_cause_acc=None)
    preds={}; detection={}
    for mode in METHODS:
        pcal,_,_,lo_cal=posterior(g,Ycal,mode)
        ptest,ph,ll,lo=posterior(g,Ytest,mode)
        # split sample-independent calibration; strict > for empirical threshold.
        # finite n_cal => target approximately alpha on fresh normal data.
        cutoff=np.quantile(lo_cal,1-alpha)
        alarm=(lo>cutoff)
        pred_source=ptest[:,1:].argmax(axis=1)+1
        covered=alarm & (pred_source==ctest) & idx_event
        true_p=np.maximum(ptest[np.arange(n_test),ctest],1e-300)
        m=dict(
          threshold_log_odds=float(cutoff),
          FPR_test=float(alarm[idx_null].mean()),
          TPR_event=float(alarm[idx_event].mean()),
          event_source_coverage=float(covered[idx_event].mean()),
          source_accuracy_if_forced=float((pred_source[idx_event]==ctest[idx_event]).mean()),
          overall_threeway_accuracy=float((ptest.argmax(axis=1)==ctest).mean()),
          class_log_loss=float(-np.log(true_p).mean()),
          predictive_NLL=float(-ll.mean()),
          brier=float(np.mean(np.sum((ptest-np.eye(3)[ctest])**2,axis=1))),
        )
        if mode=='labeled_histories':
            m['historical_cause_accuracy']=float((ph.argmax(axis=1)==htest).mean())
            m['historical_cause_log_loss']=float(-np.log(np.maximum(ph[np.arange(n_test),htest],1e-300)).mean())
            out['old_cause_acc']=m['historical_cause_accuracy']
        out['methods'][mode]=m
        preds[mode]=ptest; detection[mode]=(alarm,pred_source,covered)
    out['C_D_max_diff']=float(np.max(np.abs(preds['unlabeled_mixture']-preds['labeled_histories'])))
    assert out['C_D_max_diff']<=1e-12
    # Paired bootstrap for the difference in correct detected source per event.
    i=np.flatnonzero(idx_event)
    aC=detection['unlabeled_mixture'][2][i].astype(float)
    bB=detection['moment_gaussian'][2][i].astype(float)
    aA=detection['mean_only'][2][i].astype(float)
    rng=np.random.default_rng(seed+777)
    ids=rng.integers(0,len(i),size=(n_boot,len(i)))
    for key,x,y in [('mixture_minus_gaussian',aC,bB),('mixture_minus_mean',aC,aA)]:
        paired=x-y
        diffs=paired[ids].mean(axis=1)
        out[key]={'point':float(paired.mean()),'paired_bootstrap_95':[float(v) for v in np.quantile(diffs,[.025,.975])]}
    out['_raw']={'ctest':ctest,'htest':htest,'ptest':preds,'test_y':Ytest,'decisions':detection,'m_h':g['m_h']}
    return out


def write_plot(outcomes,path):
    labels=[o['scenario'].replace('_','\n') for o in outcomes]
    keys=['mean_only','moment_gaussian','unlabeled_mixture']
    names=['Media sola','Gaussiana por momentos','Mezcla exacta']
    x=np.arange(len(labels));width=.24
    fig,ax=plt.subplots(figsize=(10.8,5.2),layout='constrained')
    for j,(key,name) in enumerate(zip(keys,names)):
        vals=[o['methods'][key]['event_source_coverage']*100 for o in outcomes]
        ax.bar(x+(j-1)*width,vals,width,label=name)
    ax.set_ylabel('Evento detectado y fuente correcta (%)')
    ax.set_title('Mismo modelo físico, comienzo conocido, FPR calibrado al 5%')
    ax.set_xticks(x,labels);ax.set_ylim(0,100);ax.legend(fontsize=9)
    ax.grid(axis='y',alpha=.2)
    fig.savefig(path,dpi=175);plt.close(fig)


def write_density_plot(path):
    # Analytic counterexample to moment sufficiency for predictive likelihoods.
    xx=np.linspace(-3,3,1000)
    v=.25**2;m=1.0
    from scipy.stats import norm
    mix=.5*norm.pdf(xx,-m,np.sqrt(v))+.5*norm.pdf(xx,m,np.sqrt(v))
    gauss=norm.pdf(xx,0,np.sqrt(v+m*m))
    fig,ax=plt.subplots(figsize=(8.5,4.5),layout='constrained')
    ax.plot(xx,mix,label='Mezcla gaussiana (posterior completo)')
    ax.plot(xx,gauss,label='Gaussiana con misma media y varianza',linestyle='--')
    ax.set_title('Iguales dos primeros momentos; diferentes densidades predictivas')
    ax.set_xlabel('Observación estandarizada');ax.set_ylabel('Densidad predictiva')
    ax.grid(alpha=.2);ax.legend(fontsize=9)
    fig.savefig(path,dpi=175);plt.close(fig)
    return dict(means=[-m,m],weight=[.5,.5],within_var=v,
                mix_density_zero=float(.5*norm.pdf(0,-m,np.sqrt(v))+.5*norm.pdf(0,m,np.sqrt(v))),
                gaussian_density_zero=float(norm.pdf(0,0,np.sqrt(v+m*m))))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--n-test',type=int,default=2400)
    parser.add_argument('--n-cal',type=int,default=1200)
    parser.add_argument('--seed',type=int,default=20261113)
    parser.add_argument('--output',default=str(Path(__file__).parent/'results'))
    args=parser.parse_args()
    outdir=Path(args.output);outdir.mkdir(parents=True,exist_ok=True)
    out=[];allrows=[]
    for k,sc in enumerate(SCENARIOS):
        print('running',sc['name'],flush=True)
        o=run_scenario(sc,args.n_test,args.n_cal,args.seed+k*1000)
        raw=o.pop('_raw')
        if k==0:
            np.savez_compressed(outdir/'sample_200_trials.npz',
              y=raw['test_y'][:200],class_new=raw['ctest'][:200],history_previous=raw['htest'][:200],
              prob_mean=raw['ptest']['mean_only'][:200],prob_gaussian=raw['ptest']['moment_gaussian'][:200],
              prob_mixture=raw['ptest']['unlabeled_mixture'][:200],
              prob_labeled=raw['ptest']['labeled_histories'][:200],
              prior_means=raw['m_h'])
        out.append(o)
        for mode,metrics in o['methods'].items():
            allrows.append(dict(scenario=o['scenario'],method=mode,**metrics))
        print(' ',[(mode,round(v['event_source_coverage'],3),round(v['class_log_loss'],3)) for mode,v in o['methods'].items()])
    write_plot(out,outdir/'coverage_same_fpr.png')
    scalar=write_density_plot(outdir/'mixture_vs_moment_density.png')
    cols=list(dict.fromkeys(key for row in allrows for key in row.keys()))
    with (outdir/'metrics.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(allrows)
    result=dict(status='success',experiment='toy_swing_histories_exact_bayes',
      scope=['3 swing nodes + 1 grounded reference','known new event onset','single new Gaussian-amplitude event or null',
             'previous event restored before window','identical physical model/likelihood/prior across arms',
             'Gaussian state priors with two history components','time-correlated Gaussian noise modeled exactly',
             'no IEEE39 validation','old cause inference available only when mapping preserved'],
      calibration='independent normal-only data, 5% false positive target per evaluation window',
      results=out,scalar_counterexample=scalar)
    (outdir/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
    print('saved',outdir,flush=True)

if __name__=='__main__': main()
