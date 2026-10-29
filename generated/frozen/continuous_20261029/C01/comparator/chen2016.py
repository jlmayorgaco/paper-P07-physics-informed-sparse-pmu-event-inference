"""Chen et al. TPWRS2016 persistent single-outage QCD core.
Equations (7),(13),(30)-(33),(40)-(41). Native output is one stopping decision.
No restoration, load family, instantaneous-change extension or field ARL claim.
"""
from dataclasses import dataclass
import numpy as np

def laplacian(n,edges,omitted=None):
 H=np.zeros((n,n),float)
 for i,e in enumerate(edges):
  if i==omitted:continue
  x=float(e['x']);tap=float(e.get('tap',1.))
  if x<=0 or tap<=0:raise ValueError('Positive reactance/tap required')
  v=np.zeros(n);v[int(e['f'])]=1;v[int(e['t'])]=-1
  H+=np.outer(v,v)/(x*tap)
 return H

def covariance_bank(n,edges,observed,reference,credible=None):
 if reference in observed:raise ValueError('Reference must not be a selected observation')
 keep=np.array([i for i in range(n) if i!=reference]);selection=[list(keep).index(i) for i in observed]
 names=['normal'];cov=[];rejected=[];inverse=[]
 for index in [None]+list(range(len(edges)) if credible is None else credible):
  H=laplacian(n,edges,index)[np.ix_(keep,keep)]
  if np.linalg.matrix_rank(H)<n-1:
   if index is None:raise ValueError('Disconnected nominal network')
   rejected.append(index);continue
  M=np.linalg.inv(H);C=(M@M.T)[np.ix_(selection,selection)]
  np.linalg.cholesky(C);cov.append(C);inverse.append(M)
  if index is not None:names.append(edges[index].get('id',str(index)))
 return names,np.array(cov),dict(rejected_islanding_edges=rejected,reference=reference,observed=list(observed),injection_covariance='sigma2 times identity',matrix_inverses=inverse)

class ParallelCUSUM:
 def __init__(self,covariances,names,beta_observations):
  C=np.array(covariances,float)
  if len(names)!=len(C) or len(C)<2:raise ValueError('Nominal plus alternatives required')
  if not np.allclose(C,C.transpose(0,2,1)):raise ValueError('Symmetric covariance required')
  for c in C:np.linalg.cholesky(c)
  self.names=names;self.inverse=np.linalg.inv(C);self.logdet=np.linalg.slogdet(C)[1]
  self.threshold=float(np.log((len(names)-1)*beta_observations));self.scores=np.zeros(len(names)-1)
  self.stopped=False;self.count=0;self.decision=None
 def process(self,x,time_s=None):
  if self.stopped:return None
  x=np.asarray(x,float)
  if x.shape!=(self.inverse.shape[1],) or not np.isfinite(x).all():raise ValueError('Complete increment required')
  ll=-.5*(self.logdet[1:]-self.logdet[0]+np.einsum('i,hij,j->h',x,self.inverse[1:]-self.inverse[0],x))
  self.scores=np.maximum(0.,self.scores+ll);self.count+=1
  if self.scores.max()>self.threshold:
   best=int(np.argmax(self.scores));self.stopped=True
   self.decision=dict(source=self.names[best+1],observation=self.count,time_s=time_s,statistic=float(self.scores[best]),threshold=self.threshold)
   return self.decision.copy()
  return None

class PMUComparator:
 """Declared F01 adapter: degrees, nonoverlapping pairs, prefix-only scale/drift."""
 def __init__(self,shape_covariances,names,beta_seconds=3600.,fps=30,prefix_reports=300):
  self.shape=np.asarray(shape_covariances);self.names=names;self.fps=fps;self.prefix=prefix_reports
  self.beta_seconds=beta_seconds;self.increments=[];self.previous=None;self.k=-1;self.core=None
 def process(self,t,angle_deg):
  self.k+=1;a=np.asarray(angle_deg,float)
  if self.k%2==0:self.previous=a.copy();return None
  x=np.angle(np.exp(1j*np.deg2rad(a-self.previous)))
  if self.k<self.prefix:
   self.increments.append(x)
   if self.k==self.prefix-1:
    z=np.asarray(self.increments);self.center=z.mean(axis=0);v=z-self.center
    self.scale=float(np.einsum('ni,ij,nj->',v,np.linalg.inv(self.shape[0]),v)/(v.shape[0]*v.shape[1]))
    if not np.isfinite(self.scale) or self.scale<=0:raise ValueError('Uninformative prefix scale')
    self.core=ParallelCUSUM(self.shape*self.scale,self.names,self.beta_seconds*self.fps/2)
   return None
  if self.core is None:raise ValueError('Startup prefix incomplete')
  return self.core.process(x-self.center,float(t))
