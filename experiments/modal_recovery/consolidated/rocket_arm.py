"""Multivariate MiniRocket reference transform with supervised onset and source heads."""
from robust import TMP,RESULT,CONDITIONS,Errors,records,study,joblib,observations
from hashlib import sha256
from urllib.request import urlopen
import sys
import numba
import numpy as np
from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler

REV="0b1c245d9c9dbc50886f28bc7b32d5d45b5663d6"
CODE_SHA="e48c16b9b9b122d3794638d4e01303396c2db76f44b561b6cd6b21331035d940"


def module():
    path=TMP/"minirocket_multivariate.py"
    if not path.exists():
        TMP.mkdir(parents=True,exist_ok=True)
        url=f"https://raw.githubusercontent.com/angus924/minirocket/{REV}/code/minirocket_multivariate.py"
        content=urlopen(url,timeout=30).read()
        assert sha256(content).hexdigest()==CODE_SHA
        path.write_bytes(content)
    assert sha256(path.read_bytes()).hexdigest()==CODE_SHA
    sys.path.insert(0,str(TMP))
    import minirocket_multivariate
    return minirocket_multivariate


@numba.njit
def seed_numba(n):
    np.random.seed(n)


def series(y):
    z=observations(y)
    return z-z[:30].mean(axis=0)


def inputs(z,ends,length):
    return np.ascontiguousarray(np.stack([z[k+1-length:k+1].T for k in ends]),dtype=np.float32)


def features(blocks,head):
    pars,prescale,post,clf=head
    return post.transform(module().transform(np.ascontiguousarray(blocks/prescale,dtype=np.float32),pars))


def train_head(x,y,nfeatures):
    x=np.ascontiguousarray(x,dtype=np.float32)
    scale=np.maximum(x.std(axis=(0,2),keepdims=True),1e-8)
    x=np.ascontiguousarray(x/scale,dtype=np.float32)
    np.random.seed(381109)
    seed_numba(381109)
    implementation=module()
    params=implementation.fit(x,num_features=nfeatures)
    transformed=implementation.transform(x,params)
    post=StandardScaler(with_mean=False)
    clf=RidgeClassifier(alpha=10.,class_weight="balanced").fit(post.fit_transform(transformed),y)
    return params,scale,post,clf


def fit():
    numba.set_num_threads(4)
    manifest=study.read(study.ROOT/"experiments/modal_recovery/clock_stress/results/inputs.json")
    truth=study.read(study.ROOT/"experiments/modal_recovery/clock_stress/results/truth.json")
    gates,flags,sites,ids=[],[],[],[]
    conditions=list(CONDITIONS.values())
    rng=np.random.default_rng(8036501)
    for k,t in sorted(truth.items()):
        if t["panel"]!="catalog":
            continue
        path=study.ROOT/"tmp/clock_stress/pmu"/(k+".npz")
        assert study.digest(path)==manifest["records"][k]["sha"]
        y,c=study.unpack(path)
        err=Errors(510000+t["parent"],len(y),c)
        for j in (0,1+t["parent"]%3):
            z=series(err.apply(y,conditions[j]))
            if t["on"] is None:
                gates.extend(inputs(z,rng.integers(c+59,len(y),size=3),60))
                flags.extend([0]*3)
            else:
                on=int(np.ceil(30*t["on"]-1e-7))
                ends=np.maximum(c+59,on+np.array([2,11,25]))
                gates.extend(inputs(z,ends,60))
                flags.extend([1]*len(ends))
                sites.extend(inputs(z,np.maximum(c+59,on+rng.integers(0,15,size=2))+29,84))
                ids.extend([t["source"]]*2)
    detector=train_head(gates,flags,1008)
    source=train_head(sites,ids,9996)
    joblib.dump((detector,source),TMP/"rocket.joblib",compress=3)


def scan(y,c,detector):
    z=series(y)
    ends=np.arange(c+59,len(y),3)
    return z,ends,detector[-1].decision_function(features(inputs(z,ends,60),detector))


def label(z,b,source):
    if b is None or b+29>=len(z):
        return None
    site=str(source[-1].predict(features(inputs(z,[b+29],84),source))[0])
    return ["load" if site.startswith("BUS") else "line",site]


def calibrate():
    numba.set_num_threads(3)
    gate,_=joblib.load(TMP/"rocket.joblib")
    maxima=[]
    for i,k,y,c in records("cal"):
        err=Errors(480000+i,len(y),c)
        maxima.append(max(float(scan(err.apply(y,s),c,gate)[2].max()) for s in CONDITIONS.values()))
    study.save(TMP/"rocket_calibration.json",dict(tau=max(maxima),maxima=maxima))


if __name__=="__main__":
    (fit if sys.argv[1]=="fit" else calibrate)()
