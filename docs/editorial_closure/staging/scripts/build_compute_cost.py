"""Descriptive aggregation of already recorded C01 stage timings; no benchmarking."""
from pathlib import Path
import csv, json, statistics, hashlib
import pandas as pd
PAPER=Path(__file__).resolve().parents[4]
SCIENCE=PAPER.parent/'SGSMA26-Physics-Informed-AD'
RUN=SCIENCE/'experiments/PAPER_CONFIRMATORY_C01/run'
TIM=RUN/'timings'
OUT=Path(__file__).resolve().parents[1]/'generated'/'closure_analysis'
TABLE=Path(__file__).resolve().parents[1]/'tables'/'generated'/'closure_compute_cost.tex'
OUT.mkdir(parents=True,exist_ok=True); TABLE.parent.mkdir(parents=True,exist_ok=True)
records=pd.read_csv(RUN/'results'/'RECORDS.csv').drop_duplicates('record').set_index('record')
files=[]
for f in sorted(TIM.glob('*.json')):
    x=json.loads(f.read_text(encoding='utf-8'))
    sec=x.get('seconds')
    if not isinstance(sec,(int,float)): continue
    stage=str(x.get('stage',f.stem)); parts=stage.split('_')
    rec=parts[-1] if len(parts)>1 and parts[-1].startswith('S') else None
    duration=float(records.loc[rec,'duration_s']) if rec in records.index else None
    lane=str(records.loc[rec,'lane']) if rec in records.index else None
    files.append({'file':f.name,'stage':stage,'group':parts[0],'record':rec,'duration_s':duration,'lane':lane,'seconds':float(sec),'returncode':x.get('returncode')})
# Record-granular stages; retain full-record timings and describe mean amortized time per report.
rows=[]
for group in ('bank','r11','ml','chen','prefix','mlprefix'):
    for duration in (120.0,600.0):
        xs=[x for x in files if x['group']==group and x['duration_s']==duration]
        if not xs: continue
        vals=sorted(x['seconds'] for x in xs)
        nreports=int(duration*30+1)
        rows.append({'stage_group':group,'scope':{'bank':'physical bank build','r11':'physical history inference','ml':'two ExtraTrees adapters combined','chen':'Chen line detector','prefix':'physical prefix fit','mlprefix':'learned prefix fit'}[group],
          'record_duration_s':int(duration),'n_records':len(vals),'reports_per_record':nreports,
          'median_wall_s_per_record':statistics.median(vals),'min_wall_s_per_record':vals[0],'max_wall_s_per_record':vals[-1],
          'median_amortized_wall_ms_per_report':1000*statistics.median(vals)/nreports,
          'returncode_failures':sum(x['returncode'] not in (0,None) for x in xs),'memory_recorded':False,'per_report_latency_recorded':False})
# Global one-off stages are setup/reporting totals, never per-inference latency.
for x in files:
    if x['record'] is None:
        rows.append({'stage_group':x['group'],'scope':x['stage'],'record_duration_s':'','n_records':1,'reports_per_record':'','median_wall_s_per_record':x['seconds'],'min_wall_s_per_record':x['seconds'],'max_wall_s_per_record':x['seconds'],'median_amortized_wall_ms_per_report':'','returncode_failures':int(x['returncode'] not in (0,None)),'memory_recorded':False,'per_report_latency_recorded':False})
with (OUT/'COMPUTE_COST.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Table: matched 120 s event-record median by major computation stage.
major={r['stage_group']:r for r in rows if r['record_duration_s']==120}
tex=[r'\begin{table}[t]\centering\small\setlength{\tabcolsep}{3pt}',
 r'\caption{Recorded stage times from the continuous evaluation on 120-s records. Medians and ranges summarize full-record stages; the per-report column is a median-total divided by 3,601 reports and is amortized, not frame latency. Stages were recorded in a campaign with one BLAS and one Julia thread; memory and per-report latency were not recorded. This descriptive table does not establish real-time operation or a speedup under matched implementation conditions.}',
 r'\label{tab:closure-compute-cost}',r'\begin{tabular}{@{}lrrr@{}}\toprule',r'Stage & Median (s) & Range (s) & ms/report$^\dagger$ \\\midrule']
for g in ('bank','r11','ml','chen'):
    if g in major:
        r=major[g]; name={'bank':'Bank build','r11':'History inference','ml':'ExtraTrees (both)','chen':'Chen detector'}[g]
        tex.append(f"{name} & {r['median_wall_s_per_record']:.1f} & {r['min_wall_s_per_record']:.1f}--{r['max_wall_s_per_record']:.1f} & {r['median_amortized_wall_ms_per_report']:.1f} " + r"\\")
tex += [r'\bottomrule\end{tabular}\end{table}']
TABLE.write_text('\n'.join(tex)+'\n',encoding='utf-8')
env=json.loads((RUN/'ENVIRONMENT.json').read_text(encoding='utf-8'))
inputs=[RUN/'ENVIRONMENT.json',RUN/'results'/'RECORDS.csv']+sorted(TIM.glob('*.json'))
manifest={'status':'EXISTING_TIMINGS_DESCRIPTIVE_NO_NEW_BENCHMARK','source':'C01 run/timings and environment; all timing files inspected by metadata only','system':{'platform':env.get('platform'),'python':env.get('python'),'BLAS_threads':env.get('BLAS_threads'),'Julia_threads':env.get('Julia_threads'),'packages':env.get('packages')},'constraints':'No memory field or per-report latency found. Per-report normalization is amortized full-record wall time. Stage measurements may be heterogeneous and do not support a real-time or universal speedup claim.','input_hashes':{str(p.relative_to(SCIENCE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'rows':rows}
(OUT/'COMPUTE_COST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'rows':rows,'environment':manifest['system'],'table':str(TABLE)},indent=2))
