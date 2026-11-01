from pathlib import Path
import re,json,hashlib,urllib.request,urllib.parse,concurrent.futures,datetime

P=Path(__file__).resolve().parents[2]
O=P/'.aris/citation-audit'; O.mkdir(parents=True,exist_ok=True)
trace=P/'.aris/traces/citation-audit/20261101_run01'; trace.mkdir(parents=True,exist_ok=True)
def bibparse(text):
    records=[]
    for m in re.finditer(r'@(\w+)\s*\{\s*([^,]+),',text):
        i=m.end(); start=i; depth=1
        while depth and i<len(text):
            if text[i]=='{': depth+=1
            if text[i]=='}': depth-=1
            i+=1
        body=text[start:i-1]; fields={}
        for f in re.finditer(r'(\w+)\s*=\s*\{',body):
            j=f.end(); st=j; dep=1
            while dep and j<len(body):
                if body[j]=='{': dep+=1
                if body[j]=='}': dep-=1
                j+=1
            fields[f.group(1).lower()]=body[st:j-1]
        records.append({'key':m.group(2).strip(),'type':m.group(1),'fields':fields,'bib':text[m.start():i]})
    return records
seen={}; contexts=[]
def visit(rel):
    path=P/rel
    if not path.suffix:path=path.with_suffix('.tex')
    if not path.exists(): return
    rel=path.relative_to(P).as_posix()
    if rel in seen:return
    raw=path.read_text(encoding='utf-8-sig'); seen[rel]=hashlib.sha256(path.read_bytes()).hexdigest()
    text=re.sub(r'(?<!\\)%[^\n]*',lambda m:' '*len(m.group()),raw)
    for m in re.finditer(r'\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}',text):
        begin=text.rfind('\n\n',0,m.start())+2
        end=text.find('\n\n',m.end())
        if end<0:end=len(text)
        passage=text[begin:end].strip()
        for key in m.group(1).split(','):
            contexts.append({'key':key.strip(),'file':rel,'line':text[:m.start()].count('\n')+1,'context':passage})
    for m in re.finditer(r'\\(?:input|include)\{([^}]+)\}',text):visit(m.group(1))
visit('main.tex'); visit('supplement.tex')
entries=bibparse((P/'references.bib').read_text(encoding='utf-8-sig'))
keys={e['key'] for e in entries}
for e in entries:e['uses']=[c for c in contexts if c['key']==e['key']]
entries.sort(key=lambda e:(not bool(e['uses']),e['key']))
context_text='\n\n'.join(f"KEY: {c['key']}\nLOCATION: {c['file']}:{c['line']}\nCONTEXT:\n{c['context']}" for c in contexts)+'\n'
(O/'contexts.txt').write_text(context_text,encoding='utf-8')
seen['references.bib']=hashlib.sha256((P/'references.bib').read_bytes()).hexdigest()
seen['.aris/citation-audit/contexts.txt']=hashlib.sha256((O/'contexts.txt').read_bytes()).hexdigest()
manifest={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':entries,'input_hashes':{k:'sha256:'+v for k,v in seen.items()},'missing_citations':sorted({c['key'] for c in contexts}-keys),'context_count':len(contexts)}
(O/'input_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'entries':len(entries),'cited_entries':sum(bool(e['uses']) for e in entries),'contexts':len(contexts),'dependency_files':len(seen)-2,'missing_citations':manifest['missing_citations']}))

def get(url,accept='application/json'):
    req=urllib.request.Request(url,headers={'User-Agent':'CitationAudit/1.0 (research bibliography verification)','Accept':accept})
    with urllib.request.urlopen(req,timeout=35) as resp:return resp.read().decode('utf-8'),resp.geturl()
def lookup(e):
    key=e['key']; f=e['fields']; result={'key':key,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requests':[]}
    doi=f.get('doi')
    if doi:
        url='https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='')
        try:
            body,resolved=get(url); msg=json.loads(body)['message']; result['crossref']=msg; result['requests'].append({'url':url,'status':'success','resolved':resolved})
        except Exception as ex:result['requests'].append({'url':url,'status':'error','error':str(ex)})
    else:result['requests'].append({'status':'manual_web_lookup_required'})
    (trace/(key+'.lookup.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return key,'crossref' in result
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    for key,ok in ex.map(lookup,entries):print(key, 'FETCHED' if ok else 'NEEDS_FALLBACK',flush=True)
