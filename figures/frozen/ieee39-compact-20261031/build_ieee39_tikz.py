"""Planar, editable IEEE-39 TikZ diagram. All dimensions are schematic cm."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
# Compact physical coordinates; font sizes are NOT scaled down with the network.
XS, YS = .55, .50
# Busbars: left, right, height. Branches use distinct, deliberate taps.
BARS={
1:(.9,2.2,9.6),2:(.9,3.6,11.8),3:(3,4.5,9.6),4:(3,4.5,7.4),
5:(1.8,4.5,6.3),6:(3,5.3,5.2),7:(2.3,3.7,4.1),8:(1.6,3.1,2.9),
9:(.9,2.2,1.8),10:(5.8,8.1,2.9),11:(4.8,6.2,4.1),12:(5.5,7.4,5.2),
13:(6.6,8.1,4.1),14:(6.6,8.1,7.4),15:(7.4,8.8,8.5),16:(7.4,10.9,9.6),
17:(6.6,8.1,10.7),18:(3.7,5.1,10.7),19:(9.1,11.8,5.2),20:(8.6,9.9,4.1),
21:(9.9,11.2,8.5),22:(12,13.4,8.5),23:(12.7,14.1,5.2),24:(10.2,11.6,11.8),
25:(3,5.3,13),26:(6.7,8.8,13),27:(7.4,8.8,11.8),28:(9.5,10.9,13),
29:(13.6,15.3,13),30:(1.2,2.6,13),31:(3.7,5.1,2.9),32:(6.6,8.1,1.8),
33:(10.8,12.1,2.9),34:(9.1,10.5,2.9),35:(12,13.4,9.6),36:(12.7,14.1,4.1),
37:(3,4.4,14.1),38:(14.1,15.5,11.8),39:(.2,1.55,7.4)}
# Explicit electrical routes. No auto-layout and no white crossing masks.
ROUTES={
(1,2):[(1.9,9.6),(1.9,11.8)],
(1,39):[(1.15,9.6),(1.15,7.4)],
(2,3):[(3.35,11.8),(3.35,9.6)],
(2,25):[(2.7,11.8),(2.7,12.45),(3.25,12.45),(3.25,13)],
(2,30):[(1.9,11.8),(1.9,13)],
(3,4):[(3.35,9.6),(3.35,7.4)],
(3,18):[(4.1,9.6),(4.1,10.7)],
(4,5):[(3.35,7.4),(3.35,6.3)],
(4,14):[(4.15,7.4),(4.15,7.95),(6.95,7.95),(6.95,7.4)],
(5,6):[(3.35,6.3),(3.35,5.2)],
(5,8):[(2.1,6.3),(2.1,2.9)],
(6,7):[(3.35,5.2),(3.35,4.1)],
(6,11):[(5,5.2),(5,4.65),(5.7,4.65),(5.7,4.1)],
(6,31):[(4.35,5.2),(4.35,2.9)],
(7,8):[(2.65,4.1),(2.65,2.9)],
(8,9):[(1.85,2.9),(1.85,1.8)],
(9,39):[(1.15,1.8),(1.15,7.4)],
(10,11):[(5.95,2.9),(5.95,4.1)],
(10,13):[(7.75,2.9),(7.75,4.1)],
(10,32):[(7.15,2.9),(7.15,1.8)],
(12,11):[(5.95,5.2),(5.95,4.1)],
(12,13):[(7.25,5.2),(7.25,4.1)],
(13,14):[(7.75,4.1),(7.75,7.4)],
(14,15):[(7.75,7.4),(7.75,8.5)],
(15,16):[(7.75,8.5),(7.75,9.6)],
(16,17):[(7.75,9.6),(7.75,10.7)],
(16,19):[(9.45,9.6),(9.45,5.2)],
(16,21):[(10.25,9.6),(10.25,8.5)],
(16,24):[(10.7,9.6),(10.7,11.8)],
(17,18):[(6.95,10.7),(6.95,11.25),(4.8,11.25),(4.8,10.7)],
(17,27):[(7.75,10.7),(7.75,11.8)],
(19,20):[(9.45,5.2),(9.45,4.1)],
(19,33):[(11.4,5.2),(11.4,2.9)],
(20,34):[(9.45,4.1),(9.45,2.9)],
(21,22):[(10.7,8.5),(10.7,9.05),(12.5,9.05),(12.5,8.5)],
(22,23):[(13.1,8.5),(13.1,5.2)],
(22,35):[(13.1,8.5),(13.1,9.6)],
(23,24):[(13.8,5.2),(13.8,11.25),(11.4,11.25),(11.4,11.8)],
(23,36):[(13.1,5.2),(13.1,4.1)],
(25,26):[(4.95,13),(4.95,12.45),(7.1,12.45),(7.1,13)],
(25,37):[(3.55,13),(3.55,14.1)],
(26,27):[(7.75,13),(7.75,11.8)],
(26,28):[(8.45,13),(8.45,13.55),(9.85,13.55),(9.85,13)],
(26,29):[(8.05,13),(8.05,14.1),(14.6,14.1),(14.6,13)],
(28,29):[(10.55,13),(10.55,13.55),(14.25,13.55),(14.25,13)],
(29,38):[(15,13),(15,11.8)]}
GENERATORS={30:(1.9,14),31:(4.35,1.95),32:(7.15,.8),33:(11.4,1.95),
34:(9.45,1.95),35:(13.1,10.55),36:(13.1,3.15),37:(3.55,15.05),
38:(15,10.85),39:(.5,8.35)}
# Load x-coordinate and direction. Inventory is independently checked.
LOADS={3:(4.3,-1),4:(4.3,-1),7:(3.05,-1),8:(2.95,-1),12:(6.5,1),
15:(8.4,-1),16:(8.65,-1),18:(4.8,-1),20:(8.9,-1),21:(10.7,-1),
23:(13.8,-1),24:(10.35,-1),25:(4.25,-1),26:(7.1,1),27:(8.45,-1),
28:(10.2,-1),29:(14.95,1),31:(4.85,-1),39:(.45,-1)}
LABELS={2:(1.02,12.06),6:(3.03,5.46),10:(6.35,3.16),11:(4.86,4.36),
12:(5.5,5.46),13:(6.6,4.36),14:(6.6,7.14),15:(8.05,8.76),16:(8.6,9.86),
17:(6.6,10.44),19:(10.5,5.46),20:(8.6,4.36),21:(9.93,8.24),
22:(12,8.76),23:(13.3,5.46),24:(10.95,12.06),26:(6.57,13.26),
27:(8.1,12.06),28:(9.5,12.74),29:(13.6,12.74),30:(1.2,13.26),
31:(3.7,3.16),32:(6.6,1.54),33:(11.65,3.16),34:(9.75,3.16),
35:(12,9.86),36:(13.45,4.36),37:(3.9,14.36),38:(14.1,12.06),39:(.68,7.66)}
LABELS.update({9:(.7,2.12),10:(6.15,3.16),13:(6.4,4.36),22:(11.83,8.82),
               23:(13.25,5.5),25:(2.8,13.32),26:(6.5,13.32),
               31:(3.5,3.22),32:(6.5,1.48),39:(.56,7.72)})
LABELS={n:(LABELS.get(n,(l,y+.32))[0],y+(.42 if LABELS.get(n,(l,y+.32))[1]>y else -.42))
        for n,(l,r,y) in BARS.items()}
LABELS.update({11:(4.86,3.68),22:(11.85,8.08),30:(.95,13.42),
               32:(6.2,1.38),36:(14.15,4.52),38:(14.1,11.38),39:(1.35,7.82)})
PMU_BADGES={2:(3.5,12.16),5:(3.95,6.66),6:(5.05,5.56),10:(7.08,3.26),
19:(11.5,5.56),22:(12.75,8.12),29:(14.42,12.64),39:(.1,7.02)}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def point(p): return f'({p[0]:g},{p[1]:g})'
def on_segment(p,a,b):
    return all(min(a[k],b[k])-1e-8<=p[k]<=max(a[k],b[k])+1e-8 for k in (0,1))
def intersection(a,b,c,d):
    av=abs(a[0]-b[0])<1e-8;cv=abs(c[0]-d[0])<1e-8
    if av!=cv:
        p=(a[0],c[1]) if av else (c[0],a[1])
        return p if on_segment(p,a,b) and on_segment(p,c,d) else None
    fixed,free=(0,1) if av else (1,0)
    if abs(a[fixed]-c[fixed])>1e-8: return None
    lo=max(min(a[free],b[free]),min(c[free],d[free]))
    hi=min(max(a[free],b[free]),max(c[free],d[free]))
    if hi<lo-1e-8:return None
    if hi-lo>1e-8:return 'overlap'
    return (a[0],lo) if av else (lo,a[1])
def on_bus(p,n):
    l,r,y=BARS[n]
    return abs(p[1]-y)<1e-8 and l<=p[0]<=r

def audit_geometry(branches,buses,pmus):
    expected={frozenset((int(b['src_bus']),int(b['dst_bus']))) for b in branches}
    assert expected=={frozenset(k) for k in ROUTES},'Frozen branch set changed'
    assert len(ROUTES)==len(branches)==46 and set(BARS)==set(range(1,40))
    assert {int(b['bus']) for b in buses if b['has_gen']=='true'}==set(GENERATORS)
    assert {int(b['bus']) for b in buses if b['has_load']=='true'}==set(LOADS)
    assert set(pmus)==set(PMU_BADGES)=={2,5,6,10,19,22,29,39}
    segments=[]
    for (i,j),pts in ROUTES.items():
        assert on_bus(pts[0],i) and on_bus(pts[-1],j),(i,j,'terminal')
        for a,b in zip(pts,pts[1:]):
            assert (a[0]==b[0])!=(a[1]==b[1]),(i,j,'nonorthogonal')
            segments.append((a,b,(i,j)))
            for n,(l,r,y) in BARS.items():
                hit=intersection(a,b,(l,y),(r,y))
                if hit is not None:
                    assert hit!='overlap' and ((n==i and hit==pts[0]) or
                        (n==j and hit==pts[-1])),(i,j,'unrelated bar',n,hit)
    for k,(a,b,edge) in enumerate(segments):
        for c,d,other in segments[k+1:]:
            if edge==other:continue
            hit=intersection(a,b,c,d)
            if hit is not None:
                assert hit!='overlap' and any(on_bus(hit,n) for n in set(edge)&set(other)),(
                    'wire crossing/overlap',edge,other,hit)
    devices=[]
    for n,(x,y) in GENERATORS.items():
        by=BARS[n][2];end=y+(.34 if by>y else -.34)
        devices.append((n,(x,by),(x,end),'generator'))
    for n,(x,dr) in LOADS.items():
        by=BARS[n][2];devices.append((n,(x,by),(x,by+dr*.58),'load'))
    for n,a,b,kind in devices:
        assert on_bus(a,n)
        for c,d,edge in segments:
            hit=intersection(a,b,c,d)
            assert hit is None or (hit!='overlap' and hit==a and n in edge),(
                kind,n,'crosses branch',edge,hit)
        for m,(l,r,y) in BARS.items():
            hit=intersection(a,b,(l,y),(r,y))
            assert hit is None or (m==n and hit==a),(kind,n,'crosses bus',m)
    return dict(buses=39,branches=46,branch_segments=len(segments),orthogonal_routes=46,
        wire_crossings=0,wire_overlaps=0,unintended_bus_contacts=0,device_wire_crossings=0)

def write_tikz(root,branches,assets):
    selected={frozenset((a['i'],a['j'])) for a in assets if a['family']=='line'}
    loads={a['bus'] for a in assets if a['family']=='load'}
    lines=[r'% Generated by scripts/build_ieee39_tikz.py. Editable vector LaTeX.',
r'% All 46 branches use orthogonal routes without crossings or shared wire segments.',
r'% P badges identify voltage buses, not the separate oriented current terminals.',
r'\begingroup',
r'\definecolor{SLDblue}{RGB}{0,104,164}',
r'\definecolor{SLDorange}{RGB}{184,76,0}',
r'\begin{tikzpicture}[x=.55cm,y=.50cm,font=\sffamily\fontsize{7}{8}\selectfont,',
r'wire/.style={draw=black!88,line width=.50pt,line cap=butt,line join=miter},',
r'candidate/.style={wire,draw=SLDorange,line width=.65pt},',
r'busbar/.style={draw=black,line width=1.2pt,line cap=butt},',
r'measured/.style={busbar,draw=SLDblue,line width=1.45pt},',
r'number/.style={anchor=west,inner sep=0pt},',
r'badge/.style={draw=SLDblue,text=SLDblue,fill=SLDblue!5,line width=.55pt,',
r'minimum width=.20cm,minimum height=.20cm,inner sep=0pt,font=\sffamily\bfseries\fontsize{5}{6}\selectfont},',
r'load/.style={wire,-{Triangle[length=2.5pt,width=2.4pt]},draw=black!65},',
r'legend/.style={anchor=west,inner sep=0pt,font=\sffamily\fontsize{6.5}{7}\selectfont}]',
r'% Transmission branches and transformer connections.']
    for row in branches:
        edge=(int(row['src_bus']),int(row['dst_bus']));pts=ROUTES[edge]
        style='candidate' if frozenset(edge) in selected else 'wire'
        lines += [f'% Branch {edge[0]}--{edge[1]}',r'\draw['+style+'] '+' -- '.join(map(point,pts))+';']
        if int(row['transformer']):
            assert len(pts)==2 and pts[0][0]==pts[1][0]
            x=pts[0][0];y=3.5 if edge==(6,31) else (pts[0][1]+pts[1][1])/2
            lines += [f'\\fill[white] {point((x-.17,y-.27))} rectangle {point((x+.17,y+.27))};',
                f'\\draw[wire] {point((x,y-.10))} circle[radius=.085cm];',
                f'\\draw[wire] {point((x,y+.10))} circle[radius=.085cm];']
    lines += ['% Generators use the conventional G and sine-in-circle symbol.']
    for n,(x,y) in GENERATORS.items():
        by=BARS[n][2];end=y+(.34 if by>y else -.34)
        lines += [f'\\draw[wire] {point((x,by))} -- {point((x,end))};',
            f'\\draw[wire,fill=white] {point((x,y))} circle[radius=.17cm];',
            f'\\node[inner sep=0pt,font=\\sffamily\\fontsize{{5.5}}{{6}}\\selectfont] at {point((x,y+.11))} {{G}};',
            f'\\draw[wire,shift={{{point((x,y-.17))}}}] plot[domain=-.18:.18,samples=25] (\\x,{{.045*sin(1000*\\x)}});']
    lines += ['% Connected loads, with candidate interventions in orange.']
    for n,(x,dr) in LOADS.items():
        y=BARS[n][2];style='load,draw=SLDorange,line width=.65pt' if n in loads else 'load'
        lines += [f'\\draw[{style}] {point((x,y))} -- {point((x,y+dr*.58))};']
    lines += ['% Busbars and labels. Labels have no opaque masks.']
    for n,(l,r,y) in sorted(BARS.items()):
        style='measured' if n in PMU_BADGES else 'busbar';lp=LABELS.get(n,(l,y+.32))
        lines += [f'\\draw[{style}] {point((l,y))} -- {point((r,y))};',
            f'\\node[number] at {point(lp)} {{{n}}};']
    for n,p in PMU_BADGES.items():lines += [f'% PMU voltage bus {n}',f'\\node[badge] at {point(p)} {{P}};']
    lines += [
r'% Legend, kept outside all electrical routes.',
r'\draw[black!20,line width=.35pt] (.2,.12) -- (15.5,.12);',
r'\begin{scope}[x=1cm,y=1cm]',
r'\draw[measured] (.2,-.20) -- (.55,-.20);',
r'\node[badge] at (.72,-.20) {P};',
r'\node[legend] at (.93,-.20) {PMU voltage bus};',
r'\draw[wire] (4.8,-.20) circle[radius=.085cm];',
r'\draw[wire] (4.9,-.20) circle[radius=.085cm];',
r'\node[legend] at (5.18,-.20) {Transformer};',
r'\draw[candidate] (.2,-.59) -- (.72,-.59);',
r'\node[legend] at (.93,-.59) {Candidate line opening};',
r'\draw[load,draw=SLDorange,line width=.65pt] (4.85,-.44) -- (4.85,-.74);',
r'\node[legend] at (5.18,-.59) {Candidate load change};',
r'\end{scope}',
r'\end{tikzpicture}',r'\endgroup','']
    (root/'figures/ieee39_single_line.tex').write_text('\n'.join(lines),encoding='utf-8')

def audit_pdf(page, branches):
    """Check actual rendered glyph bounds against wires and device envelopes."""
    import pymupdf
    sx=XS*72/2.54;sy=YS*72/2.54
    bus=next(d for d in page.get_drawings()
             if abs(d['rect'].width-3.5*sx)<.1 and d['rect'].height<.01)
    ox=bus['rect'].x0-7.4*sx;oy=bus['rect'].y0+9.6*sy
    def rect(a,b,pad=.3):
        r=pymupdf.Rect(ox+min(a[0],b[0])*sx,oy-max(a[1],b[1])*sy,
                       ox+max(a[0],b[0])*sx,oy-min(a[1],b[1])*sy)
        return r+(-pad,-pad,pad,pad)
    objects=[]
    for edge,pts in ROUTES.items():
        objects += [(str(edge),rect(a,b)) for a,b in zip(pts,pts[1:])]
    for n,(l,r,y) in BARS.items():objects.append((f'bus {n}',rect((l,y),(r,y),.75)))
    for n,(x,y) in GENERATORS.items():
        by=BARS[n][2]
        objects += [(f'generator lead {n}',rect((x,by),(x,y+(.34 if by>y else -.34)))),
                    (f'generator {n}',rect((x-.17/XS,y-.17/YS),(x+.17/XS,y+.17/YS)))]
    for n,(x,dr) in LOADS.items():
        y=BARS[n][2];objects.append((f'load {n}',rect((x,y),(x,y+dr*.58))))
    for row in branches:
        if not int(row['transformer']):continue
        edge=(int(row['src_bus']),int(row['dst_bus']));pts=ROUTES[edge]
        x=pts[0][0];y=3.5 if edge==(6,31) else (pts[0][1]+pts[1][1])/2
        objects.append((f'transformer {edge}',rect((x-.085/XS,y-.27),(x+.085/XS,y+.27))))
    numbers=[w for w in page.get_text('words') if w[4].isdigit()]
    assert sorted(int(w[4]) for w in numbers)==list(range(1,40))
    labels=[(w[4],pymupdf.Rect(w[:4])+(-.3,-.3,.3,.3)) for w in numbers]
    labels += [(f'PMU {n}',rect((x-.1/XS,y-.1/YS),(x+.1/XS,y+.1/YS),.3))
               for n,(x,y) in PMU_BADGES.items()]
    for name,box in labels:
        for other,ob in objects:
            assert not box.intersects(ob),(name,'rendered label overlaps',other)
    for i,(name,box) in enumerate(labels):
        for other,ob in labels[i+1:]:
            assert not box.intersects(ob),(name,'rendered label overlaps',other)
    return dict(rendered_bus_labels=39,rendered_pmu_badges=8,label_wire_device_overlaps=0,
                label_label_overlaps=0,minimum_tested_label_clearance_pt=.3,
                nominal_bus_font_pt=7,layout='compact single-column')

def render(root=ROOT):
    root=Path(root);source=root/'figures/source/ieee39_single_line'
    provenance=json.loads((source/'PROVENANCE.json').read_text())
    for name,record in provenance['files'].items():
        assert digest(source/name)==record['sha256'],f'Source hash mismatch: {name}'
    def rows(name):
        with (source/name).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
    branches=rows('branch.csv');buses=rows('bus.csv');terminals=rows('terminal_mapping.csv')
    assets=json.loads((source/'assets.json').read_text());pmus=sorted(int(r['pmu_bus']) for r in terminals)
    audit=audit_geometry(branches,buses,pmus)
    audit.update(transformers=sum(int(r['transformer']) for r in branches),
        generators=sorted(GENERATORS),pmu_voltage_buses=pmus,nominal_load_connections=sorted(LOADS),
        load_candidates=sorted(a['bus'] for a in assets if a['family']=='load'),
        line_candidates=[[a['i'],a['j']] for a in assets if a['family']=='line'],
        electrical_parameters_changed=False,measurement_mapping_changed=False,
        source_hashes_verified=True,renderer='pdfLaTeX / PGF-TikZ')
    assert audit['transformers']==12
    write_tikz(root,branches,assets)
    build=root/'build/ieee39_review';build.mkdir(parents=True,exist_ok=True)
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-recorder',
        f'-output-directory={build}','main.tex'],cwd=root/'figures/ieee39',text=True,capture_output=True)
    (build/'compile_stdout.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(result.stdout[-5000:])
    out=root/'figures/generated';out.mkdir(exist_ok=True)
    shutil.copy2(build/'main.pdf',out/'narrative_topology.pdf')
    import pymupdf
    with pymupdf.open(out/'narrative_topology.pdf') as pdf:
        assert len(pdf)==1 and not pdf[0].get_images(),'Expected one vector-only page'
        audit.update(audit_pdf(pdf[0],branches))
        pdf[0].get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False).save(out/'narrative_topology.png')
        audit['pdf_size_pt']=list(pdf[0].rect)[2:];audit['embedded_raster_images']=0
        (build/'text_bounds.json').write_text(json.dumps(pdf[0].get_text('words'),indent=2))
    audit['tikz_sha256']=digest(root/'figures/ieee39_single_line.tex')
    (root/'generated/single_line_topology_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
if __name__=='__main__':render()
