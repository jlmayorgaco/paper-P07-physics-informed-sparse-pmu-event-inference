#!/usr/bin/env python3
"""Minimal verification of graph-Hamiltonian balance, edge switch, and Gaussian Bayes factor.
This is a 4-bus toy reduced network, NOT the original IEEE-39 DAE / SGSMA dataset.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm, cho_factor, cho_solve
from scipy.stats import multivariate_normal

rng = np.random.default_rng(261112)
n = 4
edges=[(0,1),(1,2),(2,3),(0,3),(1,3)]
K=np.array([2.1,1.5,0.8,1.2,0.6])
B=np.zeros((n,len(edges)))
for j,(a,b) in enumerate(edges):
    B[a,j]=1.; B[b,j]=-1.
M=np.diag([1.2,1.4,1.1,1.0])
D=np.diag([0.20,0.25,0.30,0.22]); Minv=np.linalg.inv(M)

def energy(theta,omega,enabled):
    bphi=B.T@theta
    return 0.5*omega@M@omega + np.sum(enabled*K*(1-np.cos(bphi)))

def dyn(t,y,enabled,u):
    theta=y[:n]; omega=y[n:2*n]
    grad=B@(enabled*K*np.sin(B.T@theta))
    domega=Minv@(u-D@omega-grad)
    return np.r_[omega,domega,omega@u,omega@D@omega]

initial=np.r_[np.array([.025,-.015,.02,-.01]), np.array([.013,-.009,.006,.002]),0.,0.]
q=np.ones(len(edges)); y=initial.copy()
segments=[(0.,.35,False,False),(.35,.8,True,False),(.8,1.25,True,True),(1.25,2.0,False,True)]
errors=[]; switching_jump=None
for t0,t1,input_active,line_open in segments:
    if line_open and q[-1]!=0:
        before=energy(y[:n],y[n:2*n],q)
        q[-1]=0
        after=energy(y[:n],y[n:2*n],q)
        switching_jump=after-before
        expected=-K[-1]*(1-np.cos(B[:,-1]@y[:n]))
        assert np.allclose(switching_jump,expected,atol=1e-14)
    u=np.zeros(n)
    if input_active: u[1]=0.35
    start_energy=energy(y[:n],y[n:2*n],q)
    old_work,old_diss=y[2*n:]
    sol=solve_ivp(lambda t,z: dyn(t,z,q,u),(t0,t1),y,rtol=3e-11,atol=1e-13)
    assert sol.success
    y=sol.y[:,-1]
    final_energy=energy(y[:n],y[n:2*n],q)
    balance=(final_energy-start_energy)-(y[2*n]-old_work)+(y[2*n+1]-old_diss)
    errors.append(balance)
assert max(abs(x) for x in errors)<1e-9

# Discrete graph Green's response for two candidate load buses and an uncertain initial recovery state.
L=B@np.diag(K)@B.T
A=np.block([[np.zeros((n,n)),np.eye(n)],[-Minv@L,-Minv@D]])
dt=.1
Ab=np.zeros((2*n+n,2*n+n)); Ab[:2*n,:2*n]=A; Ab[n:2*n,2*n:]=Minv
PhiGamma=expm(Ab*dt)
F=PhiGamma[:2*n,:2*n]; G=PhiGamma[:2*n,2*n:]
C=np.zeros((4,2*n)); C[0,0]=1; C[1,3]=1
C[2,:n]=K[0]*B[:,0]; C[3,:n]=K[4]*B[:,-1]
T=15; on,off=4,10
O=np.vstack([C@np.linalg.matrix_power(F,k) for k in range(T)])
def signature(bus):
    x=np.zeros(2*n); obs=[]
    e=np.zeros(n);e[bus]=1
    for k in range(T):
        obs.append(C@x)
        x=F@x + (G@e if on<=k<off else 0)
    return np.concatenate(obs)
s1=signature(1); s2=signature(2)
P0=np.diag(np.r_[np.repeat(.012**2,n),np.repeat(.009**2,n)])
R0=np.eye(O.shape[0])*(.005**2)
Sigma=R0+O@P0@O.T
x0=rng.multivariate_normal(np.zeros(2*n),P0)
yobs=O@x0 + s1*.25 + rng.multivariate_normal(np.zeros(len(s1)),R0)
v=.25**2
fact=cho_factor(Sigma,lower=True)
def log_bf(s):
    q=cho_solve(fact,s)
    g=s@q;b=s@cho_solve(fact,yobs)
    return float((v*b*b)/(2*(1+v*g)) - .5*np.log1p(v*g))

bf1=log_bf(s1); bf2=log_bf(s2)
base=multivariate_normal.logpdf(yobs,mean=np.zeros(len(yobs)),cov=Sigma,allow_singular=False)
exact1=multivariate_normal.logpdf(yobs,mean=np.zeros(len(yobs)),cov=Sigma+v*np.outer(s1,s1))-base
exact2=multivariate_normal.logpdf(yobs,mean=np.zeros(len(yobs)),cov=Sigma+v*np.outer(s2,s2))-base
assert abs(bf1-exact1)<1e-7 and abs(bf2-exact2)<1e-7

# Verify the graph line removal is a rank-one Hessian update at zero angle.
e=-1
L_open=B@np.diag(K*np.array([1,1,1,1,0]))@B.T
assert np.allclose(L_open, L-K[e]*np.outer(B[:,e],B[:,e]))

print('MODELO: 4 buses, 5 branches (illustrative, not IEEE-39)')
print(f'ENERGY_MAX_BALANCE_RESIDUAL={max(abs(x) for x in errors):.3e}')
print(f'ENERGY_SWITCH_JUMP={switching_jump:.9e}')
print(f'EDGE_HESSIAN_RANK_ONE_RESIDUAL={np.linalg.norm(L_open-L+K[e]*np.outer(B[:,e],B[:,e])):.3e}')
print(f'BAYES_FACTOR_C1={bf1:.9f}')
print(f'BAYES_FACTOR_C2={bf2:.9f}')
print(f'BAYES_MAX_IDENTITY_RESIDUAL={max(abs(bf1-exact1),abs(bf2-exact2)):.3e}')
