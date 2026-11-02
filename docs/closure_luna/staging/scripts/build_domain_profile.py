"""Build the P07 domain profile and measurement table from frozen contracts only."""
from pathlib import Path
import csv,json,hashlib,statistics
import pandas as pd
PAPER=Path(__file__).resolve().parents[4]
STAGE=Path(__file__).resolve().parents[1]
SCIENCE=PAPER.parent/'SGSMA26-Physics-Informed-AD'
EX=SCIENCE/'experiments/PAPER_CONFIRMATORY_C01'
F01=SCIENCE/'SIM0001_JuliaPD_F01'
case_path=EX/'execution_request'/'truth_private'/'cases.json'
plan_path=EX/'protocol'/'PLAN.json'
contract_path=F01/'FREEZE_CONTRACT.json'
map_path=F01/'runtime'/'reference'/'terminal_mapping.csv'
report_path=F01/'runtime'/'reference'/'reporting_config.json'
plan=json.loads(plan_path.read_text(encoding='utf-8')); cases=json.loads(case_path.read_text(encoding='utf-8'))
contract=json.loads(contract_path.read_text(encoding='utf-8')); reporting=json.loads(report_path.read_text(encoding='utf-8'))
continuous=[c for c in cases if c.get('lane')=='continuous' and c.get('condition')=='MATCH']
assert len(continuous)==18
# Each MATCH case supplies one unique continuous parent schedule; no averaging across repeated network/noise lanes.
events=[e for c in continuous for e in c['events']]
summary={}
for fam in ('load','line'):
 es=[e for e in events if e['family']==fam]
 durations=[float(e['off_s']-e['onset_s']) for e in es if e.get('off_s') is not None]
 summary[fam]={'unique_interventions':len(es),'duration_s_min':min(durations),'duration_s_max':max(durations),
   'sources':sorted({e['source'] for e in es})}
loads=[e for e in events if e['family']=='load']
amps=[float(e['amplitude']) for e in loads]
summary['load']['signed_amplitude_min']=min(amps);summary['load']['signed_amplitude_max']=max(amps)
summary['load']['absolute_amplitude_min']=min(abs(x) for x in amps);summary['load']['absolute_amplitude_max']=max(abs(x) for x in amps)
# Report-level planned exposure follows all 18 parent schedules × three R/X conditions × two noise scales.
summary['exposure']={'event_records':18*3*2,'event_record_duration_s':120,'event_hours':18*3*2*120/3600,
 'normal_records':12*3*2,'normal_record_duration_s':600,'normal_planned_hours':12*3*2*600/3600,
 'persistent_line_records':27*3*2,'persistent_line_record_duration_s':120}
summary['protocol']={'event_parents':plan['continuous']['event_parents'],'normal_parents':plan['continuous']['normal_parents'],'events_per_parent':plan['continuous']['events_per_parent'],
 'load_amplitude_absolute_fraction':plan['continuous']['load_amplitude_abs_fraction'],'duration_prespecified_s':plan['continuous']['duration_s'],
 'post_off_gap_s':plan['continuous']['post_off_gap_s'],'initial_onset_s':plan['continuous']['initial_onset_s'],
 'noise_std_factors':plan['noise_std_factors'],'noise_policy':plan['noise_policy'],'rx_out_support':plan['rx_out_support'],
 'rx_bank':'Five fixed R/X hypotheses: nominal, global +/-2%, selected-branch +/-3% paired R/X; condition tracks the simulation operating point, not an expanded model bank.',
 'sources':'Nine load buses and nine line candidates; known catalog, not unseen-source validation.',
 'warmup_and_context':'10-s startup context fit and 12-s warmup (360 reports) before monitoring; earliest scheduled event begins at 16 s.',
 'timebase_hz':30,'continuous_event_record_s':120,'normal_record_s':600}
summary['derived_channels']={'input_pmus':contract['measurement']['pmu_buses'],'measured_coordinate_count':47,
 'channels':'8 voltage magnitudes, 8 voltage angles, 8 current magnitudes, 7 current angles, 8 bus frequencies and 8 ROCOF values; BUS39 current angle omitted.',
 'frequency':'60 Hz plus derivative of reported voltage angle divided by 360; not rotor speed.',
 'rocof':'Second derivative from causal 21-report quadratic phase estimate; generator uses robust magnitude weights while predictor uses fixed unweighted fit.',
 'measurement_noise':'Noise is added to derived/report coordinates under the frozen R5C.2 noise stream at standard-deviation multipliers 1 and 2; cross-signal covariance field is not applied in the executed C01 operator.'}
