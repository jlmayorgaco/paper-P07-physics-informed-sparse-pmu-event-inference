"""Isolated DICE mathematical candidate. Not used by R11 or C01.

The legacy 137-support reference already uses support-wise Gram matrices.
The candidate shares projections/Gram blocks across overlapping supports.
"""
from pathlib import Path
import ast, copy, hashlib, itertools, math
import numpy as np
from scipy.linalg import solve_triangular
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parents[2]
REFERENCE=ROOT/'research/pmu_hybrid_dae_bayes/scripts/global_137_confirmatory_v1.py'
PILOT=ROOT/'research/pmu_hybrid_dae_bayes/scripts/load_multi_pilot_v1.py'

def reference_functions():
    """Compile pure numerical definitions only; no baseline imports/writes."""
    tree=ast.parse(REFERENCE.read_text(encoding='utf-8-sig'))
    ptree=ast.parse(PILOT.read_text(encoding='utf-8-sig')); constants={}
    for node in ptree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ['BUSES','SIGMA_A','CARD_PRIOR']:
                    constants[target.id]=ast.literal_eval(node.value)
    env=dict(np=np,math=math,logsumexp=logsumexp,DIM=960,GH=31,_SINGLE={},**constants)
    env['PAIRS']=list(itertools.combinations(env['BUSES'],2))
    names=['basis','gh_single','gh_double','infer']
    defs=[copy.deepcopy(n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    assert len(defs)==4
    exec(compile(ast.Module(body=defs,type_ignores=[]),str(REFERENCE),'exec'),env)
    new=copy.deepcopy(next(n for n in defs if n.name=='gh_double'));new.name='gh_double_stats'
    new.args.args=[ast.arg(arg=v) for v in ['rr','u','G']]
    class SuppliedStatistics(ast.NodeTransformer):
        def visit_Assign(self,node):
            if len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['rr','u']:
                return None
            return self.generic_visit(node)
    new=SuppliedStatistics().visit(new);ast.fix_missing_locations(new)
    exec(compile(ast.Module(body=[new],type_ignores=[]),'shared_Gram_candidate','exec'),env)
    return env

class SharedBank:
    def __init__(self,D,Q,cross,reference):
        self.ref=reference;self.D=D;self.Q=Q
        self.F=np.column_stack([D,Q,*[cross[p] for p in reference['PAIRS']]])
        assert self.F.shape==(960,152)
        buses=reference['BUSES']
        self.index=np.array([[buses.index(i),buses.index(j),16+buses.index(i),16+buses.index(j),32+k]
                             for k,(i,j) in enumerate(reference['PAIRS'])])
        self.H=self.F.T@self.F
        self.G=self.H[self.index[:,:,None],self.index[:,None,:]]
    def infer(self,residual,batched=False,normalized=False):
        r=np.asarray(residual,float);rr=float(r@r);projection=self.F.T@r
        singles=self.ref['gh_single'](r,self.D,self.Q)
        # Explicit successor correction; legacy replay remains the default.
        # For D=Q=0 the archived single integral is Z0/(2*pi), not Z0.
        if normalized:
            singles=singles.copy();singles[:,0]+=np.log(2*np.pi)
        doubles=(batched_double(rr,projection[self.index],self.G,self.ref) if batched
                 else self.ref['gh_double_stats'](rr,projection[self.index],self.G))
        raw=np.r_[-.5*(960*np.log(2*np.pi)+rr),singles[:,0],doubles[:,0]]
        prior=self.ref['CARD_PRIOR'];lp=np.log(np.r_[prior[0],np.full(16,prior[1]/16),np.full(120,prior[2]/120)])
        post=np.exp(raw+lp-logsumexp(raw+lp))
        return raw,post,singles,doubles

def batched_double(rr,u,G,reference):
    """Same frozen Newton proposals/GH31 normalizers, vectorized over supports."""
    sigma=reference['SIGMA_A'];prior=1/sigma**2;P=len(G);eye=np.eye(2);th=np.zeros((P,2))
    for _ in range(10):
        a,b=th[:,0],th[:,1];J=np.zeros((P,5,2));J[:,0,0]=1;J[:,1,1]=1
        J[:,2,0]=2*a;J[:,3,1]=2*b;J[:,4,0]=b;J[:,4,1]=a
        c=np.stack([a,b,a*a,b*b,a*b],1);e=np.einsum('pij,pj->pi',G,c)-u
        grad=np.einsum('pki,pk->pi',J,e)+prior*th
        H=np.einsum('pki,pkj->pij',J,np.einsum('pab,pbj->paj',G,J))+prior*eye[None,:,:]
        step=np.linalg.solve(H,grad[...,None])[...,0];th-=step
        if np.max(np.linalg.norm(step,axis=1))<1e-11:break
    a,b=th[:,0],th[:,1];J=np.zeros((P,5,2));J[:,0,0]=1;J[:,1,1]=1
    J[:,2,0]=2*a;J[:,3,1]=2*b;J[:,4,0]=b;J[:,4,1]=a
    H=np.einsum('pki,pkj->pij',J,np.einsum('pab,pbj->paj',G,J))+prior*eye[None,:,:]
    cov=np.linalg.pinv(H,rcond=1e-12);L=np.linalg.cholesky(cov+1e-15*eye)
    x,w=np.polynomial.hermite.hermgauss(reference['GH']);z=np.sqrt(2)*x;zw=w/np.sqrt(np.pi)
    z1,z2=np.meshgrid(z,z,indexing='ij');zg=np.column_stack([z1.ravel(),z2.ravel()])
    logzw=np.log(np.outer(zw,zw).ravel())
    nodes=th[:,None,:]+np.einsum('ni,pji->pnj',zg,L);aa,bb=nodes[:,:,0],nodes[:,:,1]
    C=np.stack([aa,bb,aa*aa,bb*bb,aa*bb],axis=2)
    qn=rr-2*np.einsum('pni,pi->pn',C,u)+np.einsum('pni,pij,pnj->pn',C,G,C)
    lf=-.5*(reference['DIM']*np.log(2*np.pi)+2*np.log(2*np.pi*sigma)+qn+prior*(aa*aa+bb*bb))
    lw=lf+.5*np.sum(zg*zg,axis=1)[None,:]+logzw[None,:]
    mx=lw.max(axis=1);weights=np.exp(lw-mx[:,None]);total=weights.sum(axis=1);weights/=total[:,None]
    logz=mx+np.log(total)+np.log(np.linalg.det(L))+np.log(2*np.pi)+np.log(1/sigma)
    mi=np.sum(weights*aa,axis=1);mj=np.sum(weights*bb,axis=1)
    vi=np.sum(weights*(aa-mi[:,None])**2,axis=1);vj=np.sum(weights*(bb-mj[:,None])**2,axis=1)
    cv=np.sum(weights*(aa-mi[:,None])*(bb-mj[:,None]),axis=1)
    return np.column_stack([logz,mi,mj,vi,vj,cv,mi-1.96*np.sqrt(np.maximum(vi,0)),
        mi+1.96*np.sqrt(np.maximum(vi,0)),mj-1.96*np.sqrt(np.maximum(vj,0)),
        mj+1.96*np.sqrt(np.maximum(vj,0)),np.linalg.cond(H),np.linalg.eigvalsh(H).min(axis=1)])

def gaussian_low_rank(residual,Sigma,B,Gamma_factor):
    """Exact log N(r;0,Sigma+B Gamma B'), Gamma=LL'; keep determinant."""
    r=np.asarray(residual,float);base=np.linalg.cholesky(Sigma)
    z=solve_triangular(base,r,lower=True)
    U=solve_triangular(base,B@Gamma_factor,lower=True)
    K=np.eye(U.shape[1])+U.T@U;C=np.linalg.cholesky(K)
    q=solve_triangular(C,U.T@z,lower=True)
    logdet=2*np.log(np.diag(base)).sum()+2*np.log(np.diag(C)).sum()
    return -.5*(len(r)*np.log(2*np.pi)+logdet+z@z-q@q)

def conditional_log_bf(residual,signature,Sigma,prior_variance):
    L=np.linalg.cholesky(Sigma);r=solve_triangular(L,residual,lower=True)
    s=solve_triangular(L,signature,lower=True);information=float(s@s);score=float(s@r)
    return .5*score*score/(information+1/prior_variance)-.5*np.log1p(prior_variance*information)

def whitened_statistics(blocks,observations):
    """Already causal-whitened blocks; raw rolling deletion is not supported."""
    size=blocks.shape[-1];H=np.zeros((size,size));g=np.zeros(size);rr=0.;out=[]
    for block,y in zip(blocks,observations):
        H+=block.T@block;g+=block.T@y;rr+=float(y@y)
        out.append((H.copy(),g.copy(),rr))
    return out

def synthetic_dictionary(reference,seed=390137):
    rng=np.random.default_rng(seed)
    # Pure algebra fixture with legacy dimensions; not IEEE-39 physical responses.
    F=rng.normal(size=(960,152));F/=np.linalg.norm(F,axis=0)
    F[:,:16]*=300.;F[:,16:32]*=1000.;F[:,32:]*=800.
    return F[:,:16],F[:,16:32],{p:F[:,32+k] for k,p in enumerate(reference['PAIRS'])}

def source_hashes():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [REFERENCE,PILOT]}
