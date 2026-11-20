"""Continuous IEEE-39 plant and measurements for disjoint supervised trajectories."""
import hashlib
import json
import os
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from numba import njit

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"branch_current_trial"))
from run import ARCHIVE, Experiment, dyn

FS = 30
FRAMES = 24*FS
PMUS = list(dyn.PMU)
DATA = HERE.parents[1]/"tmp/supervised_stream"
SEEDS = {"train":710993, "test":845219}


@njit
def derivative(x, transfer, mag, yg, pm, h, damping, torque):
    emf = mag*np.exp(1j*x[:10])
    terminal = transfer @ (yg*emf)
    electric = (emf*np.conj(yg*(emf-terminal))).real
    w, pt = x[10:20],x[20:]
    return np.concatenate((2*np.pi*60*w,(pt-electric-damping*w+torque)/(2*h),
                           (pm-(pm/.05)*w-pt)/.5))


@njit
def integrate(x, transfer, generator_rows, mag, yg, pm, h, damping, torque, count):
    result = np.empty((count,39),np.complex128)
    internal = np.ascontiguousarray(transfer[generator_rows])
    dt = 1/120.
    for t in range(count):
        for _ in range(4):
            a = derivative(x,internal,mag,yg,pm,h,damping,torque)
            b = derivative(x+dt*a/2,internal,mag,yg,pm,h,damping,torque)
            c = derivative(x+dt*b/2,internal,mag,yg,pm,h,damping,torque)
            d = derivative(x+dt*c,internal,mag,yg,pm,h,damping,torque)
            x = x+dt*(a+2*b+2*c+d)/6
        result[t] = transfer@(yg*mag*np.exp(1j*x[:10]))
    return x,result


@njit
def ar(states, transition):
    for k in range(1,len(states)):
        states[k] += transition@states[k-1]
    return states


def noise(model,rng):
    innovations=rng.multivariate_normal(np.zeros(len(model.q)),model.q,size=FRAMES+199)
    return np.clip(ar(innovations,model.transition)[199:]@model.loading,-8,8)*model.scale


