"""Switched terminal trajectories and marginal Gaussian innovations on the nominal graph."""
import numpy as np
from numba import njit
from scipy.optimize import minimize_scalar
from scipy.special import gammaln

from common import GRAPH, MODEL
from estimator import mechanical_prediction, physics_arrays, stationary_gain


WINDOW = 36
TAIL = 144


def coordinates(frame, floor):
    frame = np.asarray(frame, dtype=float)
    if frame.shape[-2:] != (8,5) or not np.isfinite(frame).all() or not (frame[...,4]==1).all():
        raise ValueError("Expected eight finite available PMUs")
    amp = frame[...,2]
    direction = np.minimum(1., amp[...,:7]/floor) * np.sin(np.deg2rad(frame[...,:7,3]))
    return np.concatenate((frame[...,0], frame[...,1], amp, direction), axis=-1)


def network():
    # Only nominal electrical/mechanical operators and the terminal calibration are used.
    with np.load(GRAPH/"model.npz") as f:
        return {name:f[name] for name in ("a","b","group","code","site","torque","field","power",
                                          "p0","dp","bias","base","scale")}


@njit(cache=True)
def observation(mode, x, fields, bias, floor):
    field = fields[mode] @ np.exp(1j*x[:10])
    y = np.empty(31)
    for j in range(8):
        y[j] = np.log(abs(field[j]))
        y[8+j] = np.angle(field[j])
        raw = field[8+j]
        amp = max(0.,abs(raw)+bias[j])
        y[16+j] = amp
        if j<7:
            y[24+j] = min(1.,amp/floor[j])*raw.imag/abs(raw) if abs(raw)>0 else 0.
    return y


@njit(cache=True)
def response(mode, duration, length, a, b, physics, floor, center, scale):
    state = np.zeros(30)
    z = np.empty((length,31))
    for k in range(length):
        j = mode if k<duration else 0
        state = mechanical_prediction(j,state,a,b,physics)
        z[k] = (observation(j,state,physics[0],physics[5],floor)-center)/scale
    return z


@njit(cache=True)
def innovations(y, a, h, ar, white, gain):
    """Common linear innovations transform. Applying it to mean differences preserves likelihood ratios."""
    state = np.zeros(30)
    noise = np.zeros(31)
    z = np.empty_like(y)
    for i in range(len(y)):
        forecast = a @ state
        z[i] = white @ (y[i]-h@forecast-ar@noise)
        state = forecast + gain@z[i]
        noise = y[i]-h@state
    return z


def filter_args(model):
    return tuple(model[k] for k in ("normal_a","normal_h","ar","white","gain"))


def stream(record, model):
    raw = coordinates(record,model["floor"])
    y = (raw-raw[:30].mean(axis=0))/model["scale"]
    z = innovations(y,*filter_args(model))
    departure = np.r_[0.,np.sum((y[:-1,:16]*model["scale"][:16])**2,axis=1)/8]
    return z, 1+float(model["gamma"])*departure


