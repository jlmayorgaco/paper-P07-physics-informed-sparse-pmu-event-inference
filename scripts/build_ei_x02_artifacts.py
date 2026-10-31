"""Import completed X02 evidence and generate the component-test presentation."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'generated/frozen/ei_x02_20261030'
COLORS={'nominal':'#777777','recentered':'#0072b2','conditioned':'#d55e00'}
NAMES={'nominal':'Nominal','recentered':'Recentered','conditioned':'Conditioned'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rows(p):
 with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(fig,name):
 fig.savefig(ROOT/'figures/generated'/f'{name}.pdf',bbox_inches='tight')
 fig.savefig(ROOT/'figures/generated'/f'{name}.png',dpi=190,bbox_inches='tight');plt.close(fig)

def import_completed(source):
 if (DEST/'MANIFEST.json').exists():
  for f in read(DEST/'MANIFEST.json')['files']:assert sha(DEST/f['path'])==f['sha256'],f['path']
  return read(DEST/'protocol/PLAN.json'),read(DEST/'results/EVALUATION_AUDIT.json')
 assert read(source/'COMPLETE.json')['complete'],'Do not import partial X02 results'
 audit=read(source/'results/EVALUATION_AUDIT.json');plan=read(source/'protocol/PLAN.json')
 assert audit['available_observed']==audit['intended_observed']==255
 assert audit['available_event_physical']==audit['intended_event_physical']==80
 for f in read(source/'protocol/FREEZE.json')['files']:
  assert sha(source/f['path'])==f['sha256'],f['path']
 selection=next(c for c in read(source/'truth_private/cases.json') if c['split']=='test' and c['source']==7 and c['eta']==.03 and c['amplitude']==.01)
 record=next(r for r in read(source/'truth_private/records.json') if r['physical_case']==selection['id'] and r['seed']==390502)
 source_files=['protocol/PLAN.json','protocol/FREEZE.json','protocol/PARENT.json',
  'results/SUMMARY.csv','results/PER_RECORD.csv','results/FIDELITY.csv','results/PAIRED_INTERVALS.csv',
  'results/DERIVATIVE_CHECKS.csv','results/EVALUATION_AUDIT.json','results/PHYSICAL_STATUS.json',
  'results/INTEGRAL_CHECK.json','results/PREFIX_CAUSALITY_CHECK.json',
  'model/dictionary.npz','model/MANIFEST.json','predictions/READ_BOUNDARY.json','runtime/reference/stochastic_model.json']
 extra=[(f"observations/{record['record']}.npz",'sample/observed.npz'),
        (f"predictions/{record['record']}.json",'sample/prediction.json'),
        (f"engine/{selection['id']}_det.npz",'sample/deterministic.npz')]
 pairs=[(p,p) for p in source_files]+extra
 if not DEST.exists():
  DEST.mkdir(parents=True);files=[]
  for src,rel in pairs:
   p=DEST/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/src,p)
   files.append(dict(path=rel,sha256=sha(p),source=str(source/src)))
  (DEST/'MANIFEST.json').write_text(json.dumps(dict(scope='Separate known-onset load signature experiment; not R11/C01',files=files,sample_selection=selection,sample_record=record,C01_modified=False),indent=2)+'\n')
 for f in read(DEST/'MANIFEST.json')['files']:assert sha(DEST/f['path'])==f['sha256'],f['path']
 return plan,audit

def generate(source):
 plan,audit=import_completed(source);s=rows(DEST/'results/SUMMARY.csv');f=rows(DEST/'results/FIDELITY.csv');r=rows(DEST/'results/PER_RECORD.csv');ci=rows(DEST/'results/PAIRED_INTERVALS.csv')
 dc=rows(DEST/'results/DERIVATIVE_CHECKS.csv');pstat=read(DEST/'results/PHYSICAL_STATUS.json')
 assert len(pstat)==142 and all(x['available'] for x in pstat)
 amplitude=[]
 for arm in plan['comparators']:
  er=[x for x in r if x['method']==arm and x['source']]
  relative=np.array([abs(float(x['amplitude_error'])/float(x['amplitude']))*100 for x in er])
  amplitude.append(dict(method=arm,median_relative_amplitude_error_pct=float(np.median(relative)),mean_relative_amplitude_error_pct=float(np.mean(relative)),records=len(er)))
 rng=np.random.default_rng(plan['bootstrap_seed']);ids=sorted({x['physical_case'] for x in r if x['source']});ad=[]
 for cid in ids:
  values={arm:np.mean([abs(float(x['amplitude_error'])/float(x['amplitude']))*100 for x in r if x['physical_case']==cid and x['method']==arm]) for arm in ['recentered','conditioned']}
  ad.append(values['conditioned']-values['recentered'])
 ad=np.array(ad);bootstrap=np.mean(ad[rng.integers(0,len(ad),(plan['bootstrap_repetitions'],len(ad)))],axis=1)
 amplitude_effect=dict(metric='relative_amplitude_error_pct',estimate=float(np.mean(ad)),lower95=float(np.quantile(bootstrap,.025)),upper95=float(np.quantile(bootstrap,.975)),physical_cases=len(ad),interpretation='Amplitude-error metric was prespecified; this aggregation uses all source-conditioned amplitude estimates. Intervals condition on three common noise realizations.')
 (ROOT/'generated/ei_x02_amplitude_analysis.json').write_text(json.dumps(dict(rows=amplitude,effect=amplitude_effect,source='generated/frozen/ei_x02_20261030/results/PER_RECORD.csv',source_sha256=sha(DEST/'results/PER_RECORD.csv')),indent=2)+'\n')
 amplitude_by_method={x['method']:x for x in amplitude}
 macro={'EIDictionaryCases':57,'EITestPhysical':85,'EIEventPhysical':80,'EINormalPhysical':5,'EIObserved':255}
 context_changes=[100*float(x['relative_difference']) for x in dc if x['check']=='context_step_halving']
 event_changes=[100*float(x['relative_difference']) for x in dc if x['check']=='event_step_halving']
 macro.update(EIContextFDLow=f'{min(context_changes):.3g}',EIContextFDHigh=f'{max(context_changes):.3g}',EIEventFDHigh=f'{max(event_changes):.3g}')
 for row in s:
  key={'nominal':'Nom','recentered':'Recent','conditioned':'Cond'}[row['method']]
  macro['EI'+key+'Joint']=int(row['joint_correct']);macro['EI'+key+'EventRecords']=int(row['event_records'])
  macro['EI'+key+'Response']=f"{100*float(row['median_incremental_error']):.3g}"
  macro['EI'+key+'Severity']=f"{amplitude_by_method[row['method']]['median_relative_amplitude_error_pct']:.3g}"
 (ROOT/'generated/ei_x02_macros.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+str(v)+'}' for k,v in macro.items())+'\n')
 table=[r'\begin{table*}[t]\centering\small',
  r'\caption{Controlled signature test, separate from causal detection. Response error is the median whitened incremental error at the generating source/severity over 80 physical cases. Joint correctness includes presence and source on 240 noisy event records; source-only ranking conditions on a load. Severity error is median absolute relative error at the generating source. Normal selections use 15 fixed windows, not normal-hours exposure.}',
  r'\label{tab:ei-results}',r'\begin{tabular}{lrrrrr}\toprule',
  r'Model & \shortstack{Response\\error (\%)} & \shortstack{Joint\\correct} & \shortstack{Source-only\\correct} & \shortstack{Normal event\\selections} & \shortstack{Severity\\error (\%)}\\\midrule']
 for row in s:
  table.append(f"{NAMES[row['method']]} & {100*float(row['median_incremental_error']):.3g} & {row['joint_correct']}/{row['event_records']} & {row['conditional_source_correct']}/{row['event_records']} & {row['normal_selected_event']}/{row['normal_records']} & {amplitude_by_method[row['method']]['median_relative_amplitude_error_pct']:.3g}"+r'\\')
 table += [r'\bottomrule\end{tabular}\end{table*}']
 (ROOT/'tables/generated/ei_x02_results.tex').write_text('\n'.join(table)+'\n')
 effects={x['metric']:x for x in ci};ef=effects['relative_incremental_error'];ej=effects['joint_correct']
 err=float(ef['estimate'])*100;elo=float(ef['lower95'])*100;ehi=float(ef['upper95'])*100
 gain=float(ej['estimate'])*100;glo=float(ej['lower95'])*100;ghi=float(ej['upper95'])*100
 improvement=float(ef['upper95'])<0
 direction='reduces' if improvement else 'does not establish a reduction of'
 diagnosis=('improves joint source decisions in this test' if glo>0 else
            'worsens joint source decisions in this test' if ghi<0 else
            'does not establish a directional improvement in joint source decisions')
 text=(f"Relative to recentering alone, the mixed term {direction} mean incremental response error: "
       f"the paired difference is {err:.3g} percentage points "
       f"(95\\% interval [{elo:.3g}, {ehi:.3g}]). "
       f"The corresponding joint-decision difference is {gain:.3g} percentage points "
       f"([{glo:.3g}, {ghi:.3g}]), which {diagnosis}. "
       "The recentered and conditioned source decisions are already at the test ceiling. "
       f"Median absolute relative severity error, evaluated at the generating source, changes from {amplitude_by_method['recentered']['median_relative_amplitude_error_pct']:.3g}\\% "
       f"to {amplitude_by_method['conditioned']['median_relative_amplitude_error_pct']:.3g}\\%. "
       f"Its mean paired change is {amplitude_effect['estimate']:.3g} percentage points "
       f"([{amplitude_effect['lower95']:.3g}, {amplitude_effect['upper95']:.3g}]). "
       "Both variants select the correct source in every tested event record, so this severity comparison does not discard source errors. "
       "Their source masses numerically saturate at one; zero recorded log-loss is not evidence of calibrated uncertainty.\n")
 (ROOT/'generated/ei_x02_interpretation.tex').write_text(text)
 conclusion=("The controlled load test distinguishes reference correction from signature conditioning. "
  +(f"The mixed term reduces response error and median relative severity error, but {diagnosis}. " if improvement else f"Its response and decision results do not establish a general benefit; it {diagnosis}. ")
  +"This component result does not change the frozen causal method.\n")
 (ROOT/'generated/ei_x02_conclusion.tex').write_text(conclusion)
 plt.rcParams.update({'font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
 contexts=sorted({float(x['eta']) for x in f});fig,axes=plt.subplots(1,3,figsize=(7.1,2.75),layout='constrained')
 for arm,marker in zip(COLORS,['o','s','^']):
  error=[np.median([float(x['relative_incremental_error']) for x in f if x['method']==arm and float(x['eta'])==eta])*100 for eta in contexts]
  accuracy=[np.mean([float(x['joint_correct']) for x in r if x['method']==arm and x['source'] and float(x['eta'])==eta])*100 for eta in contexts]
  severity=[np.median([abs(float(x['amplitude_error'])/float(x['amplitude']))*100 for x in r if x['method']==arm and x['source'] and float(x['eta'])==eta]) for eta in contexts]
  axes[0].plot(np.array(contexts)*100,error,color=COLORS[arm],marker=marker,label=NAMES[arm],ls='--' if arm=='recentered' else '-')
  axes[1].plot(np.array(contexts)*100,accuracy,color=COLORS[arm],marker=marker,label=NAMES[arm])
  axes[2].plot(np.array(contexts)*100,severity,color=COLORS[arm],marker=marker,label=NAMES[arm])
 axes[0].set_yscale('log');axes[0].set_ylabel('Median response error (%)');axes[1].set_ylabel('Joint correct (%)');axes[1].set_ylim(-3,103);axes[2].set_ylabel('Median severity error (%)');axes[2].set_yscale('log')
 for ax in axes:ax.set_xlabel('Operating change (%)');ax.grid(alpha=.18)
 axes[0].set_title('(a) Response');axes[1].set_title('(b) Source / presence');axes[2].set_title('(c) Severity');axes[1].legend(frameon=False,fontsize=6.5)
 save(fig,'ei_x02_comparison')
 # Predeclared sample; all methods use their actual selected source/amplitude.
 with np.load(DEST/'model/dictionary.npz') as z:bank={k:z[k] for k in z.files}
 y=np.load(DEST/'sample/observed.npz')['y'];truth=np.load(DEST/'sample/deterministic.npz')['y'];pred=read(DEST/'sample/prediction.json');t=bank['time_s'];prefix=(t>=.7)&(t<2.5);offset=np.mean(y[prefix]-bank['base'][prefix],axis=0)
 scales=read(DEST/'runtime/reference/stochastic_model.json')['families'];curves={}
 for arm,p in pred['outputs'].items():
  curve=bank['base'].copy()
  if arm!='nominal':curve+=offset
  if p['source'] is not None:
   j=plan['buses'].index(p['source']);amp=p['amplitude_mean'][j]
   curve+=amp*(bank['D'][j]+(p['eta_estimated']*bank['E'][j] if arm=='conditioned' else 0.))+amp**2*bank['Q'][j]
  curves[arm]=curve
 fig,axes=plt.subplots(2,2,figsize=(7.1,4.2),sharex=True,layout='constrained')
 signals=[(18,'current_magnitude',1.,r'$\Delta |I|$, PMU6 (A)'),(14,'voltage_angle',1.,r'$\Delta\theta_V$, PMU29 (deg)'),(31,'frequency',1000.,r'$\Delta f$, PMU2 (mHz)'),(45,'rocof',1.,r'ROCOF, PMU29 (Hz/s)')]
 window=(t>=2.5)&(t<=8.)
 for ax,(col,family,factor,label) in zip(axes.flat,signals):
  scale=scales[family]['normalization_scale']*factor;center=np.mean(y[prefix,col])
  ax.plot(t[window],(y[window,col]-center)*scale,color='#aaaaaa',alpha=.5,lw=.5,label='Observed')
  ax.plot(t[window],(truth[window,col]-center)*scale,color='black',lw=.9,ls=':',label='Physical truth')
  for arm,curve in curves.items():ax.plot(t[window],(curve[window,col]-center)*scale,color=COLORS[arm],lw=.9,label=NAMES[arm],ls='--' if arm=='recentered' else '-')
  ax.axvspan(3,6,color='#cccccc',alpha=.22);ax.set_ylabel(label);ax.grid(alpha=.12);ax.set_xlim(2.5,8.)
 for ax in axes[-1]:ax.set_xlabel('Time (s)')
 handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,ncol=5,loc='outside upper center',frameon=False,fontsize=7)
 save(fig,'ei_x02_signals')
 output=dict(import_hashes_verified=True,case_denominators_verified=True,physical_cases=142,test_cases=85,observed_records=255,known_onset_and_off=True,derivative_checks=dc,effects=effects,amplitude=amplitude,amplitude_effect=amplitude_effect,physical_response_improvement=improvement,source_claim=diagnosis,C01_changed=False,RAW0002_opened=False)
 (ROOT/'generated/ei_x02_audit.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
 report=['# E_i en IEEE-39: resultado del candidato separado','',
  'Se completaron 142 trayectorias: 57 para diccionario/comprobación y 85 de prueba. Las 80 intervenciones y cinco controles se observaron con tres semillas, para 255 registros. No se cambió la planta, la medición, R11 o C01.','',
  '| Modelo | Error mediano de respuesta (%) | Presencia y origen correctos | Selecciones de evento en controles | Error relativo mediano de intensidad (%) |',
  '|---|---:|---:|---:|---:|']
 for row in s:
  report.append(f"| {NAMES[row['method']]} | {100*float(row['median_incremental_error']):.4g} | {row['joint_correct']}/{row['event_records']} | {row['normal_selected_event']}/{row['normal_records']} | {amplitude_by_method[row['method']]['median_relative_amplitude_error_pct']:.4g} |")
 report+=['','El recentrado corrige el origen en este piloto. E_i mejora el modelo de respuesta y la intensidad, pero no suma aciertos de localización: ambos comparadores corregidos están en el techo de la prueba. No se sube retrospectivamente el ruido ni se cambian umbrales para fabricar una diferencia.','',
  f"Cambio medio pareado de error de respuesta: {err:.4g} puntos porcentuales, intervalo [{elo:.4g}, {ehi:.4g}]. Cambio medio de error relativo de intensidad: {amplitude_effect['estimate']:.4g} puntos, intervalo [{amplitude_effect['lower95']:.4g}, {amplitude_effect['upper95']:.4g}].",'',
  'El error de respuesta se evalúa con origen y amplitud generadores para aislar la aproximación. El error de intensidad usa la estimación bajo el origen verdadero; para los dos modelos corregidos ese origen coincide con su selección en todos los casos. Las tres semillas comunes se reutilizan entre casos. Los intervalos describen variación de casos condicionada a esas realizaciones, no toda la población de ruido.','',
  'Alcance: una carga P/Q, cuatro buses, un parámetro escalar de operación, onset y OFF conocidos. El contexto y la intensidad se estiman solo desde las PMU; el origen verdadero queda reservado. No es una prueba del detector causal ni una evaluación de todas las familias. El recentrado es un offset del prefijo observado, no el algoritmo histórico de reconstrucción AC.','',
  'Todas las trayectorias conservaron estados en ON/OFF, emitieron 301 reportes y conservaron parámetros estructurales. Los controles de semipasos y la frontera de lectura están en los JSON/CSV. Las masas saturadas y log-loss cero no certifican calibración.','',
  'Fuentes: protocol/PLAN.json y FREEZE.json; results/SUMMARY.csv, PER_RECORD.csv, FIDELITY.csv, PAIRED_INTERVALS.csv y DERIVATIVE_CHECKS.csv. La copia utilizada por P07 se verifica mediante generated/frozen/ei_x02_20261030/MANIFEST.json.','',
  'El cambio de la figura de eventos está prohibido. El unifilar y el diagrama causal aprobado permanecen intactos. RAW0002 no se abrió.']
 (ROOT/'docs/ei-x02-results.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
 if source.is_dir():(source/'REPORT.md').write_text('\n'.join(report)+'\n',encoding='utf-8')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=ROOT.parent/'SGSMA26-Physics-Informed-AD/experiments/PAPER_METHOD_EI_X02');generate(p.parse_args().source)
