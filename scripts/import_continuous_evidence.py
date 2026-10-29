"""Copy executed secondary evidence, never rerun a baseline or read RAW.
Usage: python -B scripts/import_continuous_evidence.py --source-repo PATH
"""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(source):
    source=Path(source).resolve();dest=ROOT/'generated/frozen/continuous_20261029'
    if dest.exists():raise FileExistsError('Evidence already imported; verify instead of replacing')
    files=[]
    for campaign,sub in [('M03_R11_FROZEN_DISCREPANCY','H03'),('M03_R12_CAUSAL_BIRTH','H04')]:
        base=source/'experiments/E5_VALIDATION_PAPER'/campaign
        for name in ['SUMMARY.csv','EVENTS.csv','EXTRAS.csv','LIFECYCLES.csv','EVALUATION_AUDIT.json','PREDICTIONS_SEAL.json']:
            files.append((base/'protocol/new_holdout/results'/name,f'{sub}/{name}'))
        for name in ['SCIENTIFIC_CONTRACT.md','METHOD.md','RESULTS.md','CANDIDATE_FREEZE.json']:
            p=base/name
            if p.exists():files.append((p,f'{sub}/{name}'))
    c=source/'experiments/PAPER_CONFIRMATORY_C01'
    for name in ['references/R11_FREEZE.json','protocol/PLAN.json','protocol/FREEZE.json','comparator/chen2016.py','comparator/run_f01.py','comparator/test_chen2016.py','comparator/TESTS.json','comparator/MATCHED_CONTRACT.json','comparator/MATCHED_SUMMARY.csv','comparator/MATCHED_TRIALS.csv','comparator/F01_STRESS.csv','comparator/README.md']:
        files.append((c/name,'C01/'+name))
    for p,_ in files:
        if not p.is_file():raise FileNotFoundError(p)
    manifest=[]
    for p,relative in files:
        target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        manifest.append(dict(path=relative,sha256=sha(target),source=p.relative_to(source).as_posix()))
    (dest/'MANIFEST.json').write_text(json.dumps(dict(status='SECONDARY_DEVELOPMENT_EVIDENCE_NOT_C01_RESULTS',date='2026-10-29',source_repo=source.name,files=manifest),indent=2)+'\n',encoding='utf-8')
    print('IMPORTED',len(files),'verified artifacts')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-repo',required=True);main(p.parse_args().source_repo)