class Generator:
    def __init__(self):
        self.exp=Experiment()
        self.plant=self.exp.plant
        br=pd.read_csv(ARCHIVE/"data/topology/ieee39/branches_physical.csv")
        graph=nx.from_pandas_edgelist(br,"from_bus","to_bus")
        bridges={tuple(sorted(edge)) for edge in nx.bridges(graph)}
        self.lines={f"LINE{min(r.from_bus,r.to_bus)}-{max(r.from_bus,r.to_bus)}":r
                    for r in br.itertuples() if tuple(sorted((r.from_bus,r.to_bus))) not in bridges}
        buses=[f"BUS{b}" for b in range(1,40)]
        generators=[f"BUS{b}" for b in dyn.GEN]
        sensors=[f"PMU{b}" for b in PMUS]
        self.catalog={1:buses,2:sorted(self.lines),3:generators,
                      4:[f"BUS{b}" for b,s in self.plant.base_load.items() if s.real>0],
                      5:sensors,6:generators,7:sensors,8:buses}

    def schedule(self,rng):
        n=rng.choice(4,p=[.20,.25,.35,.20])
        if not n:
            return []
        # Uniform discrete onsets subject to minimum separation and a quiet prefix/tail.
        starts=np.sort(rng.choice(np.arange(60,FRAMES-90-120*(n-1)),n,replace=False))+120*np.arange(n)
        events=[]
        for t in starts:
            if events and rng.random()<.22:
                code,source=events[-1]["code"],events[-1]["source"]
            else:
                code=int(rng.integers(1,9))
                source=str(rng.choice(self.catalog[code]))
            span={1:(5,12),2:(22,58),3:(27,65),4:(27,65),5:(14,36),6:(27,60),7:(16,40),8:(28,62)}
            duration=int(rng.integers(span[code][0],span[code][1]+1))
            sensors=rng.choice(PMUS,2,replace=False).tolist()
            events.append(dict(code=code,source=source,onset=int(t),end=int(t)+duration,
                               strength=float(rng.uniform(.7,1.3)),sensors=sensors))
        return events

    def simulate(self,events,rng,nominal=False):
        exp,p=self.exp,self.plant
        h=dyn.H*rng.uniform(.8,1.2)
        damping=dyn.D*rng.uniform(.8,1.2)
        if nominal:
            h,damping=dyn.H,dyn.D
        z0=np.ascontiguousarray(p.zg(()))
        x=p.init_state()
        v=np.empty((FRAMES,39),complex)
        disconnected=np.zeros((FRAMES,8),bool)
        def segment(first,last,z,torque):
            nonlocal x
            if last>first:
                x,v[first:last]=integrate(x,np.ascontiguousarray(z),np.asarray(p.gi),
                    p.mag,p.yg,p.Pm,h,damping,torque,last-first)
        cursor=0
        for event in events:
            on,off=event["onset"],event["end"]
            segment(cursor,on,z0,np.zeros(10))
            code,s,a=event["code"],event["source"],event["strength"]
            y=p.Y0+p.Yg
            torque=np.zeros(10)
            if code in (1,4,8):
                b=int(s[3:])
                demand={1:4.,4:.1*p.base_load.get(b,0),8:.01}[code]
                y[b-1,b-1]+=np.conj(a*demand)/p.net.vbase[b]**2
            elif code in (3,6):
                torque[dyn.GEN.index(int(s[3:]))]=.1*a
            elif code==2:
                r=self.lines[s]
                i,j=r.from_bus-1,r.to_bus-1
                tap=r.tap*np.exp(1j*np.deg2rad(r.shift_deg))
                ys=1/complex(r.r,r.x)
                diag=ys+.5j*r.b
                y[np.ix_([i,j],[i,j])]-=np.array([[diag/abs(tap)**2,-ys/tap.conjugate()],[-ys/tap,diag]])
                for k,m in enumerate(exp.mapping.itertuples()):
                    if {m.src,m.dst}=={i+1,j+1}:
                        disconnected[on:off,k]=True
            segment(on,off,np.linalg.inv(y)[:,p.gi],torque)
            cursor=off
        segment(cursor,FRAMES,z0,np.zeros(10))
        voltage=v[:,p.pm]/exp.v0[p.pm]
        current=(v@exp.b.T)*exp.factor
        current[disconnected]=0
        mag=np.maximum(0,abs(current)+exp.mag.center+(0 if nominal else noise(exp.mag,rng)))
        angles=np.rad2deg(np.angle(current/exp.i0))+(0 if nominal else noise(exp.ang,rng))
        obs=np.stack((np.log(abs(voltage))+(0 if nominal else rng.normal(0,.001,voltage.shape)),
                      np.angle(voltage)+(0 if nominal else rng.normal(0,.001,voltage.shape)),
                      mag, (angles+180)%360-180, np.ones_like(mag)),axis=2)
        for e in events:
            code,s=e["code"],e["source"]
            lo,hi=e["onset"],e["end"]
            if code in (5,6):
                sensor=int(s[3:]) if code==5 else e["sensors"][0]
                k=PMUS.index(sensor)
                begin=lo+(4 if code==6 else 0)
                obs[begin:hi,k,:]=0
            elif code==7:
                k=PMUS.index(int(s[3:]))
                obs[lo:hi,k,0]+=.015*e["strength"]
                obs[lo:hi,k,2]+=25*e["strength"]
            elif code==8:
                k=PMUS.index(e["sensors"][0])
                obs[lo+6:hi,k,2]*=1+.30*e["strength"]
        assert np.isfinite(obs).all()
        return obs.astype("float32")


def generate(split, count=None, seed=None, data=DATA, output=HERE):
    folder=data/split
    folder.mkdir(parents=True,exist_ok=True)
    simulator=Generator()
    if count is None:
        count=700 if split=="train" else 300
    seed=SEEDS[split] if seed is None else seed
    seeds=np.random.SeedSequence(seed).spawn(count)
    truth=[]
    array=np.lib.format.open_memmap(folder/"observations.npy",mode="w+",dtype="float32",
                                    shape=(count,FRAMES,8,5))
    for i,child_seed in enumerate(seeds):
        rng=np.random.default_rng(child_seed)
        events=simulator.schedule(rng)
        array[i]=simulator.simulate(events,rng)
        truth.append(events)
    array.flush()
    (folder/"truth.json").write_text(json.dumps(truth))
    summary={"seed":seed,"records":count,"events":sum(map(len,truth)),
             "normal_records":sum(not seq for seq in truth),
             "sha256_observations":hashlib.file_digest(open(folder/"observations.npy","rb"),"sha256").hexdigest(),
             "sha256_truth":hashlib.sha256((folder/"truth.json").read_bytes()).hexdigest()}
    (output/f"{split}_manifest.json").write_text(json.dumps(summary,indent=2))
    print(summary,flush=True)
