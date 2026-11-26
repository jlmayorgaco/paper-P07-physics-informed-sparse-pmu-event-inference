"""Fixed-design plots and portable evidence bundle for the F01 oracle control."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
PAPER=HERE.parents[2]/'paper-P07-physics-informed-sparse-pmu-event-inference'
def main():
    d=pd.read_csv(HERE/'results/PER_CASE.csv');s=json.loads((HERE/'results/SUMMARY.json').read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(7.15,2.75),layout='constrained',sharey=True)
    for ax,col,title in zip(axes,['ratio_known','ratio_uncertain'],['(a) Previous trajectory treated as known','(b) Uncertain previous severity']):
        tab=d.pivot(index=['prior_bus','source_a','source_b'],columns='delay_s',values=col)
        im=ax.imshow(tab.values,aspect='auto',vmin=.65,vmax=1.05,cmap='cividis')
        ax.set_xticks(range(len(tab.columns)),[f'{v:g}' for v in tab.columns]);ax.set_yticks(range(len(tab.index)),[f'Prior {p}: {a} vs {b}' for p,a,b in tab.index])
        ax.set(xlabel='Delay after restoration (s)',title=title)
        for (i,j),value in np.ndenumerate(tab.values):ax.text(j,i,f'{value:.3f}',ha='center',va='center',color='white' if value<.83 else 'black',fontsize=8)
    fig.colorbar(im,ax=axes,label='Profiled squared distance / equilibrium',shrink=.85)
    for ext in ['pdf','png']:fig.savefig(HERE/'figures'/f'recovery_information.{ext}',dpi=220)
    plt.close(fig)
    trace=pd.read_csv(HERE/'results/FIXED_BUS5_TRACE.csv');mask=(trace.time_s>=3.5)&(trace.time_s<=5.);tau=trace.time_s[mask]-3.5
    fig,axs=plt.subplots(3,1,figsize=(7.1,5.2),sharex=True,layout='constrained')
    for ax,field,label in zip(axs,['voltage_magnitude','current_magnitude','frequency'],['BUS5 voltage increment (V)','BUS5 terminal current increment (A)','BUS5 frequency increment (Hz)']):
        for source,style,color in [(18,'-','#0072B2'),(27,'--','#D55E00')]:
            ax.plot(tau,trace.loc[mask,f'{field}_{source}']-trace.loc[mask,f'{field}_None'],style,color=color,label=f'New load at BUS{source}')
        ax.set_ylabel(label);ax.grid(alpha=.2)
    axs[0].legend(ncol=2,frameon=False);axs[0].set_title('Same prior BUS7 history; incremental response after 0.5 s recovery')
    axs[-1].set_xlabel('Time since known secondary onset (s)')
    for ext in ['pdf','png']:fig.savefig(HERE/'figures'/f'recovery_increment.{ext}',dpi=220)
    plt.close(fig)
    dst=PAPER/'generated/frozen/recovery_x04_20261031';dst.mkdir(parents=True,exist_ok=True)
    names=['results/PER_CASE.csv','results/SUMMARY.json','results/CONTINUITY.csv','results/PREFIX_EQUALITY.csv','results/FIXED_BUS5_TRACE.csv',
           'protocol/PLAN.json','protocol/DESIGN.json','protocol/FREEZE.json','protocol/EVALUATION_FREEZE.json','protocol/PROTECTED_BEFORE.json','prepare.py','evaluate.py','measurement_bridge.py','build_artifacts.py']
    rows=[]
    for name in names:
        f=HERE/name;p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,p)
        rows.append(dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (dst/'MANIFEST.json').write_text(json.dumps(dict(scope=s['scope'],files=rows),indent=2))
    for ext in ['pdf','png']:shutil.copy2(HERE/'figures'/f'recovery_information.{ext}',PAPER/'figures/generated'/f'recovery_x04_information.{ext}')
    report=f'''# X04: comprobación física de recuperación en F01

Se ejecutaron {s['physical_trajectories']} trayectorias de 8 s: una integración por
trayectoria, 241 reportes a 30 fps, cero reinicios. Todos los estados y parámetros
estructurales F01 se preservaron. Los prefijos contrafactuales coinciden
exactamente; {s['protected_files_unchanged']} archivos protegidos conservan hash.

Diseño: cargas previas BUS7/BUS24 de +8%, ON 2 s/OFF 3 s; nueva carga de
+0.06% tras 0.5 o 2 s. Pares 18/27,16/21,3/21; horizonte 1.5 s.
Cinco fuentes, cuatro historias de recuperación, 12 celdas comparativas.
Las 38 integraciones incluyen controles y diferencias para incertidumbre.
No son 38 ensayos independientes de clasificación.

## Resultados

- Razón mediana de separación con trayectoria conocida: {s['median_ratio_known']:.6f}.
- Con una dirección incierta de severidad previa: {s['median_ratio_uncertain']:.6f}.
- Celdas de separación incierta mayor que equilibrio: {s['ratio_uncertain_above_one']}/12.
- Exactitud binaria media de firmas de equilibrio: {100*s['mean_frozen']:.4f}%.
- Exactitud binaria media de firmas condicionadas: {100*s['mean_conditioned']:.4f}%.
- Diferencia media: {s['mean_gain_pp']:.6f} puntos; {s['negative_gain_cases']} celdas empeoran.

No se observa ventaja media de clasificación. No interpretar los muchos draws
de ruido como padres independientes ni convertir este empate en prueba de
equivalencia universal. El control de incertidumbre aumenta la covarianza:
su penalización de separación a firma fija es esperable algebraicamente.
La comparación conocida muestra por separado cómo cambia la geometría física.

## Lo que no se ejecutó

No es R11 ni M3H: familia, onset, dos candidatos y recuperación sin nuevo
evento son conocidos. Se emplean secantes de amplitud finita, no operadores
tangentes analíticos. Los 47 canales son los del operador F01, sin ángulo de
corriente BUS39. El ruido es gaussiano en innovaciones del filtro congelado,
no una nueva identificación del ruido ni una realización completa del modelo
truncado. La severidad previa entra mediante una aproximación lineal de rango
uno; no se estima todo el estado causal ni se muestrean historias no lineales.

La distancia perfila amplitudes no negativas; la evidencia integra una amplitud
gaussiana firmada. Son dos diagnósticos diferentes, no una cota de error común.
No se comparan porcentajes con el prototipo X03, cuyos sensores/planta difieren.

## Decisión editorial

Incluir el control como límite de una hipótesis física, sin cambiar R11/C01
ni afirmar un nuevo algoritmo. La recuperación cambia la referencia y puede
cambiar la firma, pero no se ha probado que aumente información o aciertos.
Adjuntos, soportes simultáneos, calibración y refinamiento certificado siguen
siendo propuestas, no resultados del artículo.
'''
    (HERE/'REPORT.md').write_text(report,encoding='utf8');(PAPER/'docs/recovery-x04-results.md').write_text(report,encoding='utf8')
    print('PLOTS_AND_REPORT',dst)
if __name__=='__main__':main()
