"""Single-record PMU-only worker. Frozen estimator code is imported unchanged."""
import argparse,importlib.util,sys,shutil
import numpy as np
from threadpoolctl import threadpool_limits
from common import *
def module(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def work(mode,rid):
    sys.addaudithook(guard);sys.path.insert(0,str(RUNTIME));sys.path.insert(0,str(PHYSICS))
    record=next(r for r in read(DATA/'INPUTS.json') if r['id']==rid);obs=DATA/'observed'/(rid+'.npz');assert sha(obs)==record['sha256']
    output=DATA/'predictions'/rid
    if mode=='prefix':
        from conditional_prefix import fit_particles
        from instrument_parent import FIELDS
        with np.load(obs,allow_pickle=False) as z:t=z['time_s'][:300].copy();d={f:z[f][:300].copy() for f in FIELDS}
        fits=fit_particles(RUNTIME,t,d,record['sha256']);save(RUN/'prefix'/rid/'fits.json',fits)
        save(RUN/'prefix'/rid/'COMPLETE.json',dict(truth_read=False,prefix_reports=300,observation_sha256=record['sha256']))
    elif mode=='mlprefix':
        from adaptation import fit_prefix
        from instrument_parent import FIELDS
        with np.load(obs,allow_pickle=False) as z:t=z['time_s'][:300].copy();d={f:z[f][:300].copy() for f in FIELDS}
        fit=fit_prefix(RUNTIME,t,[{f:d[f][k] for f in FIELDS} for k in range(300)])
        save(RUN/'ml_prefix'/rid/'fit.json',fit)
        save(RUN/'ml_prefix'/rid/'COMPLETE.json',dict(truth_read=False,prefix_reports=300))
    elif mode=='bank':
        from static_bank import write_particle_caches
        banks=write_particle_caches(RUN/'derivatives/grid'/rid,RUN/'particles'/rid,read(RUN/'prefix'/rid/'fits.json'),RUNTIME,record['sha256'])
        save(RUN/'particles'/rid/'COMPLETE.json',dict(truth_read=False,banks=banks))
    elif mode=='r11':module(R11/'observer/run.py','frozen_r11').run(RUNTIME,RUN/'particles'/rid,obs,output)
    elif mode=='ml':
        sys.path.insert(0,str(ML));m=module(ML/'infer.py','frozen_ml_infer');m.predict(obs,RUN/'ml_prefix'/rid,output/'shared_ml')
        for a,b in [('BASELINE','ET_REFERENCE'),('SHORT','ET_CANDIDATE')]:
            if not (output/b).exists():shutil.copytree(output/'shared_ml'/a,output/b)
    elif mode=='chen':
        sys.path.insert(0,str(ROOT/'comparator'));from run_f01 import run
        run(obs,output/'CHEN2016')
    else:raise ValueError(mode)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['prefix','mlprefix','bank','r11','ml','chen']);a.add_argument('--record',required=True);x=a.parse_args()
    with threadpool_limits(limits=1):work(x.mode,x.record)
