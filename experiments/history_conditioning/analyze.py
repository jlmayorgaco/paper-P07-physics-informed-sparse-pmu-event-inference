import json, numpy as np
M=["N","Q","R1","F","M","QA"]; rng=np.random.default_rng(0)
def boot(d,n=4000):
    m=[d[rng.integers(0,len(d),len(d))].mean() for _ in range(n)]; return np.percentile(m,[2.5,97.5])
out={}
for c in range(1,11):
    d=json.load(open(f'results/ROWS_cell{c}.json')); rows=d['rows']; mt=d['meta']
    acc={k:np.array([r['res'][k]['top']==r['c'] for r in rows],float) for k in M}
    nll={k:np.array([r['res'][k]['nll'] for r in rows]) for k in M}
    print(f"C{c} noise x{mt['scale']:g} hist {mt['th'] if mt['th']<9 else 'full'}s mism {mt['mism']} W {mt['W']}  n={len(rows)}")
    print("   acc: "+"  ".join(f"{k} {acc[k].mean():.3f}" for k in M)+"   nll(F) %.3f"%nll['F'].mean())
    cmp={}
    for a,b in (("M","F"),("F","N"),("R1","F"),("Q","N"),("M","QA")):
        da=acc[a]-acc[b]; dn=nll[a]-nll[b]; lo,hi=boot(da); nlo,nhi=boot(dn)
        cmp[f"{a}-{b}"]=dict(dacc=float(da.mean()),ci=[float(lo),float(hi)],dnll=float(dn.mean()),nci=[float(nlo),float(nhi)])
        print(f"   {a}-{b}: dacc {da.mean():+.3f} [{lo:+.3f},{hi:+.3f}]  dnll {dn.mean():+.4f} [{nlo:+.4f},{nhi:+.4f}]")
    cost={k:float(np.mean([r['cost'][k] for r in rows])*1000) for k in M}
    cert={}
    for k in ("N","Q","R1"):
        cz=np.array([r['cert'][k]['certified'] for r in rows]); fl=np.array([r['res'][k]['top']!=r['res']['F']['top'] for r in rows])
        cert[k]=dict(certified=float(cz.mean()),flips_certified=int((fl&cz).sum()),flips_total=int(fl.sum()))
    print("   cost ms:", {k:round(v,1) for k,v in cost.items()}, " cert:", cert)
    out[f"C{c}"]=dict(meta=mt,acc={k:float(acc[k].mean()) for k in M},nll={k:float(nll[k].mean()) for k in M},cmp=cmp,cost=cost,cert=cert,
        A_err=float(np.mean([abs(r['A']-r['A_hat']) for r in rows])), sd=float(np.mean([np.sqrt(r['P_A']) for r in rows])))
json.dump(out,open('results/TEST_RESULTS.json','w'),indent=1,default=float)
