"""Reference check for P07's time ordering: observe x then propagate T*x."""
import numpy as np
from numpy.testing import assert_allclose
from scipy.linalg import solve


def p07_next_covariance(P,T,J,Q,R):
    S=J@P@J.T+R
    C=T@P@J.T
    Pnext=T@P@T.T+Q-C@solve(S,C.T,assume_a='pos')
    return Pnext,S,C


def test_schur_equals_joint_conditional():
    rng=np.random.default_rng(301)
    P0=rng.standard_normal((5,5));P=P0@P0.T+.1*np.eye(5)
    T=np.eye(5)+.1*rng.standard_normal((5,5))
    J=rng.standard_normal((4,5))
    Q=.001*np.eye(5);R=.03*np.eye(4)
    Pnext,S,C=p07_next_covariance(P,T,J,Q,R)
    joint=np.block([[T@P@T.T+Q,C],[C.T,S]])
    schur=joint[:5,:5]-joint[:5,5:]@np.linalg.solve(joint[5:,5:],joint[5:,:5])
    assert_allclose(Pnext,schur,rtol=1e-10,atol=1e-10)
    assert np.linalg.eigvalsh(Pnext).min()>-1e-10
    return Pnext


def test_switching_changes_conditional_covariance():
    P=np.eye(2);Q=.02*np.eye(2);R=.1*np.eye(1)
    T0=np.array([[.94,.08],[-.20,.96]]);T1=np.array([[1,.08],[-.40,.90]])
    J0=np.array([[1,.4]]);J1=np.array([[1,-.3]])
    Pnext0,S0,C0=p07_next_covariance(P,T0,J0,Q,R)
    Pnext1,S1,C1=p07_next_covariance(P,T1,J1,Q,R)
    assert np.linalg.norm(Pnext0-Pnext1)>0.1
    return float(np.linalg.norm(Pnext0-Pnext1))

if __name__=='__main__':
    test_schur_equals_joint_conditional()
    print('PASS: switched local Riccati matches Schur complement')
    diff=test_switching_changes_conditional_covariance()
    print(f'PASS: different modes produce different conditional P (Frobenius gap={diff:.5f})')
