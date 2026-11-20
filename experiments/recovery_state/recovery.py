"""Fit the preceding switched-network trajectory using only PMUs seen before the forecast."""
import numpy as np
from numba import njit

import design
from intervention_monitor import Observer
from operators import filter_args, innovations, network

# Nominal IEEE-39 classical machine data on the system base (history_conditioning/dynamics.py).
INERTIA = np.array([42.,30.3,35.8,28.6,26.,34.8,26.4,24.3,34.5,500.])


@njit(cache=True)
def derivative(x,power,p0,inertia,damping):
    cs,sn=np.cos(x[:10]),np.sin(x[:10])
    f=np.empty(30)
    for i in range(10):
        pe=0.
        for j in range(10):
            pe+=(power[i,j].real*(cs[i]*cs[j]+sn[i]*sn[j])
                 -power[i,j].imag*(sn[i]*cs[j]-cs[i]*sn[j]))
        w=x[10+i]
        f[i]=2*np.pi*60*w
        f[10+i]=(p0[i]+x[20+i]-pe-damping*w)/(2*inertia[i])
        f[20+i]=(-p0[i]*w/.05-x[20+i])/.5
    return f


@njit(cache=True)
def trajectory(duration,length,field,power,field0,power0,p0,bias,floor,center,scale,inertia,damping):
    x=np.zeros(30)
    out=np.empty((length,31))
    dt=1/60
    for k in range(length):
        y=power if k<duration else power0
        for _ in range(2):
            k1=derivative(x,y,p0,inertia,damping)
            k2=derivative(x+.5*dt*k1,y,p0,inertia,damping)
            k3=derivative(x+.5*dt*k2,y,p0,inertia,damping)
            k4=derivative(x+dt*k3,y,p0,inertia,damping)
            x+=dt*(k1+2*k2+2*k3+k4)/6
        terminal=(field if k<duration else field0)@np.exp(1j*x[:10])
        for j in range(8):
            out[k,j]=np.log(abs(terminal[j]))
            out[k,8+j]=np.angle(terminal[j])
            i=terminal[8+j]
            r=max(0.,abs(i)+bias[j])
            out[k,16+j]=r
            if j<7:
                out[k,24+j]=min(1.,r/floor[j])*i.imag/abs(i) if abs(i)>0 else 0.
        out[k]=(out[k]-center)/scale
    return out


def shunt_coefficient(op,modes):
    # A shunt is a rank-one update. Its AC response varies as a/(1+z*a);
    # determine z from two nominal network solves, independently for terminal and power maps.
    first,mid=modes[:2]
    a=1+.3*np.polynomial.legendre.leggauss(3)[0][0]
    delta=op[first]-op[0]
    ratio=np.vdot(delta,op[mid]-op[0])/np.vdot(delta,delta)
    return (1/a-ratio)/(ratio-1)


