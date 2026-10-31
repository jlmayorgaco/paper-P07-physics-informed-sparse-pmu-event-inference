"""Main-article coverage/delay tables from completed sealed C01 summaries."""
import pandas as pd

def write_tables(root, summary):
    labels={'R11':'Physical 5-model','R11_NOMINAL':'Physical nominal',
            'ET_REFERENCE':'ExtraTrees','ET_CANDIDATE':'ET short','CHEN2016':'Chen2016'}
    def val(x): return '--' if pd.isna(x) else f'{x:.2f}'
    def table(name, caption, columns, header, rows):
        (root/'tables/generated'/name).write_text('\n'.join([
            r'\begin{table*}[t]\centering\small',r'\caption{'+caption+'}',
            r'\label{tab:'+name.removesuffix('.tex')+'}',
            r'\begin{tabular}{'+columns+r'}\toprule',header+r'\\\midrule',
            *rows,r'\bottomrule\end{tabular}\end{table*}'])+'\n')
    cont=summary[summary.lane=='continuous']; rows=[]
    for method in ['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE']:
        d=cont[cont.method==method]; n=int(d.normal_parents.sum())
        rows.append(labels[method]+f" & {int((d.intended_records-d.available_records).sum())} & {int(d.normal_records_with_alarm.sum())}/{n} & {int(d.normal_FA.sum())} & {d.normal_available_s.sum()/3600:.3f} & {int(d.false_restorations.sum())} & {int(d.open_eof.sum())}"+r'\\')
    table('c01_operational.tex','Continuous monitoring: unavailable intended records, normal-record alarm incidence, normal alarm counts and available normal exposure, false restorations and open episodes. Counts combine six repeated strata descriptively; normal parents are not independent across strata. Missing outputs remain intended failures.','lrrrrrr',r'Method & Unavailable & Normal incidence & Normal alarms & Exposure (h) & False OFF & Open at end',rows)
    rows=[]
    for (condition,noise),group in cont.groupby(['condition','noise']):
        d=group.set_index('method')
        cells=[val(d.loc[m,'median_diagnosis_delay_s'])+'/'+val(d.loc[m,'median_restoration_delay_s']) for m in ['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE']]
        rows.append(condition.replace('_',r'\_')+f' & {noise:g} & '+' & '.join(cells)+r'\\')
    table('c01_delays.tex','Conditional median diagnosis/restoration delays (s), kept within each paired stratum. These medians summarize successful outputs and must be read alongside omissions, unavailable records and censoring; -- denotes no finite estimate. Logical delays do not measure computational throughput.','llrrrr',r'R/X condition & Noise & Physical 5-model & Physical nominal & ExtraTrees & ET short',rows)
    pers=summary[summary.lane=='persistent_line']; rows=[]
    for (condition,noise),group in pers.groupby(['condition','noise']):
        d=group.set_index('method'); cells=[]
        for m in ['R11','R11_NOMINAL','CHEN2016']:
            a=d.loc[m]; cells.append(f"{int(a.first_correct)}/{int(a.events)}; {int(a.first_prechange)}/{int(a.first_right_censored)}; "+val(a.mean_restricted_correct_delay_s))
        rows.append(condition.replace('_',r'\_')+f' & {noise:g} & '+' & '.join(cells)+r'\\')
    table('c01_first_stop.tex','Persistent-line comparison on the common observations. Each cell gives correct first source / intended openings; pre-change stops / right-censored openings; mean restricted correct delay (s). Wrong first sources remain in the denominator. Restricted delay retains the horizon penalty for failures and censoring defined by the frozen evaluator.','llrrr',r'R/X condition & Noise & Physical 5-model & Physical nominal & Chen2016',rows)
    rows=[]
    for method in ['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE','CHEN2016']:
        d=pers[pers.method==method]; n=int(d.normal_parents.sum())
        rows.append(labels[method]+f" & {int((d.intended_records-d.available_records).sum())} & {int(d.first_correct.sum())}/{int(d.events.sum())} & {int(d.first_prechange.sum())} & {int(d.first_right_censored.sum())} & {int(d.normal_records_with_alarm.sum())}/{n} & {d.normal_available_s.sum()/3600:.3f}"+r'\\')
    table('c01_persistent_coverage.tex','Persistent-line coverage and stopping outcomes across six repeated strata, including both frozen ExtraTrees comparators. Normal controls are the same controls used in the continuous table, not additional exposure. Chen2016 normal exposure ends at its first stop; the other methods monitor the full available record.','lrrrrrr',r'Method & Unavailable & Correct first & Pre-change & Censored & Normal incidence & Exposure (h)',rows)
