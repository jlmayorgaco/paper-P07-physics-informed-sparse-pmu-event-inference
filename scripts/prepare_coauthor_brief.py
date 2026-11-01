"""One-page coauthor brief from completed evidence and operational C01 status.

Does not read C01 predictions, scientific results, truth or PMU recordings.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import statistics
from collections import Counter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SG = ROOT.parent / 'SGSMA26-Physics-Informed-AD'
RUN = SG / 'experiments/PAPER_CONFIRMATORY_C01/run'
OUT = ROOT / 'output/pdf/P07_Coauthor_Brief_David_Masoud.pdf'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    progress = read(RUN / 'RECORD_PROGRESS.json')
    records = read(RUN / 'data/INPUTS.json')  # public id, duration, hash only
    done = progress['completed']
    if done and progress['last_record'] != records[done - 1]['id']:
        raise RuntimeError('Progress is not a contiguous prefix; timing projection needs review')
    remaining = records[done:]
    counts = Counter(r['duration_s'] for r in remaining)
    timing = {}
    for duration in counts:
        vals = []
        for record in reversed(records[:done]):
            if record['duration_s'] != duration:
                continue
            paths = [RUN / 'timings' / f'{mode}_{record["id"]}.json'
                     for mode in ['bank', 'r11', 'ml', 'chen']]
            if all(p.exists() for p in paths):
                vals.append(sum(read(p)['seconds'] for p in paths))
            if len(vals) == 12:
                break
        if not vals:
            raise RuntimeError('No completed comparable timing records')
        timing[str(duration)] = dict(n=len(vals), median_s=statistics.median(vals),
                                    min_s=min(vals), max_s=max(vals), remaining=counts[duration])
    hours = {key: sum(c['remaining'] * c[key] for c in timing.values()) / 3600
             for key in ['median_s', 'min_s', 'max_s']}
    status = dict(local_time=datetime.now(ZoneInfo('America/Bogota')).isoformat(),
                  progress=progress, stage=read(RUN / 'PROGRESS.json'),
                  timing_by_duration=timing, remaining_hours=hours,
                  interpretation='Timing projection, not a statistical confidence interval; excludes evaluation/build. Current record counted in full.',
                  methods_changed=False, scientific_partial_results_read=False)
    (ROOT / 'docs/C01_COAUTHOR_STATUS.json').write_text(json.dumps(status, indent=2) + '\n')

    sources = [ROOT / 'generated/continuous_macros.tex',
               ROOT / 'generated/ei_x02_macros.tex',
               ROOT / 'generated/frozen/recovery_x04_20261031/results/SUMMARY.json']
    macros = {}
    for source in sources[:2]:
        macros.update(re.findall(r'\\newcommand\{\\(\w+)\}\{([^}]+)\}', source.read_text()))
    x4 = read(sources[2])
    m = lambda name: macros[name]
    stamp = datetime.now(ZoneInfo('America/Bogota')).strftime('%d %b %Y, %H:%M Colombia')
    sections = [
        ('Question and contribution',
         'Can eight PMUs distinguish a new load/line intervention from the electrical recovery of an earlier one? '
         'P07 specifies a causal physical-history attribution procedure: retained states survive restoration, '
         'new interventions compete with recovery, and active-event mass is distinguished from originating-cause mass. '
         'This connects the physical cause, its active interval and the remaining response in one sequential explanation, tested against operational errors rather than accuracy alone.'),
        ('Where physics and Bayes enter',
         'Kirchhoff constraints, Ybus, oriented branch currents and machine/control dynamics determine reduced DAE predictors. '
         'Known PMU locations select the observation map; phase and instrument memory supply frequency/ROCOF predictions. '
         'States and operating context come from past PMU reports. Conditional Gaussian evidence integrates truncated load severity; '
         'predictive likelihoods weight five constant R/X hypotheses. Onset screening, shared regime covariances, pruning and publication rules make the complete procedure approximate.'),
        ('Completed evidence: development, not C01 confirmation', ''),
        ('What the controlled experiments establish',
         f'With load family and ON/OFF supplied, recentering and conditioned signatures both recover {m("EICondJoint")}/{m("EICondEventRecords")} sources '
         f'(80 physical event cases, three shared-noise realizations). Conditioning lowers median relative response error '
         f'{m("EIRecentResponse")}% to {m("EICondResponse")}% and severity error at the generating source '
         f'{m("EIRecentSeverity")}% to {m("EICondSeverity")}%. A separate {x4["physical_trajectories"]}-trajectory recovery control '
         'finds no mean binary-localization gain (98.35% for both arms; 12 correlated, known-history/onset comparisons). '
         'Better fit, source identity and calibrated uncertainty are distinct outcomes.'),
        ('Difference from the hackathon and the literature',
         'The contribution changes the explanation and temporal evaluation, rather than adding a source-label classifier. '
         'H04 favors the physical procedures on loads but not on extra-alarm count; it is not an official leaderboard comparison. '
         'Warner already uses physical trajectories and onset search; IMM/M3H already retains mode histories. '
         'No numerical advantage over an unexecuted matched M3H/Warner method is claimed.'),
        ('Limits and the fixed route to submission',
         f'C01: {done}/{len(records)} records complete at this snapshot; 171 physical trajectories have finished. '
         f'Estimated remaining processing is {hours["median_s"]:.0f} h (recent timing envelope {hours["min_s"]:.0f}-{hours["max_s"]:.0f} h), plus evaluation/build. '
         'Finish the frozen comparison of R11, nominal and both ExtraTrees adapters; score Chen2016 on persistent openings. '
         'Audit all intended cases, normal exposure, delays, censoring and parent-paired intervals, then finalize claims with the coauthors. '
         'Scope remains nine load and nine line assets, an event-free startup and a declared simulator. No field, unseen-source, all-family, real-time or calibrated-probability claim; BUS5 terminal and BUS39 angle limitations remain. No new method versions or test tuning.')
    ]
    rows = [['H04 procedure', 'Timely family + source', 'Extra alarms'],
            ['Physical: five models', f'{m("ContMixTimely")}/{m("ContMixTotal")}', m('ContMixExtras')],
            ['Physical: nominal', f'{m("ContNomTimely")}/{m("ContNomTotal")}', m('ContNomExtras')],
            ['Both frozen ExtraTrees adapters', f'{m("ContETTimely")}/{m("ContETTotal")}', m('ContETExtras')]]
    note = '54 realizations repeat 18 interventions across three network conditions; normal exposure is only 204 s per method. Nominal/mixture publication paths also differ, so this is not an isolated R/X-bank ablation.'
    pdfmetrics.registerFont(TTFont('BriefArial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('BriefArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
    body = ParagraphStyle('body', fontName='BriefArial', fontSize=10, leading=13, spaceAfter=5.5)
    head = ParagraphStyle('head', fontName='BriefArialBold', fontSize=10, leading=12, textColor=colors.HexColor('#125570'), spaceBefore=7, spaceAfter=4)
    small = ParagraphStyle('small', parent=body, fontSize=8.2, leading=10.2)
    title = ParagraphStyle('title', fontName='BriefArialBold', fontSize=17, leading=20, spaceAfter=5)
    story = [Paragraph('P07 | Contribution, evidence and closure', title),
             Paragraph(f'For David Celeita and Masoud Barati | Coauthor-review draft | {stamp}', small)]
    md = ['# P07: contribution, evidence and closure', '', 'Coauthor-review draft | ' + stamp, '']
    for heading, text in sections:
        story.append(Paragraph(heading, head)); md += ['## ' + heading, '']
        if text:
            story.append(Paragraph(text, body)); md += [text, '']
        else:
            t = Table([[Paragraph(c, small) for c in row] for row in rows], colWidths=[240, 160, 112])
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e7f0f3')),
                                   ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                   ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                   ('TOPPADDING', (0, 0), (-1, -1), 4)]))
            story += [t, Spacer(1, 4), Paragraph(note, small)]
            md += ['| ' + ' | '.join(rows[0]) + ' |', '|---|---|---|']
            md += ['| ' + ' | '.join(row) + ' |' for row in rows[1:]]
            md += ['', note, '']
    doc = SimpleDocTemplate(str(OUT), pagesize=(595.28, 841.89), leftMargin=41.6, rightMargin=41.6,
                            topMargin=30, bottomMargin=27, title='P07: contribution, evidence and closure')
    doc.build(story)
    with pymupdf.open(OUT) as pdf:
        if len(pdf) != 1:
            raise RuntimeError(f'Brief must be one page; got {len(pdf)}')
    (ROOT / 'docs/P07_COAUTHOR_BRIEF.md').write_text('\n'.join(md), encoding='utf-8')
    manifest = dict(status=status, numerical_sources=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],
                    output_sha256=hashlib.sha256(OUT.read_bytes()).hexdigest())
    (ROOT / 'docs/P07_COAUTHOR_BRIEF_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(pdf=str(OUT), pages=1, completed=done, remaining=len(remaining), hours=hours), indent=2))


if __name__ == '__main__':
    main()
