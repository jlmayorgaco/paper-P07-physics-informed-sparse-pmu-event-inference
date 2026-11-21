"""Reproduce the released estimators on archived P2 measurements without using labels."""
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import numpy as np
from recommended import load_estimator
from robust import TMP,RESULT,study,CONDITIONS,Errors,phase_data

LONG=Path(__file__).resolve().parent/"long_horizon/results"


def restore(root,folder):
    manifest=study.read(root/"inputs.json")
    folder.mkdir(exist_ok=True,parents=True)
    seen=set()
    for name,digest in manifest["archives"].items():
        assert study.digest(root/name)==digest
        with ZipFile(root/name) as archive:
            for filename in archive.namelist():
                k=filename.removesuffix(".npz")
                assert filename==k+".npz" and len(k)==24 and all(c in "0123456789abcdef" for c in k)
                assert k not in seen
                seen.add(k)
                payload=archive.read(filename)
                assert sha256(payload).hexdigest()==manifest["records"][k]["sha"]
                dest=folder/filename
                if dest.exists():
                    assert study.digest(dest)==manifest["records"][k]["sha"]
                else:
                    with dest.open("xb") as f:
                        f.write(payload)
    assert seen==set(manifest["records"])
    return manifest


def init():
    global model
    model=load_estimator()


def check(task):
    path,meta,expected,extended=task
    with np.load(path,allow_pickle=False) as a:
        raw={k:a[k] for k in a.files if k!="clearance"}
        c=int(a["clearance"])
    y=phase_data.channels(raw)
    errors=Errors((631337 if extended else 530000)+meta["stream"],len(y),c)
    count=0
    for name in (("native","joint") if extended else CONDITIONS):
        z=errors.apply(y,CONDITIONS[name])[:c+(900 if extended else 271)]
        r={k:v[:len(z)] for k,v in raw.items()}
        r.update(voltage_angle=z[:,16:24],current_angle=z[:,24:])
        assert model.predict(r,c)==expected[name]["graph"],(path.stem,name)
        count+=1
    return count


def replay():
    tasks=[]
    for base,folder,extended in ((RESULT,TMP/"pmu",False),(LONG,TMP/"horizon/pmu",True)):
        manifest=restore(base,folder)
        calls=study.read(base/"predictions.json")
        tasks.extend((folder/(k+".npz"),m,calls[k],extended) for k,m in manifest["records"].items())
    with ProcessPoolExecutor(3,initializer=init) as pool:
        n=sum(pool.map(check,tasks,chunksize=5))
    print(f"Verified all {len(tasks)} archived observations and reproduced {n} frozen graph decisions.")


if __name__=="__main__":
    replay()
