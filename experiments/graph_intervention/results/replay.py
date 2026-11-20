"""Replay frozen decisions from raw streams; optionally regenerate those streams from the NAS model."""
import argparse
import gc
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

import joblib
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
spec=spec_from_file_location("p07_primary_observer",HERE.parent/"operating/run.py")
entry=module_from_spec(spec)
spec.loader.exec_module(entry)
from common import DATA, FROZEN_TREES, REFIT, RESULT, load, sha
import cohort
from operators import cache_bank
from study import supervised


def replay(folder,indices):
    raw=folder/"test/pmu.npy"
    if sha(raw)!=load(RESULT/"test_manifest.json")["observations"]:
        raise ValueError("Wrong raw observations")
    x=np.load(raw,allow_pickle=False)
    primary=load(HERE.parent/"operating/predictions.json")
    archived=load(RESULT/"predictions.json")
    models=[joblib.load(k) for k in (FROZEN_TREES,REFIT)]
    for i in indices:
        observer=entry.primary_observer()
        result=[a for report in x[i] for a in observer.step(report)]
        if result!=primary[i]:
            raise ValueError(f"Primary replay differs on {i}")
        for model,name in zip(models,("trees","trees_refit")):
            if supervised(x[i],model)!=archived[name][i]:
                raise ValueError(f"Comparator {name} differs on {i}")
    print("Reproduced all three monitors on records",indices)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--regenerate",action="store_true")
    parser.add_argument("--records",nargs="+",type=int,default=[0,1,2,3,4,9,37,101])
    args=parser.parse_args()
    cache_bank()
    if not REFIT.exists():
        archived=HERE.parent/"trees_refit.joblib"
        if sha(archived)!=load(RESULT/"tree_fit.json")["refit"]:
            raise ValueError("Archived refit hash differs")
        shutil.copyfile(archived,REFIT)
    if args.regenerate:
        with TemporaryDirectory() as tmp:
            cohort.DATA=Path(tmp)/"raw"
            cohort.RESULT=Path(tmp)/"manifests"
            cohort.generate("test")
            if load(cohort.RESULT/"test_manifest.json")!=load(RESULT/"test_manifest.json"):
                raise ValueError("Independent regeneration differs")
            replay(cohort.DATA,args.records)
            gc.collect()
    else:
        replay(DATA,args.records)
