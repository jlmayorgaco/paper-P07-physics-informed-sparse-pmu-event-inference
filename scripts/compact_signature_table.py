"""Transpose the generated X02 table for the standalone supplement layout."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'tables/generated/ei_x02_results.tex'
rows = {}
for line in source.read_text(encoding='utf-8').splitlines():
    if line.startswith(('Nominal &', 'Recentered &', 'Conditioned &')):
        cells = line.rstrip('\\').split(' & ')
        if len(cells) != 6:
            raise ValueError('Unexpected generated X02 table schema')
        rows[cells[0]] = cells[1:]
if set(rows) != {'Nominal', 'Recentered', 'Conditioned'}:
    raise ValueError('Missing X02 variants')
text = r'''% Transposed from the generated X02 table, without changing values.
\begin{table}[t]\centering\footnotesize\setlength{\tabcolsep}{3pt}
\caption{Controlled known-onset load test. Response error uses 80 physical cases; joint and source-only correctness use 240 noisy event records. Severity error is evaluated at the generating source. The 15 normal windows are not normal-hours exposure.}
\label{tab:ei-results}
\begin{tabular}{lrrr}\toprule
Measure & Nominal & Recentered & Conditioned\\\midrule
'''
for index, label in enumerate(['Response error (\\%)', 'Joint correct', 'Source-only correct', 'Normal selections', 'Severity error (\\%)']):
    text += ' & '.join([label] + [rows[key][index] for key in ('Nominal', 'Recentered', 'Conditioned')]) + r'\\' + '\n'
text += '\\bottomrule\\end{tabular}\\end{table}\n'
(ROOT / 'tables/generated/ei_x02_results_compact.tex').write_text(text, encoding='utf-8')
print('X02 compact table: all source cells preserved')
