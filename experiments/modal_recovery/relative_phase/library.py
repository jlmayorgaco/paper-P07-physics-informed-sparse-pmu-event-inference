"""Run the frozen network to generate relative-phase response and recovery curves."""
from concurrent.futures import ProcessPoolExecutor
from phase_data import TMP, angular, channels, data
import numpy as np


def curve(task):
    kind, asset, amplitude, dwell = task
    start = 60 if kind=="recovery" else 120
    event = data.sim.event(np.random.default_rng(0),asset,start,2*dwell)
    event["amplitude"] = amplitude
    cut = start//2 + (dwell if kind=="recovery" else 0)
    n = 271 if kind=="recovery" else 90
    row = dict(duration_s=(max(cut+n-1, event["off_tick"]//2+2))/30,events=[event])
    sim = data.sim
    t,v,i,status = sim.plant.simulate(row,sim.sim.MAP)
    assert status["valid"]
    mapping = sim.sim.MAP
    v = v[:,np.array(sim.sim.REPORT["pmus"])-1]
    base = 100e6/(np.sqrt(3)*1000*sim.sim.KV[mapping.terminal.to_numpy()-1])
    # Constant terminal rotations, CT signs and the common clock cancel in the quiet reference.
    y = np.column_stack((abs(v),abs(i)*base*mapping.gain.to_numpy(),np.angle(v,deg=True),np.angle(i,deg=True)))
    features = np.column_stack((y[:,:16],angular(y)))
    result = features[cut:cut+n]-features[:30].mean(axis=0)
    if kind=="recovery" and dwell==60:
        _,raw = sim.physical(row)
        reported = channels(raw)
        verify = np.column_stack((reported[:,:16],angular(reported)))
        np.testing.assert_allclose(result,verify[cut:cut+n]-verify[:30].mean(axis=0),rtol=2e-8,atol=1e-8)
    return result


def build():
    TMP.mkdir(parents=True,exist_ok=True)
    data.sim.initialize()
    assets = data.sim.assets
    nodes, weights = np.polynomial.legendre.leggauss(5)
    sizes = .085+.055*nodes
    tasks, prior = [], []
    for a in assets:
        amplitudes = np.r_[-sizes,sizes] if a["family"]=="load" else [None]
        masses = np.tile(weights/4,2) if a["family"]=="load" else [1.]
        for amp,p in zip(amplitudes,masses):
            tasks.append(("switch",a,amp,95))
            prior.append(p/18)
    assert np.isclose(sum(prior),1.)
    recovery = [("recovery",a,.10 if a["family"]=="load" else None,d)
                for a in assets for d in range(60,121,3 if a["family"]=="load" else 1)]
    with ProcessPoolExecutor(8,initializer=data.sim.initialize) as pool:
        for name, work in (("switch",tasks),("recovery",recovery)):
            curves = np.stack(list(pool.map(curve,work,chunksize=3)))
            with (TMP/(name+".npz")).open("xb") as stream:
                np.savez_compressed(stream,curves=curves.astype(np.float32),ids=[t[1]["id"] for t in work],
                                    probabilities=prior if name=="switch" else [])
            print(name,len(curves),flush=True)


if __name__=="__main__":
    build()
