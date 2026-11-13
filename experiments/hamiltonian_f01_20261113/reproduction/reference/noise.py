"""Stateful port of the frozen R5C.2 instrumental noise equations.

Only seeded innovations are generated. No observations or residual traces are
accepted. Per-family RNG streams make prefixes and chunked execution stable;
this changes the seed mapping, not the archived covariance/AR parameters.
The legacy level-addition semantics are preserved and explicitly audited.
"""
import copy
import numpy as np

def psd(cov):
    cov=(np.asarray(cov,float)+np.asarray(cov,float).T)/2
    values,vectors=np.linalg.eigh(cov)
    return vectors@np.diag(np.maximum(values,1e-12))@vectors.T

class NoiseStream:
    def __init__(self, model, seed):
        self.model=model
        self.order=list(model['families'])
        self.seed=int(seed)
        self.frames=0
        self.family={}
        streams=np.random.SeedSequence(self.seed).spawn(len(self.order))
        for name,child in zip(self.order,streams):
            spec=model['families'][name]
            self.family[name]=dict(rng=np.random.default_rng(child),
                z=np.zeros(spec['rank']),local=np.zeros(len(model['pmu_order'])),
                A=np.asarray(spec['VAR1_transition']),load=np.asarray(spec['loadings']),
                phi=np.asarray(spec['PMU_local_AR1']),cov=psd(spec['innovation_covariance']),
                local_cov=psd(spec['PMU_local_innovation_covariance']),
                center=np.asarray(spec['normalization_center']),scale=spec['normalization_scale'],
                clipped=0)
            # Original index zero is the zero state; first exported state is
            # index 200. Advance 199 here and once for the first report.
            for _ in range(199):
                self._step(name)

    def _step(self,name):
        s=self.family[name]
        s['z']=s['A']@s['z']+s['rng'].multivariate_normal(np.zeros(len(s['z'])),s['cov'])
        s['local']=s['phi']*s['local']+s['rng'].multivariate_normal(np.zeros(len(s['local'])),s['local_cov'])
        normalized=s['z']@s['load']+s['local']
        s['clipped']+=int(np.sum(abs(normalized)>8))
        return np.clip(normalized,-8,8)*s['scale']+s['center']

    def generate(self,count):
        result={name:np.empty((count,len(self.model['pmu_order']))) for name in self.order}
        for k in range(count):
            for name in self.order:
                result[name][k]=self._step(name)
        self.frames+=count
        return result

    def state_dict(self):
        return dict(seed=self.seed,frames=self.frames,order=self.order,
            family={name:dict(z=s['z'].tolist(),local=s['local'].tolist(),
                rng=copy.deepcopy(s['rng'].bit_generator.state),clipped=s['clipped'])
                for name,s in self.family.items()})

    @classmethod
    def from_state(cls,model,state):
        obj=cls(model,state['seed'])
        assert obj.order==state['order']
        obj.frames=state['frames']
        for name,saved in state['family'].items():
            s=obj.family[name]
            s['z']=np.array(saved['z']);s['local']=np.array(saved['local'])
            s['rng'].bit_generator.state=copy.deepcopy(saved['rng']);s['clipped']=saved['clipped']
        return obj

def apply_noise(deterministic,noise):
    result={name:np.array(x,copy=True) for name,x in deterministic.items()}
    for name in noise:
        result[name]+=noise[name]
    for name in ('voltage_angle','current_angle'):
        result[name]=(result[name]+180)%360-180
    result['current_magnitude']=np.maximum(0,result['current_magnitude'])
    # Historical frequency and ROCOF noise are added AFTER the phase estimator.
    # Therefore samplewise derivative equality is not a property of this model.
    return result
