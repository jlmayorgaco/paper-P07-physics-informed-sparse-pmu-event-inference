"""One-page review brief derived from complete sealed C01 and A01 ledgers."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json
import pandas as pd
import pymupdf
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf/P07_Coauthor_Brief_David_Masoud.pdf'


def main():
    from build_reader_figures import verify_manifest,C01
    verify_manifest(C01)
    c=pd.read_csv(C01/'SUMMARY.csv');c=c[c.lane=='continuous']
    aroot=ROOT/'generated/frozen/ablation_a01_20261102'
    manifest=json.loads((aroot/'MANIFEST.json').read_text())
    entries=manifest.get('files',manifest)
    if isinstance(entries,dict):entries=[dict(path=k,**v) for k,v in entries.items()]
    for item in entries:
        assert hashlib.sha256((aroot/item['path']).read_bytes()).hexdigest()==item['sha256']
    a=pd.read_csv(aroot/'SUMMARY.csv');a=a[a.lane=='continuous'].set_index('method')
    methods=['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE']
    names=['Physical bank','Nominal bank','ExtraTrees','ExtraTrees short']
    rows=[['Procedure','Timely family + source','Extra alarms']]
    for method,name in zip(methods,names):
        x=c[c.method==method];rows.append([name,f'{int(x.timely.sum())}/{int(x.events.sum())}',str(int(x.event_extras.sum()))])
    carry=a.loc['BAYES_MEMORY'];reset=a.loc['BAYES_NO_CARRY'];profile=a.loc['PROFILE_MEMORY']
    assert int(profile.timely)==int(carry.timely) and int(profile.extras)==int(carry.extras)
    sections=[
      ('Contribution', 'A sparse-PMU procedure compares new load/line interventions with the response retained after restoration. Switched DAE predictors start from estimated past states; active and originating-cause weights distinguish an intervention from its continuing effect. The electrical histories connect the intervention, its active interval and the continuing response in one sequential explanation.'),
      ('Independent simulated comparison',None),
      ('What the controlled results establish',f'On 18 existing continuous parents, preserving physical-state deviations gives {int(carry.timely)}/{int(carry.events)} timely attributions and {int(carry.extras)} extra; resetting them gives {int(reset.timely)}/{int(reset.events)} and {int(reset.extras)} extras. Marginal and bounded-profile scores tie on those endpoints. The state-carry benefit persists under both severity scores. A development-only continuous single-state GLR control exists; it still needs independent validation under matched information and calibration.'),
      ('Difference from the hackathon and the literature','The gain over the fixed causal ExtraTrees adapters is predominantly timely load coverage; line coverage is similar to the short-window model. This is not an improved official hackathon score. Physical trajectory diagnosis and M3H histories have direct precedents. The useful result is recovery-consistent attribution with explicit operational errors and limitations, rather than novelty of the individual ingredients.'),
      ('Corrections and remaining submission blockers','The manuscript now uses monitored exposure (108 s per 120-s event record); alarm-rate differences and their intervals rise by 120/108, without changing predictions or matches. It states the balanced phase-A/47-coordinate map, observation memory and measured compute cost. The active validation work tests independent continuous-observer comparison at matched information and alarm budgets, followed by cross-model transfer and calibration of attribution masses. Author approval and declarations remain open. B01 is separate and still running; no partial outcome is used here.')]
    pdfmetrics.registerFont(TTFont('BriefArial','C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('BriefArialBold','C:/Windows/Fonts/arialbd.ttf'))
    body=ParagraphStyle('body',fontName='BriefArial',fontSize=9.3,leading=11.4,spaceAfter=4)
    head=ParagraphStyle('head',fontName='BriefArialBold',fontSize=10,leading=12,textColor=colors.HexColor('#125570'),spaceBefore=6,spaceAfter=3)
    small=ParagraphStyle('small',parent=body,fontSize=8.2,leading=10)
    title=ParagraphStyle('title',fontName='BriefArialBold',fontSize=16,leading=19,spaceAfter=5)
    stamp=datetime.now(ZoneInfo('America/Bogota')).strftime('%d %b %Y, %H:%M Colombia')
    story=[Paragraph('P07 | Contribution, evidence and limits',title),Paragraph('For David Celeita and Masoud Barati | Review draft | '+stamp,small)]
    md=['# P07: contribution, evidence and limits','','Review draft | '+stamp,'']
    for heading,text in sections:
        story.append(Paragraph(heading,head));md+=['## '+heading,'']
        if text:story.append(Paragraph(text,body));md += [text,'']
        else:
            tab=Table([[Paragraph(str(v),small) for v in row] for row in rows],colWidths=[220,180,112]);tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7f0f3')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
            story += [tab,Spacer(1,3),Paragraph('108 interventions replayed under three network conditions and two noise levels; 18 event parents, not 648 independent experiments. Unequal alarm operating points.',small)]
            md += ['| '+' | '.join(rows[0])+' |','|---|---|---|']+['| '+' | '.join(row)+' |' for row in rows[1:]]+['']
    SimpleDocTemplate(str(OUT),pagesize=(595.28,841.89),leftMargin=41.6,rightMargin=41.6,topMargin=28,bottomMargin=25,title='P07: contribution, evidence and limits').build(story)
    with pymupdf.open(OUT) as doc:assert len(doc)==1
    (ROOT/'docs/P07_COAUTHOR_BRIEF.md').write_text('\n'.join(md),encoding='utf-8')
    files=[OUT,C01/'SUMMARY.csv',aroot/'SUMMARY.csv',ROOT/'generated/monitored_exposure_audit.json']
    (ROOT/'docs/P07_COAUTHOR_BRIEF_MANIFEST.json').write_text(json.dumps({'state':'COMPLETE_EVIDENCE_REVIEW_DRAFT_NOT_SUBMISSION_READY','sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2)+'\n')
    print('COAUTHOR_BRIEF_ONE_PAGE_COMPLETE_EVIDENCE')


if __name__=='__main__':main()
