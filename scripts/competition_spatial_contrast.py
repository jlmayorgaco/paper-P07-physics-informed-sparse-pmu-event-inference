"""Compare the response bank with a within-family, covariance-weighted source fit."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.covariance import LedoitWolf

import competition_response_bank as previous
from benchmark_competition_windows import prepare, save, check_dynamic_startup


def pulse_bounds(frames):
    """Find overlapping sustained gain and angle-format changes at different PMUs."""
    gains, turns = [], []
    for bus, frame in frames.items():
        q = frame.TIMESTAMP < 60
        amp = frame[[f"BUS{bus}_I{p}_MAG" for p in "ABC"]]
        angle = frame[[f"BUS{bus}_V{p}_ANG" for p in "ABC"]]
        # A 360-degree encoding change has no effect on an electrical phasor.
        gain = (amp / amp[q].median() - 1).median(axis=1).abs() > .12
        outside = ((angle > angle[q].max()+90) | (angle < angle[q].min()-90)).sum(axis=1) >= 2
        valid = ~q & frame.DATA_PRESENT.eq(1)
        for flag, out in ((gain, gains), (outside, turns)):
            idx = np.flatnonzero((flag & valid).to_numpy())
            for run in np.split(idx,np.flatnonzero(np.diff(idx)>1)+1):
                if len(run)>=12:
                    out.append((bus,int(run[0]),int(run[-1])+1))
    for b,start,end in gains:
        for other,left,right in turns:
            width=end-start
            if (b!=other and min(end,right)-max(start,left)>=9
                    and start>=2*width and end+2*width<=len(frame)):
                return min(left,start),max(end,right),b
    return None


def channels(frames):
    signals=[]
    for bus in previous.BUSES:
        d=frames[bus]
        for quantity in ("V","I"):
            amplitudes=d[[f"BUS{bus}_{quantity}{p}_MAG" for p in "ABC"]].to_numpy()
            angles=d[[f"BUS{bus}_{quantity}{p}_ANG" for p in "ABC"]].to_numpy()
            normal=np.nanmedian(amplitudes[:1800],axis=0)
            ref=np.rad2deg(np.angle(np.nanmean(np.exp(1j*np.deg2rad(angles[:1800])),axis=0)))
            for x in (amplitudes/normal-1, (angles-ref+180)%360-180):
                v=np.mean(x,axis=1)
                v[d.DATA_PRESENT.to_numpy()!=1]=np.nan
                signals.append(v)
    return np.array(signals).T


def contrast(data, bounds=None):
    if bounds is None:
        # Long-lived interventions: late voltage/current displacement retains
        # the spatial information; the system-wide frequency shift does not.
        return np.nanmean(data[-300:],axis=0)-np.nanmean(data[:1800],axis=0)
    start,end,bus=bounds
    # A two-second pulse can be smaller than ambient voltage oscillations.
    # Estimate the dominant ambient frequencies in the quiet prefix; fit the
    # nuisance amplitudes on observed samples outside the suspected pulse.
    t=np.arange(len(data))/30
    usable=(np.arange(len(t)) < start-30) | (np.arange(len(t)) > end+30)
    dx=np.empty(data.shape[1])
    for j in range(0,data.shape[1],4):
        v=data[:1800,j]
        freq=np.fft.rfftfreq(8192,1/30)
        spectrum=np.abs(np.fft.rfft(np.hanning(len(v))*np.nan_to_num(v-np.nanmean(v)),8192))
        keep=(freq>=.015)&(freq<=.45)
        basis=[np.ones_like(t)]
        for _ in range(2):
            f=freq[np.argmax(np.where(keep,spectrum,-1))]
            basis.extend([np.sin(2*np.pi*f*t),np.cos(2*np.pi*f*t)])
            keep &= np.abs(freq-f)>.045
        design=np.stack(basis,axis=1)
        for col in range(j,j+4):
            mask=usable & np.isfinite(data[:,col])
            if mask.sum()<300:
                dx[col]=np.nan
                continue
            coef=np.linalg.lstsq(design[mask],data[mask,col],rcond=None)[0]
            dx[col]=np.nanmean(data[start:end,col]-design[start:end]@coef)
    # A gain error contaminates current magnitude at this site.
    dx[4*previous.BUSES.index(bus)+2]=np.nan
    return dx


def fit(directories, dest):
    groups={}
    examples=((dev,case,label) for dev in directories
              for case,label in json.loads((dev/"truth.json").read_text()).items())
    for dev,case,label in examples:
        family=label["code"]
        if family not in (3,4,6,8):
            continue
        frames=previous.frames_from(dev/"observations"/case)
        pulse=pulse_bounds(frames) if family==8 else None
        if family==8 and pulse is None:
            continue
        key=(3 if family==6 else family,label["source"])
        groups.setdefault(key,[]).append(contrast(channels(frames),pulse))
    model={}
    for family in (3,4,8):
        sources=sorted(source for fam,source in groups if fam==family)
        means=np.array([np.nanmean(groups[family,s],axis=0) for s in sources])
        errors=np.vstack([groups[family,s]-means[j] for j,s in enumerate(sources)])
        scale=np.maximum(np.nanstd(errors,axis=0),1e-9)
        cov=LedoitWolf().fit(np.nan_to_num(errors/scale)).covariance_
        model[str(family)]=dict(sources=sources,means=means.tolist(),scale=scale.tolist(),cov=cov.tolist())
    save(dest,model)


def localize(dx, model):
    scale=np.array(model["scale"])
    valid=np.isfinite(dx)
    mu=np.array(model["means"])[:,valid]/scale[valid]
    z=dx[valid]/scale[valid]
    cov=np.array(model["cov"])[np.ix_(valid,valid)]
    projected=np.linalg.solve(cov,mu.T).T
    energy=np.sum(mu*projected,axis=1)
    inner=projected@z
    amplitude=np.clip(inner/np.maximum(energy,1e-12),.4,2.)
    return model["sources"][int(np.argmax(2*amplitude*inner-amplitude**2*energy))]


def refine(frames, current, models, physical_family=None):
    pulse=pulse_bounds(frames)
    if pulse is not None and current[0] in (0,7,8):
        return [8,localize(contrast(channels(frames),pulse),models["8"])]
    fam=physical_family if current[0]==6 else current[0]
    if fam in (3,4):
        return [current[0],localize(contrast(channels(frames)),models[str(fam)])]
    return current


def initialize(zip_dir, bank, admissions, spatial):
    global models
    previous.init(zip_dir,bank,admissions)
    models=json.loads(spatial.read_text())


def infer(folder):
    case, old=previous.infer(folder)
    frames=previous.baseline.api._load_frames(folder)
    family=None
    if old["response"][0]==6 and old["route"]=="response":
        gains=previous.scores(previous.measurements(frames),np.array(previous.bank["templates"]),range(60,81))
        family=previous.bank["keys"][int(np.argmax(gains))][0]
    return case, dict(current=old["response"],response=refine(frames,old["response"],models,family))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage",choices=["fit","prepare","predict","score"])
    p.add_argument("root",type=Path)
    p.add_argument("--dev",type=Path,nargs="+")
    p.add_argument("--archive",type=Path)
    p.add_argument("--submitted",type=Path)
    a=p.parse_args()
    a.root.mkdir(parents=True,exist_ok=True)
    spatial=a.root/"spatial.json"
    if a.stage=="fit":
        fit(a.dev,spatial)
    elif a.stage=="prepare":
        for name,seed,reps in (("primary",85773209,24),("quiet",34813171,48)):
            prepare(a.root/name,a.archive.resolve(),seed=seed,repetitions=reps,
                    move_integrity=True,asset_catalog=previous.CATALOG,
                    vary_physical=True,normal_only=name=="quiet")
            check_dynamic_startup(a.root/name,a.archive.resolve())
    elif a.stage=="predict":
        admissions={}
        for split in ("primary","quiet"):
            admissions.update(json.loads((a.root/split/"dynamic_admission.json").read_text()))
        earlier=Path("experiments/competition_response_156/bank.json").resolve()
        with ProcessPoolExecutor(max_workers=4,initializer=initialize,
              initargs=(a.submitted.resolve(),earlier,admissions,spatial)) as pool:
            predictions=dict(pool.map(infer,sorted(a.root.glob("*/observations/*"))))
        save(a.root/"predictions.json",predictions)
        save(a.root/"seal.json",hashlib.sha256((a.root/"predictions.json").read_bytes()).hexdigest())
    else:
        previous.score(a.root,per_class=24)
