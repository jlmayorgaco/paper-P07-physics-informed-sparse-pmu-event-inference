"""Render the sealed descriptor validation, without rerunning the plant."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'experiments/descriptor_bridge_20261113';R=P/'run_v2'

def main():
    for name,sha in json.loads((P/'RESULTS_SEAL.json').read_text())['files'].items():
        assert hashlib.sha256((P/name).read_bytes()).hexdigest()==sha,name
    result=json.loads((R/'SUMMARY.json').read_text())
    errors=pd.read_csv(R/'report_errors.csv')
    labels={'load_up_small':r'Load $+1\%$','load_down_small':r'Load $-1\%$',
            'load_up':r'Load $+10\%$','load_down':r'Load $-10\%$','line':'Line 23--24'}
    rows={r['case']:r for r in result['cases']}
    table=[r'\begin{table}[t]',r'\centering\small',
           r'\caption{Open-loop errors at eight PMUs. Relative complex-voltage RMSE is normalized by the nonlinear event-response RMS; magnitude and phase errors use the first-order polar observation during recovery.}',
           r'\label{tab:descriptor-bridge}',r'\begin{tabular}{lrrrr}',r'\toprule',
           r'&\multicolumn{2}{c}{Complex error (\%)}&\multicolumn{2}{c}{Polar RMSE after OFF}\\',
           r'Event&ON&Recovery&$|V|$ (pu)&$\theta$ (deg)\\',r'\midrule']
    for name,label in labels.items():
        win=rows[name]['windows']
        e=errors[(errors.case==name)&(errors.window=='recovery')&(errors.reporting=='first_order_ordinary_reporting')].set_index('family')
        mag=float(e.loc['voltage_magnitude_pu','rmse']);mant,exp=f'{mag:.2e}'.split('e')
        magtex='$'+mant+r'\!\times\!10^{'+str(int(exp))+'}$'
        table.append(f"{label}&{100*win['active']['relative_rmse']:.2f}&{100*win['recovery']['relative_rmse']:.2f}&{magtex}&{e.loc['voltage_phase_deg','rmse']:.4f}"+r'\\')
    table += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    (ROOT/'tables/generated/descriptor_bridge.tex').write_text('\n'.join(table)+'\n')
    checks=json.loads((R/'DERIVATIVE_CHECKS.json').read_text())
    maxder=max(v for r in checks for k,v in r.items() if 'direction_error' in k)
    def texnum(x):
        m,e=f'{x:.2e}'.split('e');return m+r'\times10^{'+str(int(e))+'}'
    (ROOT/'generated/descriptor_bridge_macros.tex').write_text(
        '\\newcommand{\\BridgeDerivativeError}{'+texnum(maxder)+'}\n'+
        '\\newcommand{\\BridgeTerminalError}{'+texnum(max(r['terminal_stamp_error_pu'] for r in result['cases']))+'}\n')
    pmus=np.array([2,5,6,10,19,22,29,39])-1
    def vbar(mode):
        a=pd.read_csv(R/'operators'/mode/'voltage.csv').to_numpy().reshape(-1,2)
        return a[:,0]+1j*a[:,1]
    normal=np.load(R/'normal_prediction.npz')['voltage_true_pu'][:,pmus]
    plt.rcParams.update({'font.family':'serif','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axs=plt.subplots(2,2,figsize=(7.1,3.65),sharex=True,layout='constrained')
    for col,(name,title,off) in enumerate([('load_up','Bus 7: +10% P/Q setpoints',6),('line','Line 23-24: open / reclose',3)]):
        a=np.load(R/(name+'_prediction.npz'));t=a['time_s']
        truth=a['voltage_true_pu'][:,pmus];pred=a['voltage_linear_pu'][:,pmus]
        base=np.tile(vbar('normal')[pmus],(len(t),1))
        if name=='line':base[(t>=2)&(t<off)]=vbar('line')[pmus]
        dv=pred-base
        localmag=abs(base)+np.real(dv*np.conj(base)/abs(base))
        localphase=np.angle(base)+np.imag(dv/base)
        phase=lambda x:np.rad2deg(np.angle(x/normal))
        localphase=np.rad2deg(np.angle(np.exp(1j*(localphase-np.angle(normal)))))
        rms=lambda x:np.sqrt(np.mean(x*x,axis=1))
        data=[(rms(phase(truth)),rms(localphase),rms(phase(pred))),
              (1e3*rms(abs(truth)-abs(normal)),1e3*rms(localmag-abs(normal)),1e3*rms(abs(pred)-abs(normal)))]
        for row,ys in enumerate(data):
            ax=axs[row,col]
            for y,label,color,ls in zip(ys,['Nonlinear plant','First-order polar','Complex map, then polar'],['#174D67','#C46B2C','#86949A'],['-','--',':']):
                ax.plot(t,y,label=label,color=color,ls=ls,lw=1.3)
            ax.axvspan(2,off,color='#E3EBEF',alpha=.65,zorder=-2)
            for tick in [2,off]:ax.axvline(tick,color='#82929A',ls=':',lw=.6,zorder=-1)
            ax.set_xlim(0,12);ax.grid(axis='y',alpha=.16)
            ax.tick_params(labelsize=7);ax.set_xticks([0,2,4,6,8,10,12])
        axs[0,col].set_title(title,fontsize=8,loc='left')
        axs[1,col].set_xlabel('Time (s)')
    axs[0,0].set_ylabel('Phase response\nRMS (deg)')
    axs[1,0].set_ylabel('Magnitude response\n'+r'RMS ($10^{-3}$ pu)')
    handles,labels_=axs[0,0].get_legend_handles_labels()
    fig.legend(handles,labels_,loc='outside lower center',ncol=3,frameon=False,fontsize=7)
    dest=ROOT/'figures/generated/descriptor_bridge.pdf'
    fig.savefig(dest);fig.savefig(dest.with_suffix('.png'),dpi=220);plt.close(fig)
    print(dest)

if __name__=='__main__':main()
