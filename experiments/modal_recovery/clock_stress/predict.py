"""Blind prediction from sealed PMU observations. No access to simulation targets."""
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from io import BytesIO
from zipfile import ZipFile
import argparse
import gzip
import json
from stress_plan import GRID,RESULT,TMP,Errors,phase_data,study,frozen,verify
from benchmark import call
import numpy as np


def init():
    global models
    models = frozen.arms()


def compact(prediction):
    return [prediction["alarm"],prediction["label"]]


def infer(model,y,clear):
    (bg,gate,source),threshold = model
    return compact(call(bg.residual(y,clear),clear,gate,source,threshold))


def case(task):
    key,meta,bundle = task
    if bundle:
        with ZipFile(RESULT/bundle) as archive:
            raw = archive.read(key+".npz")
        assert sha256(raw).hexdigest()==meta["sha"]
        with np.load(BytesIO(raw),allow_pickle=False) as z:
            y,c = z["y"],int(z["clearance"])
    else:
        p = TMP/"pmu"/(key+".npz")
        assert study.digest(p)==meta["sha"]
        y,c = study.unpack(p)
    errors = Errors(meta["stream"],len(y),c)
    baseline = infer(models["magnitudes"],y[:,:16],c)
    phase = []
    for s in GRID:
        perturbed = errors.apply(y,s)
        assert np.array_equal(y[:,:16],perturbed[:,:16])
        decision = infer(models["angles"],perturbed,c)
        if s.name=="offset":
            assert decision==phase[0],"Static-angle reference invariance failed"
        phase.append(decision)
    return key,dict(magnitude=baseline,phase=phase)


def episodes(model,y,c):
    (bg,gate,_),threshold = model
    residual = bg.residual(y,c)
    lag = gate.length-1
    scores = np.concatenate([gate.scores(residual[i:i+768+lag]) for i in range(0,len(residual)-lag,768)])
    assert len(scores)==len(y)-c-lag and np.isfinite(scores).all()
    above = scores>threshold
    return int(np.count_nonzero(above & ~np.r_[False,above[:-1]])),len(scores)


def quiet_case(task):
    index,row = task
    key = row["id"]
    p = study.RUN/"observations/P2/TEST"/(key+"_nominal.npz")
    assert study.digest(p)==row["files"]["nominal"]
    with np.load(p,allow_pickle=False) as z:
        y = phase_data.channels(z)
    c = 360
    baseline,n = episodes(models["magnitudes"],y[:,:16],c)
    errors = Errors(1000000+index,len(y),c)
    phase = []
    for s in GRID:
        if s.name=="offset":
            # Its stressed finite-trace predictions are tested explicitly on all simulated cases.
            native = phase[0]
            if index==0:
                assert episodes(models["angles"],errors.apply(y,s),c)[0]==native
            phase.append(native)
        else:
            count,m = episodes(models["angles"],errors.apply(y,s),c)
            assert m==n
            phase.append(count)
    return key,dict(magnitude=baseline,phase=phase,reports=n)


def quiet(workers):
    verify()
    manifest = study.read(study.RUN/"OBSERVATIONS_P2_TEST.json")
    rows = sorted((r for r in manifest if r["reports"]==18001),key=lambda r:r["id"])
    assert len(rows)==36
    old = study.read(phase_data.RESULT/"predictions.json")["quiet"]
    output = {}
    with ProcessPoolExecutor(workers,initializer=init) as pool:
        for key,v in pool.map(quiet_case,enumerate(rows)):
            assert (v["reports"],v["magnitude"],v["phase"][0])==(old[key]["reports"],old[key]["magnitudes_alarms"],old[key]["alarms"])
            output[key]=v
            if len(output)%6==0:
                print("long quiet",len(output),"/36",flush=True)
    study.save(RESULT/"quiet.json",output)


def cases(workers,replay=False):
    verify()
    manifest = study.read(RESULT/"inputs.json")
    assert manifest["protocol_sha"]==study.digest(RESULT/"protocol_seal.json")
    bundles = {}
    for name,digest in manifest["archives"].items():
        assert study.digest(RESULT/name)==digest
        with ZipFile(RESULT/name) as archive:
            for p in archive.namelist():
                assert p[:-4] not in bundles
                bundles[p[:-4]]=name
    assert bundles.keys()==manifest["records"].keys()
    dest = RESULT/"calls.json.gz"
    previous = json.loads(gzip.decompress(dest.read_bytes())) if replay else {}
    tasks = [(k,v,bundles[k] if replay else None) for k,v in sorted(manifest["records"].items())]
    out = {}
    with ProcessPoolExecutor(workers,initializer=init) as pool:
        for k,v in pool.map(case,tasks,chunksize=2):
            if replay:
                assert previous[k]==v,k
            out[k]=v
            if len(out)%300==0:
                print("observations",len(out),"/1200",flush=True)
    assert len(out)==1200
    if not replay:
        with dest.open("xb") as stream:
            stream.write(gzip.compress(json.dumps(out,separators=(",",":")).encode(),mtime=0))


if __name__=="__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("stage",choices=("quiet","cases","replay"))
    cli.add_argument("--workers",type=int,default=10)
    a=cli.parse_args()
    if a.stage=="quiet":
        quiet(a.workers)
    else:
        cases(a.workers,a.stage=="replay")
