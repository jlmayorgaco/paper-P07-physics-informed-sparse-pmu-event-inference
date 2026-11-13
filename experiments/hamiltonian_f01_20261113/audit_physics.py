"""Independent rotor work and terminal-power audit of new nonlinear F01 runs."""
from pathlib import Path
import json,re,hashlib
import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
P=Path(__file__).resolve().parent;R=P/'run'
def main():
    for name in ['PHYSICS_FREEZE.json','PHYSICS_V2_FREEZE.json','PHYSICS_V3_FREEZE.json']:
        for n,h in json.loads((P/name).read_text())['files'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
    cfg=json.loads((P/'protocol.json').read_text());g=json.loads((R/'MACHINE_PARAMETERS.json').read_text())
    H,Sn,D,Rs=[np.array(g[k]) for k in ['H','Sn','D','Rs']]
    branches=pd.read_csv(P/'branch.csv');src=branches.src_bus.to_numpy(int)-1;dst=branches.dst_bus.to_numpy(int)-1
    with np.load(P/'fixed_network.npz') as z:Yf=z['Yf'];Yt=z['Yt'];Ybus=z['Ybus']
    pars=pd.read_csv(P/'initial_parameters.csv').set_index('symbol').value
    loads=[]
    for name,value in pars.items():
        if 'ZIPLoad₊Pset)' in name:
            bus=int(re.search(r'VIndex\((\d+)',name)[1]);vset=pars[f'VIndex({bus}, :ZIPLoad₊Vset)']
            assert pars[f'VIndex({bus}, :ZIPLoad₊KpZ)']==1
            loads.append((bus,value,vset))
    allrows=[];trace=[]
    for case in cfg['cases']:
        ident=case['id'];df=pd.read_csv(R/(ident+'_machine.csv'));net=pd.read_csv(R/(ident+'_network.csv'));t=df.time_s.to_numpy()
        a=lambda name:df[[f'G{k}_{name}' for k in g['buses']]].to_numpy()
        w,tm,te,p,id_,iq,dw=[a(k) for k in ['omega','tm','te','P','Id','Iq','domega']]
        torque=tm-te-D*(w-1)
        K=(H*Sn*w*w).sum(axis=1);Kd=(H*Sn*(w-1)**2).sum(axis=1)
        power=(Sn*w*torque).sum(axis=1);devpower=(Sn*(w-1)*torque).sum(axis=1)
        maxint=maxdevint=0.
        # Smooth segments only: never trapezoid across a torque discontinuity.
        segments=[(t<case['on']),(t>=case['on'])&(t<case['off']),(t>=case['off'])]
        for take in segments:
            ix=np.flatnonzero(take);tt=t[ix]
            maxint=max(maxint,float(np.max(abs(K[ix]-K[ix[0]]-cumulative_trapezoid(power[ix],tt,initial=0)))))
            maxdevint=max(maxdevint,float(np.max(abs(Kd[ix]-Kd[ix[0]]-cumulative_trapezoid(devpower[ix],tt,initial=0)))))
        V=net[[f'V{k}_r' for k in range(1,40)]].to_numpy()+1j*net[[f'V{k}_i' for k in range(1,40)]].to_numpy()
        I=[]
        for side in ['src','dst']:
            I.append(-(net[[f'E{k}_{side}_r' for k in range(1,47)]].to_numpy()+1j*net[[f'E{k}_{side}_i' for k in range(1,47)]].to_numpy()))
        If,It=I;If_model=V@Yf.T;It_model=V@Yt.T;Inodal=V@Ybus.T
        if case['kind']=='line':
            e=case['edge']-1;active=(t>=case['on'])&(t<case['off'])
            Inodal[active,src[e]]-=If_model[active,e];Inodal[active,dst[e]]-=It_model[active,e]
            If_model[active,e]=0;It_model[active,e]=0
        branch_power=np.real(V[:,src]*If.conj()+V[:,dst]*It.conj()).sum(axis=1)
        nodal_power=np.real(V*Inodal.conj()).sum(axis=1)
        p_load=np.zeros(len(t))
        for bus,ps,vs in loads:
            factor=np.ones(len(t))
            if case['kind']=='load' and bus==case['bus']:factor[(t>=case['on'])&(t<case['off'])]=case['factor']
            p_load+=factor*ps*(abs(V[:,bus-1])/vs)**2
        injection=(Sn*p).sum(axis=1)/100+p_load
        row={'case':ident,'samples':len(t),'max_torque_equation_error':float(np.max(abs(2*H*dw-torque))),
             'max_airgap_power_error_machine_pu':float(np.max(abs(w*te-p-Rs*(id_**2+iq**2)))),
             'max_kinetic_work_residual_MJ':maxint,'max_deviation_work_residual_MJ':maxdevint,
             'max_terminal_current_error_pu':float(max(np.max(abs(If-If_model)),np.max(abs(It-It_model)))),
             'max_graph_power_error_system_pu':float(np.max(abs(branch_power-nodal_power))),
             'max_generation_load_loss_error_system_pu':float(np.max(abs(injection-branch_power))),
             'minimum_branch_loss_system_pu':float(branch_power.min())}
        allrows.append(row)
        for i in range(0,len(t),4):trace.append({'case':ident,'time_s':t[i],'kinetic_change_MJ':K[i]-K[0],'deviation_energy_MJ':Kd[i],'net_mechanical_power_MW':power[i],'branch_loss_MW':100*branch_power[i]})
    status=json.loads((R/'PHYSICS_STATUS.json').read_text())
    result={'scope':'Full frozen F01 nonlinear DAE; kinetic subsystem balance and electrical terminal powers only',
            'cases':allrows,'all_solvers_successful':all(s['retcode']=='Success' for s in status),
            'max_algebraic_residual':max(s['algebraic_residual'] for s in status),'max_dynamic_jump':max(s['dynamic_jump'] for s in status),
            'quadrature':'120 Hz composite trapezoid separately on smooth segments; intervals ending at jumps excluded',
            'direct_shaft_damping_all_zero':bool(np.all(D==0))}
    result['passed']=bool(result['all_solvers_successful'] and result['max_algebraic_residual']<1e-6 and result['max_dynamic_jump']<1e-8 and all(r['max_torque_equation_error']<1e-8 and r['max_airgap_power_error_machine_pu']<1e-8 and r['max_kinetic_work_residual_MJ']<.02 and r['max_terminal_current_error_pu']<1e-6 and r['max_graph_power_error_system_pu']<1e-6 and r['max_generation_load_loss_error_system_pu']<1e-6 for r in allrows))
    (R/'PHYSICS_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    pd.DataFrame(trace).to_csv(R/'energy_traces.csv',index=False)
    print(json.dumps(result,indent=2));assert result['passed']
if __name__=='__main__':main()
