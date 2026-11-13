"""Generate the kinetic-balance figure and manuscript values from saved audits."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'experiments/hamiltonian_f01_20261113';R=P/'run'
def main():
    seal=json.loads((P/'RESULTS_SEAL.json').read_text())
    for n,h in seal['files'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
    a=json.loads((R/'PHYSICS_AUDIT.json').read_text());c=json.loads((R/'COORDINATE_RESULTS.json').read_text())
    assert a['passed']
    vals={'HamWorkError':max(r['max_kinetic_work_residual_MJ'] for r in a['cases']),
          'HamTorqueError':max(r['max_torque_equation_error'] for r in a['cases']),
          'HamNetworkError':max(r['max_generation_load_loss_error_system_pu'] for r in a['cases']),
          'HamPredictionError':c['max_relative_prediction_difference'],
          'HamLoglikError':c['max_absolute_loglik_difference']}
    def tex(v):
        s=f'{v:.2e}';m,e=s.split('e');return m+r'\times10^{'+str(int(e))+'}'
    (ROOT/'generated/hamiltonian_macros.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+tex(v)+'}' for k,v in vals.items())+'\n')
    df=pd.read_csv(R/'energy_traces.csv')
    plt.rcParams.update({'font.family':'serif','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,2,figsize=(7.1,2.35),layout='constrained')
    for case,label,color,ls in [('load_up','Load +10%','#087F78','-'),('load_down','Load -10%','#C46B2C','--'),('line','Line 23–24 opens','#2276A0','-.')]:
        d=df[df.case==case]
        axs[0].plot(d.time_s,d.deviation_energy_MJ,label=label,color=color,ls=ls,lw=1.3)
        axs[1].plot(d.time_s,d.branch_loss_MW,label=label,color=color,ls=ls,lw=1.3)
    for ax in axs:
        ax.grid(axis='y',alpha=.18);ax.set_xlabel('Time (s)');ax.set_xlim(0,12)
        for t in [2,3,6]:ax.axvline(t,color='#687781',lw=.55,ls=':',zorder=0)
    axs[0].set_ylabel('Rotor deviation energy (MJ)');axs[1].set_ylabel('Network active loss (MW)')
    axs[0].set_title('(a) Rotor states remain continuous',loc='left',fontsize=8)
    axs[1].set_title('(b) Electrical ports change at switching',loc='left',fontsize=8)
    axs[1].legend(frameon=False,fontsize=7,loc='best')
    dest=ROOT/'figures/generated/hamiltonian_balance.pdf';fig.savefig(dest);fig.savefig(dest.with_suffix('.png'),dpi=220);plt.close(fig)
    print(dest)
if __name__=='__main__':main()
