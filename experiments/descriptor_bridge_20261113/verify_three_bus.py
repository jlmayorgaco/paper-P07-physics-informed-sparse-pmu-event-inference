"""Independently reconstruct the attached illustrative AC model, not IEEE39."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import root
from scipy.linalg import expm
P=Path(__file__).resolve().parent
E=1.1;Xd=.26;M=4.;damp=1.5;delta=.24;S=.72+.25j;Vref=1.025
def realblock(y):return np.array([[y.real,-y.imag],[y.imag,y.real]])
def network(opened):
    Y=np.zeros((3,3),complex)
    for i,j,z in [(0,1,.02+.18j),(1,2,.02+.28j),(0,2,.025+.22j)]:
        if opened and (i,j)==(1,2):continue
        y=1/z;Y[i,i]+=y;Y[j,j]+=y;Y[i,j]-=y;Y[j,i]-=y
    return Y
def volts(z):return np.array([Vref,z[0]+1j*z[1],z[2]+1j*z[3]])
def g(x,z,a,Y):
    V=volts(z);r=Y@V;r[1]-=(E*np.exp(1j*x[0])-V[1])/(1j*Xd);r[2]+=np.conj((1+a)*S/V[2])
    return np.array([r[1].real,r[1].imag,r[2].real,r[2].imag])
def pe(x,z):return E/Xd*(z[0]*np.sin(x[0])-z[1]*np.cos(x[0]))
def solve(x,a,Y):
    r=root(lambda z:g(x,z,a,Y),[1.,0.,1.,0.],tol=1e-12);assert np.max(abs(r.fun))<1e-10;return r.x
def fd(fun,x,h=1e-6):
    eye=np.eye(len(x));return np.stack([(fun(x+h*e)-fun(x-h*e))/(2*h) for e in eye],axis=1)
def main():
    x=np.array([delta,0.]);z0=solve(x,0.,network(False));Pm=pe(x,z0);rows=[]
    for opened in [False,True]:
        Y=network(opened);z=solve(x,0.,Y)
        f=lambda xx,zz:np.array([xx[1],(Pm-pe(xx,zz)-damp*xx[1])/M])
        fx=np.array([[0,1],[-E/(M*Xd)*(z[0]*np.cos(delta)+z[1]*np.sin(delta)),-damp/M]])
        fz=np.array([[0,0,0,0],[-E*np.sin(delta)/(M*Xd),E*np.cos(delta)/(M*Xd),0,0]])
        gx=np.zeros((4,2));gx[:2,0]=[-E*np.cos(delta)/Xd,-E*np.sin(delta)/Xd]
        R,I=z[2:];dd=R*R+I*I;pp,qq=S.real,S.imag
        JL=np.array([[pp*dd-2*R*(pp*R+qq*I),qq*dd-2*I*(pp*R+qq*I)],[-qq*dd-2*R*(pp*I-qq*R),pp*dd-2*I*(pp*I-qq*R)]])/dd**2
        gz=np.block([[realblock(Y[1,1]-1j/Xd),realblock(Y[1,2])],[realblock(Y[2,1]),realblock(Y[2,2])+JL]])
        q=np.conj(S/volts(z)[2]);ga=np.array([0,0,q.real,q.imag])[:,None]
        A=fx-fz@np.linalg.solve(gz,gx);B=-fz@np.linalg.solve(gz,ga)
        h=lambda zz:np.array([abs(volts(zz)[1]),np.angle(volts(zz)[1]),abs((volts(zz)[1]-Vref)/(.02+.18j)),np.angle((volts(zz)[1]-Vref)/(.02+.18j))])
        Hz=fd(h,z);C=-Hz@np.linalg.solve(gz,gx);D=-Hz@np.linalg.solve(gz,ga)
        checks={k:float(np.max(abs(a-b))) for k,a,b in [('fx',fx,fd(lambda xx:f(xx,z),x)),('fz',fz,fd(lambda zz:f(x,zz),z)),('gx',gx,fd(lambda xx:g(xx,z,0.,Y),x)),('gz',gz,fd(lambda zz:g(x,zz,0.,Y),z)),('ga',ga,fd(lambda aa:g(x,z,aa[0],Y),np.array([0.])))]}
        aug=np.zeros((3,3));aug[:2,:2]=A;aug[:2,2:]=B;disc=expm(aug/30)
        rows.append({'mode':'open' if opened else 'closed','z':z.tolist(),'A':A.tolist(),'B':B.tolist(),'C':C.tolist(),'D':D.tolist(),'c':f(x,z).tolist(),'Ad':disc[:2,:2].tolist(),'Bd':disc[:2,2:].tolist(),'max_absolute_derivative_errors':checks})
    result={'scope':'Pedagogical three-bus constant-power model from supplied text; no IEEE39 validation','Pm':Pm,'modes':rows,'passed':max(v for r in rows for v in r['max_absolute_derivative_errors'].values())<1e-7}
    (P/'THREE_BUS_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['passed']
if __name__=='__main__':main()
