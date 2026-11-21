"""Post-unblinding PMU sensitivity by load bus. Twin subtraction is diagnostic only."""
from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile
from hashlib import sha256

from observations import ARCHIVE
from run import RESULT
import study
import numpy as np


def main():
    pred = study.read(RESULT/"predictions.json")
    labels = study.read(RESULT/"truth.json")
    hashes = study.read(RESULT/"test_manifest.json")["hashes"]
    assert study.digest(RESULT/"truth.json")==pred["targets_sha"]
    twins = {t["parent"]:k for k,t in labels.items() if t["on"] is None}
    records = {}
    with ZipFile(ARCHIVE) as archive:
        for k, expected in hashes.items():
            raw = archive.read(k+".npz")
            assert sha256(raw).hexdigest()==expected
            with np.load(BytesIO(raw),allow_pickle=False) as z:
                records[k]=z["y"]
    # Take a single quiet prefix per independent parent. All channels are
    # centered within record before pooling, preserving V and A units.
    quiet = [records[k][:30] for k in twins.values()]
    noise = np.sqrt(np.mean([(q-q.mean(axis=0))**2 for q in quiet],axis=(0,1)))
    by_asset = defaultdict(list)
    for k,t in labels.items():
        if t["family"]!="load":
            continue
        twin = records[twins[t["parent"]]]
        y = records[k]
        tick = 2*np.arange(len(y))
        on, off = round(60*t["on"]), round(60*t["off"])
        np.testing.assert_array_equal(y[tick<on],twin[tick<on])
        delta = (y-twin)[(on<=tick)&(tick<off)]
        rms = np.sqrt(np.mean(delta**2,axis=0))
        by_asset[t["source"]].append(float(np.max(rms/noise)))
    table = {a:dict(n=len(v), median=float(np.median(v)), minimum=min(v), maximum=max(v))
             for a,v in sorted(by_asset.items())}
    result = dict(predictions_sha=study.digest(RESULT/"predictions.json"), noise_rms=noise.tolist(),
                  median_best_channel_rms_ratio=table)
    path = RESULT/"paired_signal.json"
    if path.exists():
        assert study.read(path)==result
    else:
        study.save(path,result)
    print(table)


if __name__=="__main__":
    main()
