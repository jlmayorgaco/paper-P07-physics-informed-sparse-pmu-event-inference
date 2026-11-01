from pathlib import Path
import json,re,unicodedata
P=Path(__file__).resolve().parents[2]; T=P/'.aris/traces/citation-audit/20261101_run01'
E=json.loads((P/'.aris/citation-audit/input_manifest.json').read_text(encoding='utf-8'))['entries']
def norm(s):
    s=re.sub(r'<[^>]+>','',s);s=s.replace('\\&','and').replace('&','and').replace('\\ss','ss')
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
    return re.sub('[^a-z0-9]','',s.lower())
for e in E:
    r=json.loads((T/(e['key']+'.lookup.json')).read_text(encoding='utf-8'));c=r.get('crossref'); f=e['fields']
    if not c: print(e['key'],'NO_CROSSREF');continue
    diffs=[]
    for bf,cf in [('title','title'),('journal','container-title'),('booktitle','container-title'),('volume','volume'),('number','issue'),('pages','page')]:
        b=f.get(bf);v=c.get(cf);v=v[0] if isinstance(v,list) and v else v
        if b and v and norm(b)!=norm(str(v)):diffs.append(f'{bf}: BIB={b} CANONICAL={v}')
    dates={k:v['date-parts'] for k,v in c.items() if k in ['published','published-print','published-online','issued']}
    years={str(v[0][0]) for v in dates.values()}
    if f.get('year') not in years:diffs.append('year: '+f.get('year','')+' CANONICAL '+str(dates))
    authors='; '.join(a.get('given','')+' '+a.get('family','') for a in c.get('author',[]))
    print('\n'+e['key']+' '+('CITED' if e['uses'] else 'UNUSED')+' '+('; '.join(diffs) or 'TITLE/VENUE/YEAR/PAGES match'))
    print('BIB AUTHORS: '+f.get('author',''))
    print('CANONICAL AUTHORS: '+authors)
    if e['uses'] and c.get('abstract'):print('ABSTRACT: '+re.sub(r'<[^>]+>','',c['abstract'])[:2500])
