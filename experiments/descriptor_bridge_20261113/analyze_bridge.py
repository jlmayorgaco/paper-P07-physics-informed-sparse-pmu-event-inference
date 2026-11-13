"""Open-loop F01 descriptor audit. No state assimilation or detector scoring."""
from pathlib import Path
import hashlib, importlib.util, json
import numpy as np
import pandas as pd
from scipy.linalg import expm

P=Path(__file__).resolve().parent
R=P/'run_v2'
REF=P.parent/'hamiltonian_f01_20261113/reproduction/reference'

def read(mode,name):
    return pd.read_csv(R/'operators'/mode/(name+'.csv')).to_numpy()

def main():
    for freeze in ['EXECUTION_FREEZE.json','EXECUTION_V2_FREEZE.json','ANALYSIS_FREEZE.json']:
        for name,sha in json.loads((P/freeze).read_text())['files'].items():
            assert hashlib.sha256((P/name).read_bytes()).hexdigest()==sha,name
    cfg=json.loads((P/'protocol.json').read_text())
    mapping=pd.read_csv(REF/'terminal_mapping.csv')
    reporting=json.loads((REF/'reporting_config.json').read_text())
    buskv=pd.read_csv(REF/'data/bus.csv').base_kv.to_numpy()
    spec=importlib.util.spec_from_file_location('frozen_pmu',REF/'pmu_operator.py')
    pmu=importlib.util.module_from_spec(spec);spec.loader.exec_module(pmu)
    with np.load(REF/'fixed_network.npz') as data:
        Yf,Yt=data['Yf'],data['Yt']
    idx=pd.read_csv(R/'operators/state_index.csv')
    dyn=np.flatnonzero(idx.mass.to_numpy()!=0);alg=np.flatnonzero(idx.mass.to_numpy()==0)
    mass=pd.read_csv(R/'operators/M.csv').to_numpy()[np.ix_(dyn,dyn)]
    modes={};operator_checks={}
    for mode in ['normal','line']:
        m={name:read(mode,name) for name in ['J','Ju','H','Hu','A','B','C','D','force','voltage','state']}
        J,Ju,H,Hu=[m[k] for k in ['J','Ju','H','Hu']]
        Zx=-np.linalg.solve(J[np.ix_(alg,alg)],J[np.ix_(alg,dyn)])
        Zu=-np.linalg.solve(J[np.ix_(alg,alg)],Ju[alg])
        checks=[np.linalg.solve(mass,J[np.ix_(dyn,dyn)]+J[np.ix_(dyn,alg)]@Zx),
                np.linalg.solve(mass,Ju[dyn]+J[np.ix_(dyn,alg)]@Zu),
                H[:,dyn]+H[:,alg]@Zx,Hu+H[:,alg]@Zu]
        operator_checks[mode]={k:float(np.max(abs(v-m[k]))) for k,v in zip(['A','B','C','D'],checks)}
        assert max(operator_checks[mode].values())<1e-8
        nx=len(dyn);aug=np.zeros((nx+2,nx+2));aug[:nx,:nx]=m['A']
        aug[:nx,nx:nx+1]=m['B'];aug[:nx,nx+1:]=m['force']
        m['step']=expm(aug/30)
        m['Vbar']=m['voltage'].reshape(-1,2)[:,0]+1j*m['voltage'].reshape(-1,2)[:,1]
        modes[mode]=m
    pmuix=np.array(reporting['pmus'])-1
    n=361;t=np.arange(n)/30
    def current(V,case):
        outward=[]
        for row in mapping.itertuples():
            Y=Yf if row.side=='src' else Yt
            cur=V@Y[int(row.julia_edge_1based)-1]
            if case['kind']=='line' and row.julia_edge_1based==case['edge']:
                cur[(t>=case['on'])&(t<case['off'])]=0
            outward.append(cur)
        return -np.column_stack(outward)  # API takes currents into bus
    def families(report):
        return {'voltage_magnitude_pu':abs(report['voltage_pu']),
                'voltage_phase_deg':np.angle(report['voltage_pu'],deg=True),
                'current_magnitude_A':abs(report['current_A']),
                'current_phase_deg':np.angle(report['current_A'][:,:7],deg=True),
                'frequency_hz':report['frequency_hz'],'rocof_hz_s':report['rocof_hz_s']}
    def diff(a,b,key):
        d=a-b
        return (d+180)%360-180 if 'phase' in key else d
    results=[];metrics=[];traces=[];normal=None;normalreport=None
    for case in cfg['cases']:
        ident=case['id'];net=pd.read_csv(R/(ident+'_network.csv')).iloc[::4]
        assert np.allclose(net.time_s.to_numpy(),t,rtol=0,atol=1e-12)
        assert len(net)==n and t[0]==0 and t[-1]==12
        truth=net[[f'V{k}_r' for k in range(1,40)]].to_numpy()+1j*net[[f'V{k}_i' for k in range(1,40)]].to_numpy()
        trueI=np.column_stack([net[f'E{row.julia_edge_1based}_{row.side}_r'].to_numpy()+1j*net[f'E{row.julia_edge_1based}_{row.side}_i'].to_numpy() for row in mapping.itertuples()])
        stamp_error=float(np.max(abs(current(truth,case)-trueI)))
        assert stamp_error<1e-8
        pred=np.empty_like(truth);base=np.empty_like(truth);x=np.zeros(len(dyn))
        for k,tk in enumerate(t):
            active=case['on']<=tk<case['off']
            mode='line' if case['kind']=='line' and active else 'normal'
            m=modes[mode];amp=case.get('factor',1)-1 if active and case['kind']=='load' else 0.
            dv=(m['C']@x+m['D'][:,0]*amp).reshape(-1,2)
            base[k]=m['Vbar'];pred[k]=base[k]+dv[:,0]+1j*dv[:,1]
            # Post-switch output at tk, then propagate that mode to tk+dt.
            x=(m['step']@np.r_[x,amp,1])[:len(dyn)]
        predI=current(pred,case)
        truthreport=families(pmu.report(t,truth,trueI,mapping,buskv,reporting))
        commonreport=families(pmu.report(t,pred,predI,mapping,buskv,reporting))
        # Separate first-order polar observation + ordinary 21-report fit.
        # This deliberately exposes the robust reporting / linear predictor mismatch.
        dv=pred-base;v0=base[:,pmuix];dv=dv[:,pmuix]
        reference=reporting['common_phase_intercept_deg']+reporting['common_phase_slope_deg_s']*t
        shifts=reference[:,None]+np.array(reporting['relative_voltage_bias_deg'])
        linearreport={
            'voltage_magnitude_pu':abs(v0)+np.real(dv*np.conj(v0)/abs(v0)),
            'voltage_phase_deg':np.angle(v0,deg=True)+np.rad2deg(np.imag(dv/v0))+shifts}
        baseI=current(base,case);di=predI-baseI
        scale=np.array([100e6/(np.sqrt(3)*buskv[int(row.terminal)-1]*1000)*row.gain for row in mapping.itertuples()])
        polarity=np.array(mapping.polarity);ibias=np.array(mapping.bias_deg)
        assert np.min(abs(baseI))>1e-8
        linearreport['current_magnitude_A']=(abs(baseI)+np.real(di*np.conj(baseI)/abs(baseI)))*scale
        linearreport['current_phase_deg']=(np.angle(-baseI*polarity,deg=True)+np.rad2deg(np.imag(di/baseI))+shifts+ibias)[:,:7]
        angles=np.rad2deg(np.unwrap(np.deg2rad(linearreport['voltage_phase_deg']),axis=0))
        times=np.arange(-20,1)/30;weights=np.linalg.pinv(np.column_stack([np.ones(21),times,times**2]))
        freq=np.full((n,8),np.nan);roc=freq.copy()
        for k in range(20,n):
            coef=weights@angles[k-20:k+1];freq[k]=60+coef[1]/360;roc[k]=2*coef[2]/360
        linearreport['frequency_hz']=freq;linearreport['rocof_hz_s']=roc
        if ident=='normal':normal=truth.copy();normalreport=truthreport
        row={'case':ident,'terminal_stamp_error_pu':stamp_error,'windows':{}}
        for window,take in {'active':(t>=case['on'])&(t<case['off']),'recovery':t>=case['off']}.items():
            err=pred[take][:,pmuix]-truth[take][:,pmuix]
            signal=truth[take][:,pmuix]-normal[take][:,pmuix]
            rms=float(np.sqrt(np.mean(abs(err)**2)));srms=float(np.sqrt(np.mean(abs(signal)**2)))
            row['windows'][window]={'complex_voltage_rmse_pu':rms,'event_response_rms_pu':srms,'relative_rmse':rms/srms if srms>1e-12 else None,'max_complex_voltage_error_pu':float(np.max(abs(err)))}
            for method,rep in [('common_robust_reporting',commonreport),('first_order_ordinary_reporting',linearreport)]:
                for key in truthreport:
                    e=diff(rep[key][take],truthreport[key][take],key)
                    response=diff(truthreport[key][take],normalreport[key][take],key)
                    metrics.append(dict(case=ident,window=window,reporting=method,family=key,channels=e.shape[1],samples=e.shape[0],rmse=float(np.sqrt(np.mean(e**2))),max_error=float(np.max(abs(e))),response_rms=float(np.sqrt(np.mean(response**2)))))
        results.append(row)
        for k,tk in enumerate(t):
            traces.append(dict(case=ident,time_s=tk,nonlinear_response=float(np.sqrt(np.mean(abs(truth[k,pmuix]-normal[k,pmuix])**2))),linear_response=float(np.sqrt(np.mean(abs(pred[k,pmuix]-normal[k,pmuix])**2))),error=float(np.sqrt(np.mean(abs(pred[k,pmuix]-truth[k,pmuix])**2)))))
        np.savez_compressed(R/(ident+'_prediction.npz'),time_s=t,voltage_linear_pu=pred,voltage_true_pu=truth,native_current_linear_pu=predI,native_current_true_pu=trueI)
    out={'scope':'Six deterministic development trajectories; known event schedule, initial state and load magnitude; no Kalman updates, noise, uncertainty or detection score.',
         'operator_reconstruction_max_abs':operator_checks,'cases':results,
         'reporting_contract':'47 raw coordinates, no BUS39 current phase. Common robust reporting isolates plant linearization; first-order polar/ordinary polynomial reporting adds observation approximation. Neither is a full 376-state bank run.',
         'limitations':['One operating point, one load bus, one line; no independent replicates.','BUS5 historical 5-6 terminal hypothesis unchanged.','Topology and event timing known; no source attribution or false-alarm conclusion.','No Hamiltonian prior or data-driven parameter adaptation tested.','Legacy energy/coordinate gate fields in protocol.json are inherited and not part of this descriptor experiment.']}
    (R/'SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
    pd.DataFrame(metrics).to_csv(R/'report_errors.csv',index=False)
    pd.DataFrame(traces).to_csv(R/'voltage_traces.csv',index=False)
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
