"""Augmented full-DAE mode predictor, constructed exclusively from public physics."""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.linalg import expm,block_diag,solve_discrete_are,cho_factor,cho_solve
from threadpoolctl import threadpool_limits
from instrument_parent import ColoredInstrument,FIELDS,wrap
ROOT=Path(__file__).resolve().parent
def build(root=None, physical=None):
 ROOT=Path(root) if root is not None else Path(__file__).resolve().parent
 cfg=json.loads((ROOT/'PROTOCOL.json').read_text());d=ROOT/'model/dae';r=ROOT/'model'
 load=lambda p:pd.read_csv(p).to_numpy(float)
 A=load(d/'A.csv');B=load(d/'B.csv');C=load(d/'C_voltage.csv');D=load(d/'D_voltage.csv');v0=pd.read_csv(d/'nominal_voltage.csv').value.to_numpy();nx=len(A)
 meta=json.loads((d/'MODEL.json').read_text());assets=json.loads((r/'assets.json').read_text());noise=json.loads((r/'stochastic_model.json').read_text());reporting=json.loads((r/'reporting_config.json').read_text())
 if physical is not None:
  A=physical['normal_A'];B=physical['normal_B'];C=physical['normal_C_voltage'];D=physical['normal_D_voltage'];v0=physical['normal_voltage'].ravel()
 symbols=pd.read_csv(d/'dynamic_index.csv').symbol
 std=np.array([cfg['state_prior']['omega'] if 'machine₊ω' in s else cfg['state_prior']['delta'] if 'machine₊δ' in s else cfg['state_prior']['default'] for s in symbols])
 network=json.loads((d/'measurement_network.json').read_text());Bt=np.array(network['B_real'])+1j*np.array(network['B_imag'])
 pmus=np.array(reporting['pmus'])-1;mapping=pd.read_csv(r/'terminal_mapping.csv');kv=pd.read_csv(r/'bus.csv').base_kv.to_numpy()
 factors=mapping.polarity.to_numpy()*mapping.gain.to_numpy()*100e6/(np.sqrt(3)*kv[mapping.terminal.to_numpy(int)-1]*1000)
 keep=[np.arange(8)]*3+[np.arange(7)]+[np.arange(8)]*2
 filters=[ColoredInstrument(noise['families'][f],k) for f,k in zip(FIELDS,keep)]
 scales=np.array([noise['families'][f]['normalization_scale'] for f in FIELDS]);W=block_diag(*[f.W for f in filters]);WH=block_diag(*[f.W@f.H for f in filters]);WA=block_diag(*[f.A for f in filters]);WB=block_diag(*[f.B for f in filters])
 nh=160;nw=WA.shape[0];n=nx+nh+nw;assert nw==sum(f.n for f in filters)
 def observable(v,c):
  z=v[::2]+1j*v[1::2];dv=c[::2]+1j*c[1::2];vp=z[pmus];dp=dv[pmus];ip=Bt@z;di=Bt@dv
  base=[abs(vp)*345e3/np.sqrt(3),np.angle(vp,deg=True),abs(ip)*abs(factors),np.angle(ip,deg=True)]
  jac=[np.real(dp*np.conj(vp[:,None])/abs(vp[:,None]))*345e3/np.sqrt(3),np.imag(dp/vp[:,None])*180/np.pi,
       np.real(di*np.conj(ip[:,None])/abs(ip[:,None]))*abs(factors[:,None]),np.imag(di/ip[:,None])*180/np.pi]
  return base,jac
 base0,jac0=observable(v0,C)
 modes=[dict(A=A,g=np.zeros(nx),u=np.zeros(nx),C=C,v=v0,D=np.zeros(78),id='normal')]
 for a in assets:
  if a['family']=='load':
   i=2*meta['loads'].index(a['bus']);m=dict(A=A,g=np.zeros(nx),u=B[:,i:i+2].sum(axis=1),C=C,v=v0,D=D[:,i:i+2].sum(axis=1),id=a['id'])
  else:
   p=r/a['id'];m=dict(A=load(p/'A.csv'),g=load(p/'force.csv').ravel(),u=np.zeros(nx),C=load(p/'C_voltage.csv'),v=load(p/'voltage.csv').ravel(),D=np.zeros(78),id=a['id'])
  if physical is not None and a['family']=='line':
   m.update(A=physical[a['id']+'_A'],g=physical[a['id']+'_force'].ravel(),C=physical[a['id']+'_C_voltage'],v=physical[a['id']+'_voltage'].ravel())
  modes.append(m)
 theta_t=np.arange(-20,1)/30;poly=np.linalg.pinv(np.c_[np.ones(21),theta_t,theta_t**2]);derivatives=[poly[1]/360,2*poly[2]/360]
 for m in modes:
  base,jac=observable(m['v'],m['C']);_,jd=observable(m['v'],m['D'][:,None]);raw=np.zeros((47,n));offset=np.zeros(47);amp=np.zeros(47);pos=0
  for j in range(4):
   k=keep[j];sl=slice(pos,pos+len(k));raw[sl,:nx]=jac[j][k]*std/scales[j]
   delta=base[j]-base0[j];delta=wrap(delta) if j in [1,3] else delta
   offset[sl]=delta[k]/scales[j];amp[sl]=jd[j][k,0]/scales[j];pos+=len(k)
  for j,weights in enumerate(derivatives):
   sl=slice(31+j*8,39+j*8);factor=scales[1]/scales[4+j]
   raw[sl]=factor*weights[-1]*raw[8:16];offset[sl]=factor*weights[-1]*offset[8:16];amp[sl]=factor*weights[-1]*amp[8:16]
   for lag in range(20):raw[sl,nx+lag*8:nx+(lag+1)*8]+=np.eye(8)*factor*weights[-2-lag]
  # Memory is deterministic predicted history, distinct from the observed noise filter.
  roll=np.zeros((n,n));roll[:nx,:nx]=np.eye(nx);roll[nx:nx+8]=raw[8:16];roll[nx+8:nx+nh,nx:nx+nh-8]=np.eye(nh-8)
  roll[nx+nh:]=WB@raw;roll[nx+nh:,nx+nh:]+=WA
  rg=np.r_[np.zeros(nx),offset[8:16],np.zeros(nh-8),WB@offset];ru=np.r_[np.zeros(nx),amp[8:16],np.zeros(nh-8),WB@amp]
  obs=W@raw;obs[:,nx+nh:]-=WH
  m.update(raw=raw,offset=offset,amp=amp,roll=roll,rg=rg,ru=ru,obs=obs,og=W@offset,ou=W@amp)
 flows={}
 def flow(mode,h):
  key=(mode,h)
  if key not in flows:
   m=modes[mode];aug=np.zeros((nx+2,nx+2));aug[:nx,:nx]=m['A'];aug[:nx,nx]=m['g'];aug[:nx,nx+1]=m['u'];e=expm(aug*h)
   flows[key]=(e[:nx,:nx]*std[None,:]/std[:,None],e[:nx,nx]/std,e[:nx,nx+1]/std)
  return flows[key]
 ops=[];keys={}
 def operator(old,new,before,key):
  f1,g1,u1=flow(old,before);f2,g2,u2=flow(new,1/30-before)
  f=f2@f1;g=f2@g1+g2;u=f2@u1+u2
  full=np.eye(n);full[:nx,:nx]=f;gg=np.r_[g,np.zeros(n-nx)];uu=np.r_[u,np.zeros(n-nx)];m=modes[new]
  keys[key]=len(ops);ops.append(dict(T=m['roll']@full,J=m['obs']@full,g=m['roll']@gg+m['rg'],u=m['roll']@uu+m['ru'],j=m['obs']@gg+m['og'],v=m['obs']@uu+m['ou']))
 operator(0,0,0.,'normal')
 for c,a in enumerate(assets):
  mode=c+1;operator(mode,mode,0.,f'stay:{c}')
  for ix,before in enumerate([1/30,1/60]):
   operator(0,mode,before,f'on:{c}:{ix}');operator(mode,0,before,f'off:{c}:{ix}')
 normal=ops[0];Q0=np.eye(n)*cfg['auxiliary_process_variance_per_frame'];Q0[:nx,:nx]=np.eye(nx)*cfg['physical_process_variance_per_frame']
 with np.load(r/'discrepancy.npz') as qd:
  QQ=[Q0.copy() for _ in range(4)];RR=[np.eye(47) for _ in range(4)]
  for j,key in enumerate(['load','line','recovery'],1):QQ[j][:nx,:nx]+=qd[key];RR[j]+=qd['R_'+key]
 # Persistent observation discrepancy is a latent AR state, not a fresh
 # independent error on every report. Parameters come only from the old
 # public deterministic model bank; physical operators are unchanged.
 rho=json.loads((r/'TEMPORAL_DISCREPANCY.json').read_text())['rho'];nd=47
 for op in ops:
  op['T']=block_diag(op['T'],rho*np.eye(nd));op['J']=np.c_[op['J'],np.eye(nd)]
  for key in ['g','u']:op[key]=np.r_[op[key],np.zeros(nd)]
 QQ=[block_diag(q,(1-rho*rho)*(rr-np.eye(nd))+np.eye(nd)*1e-14) for q,rr in zip(QQ,RR)]
 RR=[np.eye(nd) for _ in RR];n+=nd
 groups=[];group=[];group_error=0.
 for op in ops:
  match=next((j for j,g in enumerate(groups) if np.allclose(op['T'],g['T'],atol=1e-11,rtol=1e-13) and np.allclose(op['J'],g['J'],atol=1e-11,rtol=1e-13)),None)
  if match is None:match=len(groups);groups.append(op)
  group_error=max(group_error,float(abs(op['T']-groups[match]['T']).max()),float(abs(op['J']-groups[match]['J']).max()));group.append(match)
 Ps=[];Ks=[];Sis=[];lds=[];errors=[]
 for Q,R in zip(QQ,RR):
  P=solve_discrete_are(normal['T'].T,normal['J'].T,Q,R);P=(P+P.T)/2;kr=[];sr=[];lr=[]
  for op in groups:
   S=R+op['J']@P@op['J'].T;cf=cho_factor(S);K=cho_solve(cf,op['J']@P@op['T'].T).T
   kr.append(K);sr.append(cho_solve(cf,np.eye(47)));lr.append(2*np.log(np.diag(cf[0])).sum())
  ric=normal['T']@P@normal['T'].T+Q-kr[0]@(R+normal['J']@P@normal['J'].T)@kr[0].T
  err=np.linalg.norm(P-ric)/np.linalg.norm(P);assert err<1e-6,err
  Ps.append(P);Ks.append(kr);Sis.append(sr);lds.append(lr);errors.append(float(err))
 nominal_report=np.concatenate([base0[0],base0[1]+reporting['common_phase_intercept_deg']+np.array(reporting['relative_voltage_bias_deg']),base0[2],
  np.angle((Bt@(v0[::2]+1j*v0[1::2]))*factors,deg=True)+reporting['common_phase_intercept_deg']+np.array(reporting['relative_voltage_bias_deg'])+mapping.bias_deg.to_numpy(),
  np.full(8,60+reporting['common_phase_slope_deg_s']/360),np.zeros(8)])
 bank=dict(**{k:np.array([o[k] for o in ops]) for k in ['g','u','j','v']},T=np.array([o['T'] for o in groups]),J=np.array([o['J'] for o in groups]),group=np.array(group),K=np.array(Ks),Sinv=np.array(Sis),logdet=np.array(lds),P=np.array(Ps),Q=np.array(QQ),R=np.array(RR),std=std,base=nominal_report,step_signatures=np.array([m['amp'][:31] if a['family']=='load' else m['offset'][:31] for a,m in zip(assets,modes[1:])]))
 info=dict(differential_states=nx,phase_history=nh,instrument_memory=nw,discrepancy_states=nd,discrepancy_rho=rho,total_states=n,cells=len(assets),operators=len(ops),unique_linear_operators=len(groups),grouping_absolute_error=group_error,riccati_relative_residual=errors,covariance_min_eigenvalues=[float(np.linalg.eigvalsh(p)[0]) for p in Ps],raw_access=False,discrepancy_regimes=['quiet','load','line','recovery'])
 return bank,info