class Dynamics:
    def __init__(self,model):
        self.net=network()
        self.params=filter_args(model)
        self.model=model
        self.shunts={}
        for g in np.flatnonzero(model["code"]==1):
            modes=np.flatnonzero(self.net["group"]==g)
            self.shunts[g]=tuple(shunt_coefficient(self.net[key],modes) for key in ("field","power"))

    def wave(self,group,duration,theta,length):
        net,m=self.net,self.model
        modes=np.flatnonzero(net["group"]==group)
        nominal=modes[len(modes)//2]
        field,power=net["field"][nominal],net["power"][nominal]
        if group in self.shunts:
            a=theta[0]
            zf,zp=self.shunts[group]
            field=net["field"][0]+(field-net["field"][0])*a*(1+zf)/(1+a*zf)
            power=net["power"][0]+(power-net["power"][0])*a*(1+zp)/(1+a*zp)
        raw=trajectory(duration,length,field,power,net["field"][0],net["power"][0],net["p0"][0],net["bias"],
                       m["floor"],m["center"],m["scale"],INERTIA*theta[1],4*theta[2])
        return innovations(raw,*self.params)


class Continuation:
    """Robust local MAP of fault strength, common machine inertia and damping multipliers."""
    def __init__(self,physics,group,start,duration,z):
        self.physics,self.group=physics,group
        self.theta=np.ones(3)
        self.active=np.array([0,1,2] if group in physics.shunts else [1,2])
        self.start,self.duration=start,duration
        self.precision=np.diag(1/np.array([.25,.18,.25])[self.active]**2)
        self.last_fit=-1
        # Profile mechanical parameters at each possible onset. A fixed-inertia
        # comparison can explain a faster swing by moving the onset one sample.
        candidates=[]
        for t in range(start-1,start+2):
            if t<30:
                continue
            prefix_loss=self.loss(z[max(30,start-1):t])
            times=[]
            for end in range(start+duration-2,start+duration+3):
                if end<=t or end>=len(z):
                    continue
                r=z[t:]-physics.wave(group,end-t,np.ones(3),len(z)-t)
                times.append((self.loss(r),end-t))
            if times:
                self.start=t
                _,self.duration=min(times)
                theta,_=self.optimize(z,np.ones(3))
                for _,d in times:
                    pred=physics.wave(group,d,theta,len(z)-t)
                    offset=theta[self.active]-1
                    loss=self.loss(z[t:]-pred)+prefix_loss+offset@self.precision@offset
                    candidates.append((loss,t,d,theta))
        if candidates:
            _,self.start,self.duration,self.theta=min(candidates,key=lambda item:item[0])
        self.fit(z)

    @staticmethod
    def loss(residual):
        return float(np.sum(34*np.log1p(np.sum(residual**2,axis=1)/3)))

    def optimize(self,z,theta):
        y=z[self.start:]
        n=len(y)
        def wave(theta):
            return self.physics.wave(self.group,self.duration,theta,n)
        predicted=wave(theta)
        for _ in range(6):
            residual=y-predicted
            w=34/(3+np.sum(residual**2,axis=1))
            jac=np.stack([(wave(theta+np.eye(3)[j]*.0002)-predicted)/.0002 for j in self.active],axis=2)
            normal=np.einsum("tci,t,tcj->ij",jac,w,jac)+self.precision
            rhs=np.einsum("tci,t,tc->i",jac,w,residual)-self.precision@(theta[self.active]-1)
            direction=np.linalg.solve(normal,rhs)
            old=self.loss(residual)+(theta[self.active]-1)@self.precision@(theta[self.active]-1)
            accepted=False
            for fraction in (1.,.5,.25,.125):
                trial=theta.copy()
                trial[self.active]+=fraction*direction
                trial=np.clip(trial,[.6,.65,.5],[1.4,1.35,1.5])
                new=wave(trial)
                offset=trial[self.active]-1
                if self.loss(y-new)+offset@self.precision@offset < old:
                    theta,predicted=trial,new
                    accepted=True
                    break
            if not accepted or np.max(abs(direction))<1e-5:
                break
        return theta,normal

    def fit(self,z):
        n=len(z)-self.start
        theta,normal=self.optimize(z,self.theta)
        self.theta=theta
        self.last_fit=n
        self.predicted=self.physics.wave(self.group,self.duration,theta,n+65)
        self.cov=np.linalg.inv(normal)
        horizon=n+65
        j=np.stack([(self.physics.wave(self.group,self.duration,theta+np.eye(3)[i]*.0002,horizon)
                      -self.predicted)/.0002 for i in self.active],axis=2)
        self.spread=np.einsum("tci,ij,tcj->t",j,self.cov,j)/31

    def predict(self,tick,z,adapt):
        age=tick-self.start
        # Leave a guard interval so an emerging second intervention does not
        # immediately enter the nuisance estimate.
        if adapt and self.last_fit < self.duration+120 and age-self.last_fit>=30:
            self.fit(z[:tick-9])
        if age>=len(self.predicted):
            self.predicted=self.physics.wave(self.group,self.duration,self.theta,age+65)
            self.spread=np.pad(self.spread,(0,len(self.predicted)-len(self.spread)),mode="edge")
        return self.predicted[age],self.spread[age]


class RecoveryObserver(Observer):
    def __init__(self,bank,model,config,physics):
        super().__init__(bank,model,config)
        self.physics=physics
        self.post_gate=config["post_gate"]
        self.samples=[np.zeros(31) for _ in range(30)]
        self.first=None
        self.twin=None
        self.adapt=True

    def _scan(self,z,v):
        self.samples.append(z)
        if self.first is not None and self.twin is None and self.previous is not None:
            start,ids,logw=self.previous
            age=self.k-start
            durations=self.bank.duration[ids]
            if np.exp(logw[durations<=age-7]).sum()>.99:
                duration=int(durations[np.argmax(logw)])
                self.twin=Continuation(self.physics,self.first,start,duration,np.asarray(self.samples[:-1]))
                self.previous=None
                self.carry.fill(0)
                self.context=0
                self.count=0
                self.history.clear()
                self.threshold=self.post_gate
        if self.twin is not None:
            mean,spread=self.twin.predict(self.k,self.samples,self.adapt)
            z=z-mean
            v=1.+spread
        alerts=super()._scan(z,v)
        if alerts:
            if self.first is None and self.context in (1,2) and self.adapt:
                self.first=int(np.flatnonzero((self.bank.code==self.context)&
                                              (self.bank.site==alerts[0]["source"]))[0])
            else:
                self.adapt=False
                self.first=None
        return alerts


def monitor(record,bank,model,config,physics):
    observer=RecoveryObserver(bank,model,config,physics)
    return [a for report in record for a in observer.step(report)]
