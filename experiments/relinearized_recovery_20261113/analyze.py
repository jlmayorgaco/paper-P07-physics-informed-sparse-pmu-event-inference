"""Frozen prediction comparison, never a detector or a C03 evaluator."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
import pandas as pd

P=Path(__file__).resolve().parent;REF=P.parent/'hamiltonian_f01_20261113/reproduction/reference'
def main():
    for freeze in ['EXECUTION_FREEZE.json','ANALYSIS_FREEZE.json']:
        for name,sha in json.loads((P/freeze).read_text())['files'].items():
            assert hashlib.sha256((P/name).read_bytes()).hexdigest()==sha,name
    cfg=json.loads((P/'protocol.json').read_text());mapping=pd.read_csv(REF/'terminal_mapping.csv')
    reportcfg=json.loads((REF/'reporting_config.json').read_text());pmus=np.array(reportcfg['pmus'])-1
    kv=pd.read_csv(REF/'data/bus.csv').base_kv.to_numpy()
    spec=importlib.util.spec_from_file_location('frozen_pmu',REF/'pmu_operator.py');pmu=importlib.util.module_from_spec(spec);spec.loader.exec_module(pmu)
    with np.load(REF/'fixed_network.npz') as z:Yf,Yt=z['Yf'],z['Yt']
    status=json.loads((P/'predictions/STATUS.json').read_text());solves=json.loads((P/'truth/PHYSICS_STATUS.json').read_text())
    assert len(status)==len(cfg['cases']) and len(solves)==len(cfg['cases'])
    t=np.arange(361)/30
    shifts=(reportcfg['common_phase_intercept_deg']+reportcfg['common_phase_slope_deg_s']*t)[:,None]+np.array(reportcfg['relative_voltage_bias_deg'])
    scale=np.array([100e6/(np.sqrt(3)*kv[int(r.terminal)-1]*1000)*r.gain for r in mapping.itertuples()])
    poly_t=np.arange(-20,1)/30;weights=np.linalg.pinv(np.column_stack([np.ones(21),poly_t,poly_t**2]))
    def read(path,step=1):
        a=pd.read_csv(path).iloc[::step];assert np.allclose(a.time_s.to_numpy(),t,rtol=0,atol=1e-12)
        return a[[f'V{k}_r' for k in range(1,40)]].to_numpy()+1j*a[[f'V{k}_i' for k in range(1,40)]].to_numpy()
    def currents(v,case):
        out=[]
        for r in mapping.itertuples():
            y=(Yf if r.side=='src' else Yt)[int(r.julia_edge_1based)-1]
            cur=v@y
            if case['kind']=='line' and int(r.julia_edge_1based)==case['edge']:
                cur[(t>=case['on'])&(t<case['off'])]=0
            out.append(cur)
        return np.column_stack(out)
    def families(v,case,base=None,truth=False):
        cur=currents(v,case);vp=v[:,pmus]
        if base is None:
            vm=abs(vp);va=np.angle(vp,deg=True)+shifts
            im=abs(cur)*scale;ia=np.angle(cur*np.array(mapping.polarity),deg=True)+shifts+np.array(mapping.bias_deg)
        else:
            b=base[:,pmus];dv=vp-b;bc=currents(base,case);di=cur-bc
            assert np.min(abs(bc))>1e-8
            vm=abs(b)+np.real(dv*np.conj(b)/abs(b));va=np.angle(b,deg=True)+np.rad2deg(np.imag(dv/b))+shifts
            im=(abs(bc)+np.real(di*np.conj(bc)/abs(bc)))*scale
            ia=np.angle(bc*np.array(mapping.polarity),deg=True)+np.rad2deg(np.imag(di/bc))+shifts+np.array(mapping.bias_deg)
        if truth:
            rep=pmu.report(t,v,-cur,mapping,kv,reportcfg);f=rep['frequency_hz'];roc=rep['rocof_hz_s']
        else:
            phase=np.rad2deg(np.unwrap(np.deg2rad(va),axis=0));f=np.full((len(t),8),np.nan);roc=f.copy()
            for k in range(20,len(t)):
                coef=weights@phase[k-20:k+1];f[k]=60+coef[1]/360;roc[k]=2*coef[2]/360
        return dict(voltage_magnitude_pu=vm,voltage_phase_deg=va,current_magnitude_A=im,current_phase_deg=ia[:,:7],frequency_hz=f,rocof_hz_s=roc)
    rms=lambda a:float(np.sqrt(np.mean(a*a)))
    rows=[];traces=[];cases=[];timings=[]
    for case in cfg['cases']:
        name=case['id'];vtrue=read(P/'truth'/(name+'_network.csv'),4)
        native=pd.read_csv(P/'truth'/(name+'_network.csv')).iloc[::4]
        ni=np.column_stack([native[f'E{r.julia_edge_1based}_{r.side}_r'].to_numpy()+1j*native[f'E{r.julia_edge_1based}_{r.side}_i'].to_numpy() for r in mapping.itertuples()])
        current_error=float(np.max(abs(ni+currents(vtrue,case))))
        assert current_error<1e-8
        true=families(vtrue,case,truth=True)
        cs=dict(case=name,terminal_error_pu=current_error,status=next(r['status'] for r in status if r['case']==name),arms={})
        if cs['status']!='SUCCESS':cases.append(cs);continue
        for arm,suffix in [('fixed_polar','fixed_complex'),('fixed_nonlinear_observation','fixed_nonlinear_observation'),('relinearized_3','relinearized_3'),('relinearized_1','relinearized_1')]:
            v=read(P/'predictions'/(name+'_'+suffix+'.csv'))
            base=read(P/'predictions'/(name+'_fixed_base.csv')) if arm=='fixed_polar' else None
            rep=families(v,case,base=base)
            ar={}
            for window,take in dict(active=(t>=case['on'])&(t<case['off']),recovery=t>=case['off']).items():
                for key in true:
                    e=rep[key]-true[key]
                    if 'phase' in key:e=(e+180)%360-180
                    rows.append(dict(case=name,arm=arm,window=window,family=key,reports=int(take.sum()),channels=e.shape[1],rmse=rms(e[take]),max_error=float(np.max(abs(e[take])))))
                    if key=='voltage_phase_deg':ar[window+'_phase_rmse_deg']=rms(e[take])
            # For fixed_polar, reconstruct the phasor from its actual polar observation.
            reconstructed=rep['voltage_magnitude_pu']*np.exp(1j*np.deg2rad(rep['voltage_phase_deg']-shifts))
            ar['max_complex_voltage_error_pu']=float(np.max(abs(reconstructed-vtrue[:,pmus])))
            cs['arms'][arm]=ar
            pe=(rep['voltage_phase_deg']-true['voltage_phase_deg']+180)%360-180
            me=rep['voltage_magnitude_pu']-true['voltage_magnitude_pu']
            for i,tk in enumerate(t):traces.append(dict(case=name,arm=arm,time_s=tk,phase_rmse_deg=rms(pe[i]),magnitude_rmse_pu=rms(me[i])))
            if arm.startswith('relinearized'):
                timing=pd.read_csv(P/'predictions'/(name+'_timing_'+arm.split('_')[-1]+'.csv')).seconds.to_numpy()
                timings.append(dict(case=name,arm=arm,total_s=float(timing.sum()),mean_ms=float(1e3*timing.mean()),p95_ms=float(1e3*np.quantile(timing,.95)),max_ms=float(1e3*timing.max())))
        cases.append(cs)
    lookup={c['case']:c for c in cases};rule=cfg['decision_rule'];gates={}
    gates['all_cases_success']=all(c['status']=='SUCCESS' for c in cases) and all(s['retcode']=='Success' for s in solves)
    if gates['all_cases_success']:
        for case in cfg['cases']:
            n=case['id'];a=lookup[n]['arms'];old=a['fixed_polar']['recovery_phase_rmse_deg'];new=a['relinearized_3']['recovery_phase_rmse_deg']
            if case['kind']=='line':gates[n+'_phase_improves_50pct']=new<=(1-rule['recovery_phase_reduction_each_line_at_least_fraction'])*old
            elif n!='normal':gates[n+'_no_phase_regression']=new<=rule['load_voltage_phase_rmse_max_ratio']*old
        gates['normal_stays_quiet']=lookup['normal']['arms']['relinearized_3']['max_complex_voltage_error_pu']<=rule['normal_voltage_complex_max_pu']
        prior=pd.read_csv(P.parent/'descriptor_bridge_20261113/run_v2/report_errors.csv')
        baseline=float(prior[(prior.case=='line')&(prior.reporting=='first_order_ordinary_reporting')&(prior.window=='recovery')&(prior.family=='voltage_phase_deg')].rmse.iloc[0])
        gates['reference_baseline_reproduced']=abs(lookup['line_ref']['arms']['fixed_polar']['recovery_phase_rmse_deg']-baseline)<=rule['reference_baseline_rmse_abs_tolerance_deg']
    gates['algebraic_consistency']=max([s['algebraic_residual'] for s in solves]+[r['relinearized_3']['algebraic_residual'] for r in status if r['status']=='SUCCESS'])<rule['algebraic_residual_max']
    gates['physical_continuity']=all(s['dynamic_jump']<1e-8 for s in solves) and all(r['relinearized_3']['recenter_state_jump']==0 for r in status if r['status']=='SUCCESS')
    out=dict(scope=cfg['scope'],gates=gates,passed=all(gates.values()),cases=cases,timings=timings,
             limitations=['Known intervention and initial state; no assimilation, covariance recursion, source search or false-alarm evaluation.','Same F01 plant generates truth and derivative models.','One selected development episode plus deterministic new schedules/assets, not random independent parents.','Predictor timings include encountered JIT and exclude initialization/report formation; not a bank or real-time benchmark.','Frequency/ROCOF prediction uses ordinary causal polynomial; truth uses frozen robust estimator.','Raw report errors do not imply calibration of Bayesian evidence.'])
    (P/'SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
    pd.DataFrame(rows).to_csv(P/'report_errors.csv',index=False);pd.DataFrame(traces).to_csv(P/'error_traces.csv',index=False)
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
