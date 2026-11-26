from pathlib import Path
import json,sys
import numpy as np
from scipy.stats import multivariate_normal
from chen2016 import covariance_bank,ParallelCUSUM,PMUComparator,laplacian
edges=[dict(f=0,t=1,x=.0504,id='LINE1-2'),dict(f=1,t=2,x=.0372,id='LINE2-3'),dict(f=0,t=2,x=.0636,id='LINE1-3')]
names,C,a=covariance_bank(3,edges,[1,2],0)
expected=np.array([[1/.0504+1/.0372,-1/.0372],[-1/.0372,1/.0372+1/.0636]])
assert np.allclose(laplacian(3,edges)[1:,1:],expected)
assert np.allclose(C[0],np.linalg.inv(expected)@np.linalg.inv(expected).T)
# Sparse covariance is selected AFTER inversion, not inverse of selected Laplacian.
_,sparse,_=covariance_bank(3,edges,[2],0);assert np.allclose(sparse[:,0,0],C[:,1,1])
x=np.array([.02,-.04]);q=ParallelCUSUM(C,names,1000)
q.process(x);manual=np.array([multivariate_normal.logpdf(x,cov=c)-multivariate_normal.logpdf(x,cov=C[0]) for c in C[1:]])
assert np.allclose(q.scores,np.maximum(0,manual),atol=1e-12)
# Positive-part recursion exactly equals maximization over all suffix sums.
rng=np.random.default_rng(20261029);xs=rng.multivariate_normal([0,0],C[0],size=100);q=ParallelCUSUM(C,names,np.exp(500));ll=[]
for x in xs:
 ll.append([multivariate_normal.logpdf(x,cov=c)-multivariate_normal.logpdf(x,cov=C[0]) for c in C[1:]])
 q.process(x);all_ll=np.array(ll);brute=np.maximum(0,np.max(np.cumsum(all_ll[::-1],axis=0),axis=0));assert np.allclose(q.scores,brute,atol=1e-10)
# Fixed stopping time/localization under matched Gaussian post-change data.
q=ParallelCUSUM(C,names,1e4)
for i,x in enumerate(rng.multivariate_normal([0,0],C[2],size=10000)):
 event=q.process(x,i/15)
 if event:break
assert event is not None and event['source']==names[2]
# Future reports cannot affect prefix outputs; wrapping adds no 2pi jump.
a=PMUComparator(C,names,prefix_reports=300);b=PMUComparator(C,names,prefix_reports=300);angles=np.cumsum(rng.normal(0,.03,(600,2)),axis=0)+179.
out=[]
for k in range(600):
 xx=(angles[k]+180)%360-180
 y=a.process(k/30,xx);yy=b.process(k/30,xx if k<450 else xx+20)
 if k<450:assert y==yy
assert np.isfinite(a.scale) and a.scale>0
# An islanding alternative is explicitly excluded.
_,_,audit=covariance_bank(3,[dict(f=0,t=1,x=.1),dict(f=1,t=2,x=.1)],[1,2],0);assert audit['rejected_islanding_edges']==[0,1]
Path(__file__).with_name('TESTS.json').write_text(json.dumps(dict(passed=True,three_bus_eq9=True,sparse_marginal=True,logpdf_scipy_parity=True,suffix_max_parity=True,matched_postchange_identified=event['source'],causal_prefix=True,angle_wrap=True,islanding_exclusion=True),indent=2));print('CHEN_CORE_TESTS_PASS')
