from pathlib import Path
import json,urllib.request,urllib.parse,time,datetime
P=Path(__file__).resolve().parents[2]; T=P/'.aris/traces/citation-audit/20261101_run01'
entries=json.loads((P/'.aris/citation-audit/input_manifest.json').read_text(encoding='utf-8'))['entries']
for e in entries:
    path=T/(e['key']+'.lookup.json'); r=json.loads(path.read_text(encoding='utf-8'))
    if 'crossref' in r or 'doi' not in e['fields']:continue
    url='https://api.crossref.org/works/'+e['fields']['doi']
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
        with urllib.request.urlopen(req,timeout=12) as resp:m=json.load(resp)['message']
        r['crossref']=m;r['requests'].append({'url':url,'status':'success','retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        print(e['key'],'FETCHED',flush=True)
    except Exception as ex:
        r['requests'].append({'url':url,'status':'error','error':str(ex)});print(e['key'],str(ex),flush=True)
    path.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8');time.sleep(0.7)
