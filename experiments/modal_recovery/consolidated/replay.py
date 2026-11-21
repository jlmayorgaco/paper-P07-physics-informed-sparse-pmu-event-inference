"""Restore verified inputs and reproduce decisions without opening event labels."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from zipfile import ZipFile
from robust import TMP, RESULT, study
from freeze_final import verify
import predict_final


def restore(manifest):
    folder=TMP/"pmu"
    folder.mkdir(exist_ok=True,parents=True)
    seen=set()
    for name,expected in manifest["archives"].items():
        path=RESULT/name
        assert study.digest(path)==expected
        with ZipFile(path) as z:
            for member in z.namelist():
                key=member.removesuffix(".npz")
                assert member==key+".npz" and len(key)==24 and all(ch in "0123456789abcdef" for ch in key)
                assert key not in seen and key in manifest["records"]
                data=z.read(member)
                sha=manifest["records"][key]["sha"]
                assert sha256(data).hexdigest()==sha
                out=folder/member
                if out.exists():
                    assert study.digest(out)==sha
                else:
                    with out.open("xb") as f:
                        f.write(data)
                seen.add(key)
    assert seen==set(manifest["records"])


def replay(all_records=False,workers=2):
    verify()
    manifest=study.read(RESULT/"inputs.json")
    restore(manifest)
    calls=study.read(RESULT/"predictions.json")
    windows=study.read(RESULT/"window_predictions.json")
    ids=sorted(calls)
    selected=ids if all_records else sorted(set(ids[::61])|set(sorted(windows)[::23]))
    tasks=[(k,manifest["records"][k]) for k in selected]
    with ProcessPoolExecutor(workers,initializer=predict_final.init) as pool:
        for key,call,window in pool.map(predict_final.compute,tasks):
            assert call==calls[key] and window==windows.get(key,{}),key
    print(f"Verified {len(ids)} complete observation hashes; reproduced {len(tasks)} records across four conditions.")


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--all",action="store_true")
    p.add_argument("--workers",type=int,default=2)
    a=p.parse_args()
    replay(a.all,a.workers)
