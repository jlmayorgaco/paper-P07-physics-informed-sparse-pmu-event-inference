"""Measure incremental voltage and current phase visibility in paired development data."""
from collections import Counter
from phase_data import TMP,RESULT,folder,study
from phase_model import observations
import numpy as np


def sensitivity():
    truth = study.read(TMP/"dev/targets.json")
    controls = {t["parent"]:k for k,t in truth.items() if t["on"] is None}
    manifests = study.read(RESULT/"dev_manifest.json")["hashes"]
    def load(key):
        path = folder("dev")/(key+".npz")
        assert study.digest(path)==manifests[key]
        return study.unpack(path)[0]
    noise, angle_noise = [], []
    for k in controls.values():
        raw = load(k)[:30]
        z = observations(raw)
        noise.append(z.var(axis=0))
        phi = np.column_stack((raw[:,17:24]-raw[:,16:17],raw[:,24:]-raw[:,16:24]))
        centered = (phi-phi[:1]+180)%360-180
        angle_noise.append(centered.var(axis=0))
    sigma = np.sqrt(np.mean(noise,axis=0))
    phase_sigma = np.sqrt(np.mean(angle_noise,axis=0))
    cases = []
    for k,t in truth.items():
        if t["source"]!="BUS31":
            continue
        full = load(k)
        twin = load(controls[t["parent"]])
        tick = 2*np.arange(len(full))
        onset,off = round(60*t["on"]),round(60*t["off"])
        np.testing.assert_array_equal(full[tick<onset],twin[tick<onset])
        delta = (observations(full)-observations(twin))[(tick>=onset)&(tick<off)]
        ratio = np.sqrt(np.mean(delta**2,axis=0))/sigma
        groups = {"magnitude":ratio[:16],"relative_voltage":ratio[16:23],"relative_current":ratio[23:]}
        cases.append({name:dict(best=int(np.argmax(v)),rms_ratio=float(np.max(v))) for name,v in groups.items()})
    assert len(cases)==19
    result = dict(n=len(cases),phase_quiet_rms_deg=dict(relative_voltage=phase_sigma[:7].tolist(),
                  relative_current=phase_sigma[7:].tolist()),median_best_channel={
                  k:float(np.median([v[k]["rms_ratio"] for v in cases])) for k in cases[0]},
                  best_channel_indices={k:dict(Counter(str(v[k]["best"]) for v in cases)) for k in cases[0]})
    target = RESULT/"development_sensitivity.json"
    if target.exists():
        assert study.read(target)==result
    else:
        study.save(target,result)
    print(result)


if __name__=="__main__":
    sensitivity()
