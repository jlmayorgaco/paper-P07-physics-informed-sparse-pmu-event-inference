"""Generate opaque paired PMU traces from the unmodified P2 electrical plant."""
from concurrent.futures import ProcessPoolExecutor
from zipfile import ZipFile,ZIP_STORED
from design import RESULT,TMP,SIZES,SEEDS,phase_data,study,verify
from phase_data import data
import numpy as np


def simulate(task):
    panel, i = task
    rng = np.random.default_rng([SEEDS[panel],i])
    families = ("load","line")
    first_family = families[i%2]
    second_family = families[i//2%2] if panel=="catalog" else "load"
    assets = data.sim.assets
    options = [a for a in assets if a["family"]==first_family and (panel=="catalog" or a["id"]!="BUS31")]
    first_asset = options[int(rng.integers(len(options)))]
    first = data.sim.event(rng,first_asset,2*int(rng.integers(52,69)),2*int(rng.integers(60,121)))
    clear = first["off_tick"]//2
    duration = clear/30+9
    noise_seed = int(rng.integers(1,2**31))
    options = [a for a in assets if a["family"]==second_family and a["id"]!=first["source"]
               and (panel=="catalog" or a["id"]=="BUS31")]
    asset = options[int(rng.integers(len(options)))]
    second = data.sim.event(rng,asset,first["off_tick"]+int(rng.integers(75,241)),int(rng.integers(120,241)))
    noise = data.sim.sim.NoiseStream(data.sim.sim.NOISE,noise_seed).generate(round(duration*30)+1)
    targets,observations = {},{}
    stream = i if panel=="catalog" else SIZES["catalog"]+i
    for e in (None,second):
        key = rng.bytes(12).hex()
        _,raw = data.sim.physical(dict(duration_s=duration,events=[first,e] if e else [first]))
        y = phase_data.channels(data.sim.sim.apply_noise(raw,noise))
        if e is None:
            twin = y
        else:
            before = 2*np.arange(len(y))<e["onset_tick"]
            np.testing.assert_array_equal(y[before],twin[before])
        path = TMP/"pmu"/(key+".npz")
        with path.open("xb") as out:
            np.savez_compressed(out,y=y,clearance=np.int32(clear))
        targets[key] = dict(panel=panel,parent=i,first=first["source"],clearance=clear,
                            on=e["onset_s"] if e else None,off=e["off_s"] if e else None,
                            family=e["family"] if e else "none",source=e["source"] if e else None)
        observations[key] = dict(sha=study.digest(path),stream=stream)
    return targets,observations


def generate():
    verify()
    (TMP/"pmu").mkdir(parents=True,exist_ok=False)
    tasks = [(panel,k) for panel,n in SIZES.items() for k in range(n)]
    truth,observations = {},{}
    with ProcessPoolExecutor(12,initializer=data.sim.initialize) as pool:
        for i,(t,o) in enumerate(pool.map(simulate,tasks,chunksize=2),1):
            truth.update(t)
            observations.update(o)
            if i%150==0:
                print("simulated",i,"pairs",flush=True)
    assert len(observations)==len(truth)==2*sum(SIZES.values())
    old_ids = study.read(phase_data.RESULT/"test_manifest.json")["hashes"]
    assert not (observations.keys() & old_ids.keys())
    study.save(TMP/"targets.json",truth)
    paths = sorted((TMP/"pmu").glob("*.npz"))
    archives = {}
    for start in range(0,len(paths),300):
        path = RESULT/f"pmus_{start//300+1}.zip"
        with ZipFile(path,"x",compression=ZIP_STORED) as z:
            for p in paths[start:start+300]:
                assert study.digest(p)==observations[p.stem]["sha"]
                z.write(p,arcname=p.name)
        archives[path.name]=study.digest(path)
    study.save(RESULT/"inputs.json",dict(targets_sha=study.digest(TMP/"targets.json"),records=observations,
                                         archives=archives,protocol_sha=study.digest(RESULT/"protocol_seal.json")))


if __name__=="__main__":
    generate()
