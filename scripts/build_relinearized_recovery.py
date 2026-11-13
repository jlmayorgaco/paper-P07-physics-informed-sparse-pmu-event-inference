"""Publish only sealed open-loop results; no simulation or C03 access."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];P=ROOT/'experiments/relinearized_recovery_20261113'
def main():
    for n,h in json.loads((P/'RESULTS_SEAL.json').read_text())['files'].items():
        assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h,n
    data=json.loads((P/'SUMMARY.json').read_text());assert data['passed']
    rows={c['case']:c for c in data['cases']};ref=rows['line_ref']['arms']
    val=lambda case,arm:rows[case]['arms'][arm]['recovery_phase_rmse_deg']
    macros={'RefineOld':f"{val('line_ref','fixed_polar'):.3f}",
            'RefineNew':f"{val('line_ref','relinearized_3'):.3f}",
            'RefineFine':f"{val('line_ref','relinearized_1'):.4f}",
            'RefineGain':f"{100*(1-val('line_ref','relinearized_3')/val('line_ref','fixed_polar')):.1f}"}
    (ROOT/'generated/relinearized_recovery_macros.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in macros.items())+'\n')
    names={'line_ref':'23--24, 1 s','line_short':'23--24, 0.5 s','line_long':'23--24, 1.5 s','line_other':'26--28, 1 s','load_up':r'Bus 7, $+10\%$','load_down':r'Bus 7, $-10\%$'}
    lines=[r'\begin{table}[t]\centering\small',r'\caption{Recovery voltage-phase RMSE (degrees). All methods receive the same known event and initial state. The 30-Hz refresh is a convergence check, not a replacement selected after evaluation.}',r'\label{tab:relinearized-recovery}',r'\setlength{\tabcolsep}{3.1pt}',r'\begin{tabular}{lrrrr}',r'\toprule',r'&Fixed&Nonlinear&\multicolumn{2}{c}{Relinearize}\\',r'Event&polar&output only&10 Hz&30 Hz\\',r'\midrule']
    for c,label in names.items():
        def fmt(v):
            if v<.001:
                mantissa,exponent=f'{v:.1e}'.split('e')
                return mantissa+r'\times10^{'+str(int(exponent))+'}'
            return f'{v:.4f}' if v<.1 else f'{v:.3f}'
        lines.append(label+'&'+'&'.join('$'+fmt(val(c,a))+'$' for a in ['fixed_polar','fixed_nonlinear_observation','relinearized_3','relinearized_1'])+r'\\')
    lines += [r'\bottomrule\end{tabular}',r'\end{table}']
    (ROOT/'tables/generated/relinearized_recovery.tex').write_text('\n'.join(lines)+'\n')
    df=pd.read_csv(P/'error_traces.csv')
    plt.rcParams.update({'font.family':'serif','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,2,figsize=(7.1,2.8),layout='constrained',gridspec_kw={'width_ratios':[1.15,1]})
    styles=[('fixed_polar','Fixed polar','#174D67','-'),('fixed_nonlinear_observation','Nonlinear output only','#86949A',':'),('relinearized_3','Relinearize at 10 Hz','#087F78','--'),('relinearized_1','30 Hz convergence check','#C46B2C','-.')]
    for arm,label,color,ls in styles:
        d=df[(df.case=='line_ref')&(df.arm==arm)&(df.time_s>=2)]
        axs[0].plot(d.time_s,np.maximum(d.phase_rmse_deg,1e-10),label=label,color=color,ls=ls,lw=1.25)
    axs[0].set_yscale('log');axs[0].set_ylim(1e-4,10);axs[0].set_xlim(2,12)
    axs[0].axvspan(2,3,color='#E3EBEF',zorder=-2);axs[0].axvline(3,color='#687781',lw=.6,ls=':')
    axs[0].set_xlabel('Time (s); line restored at 3 s');axs[0].set_ylabel('Phase RMSE across 8 PMUs (deg)')
    axs[0].set_title('(a) Line 23-24: error over time',loc='left',fontsize=8)
    cs=list(names)[:4]
    for i,c in enumerate(cs):
        old,new=val(c,'fixed_polar'),val(c,'relinearized_3')
        axs[1].plot([new,old],[i,i],color='#C7D3D9',lw=2,zorder=-1)
        axs[1].plot(old,i,'o',color='#174D67',ms=4);axs[1].plot(new,i,'s',color='#087F78',ms=4)
        axs[1].annotate(f'{new:.3f}',(new,i),xytext=(0,7),textcoords='offset points',ha='center',fontsize=7,color='#087F78')
    axs[1].set_yticks(range(4),[names[c].replace('--','-') for c in cs]);axs[1].invert_yaxis();axs[1].set_ylim(3.5,-.6)
    axs[1].set_xscale('log');axs[1].set_xlim(.09,5);axs[1].set_xlabel('Recovery phase RMSE (deg)')
    axs[1].set_title('(b) Fixed versus 10-Hz refresh',loc='left',fontsize=8)
    for ax in axs:ax.grid(axis='y',alpha=.18);ax.tick_params(labelsize=7)
    handles,labels=axs[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=2,frameon=False,fontsize=7)
    path=ROOT/'figures/generated/relinearized_recovery.pdf';fig.savefig(path);fig.savefig(path.with_suffix('.png'),dpi=220);plt.close(fig)
    print(path)
if __name__=='__main__':main()
