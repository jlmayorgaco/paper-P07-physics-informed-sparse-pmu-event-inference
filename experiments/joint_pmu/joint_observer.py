"""Causal event proposals followed by a switched-history PMU likelihood fit."""
from dataclasses import replace
import numpy as np
from joint_physics import Episode,fit,loss_rows
from intervention_monitor import Observer


class JointObserver(Observer):
    def __init__(self,bank,model,cfg,physics):
        super().__init__(bank,model,cfg)
        self.physics=physics
        self.theta=np.ones(2)
        self.events=[]
        self.data=[np.zeros(31) for _ in range(30)]
        self.active=False
        self.proposal=None
        self.forecast=np.zeros((720,31))
        self.path=np.zeros((721,91))
        self.post_gate=cfg["post_gate"]
        self.next_fit=None
        self.last_clear=30
        self.scale_evidence=[]

    def _commit(self,start,group):
        # This is only a proposal; do not alter the committed null or announce it.
        self.proposal=(start,group)

    def refresh(self,end):
        if self.events:
            self.forecast,self.path=self.physics.history(self.events,self.theta,end)
        else:
            self.forecast=np.zeros((end,31))
            self.path=np.zeros((end+1,91))

    def physical_candidate(self,start):
        if self.k-start<5:
            return None
        low=max(self.last_clear,start-4,30)
        ticks=range(low,min(self.k,start+4)+1)
        y=np.asarray(self.data)
        shortlist={}
        scores={code:[] for code in range(1,5)}
        for t in ticks:
            for g in range(1,len(self.bank.code)):
                code=self.bank.code[g]
                n=min(self.k+1-t,int(self.model["dmin"][code-1]))
                prior=self.forecast[t:t+n]
                residual=y[t:t+n]-prior
                null=loss_rows(residual).sum()
                wave,_=self.physics.propagate(self.path[t],g,1.,self.theta,n)
                mark=wave-prior
                # Initial scalar amplitude projection only ranks candidates.
                amp=1. if code==2 else np.clip(np.vdot(mark,residual)/max(1e-10,np.vdot(mark,mark)),.65,1.35)
                gain=null-loss_rows(residual-amp*mark).sum()
                scores[code].append((gain,int(g),t,float(amp)))
        # Refine the leading sites at their best starts using the nonlinear operator.
        for candidates in scores.values():
            added=0
            for score,g,t,amp in sorted(candidates,reverse=True):
                if g not in shortlist:
                    shortlist[g]=(t,amp)
                    added+=1
                    if added==4:
                        break
        choices=[]
        for g,(onset,amp) in shortlist.items():
            code=self.bank.code[g]
            dmin=int(self.model["dmin"][code-1])
            for t in range(max(low,onset-2),min(self.k,onset+2)+1):
                n=self.k+1-t
                base=self.forecast[t:self.k+1]
                null=loss_rows(y[t:self.k+1]-base).sum()
                amplitude=amp
                initial=self.path[t]
                # Profile amplitude from the part certain to precede return.
                if code!=2:
                    support=min(dmin,n)
                    for _ in range(2):
                        wave,_=self.physics.propagate(initial,g,amplitude,self.theta,support)
                        plus,_=self.physics.propagate(initial,g,amplitude+.001,self.theta,support)
                        jac=(plus-wave)/.001
                        r=y[t:t+support]-wave
                        w=34/(3+np.einsum("ij,ij->i",r,r))
                        delta=(np.sum(w[:,None]*jac*r)-16*(amplitude-1))/(np.sum(w[:,None]*jac**2)+16)
                        amplitude=float(np.clip(amplitude+delta,.65,1.35))
                        if abs(delta)<.001:
                            break
                wave,states=self.physics.propagate(initial,g,amplitude,self.theta,n)
                err=loss_rows(y[t:self.k+1]-wave)
                best=err.sum()
                if code!=3 and n>dmin:
                    for d in range(dmin,min(n,int(self.model["dmax"][code-1]))+1):
                        restored,_=self.physics.propagate(states[d],0,1.,self.theta,n-d)
                        best=min(best,err[:d].sum()+loss_rows(y[t+d:self.k+1]-restored).sum())
                choices.append((.5*(null-best-16*(amplitude-1)**2),g,t,amplitude))
        if not choices:
            return None
        gain,g,t,amp=max(choices)
        if gain<self.threshold:
            return None
        competing=max((item[0] for item in choices if item[1]!=g),default=-np.inf)
        if gain-competing<3:
            return None
        return Episode(g,t,int(self.model["dmax"][code-1])),amp

    def duration(self,y):
        e=self.events[-1]
        age=len(y)-e.start
        code=self.bank.code[e.group]
        dmin=int(self.model["dmin"][code-1])
        dmax=int(self.model["dmax"][code-1])
        ongoing,states=self.physics.propagate(self.path[e.start],e.group,self.theta[-1],self.theta,age)
        err=loss_rows(y[e.start:]-ongoing)
        # Equal prior on the admissible integer pulse lengths. All future clearing
        # times have the same likelihood as an ongoing pulse at the present report.
        loss=np.full(dmax-dmin+1,err.sum())
        for d in range(dmin,min(age,dmax+1)):
            tail,_=self.physics.propagate(states[d],0,1.,self.theta,age-d)
            loss[d-dmin]=err[:d].sum()+loss_rows(y[e.start+d:]-tail).sum()
        weights=np.exp(-.5*(loss-loss.min()))
        probability=weights[np.arange(dmin,dmax+1)<=age-3].sum()/weights.sum()
        return dmin+int(loss.argmin()),probability

    def refine_switch(self,y):
        e=self.events[-1]
        code=self.bank.code[e.group]
        left=max(self.last_clear,e.start-2)
        best=(float("inf"),e.start,e.duration)
        # The prefix through each proposed onset must contain only earlier events.
        if len(self.events)>1:
            previous,states=self.physics.history(self.events[:-1],self.theta[:-1],len(y))
        else:
            previous=np.zeros_like(y)
            states=np.zeros((len(y)+1,91))
        for t in range(left,min(e.start+3,len(y))):
            n=len(y)-t
            active,path=self.physics.propagate(states[t],e.group,self.theta[-1],self.theta,n)
            fit_before=loss_rows(y[left:t]-previous[left:t]).sum()
            for end in range(e.start+e.duration-2,e.start+e.duration+3):
                d=end-t
                if not self.model["dmin"][code-1]<=d<=self.model["dmax"][code-1] or d>=n:
                    continue
                clear,_=self.physics.propagate(path[d],0,1.,self.theta,n-d)
                value=fit_before+loss_rows(y[t:end]-active[:d]).sum()+loss_rows(y[end:]-clear).sum()
                best=min(best,(value,t,d))
        self.events[-1]=replace(e,start=best[1],duration=best[2])

    def track(self):
        e=self.events[-1]
        age=self.k+1-e.start
        code=self.bank.code[e.group]
        if self.k%3 or age<self.model["dmin"][code-1]+3:
            return
        y=np.asarray(self.data)
        if not self.initial_fit:
            n=e.start+int(self.model["dmin"][code-1])
            self.theta=fit(self.physics,self.events,self.theta,y[:n],steps=4)
            self.refresh(self.k+2)
            self.initial_fit=True
        d,p=self.duration(y)
        if p<.99:
            return
        self.events[-1]=replace(e,duration=d)
        self.theta=fit(self.physics,self.events,self.theta,y)
        self.refine_switch(y)
        self.theta=fit(self.physics,self.events,self.theta,y)
        self.refresh(self.k+101)
        self.last_clear=self.events[-1].start+self.events[-1].duration
        self.active=False
        self.next_fit=self.k+24
        self.count=0
        self.history.clear()
        self.scale_evidence.clear()

    def _scan(self,z,v):
        self.data.append(z)
        if self.active:
            self.track()
            return []
        if self.next_fit is not None and self.k>=self.next_fit:
            self.theta=fit(self.physics,self.events,self.theta,np.asarray(self.data[:-9]),steps=3)
            self.next_fit=self.k+60 if self.k-self.last_clear<125 else None
            self.refresh(self.k+101)
        if self.k>=len(self.forecast):
            self.refresh(self.k+101)
        r=z-self.forecast[self.k]
        # A variance-change GLR is an additional onset proposal when a signature
        # computed at equilibrium misses the direction of a later perturbation.
        self.scale_evidence.append(.375*(r@r)-15.5*np.log(4.))
        self.scale_evidence=self.scale_evidence[-36:]
        self.proposal=None
        super()._scan(r,1. if self.events else v)
        if self.k%3:
            return []
        starts=[] if self.proposal is None else [self.proposal[0]]
        cumulative=np.cumsum(self.scale_evidence[::-1])
        age=int(np.argmax(cumulative))
        if cumulative[age]>self.threshold and all(abs(self.k-age-t)>4 for t in starts):
            starts.append(self.k-age)
        candidate=next((x for t in starts if (x:=self.physical_candidate(t)) is not None),None)
        if candidate is None:
            return []
        e,amp=candidate
        self.events.append(e)
        self.theta=np.append(self.theta,amp)
        self.active=True
        self.initial_fit=False
        self.threshold=self.post_gate
        self.next_fit=None
        self.count=0
        self.history.clear()
        self.scale_evidence.clear()
        return [dict(detected=self.k,published=self.k,code=int(self.bank.code[e.group]),
                     source=str(self.bank.site[e.group]),onset_est=e.start)]
