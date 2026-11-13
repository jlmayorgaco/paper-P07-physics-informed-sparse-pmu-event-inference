"""Independent recount of the sealed nominal diagnostic; no inference rerun."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.stats import chi2

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'experiments/adaptive_innovation_20261113'
R=D/'run'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def publications(score,source,h,p):
    # Alternative implementation: consecutive-run index, then refractory skip.
    above=score>=h; out=[]; k=p['startup_reports']; streak=0
    while k<len(score):
        streak=streak+1 if above[k] else 0
        if streak==p['confirmation_reports']:
            out.append((k/30,int(source[k])))
            k+=p['refractory_reports'];streak=0
        else:k+=1
    return out
def main():
    p=read(D/'protocol.json');seal=read(R/'COMPLETE.json')
    assert seal['status']=='COMPLETE'
    for name,h in seal['files'].items():assert sha(R/name)==h,name
    frozen=read(R/'EXECUTION_FREEZE.json')
    assert frozen['code_sha256']==sha(D/'study.py')
    assert frozen['protocol_sha256']==sha(D/'protocol.json')
    assert p['snapshot_sha256']==sha(D.parent/'channel_information_20261112/input_snapshot.npz')
    assert read(R/'TEST_STARTED.json')['cal_selection_sha256']==sha(R/'CAL_SELECTION.json')
    selection=read(R/'CAL_SELECTION.json');counts=np.zeros((3,len(p['threshold_grid'])),int)
    files=list(R.glob('CAL_normal_[0-9][0-9][0-9].npz'));assert len(files)==36
    for f in files:
        with np.load(f) as z:
            assert z['score'].shape==(3,18000) and np.isfinite(z['score']).all()
            for a in range(3):
                for j,h in enumerate(p['threshold_grid']):counts[a,j]+=len(publications(z['score'][a],z['source'][a],h,p))
    assert np.array_equal(counts,selection['counts'])
    exposure=36*(600-12)/3600;assert np.isclose(selection['normal_hours'],exposure)
    for a in range(3):
        ok=np.flatnonzero(counts[a]/exposure<=1)
        assert selection['thresholds'][a]==(p['threshold_grid'][ok[0]] if len(ok) else None)
    records=read(R/'PARENT_METRICS.json');summary=read(R/'STREAM_RESULTS.json')
    for kind,length in [('normal',18000),('event',3600)]:
        files=list(R.glob(f'TEST_{kind}_[0-9][0-9][0-9].npz'));assert len(files)==36
        for f in files:
            i=int(f.stem[-3:])
            with np.load(f) as z:
                assert z['score'].shape==(3,length) and np.isfinite(z['score']).all()
                for a,arm in enumerate(('fixed','adaptive','guarded')):
                    rows=publications(z['score'][a],z['source'][a],selection['thresholds'][a],p)
                    matched=set()
                    for t,c in rows:
                        if kind=='event':
                            for j,(on,off,src) in enumerate([(30,70,i%9),(80,90,(i%9+4)%9)]):
                                if on<=t<off and c==src and j not in matched:matched.add(j);break
                    stored=next(r for r in records if r['parent']==f.stem and r['arm']==arm)
                    assert stored['hits']==len(matched) and stored['alarms']==len(rows)
                    assert stored['extras']==len(rows)-len(matched)
    for arm,s in summary['arms'].items():
        ns=[r for r in records if r['arm']==arm and r['kind']=='normal']
        es=[r for r in records if r['arm']==arm and r['kind']=='event']
        assert s['normal_alarms']==sum(r['alarms'] for r in ns)
        assert s['timely_joint_hits']==sum(r['hits'] for r in es)
        assert s['extra_alarms']==sum(r['extras'] for r in es)
        assert s['events']==72 and np.isclose(s['normal_hours'],exposure)
        assert np.isclose(s['poisson_upper95_per_hour'],chi2.ppf(.95,2*(s['normal_alarms']+1))/2/exposure)
    cov=read(R/'COVARIANCE_RESULTS.json');parents=read(R/'COVARIANCE_PARENTS.json')
    for arm,s in cov['arms'].items():
        rows=[r for r in parents if r['arm']==arm];assert len(rows)==360
        assert s['correct']==sum(r['correct'] for r in rows)
        assert np.isclose(s['nis95_coverage'],np.mean([r['nis_covered'] for r in rows]))
    result={'passed':True,'sealed_files':len(seal['files']),'normal_hours_per_split':exposure,'test_events':72,
            'scope':'Independent seal, CAL selection, prediction publication and endpoint recount; not full-bank validation.'}
    (ROOT/'generated/adaptive_diagnostic_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
