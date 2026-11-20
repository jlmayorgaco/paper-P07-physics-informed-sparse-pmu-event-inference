"""Switched nonlinear network in a common rotor and PMU-innovations reference frame."""
from dataclasses import dataclass,replace
import numpy as np
from numba import njit
import cohort_joint
from recovery import INERTIA,derivative,shunt_coefficient
from operators import filter_args,network


@dataclass(frozen=True)
class Episode:
    group:int
    start:int
    duration:int


@njit(cache=True)
def motion(x,power,p0,inertia,damping,torque):
    dx=derivative(x,power,p0,inertia,damping)
    dx[10:20]+=torque/(2*inertia)
    return dx


@njit(cache=True)
def segment(initial,n,field,power,p0,torque,inertia,damping,bias,floor,center,scale,a,h,ar,white,gain):
    # The last 61 coordinates are the common linear whitening filter state.
    states=np.empty((n+1,91))
    states[0]=initial
    z=np.empty((n,31))
    x=initial[:30].copy()
    dt=1/60
    for k in range(n):
        for _ in range(2):
            k1=motion(x,power,p0,inertia,damping,torque)
            k2=motion(x+.5*dt*k1,power,p0,inertia,damping,torque)
            k3=motion(x+.5*dt*k2,power,p0,inertia,damping,torque)
            k4=motion(x+dt*k3,power,p0,inertia,damping,torque)
            x+=dt*(k1+2*k2+2*k3+k4)/6
        terminal=field@np.exp(1j*x[:10])
        y=np.empty(31)
        for j in range(8):
            y[j]=np.log(abs(terminal[j]))
            y[8+j]=np.angle(terminal[j])
            current=terminal[8+j]
            amp=max(0.,abs(current)+bias[j])
            y[16+j]=amp
            if j<7:
                y[24+j]=min(1.,amp/floor[j])*current.imag/abs(current) if abs(current)>0 else 0.
        y=(y-center)/scale
        forecast=a@states[k,30:60]
        z[k]=white@(y-h@forecast-ar@states[k,60:])
        states[k+1,:30]=x
        states[k+1,30:60]=forecast+gain@z[k]
        states[k+1,60:]=y-h@states[k+1,30:60]
    return z,states


class Physics:
    def __init__(self,model):
        net=network()
        self.model=model
        self.args=(net["bias"],model["floor"],model["center"],model["scale"],*filter_args(model))
        self.fields=net["field"]
        self.powers=net["power"]
        self.p0=net["p0"][0]
        self.zero=np.zeros(10)
        self.modes=[np.flatnonzero(net["group"]==g) for g in range(len(model["code"]))]
        self.zcoef={}
        for g,code in enumerate(model["code"]):
            if code in (1,4):
                self.zcoef[g]=[shunt_coefficient(x,self.modes[g]) for x in (self.fields,self.powers)]
        self.machines=sorted(int(s[3:]) for s in model["site"][model["code"]==3])

    def propagate(self,state,g,amp,theta,n):
        modes=self.modes[g]
        j=modes[len(modes)//2]
        field,power=self.fields[j],self.powers[j]
        torque=self.zero
        if g in self.zcoef:
            zf,zp=self.zcoef[g]
            field=self.fields[0]+(field-self.fields[0])*amp*(1+zf)/(1+amp*zf)
            power=self.powers[0]+(power-self.powers[0])*amp*(1+zp)/(1+amp*zp)
        if self.model["code"][g]==3:
            torque=self.zero.copy()
            torque[self.machines.index(int(self.model["site"][g][3:]))]=.1*amp
        return segment(state,n,field,power,self.p0,torque,INERTIA*theta[0],4*theta[1],*self.args)

    def history(self,events,theta,end):
        # Entry i holds the state immediately BEFORE report i. At a switch the
        # rotor state is continuous and the voltage/current operator changes.
        z=np.zeros((end,31))
        states=np.zeros((end+1,91))
        tick=events[0].start
        def advance(stop,group,amp):
            nonlocal tick
            if stop>tick:
                wave,path=self.propagate(states[tick],group,amp,theta,stop-tick)
                z[tick:stop]=wave
                states[tick+1:stop+1]=path[1:]
                tick=stop
        for i,e in enumerate(events):
            if e.start>=end:
                break
            advance(e.start,0,1.)
            advance(min(end,e.start+e.duration),e.group,theta[2+i])
        advance(end,0,1.)
        return z,states


def loss_rows(r):
    return 34*np.log1p(np.einsum("ij,ij->i",r,r)/3)


def fit(physics,events,theta,z,steps=5):
    start=events[0].start
    active=[0,1]+[i+2 for i,e in enumerate(events) if physics.model["code"][e.group]!=2]
    scale=np.array([.18,.25]+[.25]*len(events))[active]
    precision=np.diag(1/scale**2)
    def wave(params):
        return physics.history(events,params,len(z))[0][start:]
    pred=wave(theta)
    for _ in range(steps):
        r=z[start:]-pred
        w=34/(3+np.einsum("ij,ij->i",r,r))
        jac=np.stack([(wave(theta+np.eye(len(theta))[j]*.0002)-pred)/.0002 for j in active],axis=2)
        normal=np.einsum("tci,t,tcj->ij",jac,w,jac)+precision
        offset=theta[active]-1.
        delta=np.linalg.solve(normal,np.einsum("tci,t,tc->i",jac,w,r)-precision@offset)
        objective=loss_rows(r).sum()+offset@precision@offset
        for fraction in (1.,.5,.25,.125):
            trial=theta.copy()
            trial[active]+=fraction*delta
            trial=np.clip(trial,[.68,.5]+[.62]*len(events),[1.32,1.5]+[1.38]*len(events))
            future=wave(trial)
            offset=trial[active]-1.
            if loss_rows(z[start:]-future).sum()+offset@precision@offset<objective:
                theta,pred=trial,future
                break
        else:
            break
        if np.max(abs(delta))<1e-5:
            break
    return theta
