"""Editorial adapter after the sealed executor imports C01; no inference changes.
Keeps the revised narrative when the older frozen integration hook completes.
"""
from pathlib import Path
import hashlib,json
import pandas as pd
from c01_main_tables import write_tables
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'generated/frozen/c01_20261029'
def main():
    if not (DATA/'MANIFEST.json').exists():print('C01_NOT_COMPLETE_NARRATIVE_USES_DEVELOPMENT_ONLY');return
    for f in json.loads((DATA/'MANIFEST.json').read_text())['files']:
        if hashlib.sha256((DATA/f['path']).read_bytes()).hexdigest()!=f['sha256']:raise RuntimeError('C01 imported evidence changed: '+f['path'])
    s=pd.read_csv(DATA/'SUMMARY.csv');p=pd.read_csv(DATA/'PAIRED_INTERVALS.csv');g=s[s.lane=='continuous'];rows=[]
    for (condition,noise),d in g.groupby(['condition','noise']):
        d=d.set_index('method');rows.append(condition.replace('_',r'\_')+f' & {noise:g} & '+' & '.join(f"{int(d.loc[a,'timely'])}/{int(d.loc[a,'events'])}; {int(d.loc[a,'event_extras'])}" for a in ['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE'])+r'\\')
    table=[r'\begin{table*}[t]\centering\small',r'\caption{C01 continuous outcomes: timely family/source decisions followed by unmatched event-stream alarms. Each row is a paired condition/noise stratum; intervals resample physical parents, not individual reports or repeated conditions.}',r'\label{tab:c01-narrative}',r'\begin{tabular}{llrrrr}\toprule',r'R/X condition & Noise & Physical 5-model & Physical nominal & ExtraTrees & ET short\\\midrule',*rows,r'\bottomrule\end{tabular}\end{table*}'];(ROOT/'tables/generated/c01_narrative.tex').write_text('\n'.join(table)+'\n')
    write_tables(ROOT,s)
    text=r'''\subsection{The Frozen Confirmatory Result}
\label{sec:c01-results}
C01 has completed without changing methods or selecting a new variant.
Table~\ref{tab:c01-narrative} gives the operational comparison under each fixed
network condition and noise scale. Across the paired continuous realizations,
the five-model physical reference obtains \COneMixTimely{}/\COneMixTotal{}
timely decisions and \COneMixExtras{} extras; nominal obtains
\COneNomTimely{}/\COneNomTotal{} with \COneNomExtras{} extras; ExtraTrees reference
obtains \COneETTimely{}/\COneETTotal{} with \COneETExtras{} extras.
The total repeats 108 interventions over six conditions/noise combinations.
It is not that many independent events and does not replace the stratified comparison.
\input{tables/generated/c01_narrative}
\input{tables/generated/c01_operational}
\input{tables/generated/c01_delays}
\begin{figure*}[t]\centering
\includegraphics[width=.95\textwidth]{figures/generated/c01_paired_intervals.pdf}
\caption{What survives confirmation: paired timely-attribution differences
against ExtraTrees reference, with 95\% percentile intervals from 10,000
physical-parent resamples. A zero-crossing interval does not establish a
directional advantage in that stratum. The complete table also retains the
second frozen ExtraTrees reference.}
\label{fig:c01-ci}\end{figure*}

The persistent-line lane scores each algorithm's first stopping decision,
not its best later diagnosis. Pre-change stops, wrong sources, omissions and
right censoring remain in its denominator. Chen2016 uses its native
nonoverlapping 15-Hz angle increments from the common 30-fps stream and has no
load-family or restoration output. Its normal exposure ends at its first stop;
the other methods monitor the complete available record. Normal-record alarm
incidence and native exposure are therefore reported together. The F01 adapter
does not inherit an ARL guarantee under colored instrumental noise.
Tables~\ref{tab:c01_first_stop} and~\ref{tab:c01_persistent_coverage}
retain the published comparator and its failures in this article.
Table~\ref{tab:c01_operational} and Table~\ref{tab:c01_delays}
separate unmatched alarms, closure errors and conditional delays. A small
median delay cannot compensate for an omitted event.
\input{tables/generated/c01_first_stop}
\input{tables/generated/c01_persistent_coverage}

The frozen archive contains per-source outcomes, false alarms, diagnosis and
restoration delays, solver/inference failures, censoring and all intended
denominators. No intended failure is silently removed. The confirmation tests
the known load/line catalog, F01 operation and specified R/X/noise ranges; it
does not establish the hackathon leaderboard, unseen-source causal transfer,
calibrated event probabilities or field validation.
'''
    (ROOT/'sections/08c_c01_confirmatory.tex').write_text(text,encoding='utf-8')
    section=ROOT/'supplement/c01_narrative_details.tex';section.write_text(r'''\section{Complete C01 Confirmation Tables}
\input{tables/generated/c01_continuous}
\input{tables/generated/c01_persistent_line}
\begin{figure*}[t]\centering\includegraphics[width=.98\textwidth]{figures/generated/c01_continuous.pdf}
\caption{Full stratified continuous outcomes. Counts retain intended failures.}\end{figure*}
\begin{figure*}[t]\centering\includegraphics[width=.98\textwidth]{figures/generated/c01_persistent.pdf}
\caption{First-stop line attribution under each condition/noise stratum.}\end{figure*}
\FloatBarrier
''',encoding='utf-8')
    replacements={
      'main.tex': [('Confirmatory performance remains pending completion of the frozen campaign.',r'The completed confirmatory continuous study obtains \COneMixTimely{}/\COneMixTotal{} timely decisions with \COneMixExtras{} extras for the five-model reference; paired strata and intervals retain its failures.')],
      'sections/narrative_results.tex': [('The present development evidence supports causal load/line attribution on a known catalog and shows its failure modes. It does not yet support a final performance claim on C01. The confirmatory executor is running with fixed methods, cases, thresholds and metrics; its completed results will enter the dedicated section below through the same hash-to-table/figure chain. No partial C01 result is used here to choose a variant or revise the method.','The preceding illustrations remain development evidence. The completed frozen C01 outcomes are reported separately below, without using them to select another variant or change the method.'),('\\subsection{What Is Still Being Confirmed}','\\subsection{Development and Confirmation Remain Separate}')],
      'sections/narrative_protocol.tex': [('Until that evaluation exists, the following section reports only completed development evidence.','The completed confirmation is reported separately from the development illustrations.')],
    }
    for name,pairs in replacements.items():
        q=ROOT/name;t=q.read_text(encoding='utf-8')
        for a,b in pairs:t=t.replace(a,b)
        q.write_text(t,encoding='utf-8')
    q=ROOT/'sections/narrative_conclusion.tex'
    if q.exists():
        t=q.read_text(encoding='utf-8');t=t.replace('Final performance claims depend on the frozen confirmatory results.',r'The subsequent C01 continuous confirmation obtains \COneMixTimely{}/\COneMixTotal{} timely decisions with \COneMixExtras{} extras for the mixture, versus \COneNomTimely{}/\COneNomTotal{} with \COneNomExtras{} extras for nominal; the stratified paired comparison determines the direction of each advantage.');q.write_text(t,encoding='utf-8')
    marker='## C01 completed evidence update'
    for name in ['CLAIMS.md','docs/claims-and-evidence.md']:
        q=ROOT/name
        if q.exists():
            t=q.read_text(encoding='utf-8')
            if marker not in t:q.write_text(marker+'\n\nC01 completed without method retuning. The governing evidence is generated/frozen/c01_20261029/MANIFEST.json, the complete failure ledger and paired parent-cluster intervals. Section sec:c01-results and its generated tables report the confirmation separately from H03/H04 development. No all-family, unseen-source, calibrated-probability, field or leaderboard claim follows. Earlier pending statuses are historical.\n\n'+t,encoding='utf-8')
    (ROOT/'generated/narrative_c01_audit.json').write_text(json.dumps(dict(import_hashes_verified=True,methods_changed=False,conditional_editorial_refresh=True,comparative_rows=len(p)),indent=2)+'\n');print('C01_NARRATIVE_REFRESHED')
if __name__=='__main__':main()
