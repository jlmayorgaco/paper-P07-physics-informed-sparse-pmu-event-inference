"""Run declared numerical checks, preserve numerical failures in the output."""
from pathlib import Path
import hashlib, itertools, json, platform
import numpy as np
import scipy
from scipy.linalg import solve_triangular
from scipy.special import logsumexp
from bounds import gaussian_score_radius, certified_winner, group_mass_interval, quadrature_log_interval

HERE=Path(__file__).resolve().parent
cfg=json.loads((HERE/'protocol.json').read_text())
rng=np.random.default_rng(cfg['seed']); tol=cfg['tolerance']
results={}; gates={}

def logpdf(y,m,S):
    L=np.linalg.cholesky(S);v=solve_triangular(L,y-m,lower=True)
    return -.5*(len(y)*np.log(2*np.pi)+2*np.log(np.diag(L)).sum()+v@v)

def main():
    freeze=json.loads((HERE/'EXECUTION_FREEZE.json').read_text())
    for name,h in freeze['files'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==h,name
    violations=0; ratios=[]; max_reduction=0.; winners=0; wrong=0
    for i in range(cfg['gaussian_trials']):
        n=cfg['gaussian_dimensions'][i%len(cfg['gaussian_dimensions'])]
        B=rng.normal(size=(n,n));St=B@B.T+np.eye(n)
        L=np.linalg.cholesky(St);Q,_=np.linalg.qr(rng.normal(size=(n,n)))
        es=rng.uniform(-.8,.8,n);E=(Q*es)@Q.T;eta=float(np.max(np.abs(es)))
        delta=rng.normal(size=n)*.15;eps=float(np.linalg.norm(delta))
        mt=rng.normal(size=n);m=mt+L@delta;y=mt+L@rng.normal(size=n)
        S=L@(np.eye(n)+E)@L.T;r=float(np.linalg.norm(solve_triangular(L,y-mt,lower=True)))
        radius=gaussian_score_radius(r,eps,eta,n)
        err=abs(logpdf(y,m,S)-logpdf(y,mt,St))
        violations+=int(err>radius+tol);ratios.append(err/radius)
        max_reduction=max(max_reduction,abs(gaussian_score_radius(r,eps,0,n)-(r*eps+.5*eps**2)))
        scores=rng.normal(size=4)*3;radii=rng.uniform(0,2,4)
        true=scores+rng.uniform(-1,1,4)*radii
        winner=certified_winner(scores,radii)
        if winner is not None:
            winners+=1;wrong+=int(winner!=np.argmax(true))
    results['gaussian']={'trials':cfg['gaussian_trials'],'violations':violations,'max_error_bound_ratio':max(ratios),'fixed_covariance_identity_error':max_reduction,'interval_winner_certificates':winners,'wrong_certificates':wrong}
    gates['gaussian_score_bound']=violations==0 and max_reduction<tol and wrong==0
    # Enumerate all corners; extrema of normalized group probability occur there.
    scores=np.array([1.,-.3,.2,-1.]);radii=np.array([.2,.5,.1,.3]);mask=np.array([1,0,1,0],bool)
    low,high=group_mass_interval(scores,radii,mask);values=[]
    for sign in itertools.product([-1,1],repeat=4):
        x=scores+radii*np.array(sign);values.append(float(np.exp(logsumexp(x[mask])-logsumexp(x))))
    weights=np.array([.1,.2,.3,.4]);ql,qh=quadrature_log_interval(scores,radii,weights)
    quad=[float(logsumexp(np.log(weights)+scores+radii*np.array(s))) for s in itertools.product([-1,1],repeat=4)]
    gates['mass_and_quadrature']=abs(low-min(values))<tol and abs(high-max(values))<tol and abs(ql-min(quad))<tol and abs(qh-max(quad))<tol
    results['mass_and_quadrature']={'mass_interval':[low,high],'corner_extrema':[min(values),max(values)],'quadrature_interval':[ql,qh]}
    # Same mean does not imply same score if covariance changes.
    results['covariance_counterexample']={'mean_error':0.,'abs_log_score_error':abs(logpdf(np.array([0.]),np.array([0.]),np.array([[4.]]))-logpdf(np.array([0.]),np.array([0.]),np.eye(1)))}
    gates['fail_closed']=np.isinf(gaussian_score_radius(1,0,1,1)) and certified_winner([2,1],[np.inf,0]) is None and group_mass_interval([2,1],[np.inf,0],[1,0])==(0.,1.)
    # Three-node path: endpoint swap preserves sensor SET but swaps labelled outputs.
    Lap=np.array([[1.,-1,0],[-1,2,-1],[0,-1,1]])
    Lp=np.linalg.pinv(Lap);C=np.eye(3)[[0,2]]
    h0=C@Lp@np.array([1.,-1,0]);h2=C@Lp@np.array([0.,-1,1])
    results['labelled_sensor_symmetry']={'signature_source_0':h0.tolist(),'signature_source_2':h2.tolist(),'difference_norm':float(np.linalg.norm(h0-h2))}
    gates['sensor_permutation_counterexample']=np.linalg.norm(h0-h2)>1
    # Opening a full pi branch removes charging as well as its series stamp.
    y=2-5j;sh=.02j;stamp=np.array([[y+sh,-y],[-y,y+sh]])
    results['pi_branch']={'complex_stamp_rank':int(np.linalg.matrix_rank(stamp)),'series_only_rank':int(np.linalg.matrix_rank(stamp-np.eye(2)*sh))}
    gates['pi_branch_rank']=np.linalg.matrix_rank(stamp)==2
    results['constant_bias']={'K':[1,2,10,100],'expected_log_ratio':[.5*k*.2**2 for k in [1,2,10,100]],'scaling':'linear in K for independent constant-bias observations, not K squared'}
    sigma_t=.001;omega=2*np.pi*60
    results['clock']={'single_clock_phase_deg':360*60*sigma_t,'independent_pair_variance_rad2':2*omega**2*sigma_t**2,'identical_common_pair_variance_rad2':0.}
    # Woodbury with singular P: factor form needs no inverse of P.
    R=np.array([[2.,.3],[.3,1.]]);O=np.array([[1.,.5],[-.2,.8]]);P=np.diag([.7,0]);s=np.array([1.,.2]);U=O@np.diag([np.sqrt(.7),0]);Ri=np.linalg.inv(R)
    g=float(s@np.linalg.solve(R+U@U.T,s));g0=float(s@Ri@s);loss=float(s@Ri@U@np.linalg.solve(np.eye(2)+U.T@Ri@U,U.T@Ri@s))
    gates['singular_recovery_information']=abs(g-(g0-loss))<tol and loss>=0
    results['singular_recovery_information']={'known_state':g0,'uncertain_state':g,'loss':loss,'identity_error':abs(g-(g0-loss))}
    # Audit exactly the saved native operators, without selecting/rebuilding a plant.
    native={}
    for mode in ['normal','line']:
        folder=HERE.parent/'descriptor_bridge_20261113/run_v2/operators'/mode
        A=np.loadtxt(folder/'A.csv',delimiter=',',skiprows=1);C=np.loadtxt(folder/'C.csv',delimiter=',',skiprows=1)
        ev,V=np.linalg.eig(A);idx=int(np.argmin(abs(ev)));v=V[:,idx]
        native[mode]={'A_shape':list(A.shape),'C_shape':list(C.shape),'relative_asymmetry':float(np.linalg.norm(A-A.T)/np.linalg.norm(A)),'max_eigenvalue_real':float(ev.real.max()),'minimum_eigenvalue_modulus':float(abs(ev[idx])),'near_zero_eigenvalues_1e_minus_7':int(sum(abs(ev)<1e-7)),'near_zero_mode_voltage_output_norm':float(np.linalg.norm(C@v)),'strict_decay_certified':False}
    results['native_F01']=native
    gates['native_not_undirected_laplacian']=all(d['relative_asymmetry']>.1 and d['C_shape'][0]!=d['C_shape'][1] for d in native.values())
    output={'scope':cfg['scope'],'passed':all(gates.values()),'gates':gates,'results':results,'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'limits':['No F01 detection evaluation','No construction of a cheap valid DAE error bound','No global decay certificate from a near-zero eigenvalue','No C03 access']}
    (HERE/'RESULTS.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))
    assert output['passed']

if __name__=='__main__': main()
