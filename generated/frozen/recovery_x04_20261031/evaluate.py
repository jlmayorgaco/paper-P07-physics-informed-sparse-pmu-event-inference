"""Oracle geometry check on continuous full F01 trajectories, NOT a detector."""
from pathlib import Path
import importlib.util,json,sys,hashlib
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]
spec=importlib.util.spec_from_file_location('read_only_x02_measurement',HERE/'measurement_bridge.py')
x02=importlib.util.module_from_spec(spec);spec.loader.exec_module(x02)
def write(name,obj):
    (HERE/'results'/name).write_text(json.dumps(obj,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
def inv(v,U):return v-U@np.linalg.solve(np.eye(U.shape[1])+U.T@U,U.T@v)
def distance(a,b,U):
    values=[]
    for x,y in [(a,b),(b,a)]:
        c=max(0.,float(x@inv(y,U))/max(float(y@inv(y,U)),1e-30))
        r=x-c*y;values.append(float(r@inv(r,U)))
    return max(0.,min(values))
def accuracy(samples,g1,g2,U,sd,n):
    scores=[]
    for g in [g1,g2]:
        ig=inv(g,U);q=float(g@ig);scores.append(.5*(sd**2*(samples@ig)**2/(1+sd**2*q)-np.log1p(sd**2*q)))
    return float((np.sum(scores[0][:n]>scores[1][:n])+np.sum(scores[1][n:]>scores[0][n:]))/(2*n))
def main():
    plan=json.loads((HERE/'protocol/PLAN.json').read_text());design=json.loads((HERE/'protocol/DESIGN.json').read_text())
    cm=x02.CoordinateMap();mapping=pd.read_csv(HERE/'runtime/reference/terminal_mapping.csv');kv=pd.read_csv(HERE/'runtime/reference/data/bus.csv').base_kv.to_numpy()
    lookup={};signals={};continuity=[]
    for case in design:
        folder=HERE/'engine/events/diagnostics'/case['id'];p=folder/'status.json'
        assert p.exists(),f'Incomplete/rejected trajectory {case["id"]}'
        status=json.loads(p.read_text());assert status['continuity_and_frozen_plant_pass']
        assert status['trajectory_solves']==1 and status['dynamic_state_resets']==0 and status['reports']==241
        v=pd.read_csv(folder/'voltage_all_pu.csv');i=pd.read_csv(folder/'native_terminal_current_pu.csv');t=v.time_s.to_numpy()
        va=v.iloc[:,1:].to_numpy().reshape(len(t),39,2);ia=i.iloc[:,1:].to_numpy().reshape(len(t),8,2)
        z=x02.report(t,va[:,:,0]+1j*va[:,:,1],ia[:,:,0]+1j*ia[:,:,1],mapping,kv,cm.cfg)
        det=dict(voltage_magnitude=abs(z['voltage_pu'])*345e3/np.sqrt(3),current_magnitude=abs(z['current_A']),voltage_angle=np.angle(z['voltage_pu'],deg=True),current_angle=np.angle(z['current_A'],deg=True),frequency=z['frequency_hz'],rocof=z['rocof_hz_s'])
        y=cm.coordinates(t,det);signals[case['id']]=det
        lookup[case['prior'],case['delay'],case['source'],case['prior_amp']]=(case,y)
        np.savez_compressed(HERE/'results'/f'{case["id"]}_coordinates.npz',time_s=t,y=y)
        continuity.append(dict(id=case['id'],max_differential_jump=status['max_differential_jump'],max_algebraic_residual=status['max_algebraic_residual'],trajectory_solves=1,dynamic_state_resets=0))
    def window(y,tau):return cm.whiten(y)[round(tau*30):round((tau+1.5)*30)+1].ravel()
    eqbase=lookup[0,0.,None,.08][1];eq={s:window(lookup[0,0.,s,.08][1]-eqbase,3.5) for s in [3,16,18,21,27]}
    rows=[];pre=[];rng=np.random.default_rng(plan['noise_seed']);n=plan['draws_per_source'];amp=plan['secondary_fraction'];sd=plan['amplitude_prior_sd']
    for prior in plan['prior_buses']:
        for delay in plan['delays_s']:
            base=lookup[prior,delay,None,.08][1];tau=3.+delay
            U=(plan['previous_fraction_sd']*window((lookup[prior,delay,None,.082][1]-lookup[prior,delay,None,.078][1])/.004,tau))[:,None]
            rec={s:window(lookup[prior,delay,s,.08][1]-base,tau) for s in eq}
            for source in eq:
                dy=lookup[prior,delay,source,.08][1]-base
                pre.append(dict(prior=prior,delay=delay,source=source,max_prefix_difference=float(np.max(np.abs(dy[:round(tau*30)])))))
            for a,b in plan['source_pairs']:
                g1,g2=rec[a]/amp,rec[b]/amp;e1,e2=eq[a]/amp,eq[b]/amp
                Z=rng.standard_normal((2*n,len(g1)))+rng.standard_normal((2*n,1))@U.T
                Z[:n]+=rec[a];Z[n:]+=rec[b]
                d0=distance(eq[a],eq[b],np.empty((len(g1),0)));known=distance(rec[a],rec[b],np.empty((len(g1),0)));unc=distance(rec[a],rec[b],U)
                rows.append(dict(prior_bus=prior,delay_s=delay,source_a=a,source_b=b,d2_equilibrium=d0,d2_recovery_known=known,d2_recovery_uncertain=unc,
                                 ratio_known=known/d0,ratio_uncertain=unc/d0,
                                 signature_change_a=np.linalg.norm(rec[a]-eq[a])/np.linalg.norm(eq[a]),signature_change_b=np.linalg.norm(rec[b]-eq[b])/np.linalg.norm(eq[b]),
                                 accuracy_frozen=accuracy(Z,e1,e2,U,sd,n),accuracy_conditioned=accuracy(Z,g1,g2,U,sd,n)))
    df=pd.DataFrame(rows);df['gain_pp']=100*(df.accuracy_conditioned-df.accuracy_frozen)
    df.to_csv(HERE/'results/PER_CASE.csv',index=False);pd.DataFrame(continuity).to_csv(HERE/'results/CONTINUITY.csv',index=False);pd.DataFrame(pre).to_csv(HERE/'results/PREFIX_EQUALITY.csv',index=False)
    assert max(p['max_prefix_difference'] for p in pre)<1e-6,'Counterfactual prefix mismatch'
    protected=json.loads((HERE/'protocol/PROTECTED_BEFORE.json').read_text())
    assert all(hashlib.sha256((REPO/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in protected)
    summary=dict(scope=plan['scope'],physical_trajectories=len(design),comparisons=len(df),distinct_recovery_histories=4,
                 median_ratio_known=float(df.ratio_known.median()),median_ratio_uncertain=float(df.ratio_uncertain.median()),
                 ratio_uncertain_above_one=int((df.ratio_uncertain>1).sum()),mean_frozen=float(df.accuracy_frozen.mean()),mean_conditioned=float(df.accuracy_conditioned.mean()),
                 mean_gain_pp=float(df.gain_pp.mean()),negative_gain_cases=int((df.gain_pp<0).sum()),protected_files_unchanged=len(protected),
                 max_prefix_difference=max(p['max_prefix_difference'] for p in pre),
                 warnings=['Oracle recovery state/baseline and known onset/pair','Finite-amplitude secants, not infinitesimal analytical tangents','Gaussian innovation surrogate; no new PMU-noise calibration','Not R11/M3H or a causal detection benchmark','No independent confirmation; no significance claim'])
    write('SUMMARY.json',summary)
    # Fixed illustrative case chosen in protocol: previous BUS7, delay .5, sources 18/27.
    ids={s:lookup[7,.5,s,.08][0]['id'] for s in [None,18,27]}
    trace={'time_s':t}
    for field in ['voltage_magnitude','current_magnitude','frequency']:
        for s in [None,18,27]:trace[f'{field}_{s}']=signals[ids[s]][field][:,1]
    pd.DataFrame(trace).to_csv(HERE/'results/FIXED_BUS5_TRACE.csv',index=False)
    write('COMPLETE.json',dict(complete=True,plant_changed=False,C01_changed=False))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
