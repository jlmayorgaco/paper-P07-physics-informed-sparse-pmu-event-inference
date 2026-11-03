"""Build the one-page coauthor brief from sealed C01 results and fixed controls."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json

import pandas as pd
import pymupdf
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parents[1]
SG = ROOT.parent / 'SGSMA26-Physics-Informed-AD'
FROZEN = ROOT / 'generated/frozen/c01_20261029'
OUT = ROOT / 'output/pdf/P07_Coauthor_Brief_David_Masoud.pdf'


def main():
    manifest_file = FROZEN / 'MANIFEST.json'
    manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    for item in manifest['files']:
        source = FROZEN / item['path']
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError(f'C01 import differs from seal: {item["path"]}')
    complete = json.loads((SG / 'experiments/PAPER_CONFIRMATORY_C01/run/COMPLETE.json').read_text())
    if complete['status'] != 'COMPLETE_WITH_ALL_INTENDED_DENOMINATORS' or complete['models_retuned']:
        raise RuntimeError('C01 has not passed the frozen completion gate')
    audit = json.loads((FROZEN / 'EVALUATION_AUDIT.json').read_text())
    if audit['intended_observed_records'] != 342 or not audit['prediction_sealed_before_truth']:
        raise RuntimeError('C01 audit is incomplete')
    summary = pd.read_csv(FROZEN / 'SUMMARY.csv')
    cont = summary[summary.lane == 'continuous']
    persistent = summary[summary.lane == 'persistent_line']
    total = cont.groupby('method')[['events', 'timely', 'event_extras']].sum()
    outside = cont[cont.condition == 'RX_OUT_SUPPORT'].groupby('method')[['events', 'timely', 'event_extras']].sum()
    line = persistent.groupby('method')[['events', 'first_correct', 'first_prechange', 'normal_records_with_alarm']].sum()
    if int(total.loc['R11', 'events']) != 648 or int(line.loc['CHEN2016', 'events']) != 162:
        raise RuntimeError('Unexpected C01 denominators')

    stamp = datetime.now(ZoneInfo('America/Bogota')).strftime('%d %b %Y, %H:%M Colombia')
    names = [('Physical bank (5 models)', 'R11'), ('Physical bank (nominal)', 'R11_NOMINAL'),
             ('ExtraTrees reference', 'ET_REFERENCE'), ('ExtraTrees short', 'ET_CANDIDATE')]
    rows = [['Frozen continuous method', 'Timely / 648', 'Extras', 'Outside-bank timely / 216', 'Outside-bank extras']]
    for label, key in names:
        rows.append([label, f'{int(total.loc[key,"timely"])}/648', str(int(total.loc[key,'event_extras'])),
                     f'{int(outside.loc[key,"timely"])}/216', str(int(outside.loc[key,'event_extras']))])
    chen = line.loc['CHEN2016']
    records = pd.read_csv(FROZEN / 'RECORDS.csv')
    maintained = records[records.lane == 'persistent_line'].groupby('method')['extras'].sum()
    sections = [
        ('Question and actual contribution',
         'How can eight PMUs distinguish the physical cause of a network disturbance? The paper connects '
         'network-constrained reconstruction, physical response signatures and Bayesian history attribution, '
         'with engineered-feature ExtraTrees as a retained alternative. The implemented causal bank predicts '
         'each candidate intervention from estimated past states, integrates load severity and retains recovery. '
         'Active and cause masses expose its decisions. These are approximate conditional calculations, not '
         'a new Bayes theorem or a globally optimal filter.'),
        ('Earlier evidence is part of the paper',
         'Separate component tests recover hidden voltages, quantify feature gains and show that mixed-source '
         'sensitivities improve local response fit. A direct historical transfer of the submitted ZIP yields '
         '0/96 joint source decisions versus 96/96 for an earlier physical estimator; its confusion matrices '
         'are included, with the development/domain advantage explicit. The archived batch Bayesian support '
         'test retains its evidence-normalization caveat. None of these tests isolates a tensor/Bayes contribution '
         'to final causal accuracy. The frozen continuous comparison uses new causal ExtraTrees comparators, not the original 30-s submission.'),
        ('Sealed comparison: 171 physical trajectories, 342 observed records', ''),
        ('Other outcomes that change the interpretation',
         f'Continuous: the physical bank attributes 322/324 loads and 322/324 lines before OFF; the ExtraTrees reference attributes '
         f'15/324 loads and 315/324 lines; the short-window variant gets 30/324 loads and 322/324 lines. '
         'All timely matched decisions have correct family/source: the main gap is timely coverage, not conditional classification accuracy. '
         f'Persistent line: both physical banks and both ExtraTrees adapters make 162/162 correct first decisions; Chen2016 makes '
         f'{int(chen["first_correct"])}/162, with {int(chen["first_prechange"])} pre-change stops. '
         f'After first detection, physical banks produce 0 extras versus {int(maintained["ET_REFERENCE"])}/{int(maintained["ET_CANDIDATE"])} for the two trees (post hoc persistence audit). '
         f'Chen stops on all {int(chen["normal_records_with_alarm"])}/72 normal records; physical banks and trees alarm on 0/72, with different exposure.'),
        ('Interpretation and limits',
         'The sealed study supports timely attribution on the declared nine-load/nine-line simulator catalog, especially loads, while '
         'exposing an alarm burden under network mismatch. Replayed conditions and noise share parents; 648 is not '
         '648 independent events. Original tree validation shares two normal groups with fitting; the later grouped 70/30 study is a different model. No official '
         'hackathon-score improvement, source-excluded transfer, all-family diagnosis, calibrated probabilities, '
         'field operation or real-time throughput is established. Warner trajectory search and IMM/multiple-history '
         'methods are acknowledged; no matched numerical advantage over them is claimed.'),
        ('For David and Masoud',
         'Ready for scientific coauthor review, not yet certified for journal submission. The central claim is the complete procedure and its measured trade-off. The comparison does not '
         'isolate recovery memory and the methods have different fixed false-alarm budgets. Decide whether to '
         'state only the complete-procedure claim or obtain a controlled component/comparator test. '
         'No method was retuned after the sealed comparison.')
    ]

    ablation = ROOT / 'generated/frozen/ablation_a01_20261102'
    if (ablation / 'SUMMARY.csv').exists():
        audit_a = json.loads((ablation / 'EVALUATION_AUDIT.json').read_text())
        assert audit_a['intended_outputs'] == 96
        manifest_a = json.loads((ablation / 'MANIFEST.json').read_text())
        for name in ('SUMMARY.csv', 'EVALUATION_AUDIT.json'):
            assert hashlib.sha256((ablation / name).read_bytes()).hexdigest() == manifest_a[name]['sha256']
        a = pd.read_csv(ablation / 'SUMMARY.csv');a = a[a.lane == 'continuous'].set_index('method')
        pairs = [('marginal/carry','BAYES_MEMORY'),('profile/carry','PROFILE_MEMORY'),('marginal/reset','BAYES_NO_CARRY'),('profile/reset','PROFILE_NO_CARRY')]
        outcomes = '; '.join(f'{label}: {int(a.loc[key,"timely"])}/108 and {int(a.loc[key,"extras"])} extras' for label,key in pairs)
        sections[-1] = ('Controlled component study and coauthor decision',
            'Posthoc study on 18 parents/108 events: ' + outcomes + '. Both carry arms also have one unmatched restoration; both reset arms have 130 and 33/108 events without a timely diagnosis. Median diagnosis delay is 0.267 s with carry and 0.337 s after reset. Normal controls have 0 false alarms in 1,764 s measured exposure (588 s from each of three 600-s records). Paired 18-parent intervals for carry versus reset are +0.306 timely fraction (95% CI 0.241-0.380) and -275 extras per event-record hour (95% CI -325 to -223.333), descriptive and posthoc. The marginal and bounded-profile scores tie on these endpoints. The profile arm retains conditional Bayesian state estimation and fixed priors; reset removes only physical-state carry at inferred closure, not instrumental memory or simulated state. These outcomes do not establish independent confirmation or superiority at matched false-alarm rates. Author declarations remain open.')
    else:
        sections[-1] = ('For David and Masoud',
            'Coauthor-review draft. A controlled 24-record factorial study is running with the same five-model bank and publisher: '
            'marginal versus profile amplitude scores, and physical-state carry versus reset at inferred closure. '
            'No effect is claimed before completion. This is a posthoc study on existing data, not independent confirmation. '
            'Scientific packaging, bibliography and author declarations remain pending before submission.')

    pdfmetrics.registerFont(TTFont('BriefArial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('BriefArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
    body = ParagraphStyle('body', fontName='BriefArial', fontSize=10, leading=13, spaceAfter=5)
    head = ParagraphStyle('head', fontName='BriefArialBold', fontSize=10.5, leading=13,
                          textColor=colors.HexColor('#125570'), spaceBefore=8, spaceAfter=3)
    small = ParagraphStyle('small', parent=body, fontSize=8.5, leading=10.5)
    title = ParagraphStyle('title', fontName='BriefArialBold', fontSize=17, leading=20, spaceAfter=5)
    story = [Paragraph('P07 | Contribution, evidence and limits', title),
             Paragraph(f'For David Celeita and Masoud Barati | Coauthor-review draft | {stamp}', small)]
    md = ['# P07: contribution, evidence and limits', '', 'Coauthor-review draft | ' + stamp, '']
    for heading, paragraph in sections:
        story.append(Paragraph(heading, head))
        md.extend(['## ' + heading, ''])
        if paragraph:
            story.append(Paragraph(paragraph, body))
            md.extend([paragraph, ''])
        else:
            table = Table([[Paragraph(str(cell), small) for cell in row] for row in rows],
                          colWidths=[128, 76, 43, 152, 111])
            table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7f0f3')),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                       ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                                       ('TOPPADDING', (0, 0), (-1, -1), 3)]))
            story.extend([table, Spacer(1, 2)])
            md.extend(['| ' + ' | '.join(rows[0]) + ' |', '|---|---:|---:|---:|---:|'])
            md.extend(['| ' + ' | '.join(row) + ' |' for row in rows[1:]])
            md.append('')
    doc = SimpleDocTemplate(str(OUT), pagesize=(595.28, 841.89), leftMargin=40,
                            rightMargin=40, topMargin=29, bottomMargin=26,
                            title='P07: contribution, evidence and limits')
    doc.build(story)
    with pymupdf.open(OUT) as pdf:
        if len(pdf) != 1:
            raise RuntimeError(f'Brief must remain one page; got {len(pdf)}')
    (ROOT / 'docs/P07_COAUTHOR_BRIEF.md').write_text('\n'.join(md), encoding='utf-8')
    status = {'status': 'C01_COMPLETE', 'completed_records': 342, 'physical_trajectories': 171,
              'date_local': stamp, 'methods_changed': False, 'remaining_hours': 0,
              'scientific_results_source': 'generated/frozen/c01_20261029/SUMMARY.csv'}
    (ROOT / 'docs/C01_COAUTHOR_STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
    provenance = {'c01_manifest_sha256': hashlib.sha256(manifest_file.read_bytes()).hexdigest(),
                  'c01_summary_sha256': hashlib.sha256((FROZEN / 'SUMMARY.csv').read_bytes()).hexdigest(),
                  'c01_records_sha256': hashlib.sha256((FROZEN / 'RECORDS.csv').read_bytes()).hexdigest(),
                  'brief_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(), 'pages': 1}
    (ROOT / 'docs/P07_COAUTHOR_BRIEF_MANIFEST.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(json.dumps(status, indent=2))


if __name__ == '__main__':
    main()