def fit(records, labels):
    net = network()
    physics = physics_arrays(net)
    # One SD of the quiet magnitude sets the radial scale for the direction at low current.
    floor = records[:,:30,:7,2].std(axis=(0,1)).astype(float)
    quiet = coordinates(records[:,:55],floor)
    scale = quiet.std(axis=(0,1))
    quiet = (quiet-quiet.mean(axis=(0,1)))/scale
    prev, curr = [q.reshape(-1,31) for q in (quiet[:,:-1],quiet[:,1:])]
    ar = np.linalg.lstsq(prev,curr,rcond=None)[0].T.copy()
    if np.max(abs(np.linalg.eigvals(ar)))>=1:
        raise ValueError("Unstable training instrument")
    noise = np.cov((curr-prev@ar.T).T)
    center = observation(0,np.zeros(30),net["field"],net["bias"],floor)
    basis = np.eye(30)*1e-5
    h = np.column_stack([(observation(0,d,net["field"],net["bias"],floor)
                         -observation(0,-d,net["field"],net["bias"],floor))/(2e-5*scale) for d in basis])
    base = dict(floor=floor, scale=scale, center=center, normal_a=net["a"][0], normal_h=h,
                ar=ar, code=net["code"], site=net["site"])
    nodes = 1+.3*np.polynomial.legendre.leggauss(3)[0]
    lengths = [np.array([e["end"]-e["onset"] for row in labels for e in row if e["code"]==c])
               for c in range(1,5)]
    base["dmin"] = np.array([v.min() for v in lengths])-1
    base["dmax"] = np.array([v.max() for v in lengths])+1
    base["young_durations"] = np.array([np.quantile(v,[1/6,.5,5/6],method="nearest") for v in lengths])
    residuals, departures = [], []
    for record,events in zip(records,labels,strict=True):
        raw = coordinates(record,floor)
        y = (raw-raw[:30].mean(axis=0))/scale
        departures.append(np.r_[0.,np.sum((y[:-1,:16]*scale[:16])**2,axis=1)/8][30:])
        for e in events:
            group = np.flatnonzero((net["code"]==e["code"])&(net["site"]==e["source"]))[0]
            modes = np.flatnonzero(net["group"]==group)
            mode = modes[0] if len(modes)==1 else modes[np.argmin(abs(nodes-e["strength"]))]
            start = e["onset"]
            y[start:] -= response(mode,e["end"]-start,len(y)-start,net["a"],net["b"],physics,floor,center,scale)
        residuals.append(y)
    dep = np.concatenate(departures)
    best, diagnostics = None, []
    for sigma in (.01,.1,1.):
        torque = net["torque"][0]
        white,gain,logdet = stationary_gain(net["a"][0],h,sigma**2*(torque@torque.T),ar,noise)
        pars = (net["a"][0],h,ar,white,gain)
        norms = np.concatenate([np.sum(innovations(y,*pars)[30:]**2,axis=1) for y in residuals])
        for nu in (3.,10.,100000.):
            constant = gammaln(nu/2)-gammaln((nu+31)/2)+15.5*np.log(nu*np.pi)+logdet
            def loss(log_gamma):
                v = 1.+np.expm1(log_gamma)*dep
                return constant+.5*np.mean(31*np.log(v)+(nu+31)*np.log1p(norms/(nu*v)))
            maximum = np.log1p(1e12)
            interior = minimize_scalar(loss,method="bounded",bounds=(0.,maximum)).x
            theta = min((0.,interior,maximum),key=loss)
            nll = float(loss(theta))
            diagnostics.append(dict(sigma=sigma,nu=nu,gamma=float(np.expm1(theta)),nll=nll))
            if best is None or nll<best[0]:
                best = (nll,dict(**base,white=white,gain=gain,gamma=np.expm1(theta),nu=nu,sigma=sigma))
    np.savez_compressed(MODEL,**best[1])
    return diagnostics


def build_bank(model):
    net, nodes = network(), np.polynomial.legendre.leggauss(3)[1]/2
    physics = physics_arrays(net)
    args = filter_args(model)
    c, s = model["code"], model["site"]
    groups, durations, weights, is_young, waves = [],[],[],[],[]
    for mode,g in enumerate(net["group"]):
        if not g:
            continue
        family = c[g]-1
        modes = np.flatnonzero(net["group"]==g)
        weight = 1. if len(modes)==1 else nodes[np.flatnonzero(modes==mode)[0]]
        for duration in range(model["dmin"][family],model["dmax"][family]+1):
            raw = response(mode,duration,TAIL,net["a"],net["b"],physics,model["floor"],model["center"],model["scale"])
            waves.append(innovations(raw,*args).astype("float32"))
            groups.append(g)
            durations.append(duration)
            weights.append(weight)
            is_young.append(np.count_nonzero(model["young_durations"][family]==duration))
    groups,weights,is_young = map(np.asarray,(groups,weights,is_young))
    young = np.flatnonzero(is_young)
    priors = np.array([1/(4*sum(c==code)) for code in c[groups[young]]])*weights[young]*is_young[young]/3
    if not np.isclose(priors.sum(),1):
        raise ArithmeticError("Unnormalized candidate mixture")
    return dict(waves=np.asarray(waves),group=groups,weight=weights,duration=np.array(durations),
                young=young,logprior=np.log(priors),site=s,code=c)


def cache_bank():
    from common import DATA, HERE, load, save, sha
    target = DATA/"bank"
    target.mkdir(parents=True,exist_ok=True)
    stamp = target/"inputs.json"
    inputs = {str(key):sha(path) for key,path in (("model",MODEL),("physics",GRAPH/"model.npz"),
              ("operators",HERE/"operators.py"),("dynamics",GRAPH/"estimator.py"))}
    if stamp.exists() and load(stamp)["inputs"]==inputs:
        meta = load(stamp)
        if all(sha(target/(k+".npy"))==v for k,v in meta["arrays"].items()):
            return
    with np.load(MODEL) as archive:
        bank = build_bank(dict(archive))
    for k,v in bank.items():
        np.save(target/(k+".npy"),v,allow_pickle=False)
    save(stamp,dict(inputs=inputs,arrays={k:sha(target/(k+".npy")) for k in bank}))
