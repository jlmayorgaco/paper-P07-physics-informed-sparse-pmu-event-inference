"""Enforce the user's retention contract for the event and IEEE-39 figures."""
from pathlib import Path
import argparse, hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'figures/frozen/PROTECTED_FIGURES.json'
REQUIRED={
    'fig:reference-event-types':'figures/generated/event_signatures.pdf',
    'fig:narrative-topology':'figures/generated/narrative_topology.pdf',
}

def without_comments(text):
    return '\n'.join(re.split(r'(?<!\\)%',line,maxsplit=1)[0] for line in text.splitlines())

def active_source(path,seen=None):
    seen=set() if seen is None else seen
    path=path.resolve()
    if path in seen:return ''
    seen.add(path);text=without_comments(path.read_text(encoding='utf-8-sig'))
    for name in re.findall(r'\\(?:input|include)\{([^}]+)\}',text):
        target=ROOT/name
        if not target.suffix:target=target.with_suffix('.tex')
        if target.is_file():text+='\n'+active_source(target,seen)
    return text

def verify(pdf_path=None):
    contract=json.loads(MANIFEST.read_text())
    for name,expected in contract['files'].items():
        path=ROOT/name
        if not path.is_file():raise RuntimeError('Protected recovery file missing: '+name)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('Protected file changed; restore it, do not reset the hash: '+name)
    source=active_source(ROOT/'main.tex')
    floats=re.findall(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}',source,re.S)
    for label,asset in REQUIRED.items():
        matches=[f for f in floats if r'\label{'+label+'}' in f]
        if len(matches)!=1:raise RuntimeError('Required figure was removed or duplicated: '+label)
        if not re.search(r'\\includegraphics(?:\[[^]]*\])?\{'+re.escape(asset)+r'\}',matches[0]):
            raise RuntimeError('Required figure is no longer visibly included: '+label)
        if not (ROOT/asset).is_file():raise RuntimeError('Required figure asset missing: '+asset)
    if not (ROOT/'figures/ieee39_single_line.tex').is_file():
        raise RuntimeError('Editable IEEE-39 TikZ must remain available')
    result={'protected_hashes_verified':len(contract['files']),
            'both_figures_in_active_article_source':True}
    if pdf_path:
        import pymupdf
        pdf_path=Path(pdf_path)
        if not pdf_path.is_absolute():pdf_path=ROOT/pdf_path
        with pymupdf.open(pdf_path) as pdf:
            text=[' '.join(p.get_text().split()) for p in pdf]
            events=[i for i,t in enumerate(text) if 'Representative signatures from the archived RAW0001' in t]
            topology=[i for i,t in enumerate(text) if 'IEEE 39-bus single-line diagram' in t]
            assert len(events)==len(topology)==1,'Protected figure caption absent from compiled article'
            assert 'FIGURE 2.' in text[events[0]],'The protected event figure must remain Figure 2'
            assert all(s in text[topology[0]] for s in ['PMU voltage bus','Transformer','Candidate line opening']),\
                'IEEE-39 drawing content absent from compiled page'
            assert len(pdf[topology[0]].get_drawings())>=100,'IEEE-39 vector content absent'
            result.update(article_pages=len(pdf),event_figure_page=events[0]+1,
                          ieee39_figure_page=topology[0]+1,both_figures_in_compiled_pdf=True)
        aux=pdf_path.with_suffix('.aux')
        if aux.is_file():
            text=aux.read_text(errors='replace')
            assert r'\newlabel{fig:reference-event-types}{{2}' in text,'Event figure label changed'
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pdf',type=Path)
    verify(parser.parse_args().pdf)
