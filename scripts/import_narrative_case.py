"""Read-only import of a fixed H04 development parent, never partial C01."""
from pathlib import Path
import argparse,json,hashlib,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(repo):
    repo=Path(repo).resolve();src=repo/'experiments/E5_VALIDATION_PAPER/M03_R12_CAUSAL_BIRTH/protocol/new_holdout';dest=ROOT/'generated/frozen/narrative_case_20261030'
    if dest.exists():raise FileExistsError(dest)
    cases=json.loads((src/'data/truth_private/cases.json').read_text());replays=json.loads((src/'data/truth_private/replays.json').read_text());manifest=[]
    for condition in ['MATCH','OUT_SUPPORT']:
        c=next(c for c in cases if c['parent_schedule']=='H002' and c['condition']==condition);r=next(r for r in replays if r['physical_id']==c['id']);rid=r['id'];obs=src/'data/observed'/(rid+'.npz');pred=src/'data/predictions'/rid/'R11';meta=json.loads((pred/'prediction.json').read_text());assert meta['observation_sha256']==sha(obs)==r['sha256']
        pairs=[(obs,'observed/'+rid+'.npz'),(pred/'prediction.json','prediction/'+rid+'.json')]
        for p,name in pairs:
            out=dest/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);manifest.append(dict(path=name,sha256=sha(out),source=p.relative_to(repo).as_posix(),source_sha256=sha(p)))
        keys=['time_s','M','M_cause','theta_weights','delta_M_conditional','delta_M_parameter']
        with np.load(pred/'prediction.npz',allow_pickle=False) as z:a={k:z[k].copy() for k in keys}
        out=dest/'prediction'/(rid+'_compact.npz');np.savez_compressed(out,**a);manifest.append(dict(path=out.relative_to(dest).as_posix(),sha256=sha(out),source=(pred/'prediction.npz').relative_to(repo).as_posix(),source_sha256=sha(pred/'prediction.npz'),retained_arrays=keys))
        out=dest/'evaluation'/(rid+'.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(dict(case=c,record=r),indent=2));manifest.append(dict(path=out.relative_to(dest).as_posix(),sha256=sha(out),source='H04 sealed truth, used only for retrospective illustration'))
    for p,name in [(src/'runtime/model/assets.json','assets.json'),(src/'runtime/model/physics/reference/data/branch.csv','branch.csv'),(src/'runtime/PROTOCOL.json','PROTOCOL.json')]:
        out=dest/name;shutil.copy2(p,out);manifest.append(dict(path=name,sha256=sha(out),source=p.relative_to(repo).as_posix(),source_sha256=sha(p)))
    (dest/'MANIFEST.json').write_text(json.dumps(dict(status='DEVELOPMENT_ILLUSTRATION_NOT_CONFIRMATORY',selection='Fixed parent H002; MATCH/OUT pair. First load and first line for waveform windows; BUS31 for declared timing failure. No selection using C01.',files=manifest),indent=2));print('NARRATIVE_CASE_IMPORTED',len(manifest))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-repo',required=True);main(p.parse_args().source_repo)
