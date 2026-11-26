from pathlib import Path
import hashlib,json,os,sys,subprocess,time
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
RUN=ROOT/'run';DATA=RUN/'data';RUNTIME=RUN/'runtime';ENGINE=RUN/'engine'
BASE=REPO/'experiments/E5_VALIDATION_PAPER';H04=BASE/'M03_R12_CAUSAL_BIRTH/protocol/new_holdout'
R11=BASE/'M03_R11_FROZEN_DISCREPANCY';PHYSICS=R11/'physics';ML=BASE/'M03_R09_NUISANCE_DEV/ml'
ARMS=['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE','CHEN2016']
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',JULIA_NUM_THREADS='1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def encode(x):
    import numpy as np
    return x.tolist() if isinstance(x,np.ndarray) else x.item() if isinstance(x,np.generic) else str(x)
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(x,indent=2,default=encode)+'\n',encoding='utf-8');os.replace(tmp,p)
def guard(event,args):
    if event=='open' and isinstance(args[0],(str,bytes)):
        s=Path(args[0]).resolve().as_posix().lower()
        if any(v in s for v in ['raw000','/truth_private/','/engine/']):raise PermissionError(s)
def call(label,command,check=True):
    folder=RUN/'logs';folder.mkdir(parents=True,exist_ok=True);start=time.time();log=folder/(label+'.log')
    save(RUN/'PROGRESS.json',dict(stage=label,status='RUNNING',started_unix_s=start,log=str(log),method_changes=False))
    with log.open('a',encoding='utf-8') as f:p=subprocess.run(list(map(str,command)),env=ENV,stdout=f,stderr=subprocess.STDOUT)
    save(RUN/'timings'/(label+'.json'),dict(stage=label,seconds=time.time()-start,returncode=p.returncode))
    if check and p.returncode:raise RuntimeError(f'{label} failed; see {log}')
    return p.returncode
