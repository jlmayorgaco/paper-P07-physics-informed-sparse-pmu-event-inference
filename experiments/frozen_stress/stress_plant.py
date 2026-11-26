"""Perturb only the plant. Keep nominal PMU references and integrate simultaneous active stamps."""
import csv
import os
from pathlib import Path
from dataclasses import dataclass
import networkx as nx
import numpy as np
from scipy.optimize import root
from design_stress import c,SEED
from plant import integrate,noise,FRAMES


@dataclass
class Equilibrium:
    y:np.ndarray
    voltage:np.ndarray
    transfer:np.ndarray
    state:np.ndarray
    pm:np.ndarray
    shunts:np.ndarray
    error:float


class StressPlant:
    def __init__(self):
        self.sim=c.design.Generator()
        self.plant=p=self.sim.plant
        self.gi=np.array(p.gi)
        with (Path(os.environ["P07_SCIENCE_ARCHIVE"])/"data/topology/ieee39/branches_physical.csv").open() as f:
            self.graph=nx.Graph((int(row["from_bus"]),int(row["to_bus"])) for row in csv.DictReader(f))
        self.stamps={}
        for name,r in self.sim.lines.items():
            a,b=int(r.from_bus)-1,int(r.to_bus)-1
            tap=r.tap*np.exp(1j*np.deg2rad(r.shift_deg))
            series=1/complex(r.r,r.x)
            diag=series+.5j*r.b
            self.stamps[name]=(np.ix_([a,b],[a,b]),np.array([[diag/abs(tap)**2,-series/tap.conjugate()],
                                                            [-series/tap,diag]]))
        self.terminals=[f"LINE{min(k.src,k.dst)}-{max(k.src,k.dst)}" for k in self.sim.exp.mapping.itertuples()]
        self.adm=np.zeros(39,complex)
        for b,s in p.base_load.items():
            self.adm[b-1]=np.conj(s)/p.net.vbase[b]**2
        v=self.sim.exp.v0
        self.sbase=np.conj(self.adm)*abs(v)**2
        self.wire=p.Y0-np.diag(self.adm)
        self.cache={}

    def equilibrium(self,load,opened):
        key=(load,tuple(sorted(opened)))
        if key in self.cache:
            return self.cache[key]
        p=self.plant
        if load==1. and not opened:
            eq=Equilibrium(p.Y0+p.Yg,self.sim.exp.v0,p.zg(()),p.init_state(),p.Pm,self.adm,0.)
        else:
            wire=self.wire.copy()
            for name in opened:
                idx,stamp=self.stamps[name]
                wire[idx]-=stamp
            demand=load*self.sbase
            # Preserve the base dispatch participation. The last generator supplies
            # the remaining active losses. Internal voltage magnitudes stay fixed.
            desired=p.Pm*(1+np.sum((demand-self.sbase).real)/p.Pm.sum())
            def unpack(w):
                v=w[:39]+1j*w[39:78]
                angles=np.r_[w[78:],p.d0[-1]]
                emf=p.mag*np.exp(1j*angles)
                current=p.yg*(emf-v[self.gi])
                power=(emf*np.conj(current)).real
                return v,angles,current,power
            def residual(w):
                v,_,current,power=unpack(w)
                mismatch=wire@v+np.conj(demand/v)
                mismatch[self.gi]-=current
                return np.r_[mismatch.real,mismatch.imag,power[:-1]-desired[:-1]]
            v0=self.sim.exp.v0
            guess=np.r_[v0.real,v0.imag,p.d0[:-1]]
            # Continue the physical load path for larger redispatches, using the
            # last converged high-voltage solution as the next initial condition.
            if abs(load-1)>.075:
                prev=self.equilibrium(1+round((load-1)*.8,4),opened)
                guess=np.r_[prev.voltage.real,prev.voltage.imag,prev.state[:9]]
            sol=root(residual,guess,tol=1e-10)
            v,angles,_,pm=unpack(sol.x)
            err=float(np.max(abs(residual(sol.x))))
            if not np.isfinite(err) or err>1e-7 or min(abs(v))<.70 or max(abs(v))>1.30:
                raise ValueError(f"Unusable AC equilibrium {key}: residual {err}, Vmin {min(abs(v))}")
            shunts=np.conj(demand)/abs(v)**2
            y=wire+np.diag(shunts)+p.Yg
            transfer=np.linalg.inv(y)[:,self.gi]
            np.testing.assert_allclose(transfer@(p.yg*p.mag*np.exp(1j*angles)),v,atol=2e-7,rtol=0)
            eq=Equilibrium(y,v,transfer,np.r_[angles,np.zeros(10),pm],pm,shunts,err)
        self.cache[key]=eq
        return eq

    def outages(self,events,index):
        rng=np.random.default_rng([SEED,3020,index])
        event_lines={e["source"] for e in events if e["code"]==2}
        candidates=sorted(set(self.stamps)-event_lines)
        opened=[]
        rejected=0
        for name in rng.permutation(candidates):
            trial=opened+[str(name)]
            changed=self.graph.copy()
            changed.remove_edges_from(tuple(map(int,s[4:].split("-"))) for s in trial+sorted(event_lines))
            if not nx.is_connected(changed):
                rejected+=1
                continue
            try:
                self.equilibrium(1.,trial)
                if len(trial)==1:
                    self.equilibrium(1.1,trial)
            except ValueError:
                rejected+=1
                continue
            opened=trial
            if len(opened)==2:
                return opened,rejected
        raise ValueError("No nested connected outage pair with a feasible pre-event equilibrium")

    def simulate(self,events,load,opened,seed):
        sim=self.sim
        p=self.plant
        eq=self.equilibrium(load,opened)
        rng=np.random.default_rng(seed)
        h=sim.dynamics.H*rng.uniform(.8,1.2)
        d=sim.dynamics.D*rng.uniform(.8,1.2)
        x=eq.state.copy()
        volt=np.empty((FRAMES,39),complex)
        disconnected=np.zeros((FRAMES,8),bool)
        times=sorted({0,FRAMES}|{t for e in events for t in (e["onset"],e["end"])})
        for a,b in zip(times,times[1:]):
            active=[e for e in events if e["onset"]<=a<e["end"]]
            y=eq.y.copy()
            disconnected_lines=set(opened)
            torque=np.zeros(10)
            for e in active:
                code,site,amp=e["code"],e["source"],e["strength"]
                if code==2:
                    idx,stamp=self.stamps[site]
                    y[idx]-=stamp
                    disconnected_lines.add(site)
                else:
                    bus=int(site[3:])
                    if code==1:
                        y[bus-1,bus-1]+=4*amp/p.net.vbase[bus]**2
                    elif code==3:
                        torque[sim.dynamics.GEN.index(bus)]+=.1*amp
                    elif code==4:
                        y[bus-1,bus-1]+=.1*amp*eq.shunts[bus-1]
            for j,branch in enumerate(self.terminals):
                disconnected[a:b,j]=branch in disconnected_lines
            transfer=np.linalg.inv(y)[:,self.gi] if active else eq.transfer
            x,volt[a:b]=integrate(x,np.ascontiguousarray(transfer),self.gi,p.mag,p.yg,eq.pm,h,d,torque,b-a)
        exp=sim.exp
        v=volt[:,p.pm]/exp.v0[p.pm]
        current=(volt@exp.b.T)*exp.factor
        current[disconnected]=0
        mag=np.maximum(0,abs(current)+exp.mag.center+noise(exp.mag,rng))
        angle=np.rad2deg(np.angle(current/exp.i0))+noise(exp.ang,rng)
        out=np.stack((np.log(abs(v))+rng.normal(0,.001,v.shape),np.angle(v)+rng.normal(0,.001,v.shape),
                      mag,(angle+180)%360-180,np.ones_like(mag)),axis=2)
        if not np.isfinite(out).all():
            raise ValueError("Nonfinite PMU record")
        return out.astype("float32")
