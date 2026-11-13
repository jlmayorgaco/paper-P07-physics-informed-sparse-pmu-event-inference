"""Regenerate tables/macros only after independent sealed-evidence audit."""
from pathlib import Path
import json
from audit_adaptive_diagnostic import main as audit
ROOT=Path(__file__).resolve().parents[1]
def main():
    audit()
    run=ROOT/'experiments/adaptive_innovation_20261113_corrected/run'
    s=json.loads((run/'STREAM_RESULTS.json').read_text());c=json.loads((run/'COVARIANCE_RESULTS.json').read_text())
    lines=[r'\begin{table}[t]\centering',r'\caption{Nominal innovation diagnostic: independent calibration at one normal alarm per hour. All TEST arms use 5.88 normal hours and 72 load interventions in 36 paired records.}',r'\label{tab:adaptive-diagnostic}',r'\footnotesize\setlength{\tabcolsep}{3.5pt}',r'\begin{tabular}{lrrrr}',r'\toprule',r'Noise rule & $h$ & Correct/72 & Extras & FAR (upper)\\',r'\midrule']
    for key,name in [('fixed','Fixed'),('adaptive','Continuous'),('guarded','Guarded')]:
        r=s['arms'][key]
        lines.append(f"{name} & {r['threshold']:g} & {r['timely_joint_hits']} & {r['extra_alarms']} & {r['normal_far']:.2f} ({r['poisson_upper95_per_hour']:.2f})"+r'\\')
    lines.extend([r'\bottomrule',r'\end{tabular}',r'\par\smallskip\parbox{\columnwidth}{\footnotesize FAR and its one-sided 95\% Poisson upper bound are in h$^{-1}$. Extras include repeated or incorrect publications, over 1.08 monitored event hours. Correct means source identified during its true ON interval; this diagnostic estimates neither event family nor OFF.}',r'\end{table}'])
    (ROOT/'tables/generated/adaptive_diagnostic.tex').write_text('\n'.join(lines)+'\n')
    vals={'CovMeanHits':c['arms']['mean_only']['correct'],'CovCarryHits':c['arms']['mean_covariance']['correct'],
          'CovDelta':f"{100*c['paired_correctness']['difference']:.2f}",
          'CovLow':f"{100*c['paired_correctness']['ci95'][0]:.2f}",'CovHigh':f"{100*c['paired_correctness']['ci95'][1]:.2f}",
          'CovNisMean':f"{100*c['arms']['mean_only']['nis95_coverage']:.2f}",'CovNisCarry':f"{100*c['arms']['mean_covariance']['nis95_coverage']:.2f}",
          'AdaptDelta':f"{100*s['paired_timely_contrasts']['adaptive-fixed']['difference']:.2f}",
          'AdaptLow':f"{100*s['paired_timely_contrasts']['adaptive-fixed']['ci95'][0]:.2f}",
          'AdaptHigh':f"{100*s['paired_timely_contrasts']['adaptive-fixed']['ci95'][1]:.2f}",
          'GateFraction':f"{100*s['arms']['guarded']['normal_admission_fraction']:.2f}"}
    for key,arm in [('Fixed','fixed'),('Cont','adaptive'),('Guard','guarded')]:
        vals[key+'NoiseRmse']=f"{s['arms'][arm]['normal_noise_rmse']:.3f}"
    (ROOT/'generated/adaptive_diagnostic_macros.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+str(v)+'}' for k,v in vals.items())+'\n')
if __name__=='__main__':main()
