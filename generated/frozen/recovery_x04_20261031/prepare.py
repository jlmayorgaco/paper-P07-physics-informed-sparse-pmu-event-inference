"""Fixed, separate full-F01 physical falsification; no detector tuning."""
from pathlib import Path
import hashlib,json,shutil,time
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1];PARENT=REPO/'experiments/PAPER_METHOD_EI_X02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf8')
def main():
    assert not (HERE/'protocol/PLAN.json').exists(),'Preserve existing candidate'
    shutil.copytree(PARENT/'runtime',HERE/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copy2(PARENT/'simulate.jl',HERE/'simulate.jl')
    for p in ['engine/diagnostics','engine/events/results','results','logs','figures','protocol']:(HERE/p).mkdir(parents=True,exist_ok=True)
    cases=[];design=[]
    sources=[3,16,18,21,27]
    contexts=[(0,0.)]+[(p,d) for p in [7,24] for d in [.5,2.]]
    def add(prior,delay,source,amp,prior_amp=.08,role='response'):
        tau=3.5 if not prior else 3.+delay
        cid=f'X{len(cases)+1:03d}';actions=[]
        for bus,t,v in [(prior or 7,2.,1.+(prior_amp if prior else 0.)),(prior or 7,3.,1.),(source or 3,tau,1.+(amp if source else 0.))]:
            for par in ['ZIPLoad₊Pset','ZIPLoad₊Qset']:actions.append(dict(kind='vertex',asset=bus,time_s=t,parameter=par,mode='factor',value=v))
        cases.append(dict(id=cid,duration_s=8.,operating_point='F01',actions=actions))
        design.append(dict(id=cid,prior=prior,delay=delay,prior_amp=prior_amp,source=source,amplitude=amp,onset_s=tau,role=role))
    for prior,delay in contexts:
        add(prior,delay,None,0.)
        for source in sources:add(prior,delay,source,.0006)
        if prior:
            for pa in [.078,.082]:add(prior,delay,None,0.,pa,'history_uncertainty')
    plan=dict(id='F01_RECOVERY_X04',created_unix_s=time.time(),scope='Oracle physical falsification, not a causal inference or R11 comparison',
              hypothesis='Recovery can change a source response without increasing profiled source separation.',
              source_pairs=[[18,27],[16,21],[3,21]],prior_buses=[7,24],delays_s=[.5,2.],horizon_s=1.5,
              prior_on_s=2.,prior_off_s=3.,prior_fraction=.08,secondary_fraction=.0006,
              previous_fraction_sd=.01,amplitude_prior_sd=.0015,noise_seed=391004,draws_per_source=300,
              assumed_noise='Unit Gaussian innovations after frozen 47-coordinate instrument whitener; not a new F01 noise calibration',
              nuisance='Scalar prior severity derivative; excludes full state posterior; oracle recovery-only baseline',
              decisions='Known onset and family, two candidates; no H0, no cardinality test, no field inference',
              comparisons=['equilibrium signatures on recovery data','recovery-conditioned signatures on identical data'],
              physical_trajectories=len(cases),no_parameter_selection_after_results=True,
              interpretation='All outcomes retained. No new C01 result or operational superiority claim.')
    write(HERE/'protocol/PLAN.json',plan);write(HERE/'protocol/DESIGN.json',design)
    cfg=json.loads((PARENT/'engine/REQUEST.json').read_text())
    cfg['operating_points']=[dict(id='F01',p_factor=1.,q_factor=1.,dispatch_factor=1.)];cfg['cases']=cases
    write(HERE/'engine/REQUEST.json',cfg)
    protected=[]
    for p in (REPO/'SIM0001_JuliaPD_F01').rglob('*'):
        if p.is_file() and '__pycache__' not in str(p):protected.append(dict(path=str(p.relative_to(REPO)),sha256=sha(p)))
    for f in ['protocol/EXECUTION_FREEZE.json','protocol/FREEZE.json']:
        p=REPO/'experiments/PAPER_CONFIRMATORY_C01'/f
        if p.exists():protected.append(dict(path=str(p.relative_to(REPO)),sha256=sha(p)))
    write(HERE/'protocol/PROTECTED_BEFORE.json',protected)
    inputs=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in ['.py','.jl','.json','.csv','.npz','.toml'] and '/results/' not in p.as_posix()]
    write(HERE/'protocol/FREEZE.json',dict(before_simulation=True,files=[dict(path=str(p.relative_to(HERE)),sha256=sha(p)) for p in inputs]))
    print('FROZEN',len(cases),'trajectories')
if __name__=='__main__':main()