source_paths=[plan_path,case_path,contract_path,map_path,report_path,SCIENCE/'SIM0001_CURRENT.json',EX/'protocol'/'FREEZE.json',EX/'protocol'/'EXECUTION_FREEZE.json']
summary['source_hashes']={str(p.relative_to(SCIENCE)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
(STAGE/'generated'/'closure_analysis'/'DOMAIN_PROFILE.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
# Full eight-row terminal contract: fields are read directly from F01 frozen map.
rows=list(csv.DictReader(map_path.open(encoding='utf-8-sig',newline='')))
voltage_base=float(contract['measurement']['voltage_base_for_these_PMUs_V'])
lines=[r'\subsection{F01 Measurement Contract}',r'\label{app:measurement-contract}',
 r'The executed channel map is taken from the frozen SIM0001-JuliaPD-F01 research snapshot. The eight voltage buses are $\{2,5,6,10,19,22,29,39\}$. Voltage magnitude is reported in per unit with unit gain; voltage angle uses one common affine phase reference plus the archived relative offsets. The reference interpretation is observational: physical common drift and instrument clock drift are not separately identified. Terminal currents are converted to outward branch convention from the simulator\textquotesingle s into-terminal observable, then mapped with the row-specific polarity, gain and phase bias. Current bases use $100\,\mathrm{MVA}/(\sqrt{3}\,V_{\mathrm{terminal}})$; the common voltage base is %.3f kV.\par'% (voltage_base/1000),
 r'\begin{table*}[t]\centering\scriptsize\setlength{\tabcolsep}{3pt}',r'\caption{Eight PMU rows in the frozen F01 measurement map. V is a bus voltage in p.u.; I is an oriented branch-terminal phasor. Gains and phase biases are applied to current channels. BUS5 retains the historical 5--6, terminal-5 hypothesis and its producer CT identity is unverified. BUS39 current phase is partially validated.}',r'\label{tab:f01-measurement-contract}',
 r'\begin{tabular}{@{}rrrrllrrrll@{}}\toprule',r'PMU & V bus & Edge & Branch & Terminal & Side & Polarity & Gain & Bias ($^\circ$) & I unit & Provenance \\\midrule']
for r in rows:
 status=r['status']
 if r['pmu_bus']=='5': short='BUS5 5--6 historical hypothesis; CT unverified'
 elif r['pmu_bus']=='39': short='BUS39 partial phase validation'
 else: short='F01 archived terminal hypothesis; CT unverified'
 lines.append(f"{int(r['pmu_bus'])} & {int(r['pmu_bus'])} & {r['edge']} & {r['src']}--{r['dst']} & {r['terminal']} & {r['side']} & {r['polarity']} & {float(r['gain']):.4f} & {float(r['bias_deg']):.3f} & A & {short} " + r'\\')
lines += [r'\bottomrule\end{tabular}',r'\end{table*}',
 r'Frequency is computed as $60+\dot\theta/(360)$ from the reported voltage angle, and ROCOF as $\ddot\theta/360$ using a causal 21-report quadratic estimate. The generator fit is robust and magnitude weighted; the predictor uses a fixed unweighted quadratic fit over the same history. Four warmup outputs are unavailable; the confirmatory evaluation uses a 10-s startup context and begins monitoring after 12 s. The 47 retained coordinates exclude the BUS39 current-angle coordinate. Noise multipliers 1 and 2 scale the standard deviation under the frozen stream. The stochastic model archives a cross-signal covariance field, but the executed report operator applies noise by signal family without that cross-family factor. These choices describe a simulated sensor configuration, not a verified eight-PMU CT/PT installation.' ]
(STAGE/'supplement'/'measurement_contract.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
# Concise scope paragraph and table in supplement; all ranges computed from the 18 MATCH schedules.
d=summary
profile=[r'\subsection{Evaluated Domain Profile}',r'\label{app:domain-profile}',
 f"The confirmatory evaluation covers {d['protocol']['event_parents']} continuous six-event parent schedules, repeated under three network conditions and two standard-deviation noise scales, for {d['exposure']['event_records']} 120-s event records per method ({d['exposure']['event_hours']:.1f} event-record hours). It includes {d['protocol']['normal_parents']} normal parents under the same condition/noise crossing, giving {d['exposure']['normal_records']} 600-s records ({d['exposure']['normal_planned_hours']:.1f} planned normal hours). A separate persistent-line lane has nine line sources with three repetitions each, crossed with the same network/noise settings. The twelve-second monitoring warmup follows a ten-second context fit; the earliest scheduled intervention is at 16 s.",
 f"Across the 18 unique continuous schedules, finite event duration ranges from {summary['load']['duration_s_min']:.2f} to {summary['line']['duration_s_max']:.2f} s. Load changes multiply both active and reactive setpoints by $1+a$ under the frozen impedance law; the prespecified $|a|$ range is {plan['continuous']['load_amplitude_abs_fraction'][0]:.2f}--{plan['continuous']['load_amplitude_abs_fraction'][1]:.2f} (realized signed schedule values range {summary['load']['signed_amplitude_min']:.3f} to {summary['load']['signed_amplitude_max']:.3f}). Line events are full branch openings followed by restoration. The three network conditions are MATCH, RX\_IN\_SUPPORT and RX\_OUT\_SUPPORT; out-of-support cases use independently signed 1--3% branch factors with R and X paired, fixed before the trajectory and solved at equilibrium. The estimator bank remains fixed at nominal, global $\\pm2\\%$, and selected-branch $\\pm3\\%$ paired R/X alternatives.",
 r"Noise scales 1 and 2 are standard-deviation multipliers of the frozen R5C.2 stream, with the same seed paired across conditions and scales. Event extras retain the full 120-s event-record denominator; this is not the monitored post-warmup duration. Parent schedules, not repeated condition/noise runs or PMU samples, are the independent unit. The catalog contains nine candidate loads and nine candidate lines; it is not an unseen-source or all-39-bus evaluation."]
(STAGE/'supplement'/'domain_profile.tex').write_text('\n\n'.join(profile)+'\n',encoding='utf-8')
print(json.dumps({'domain':summary,'measurement_contract':str(STAGE/'supplement'/'measurement_contract.tex'),'domain_tex':str(STAGE/'supplement'/'domain_profile.tex')},indent=2))
