import json,sys,numpy as np
for t in sys.argv[1:]:
    d=json.load(open(f'results/{t}/ROWS.json'));rows=d['rows']
    acc={k:np.mean([r['res'][k]['top']==r['c'] for r in rows]) for k in ('N','Q','R1','F','M','QA')}
    ae=np.mean([abs(r['A_hat']-r['A']) for r in rows])
    print(t,len(rows),{k:round(v,3) for k,v in acc.items()},'Aerr',round(ae,4))
