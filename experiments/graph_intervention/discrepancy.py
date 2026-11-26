"""Fit a conditional discrepancy law from isolated interventions and their recovery tails."""
import numpy as np
from scipy.linalg import solve_triangular
from scipy.optimize import minimize_scalar

from common import HERE, MODEL
from operators import innovations, filter_args, network, physics_arrays, response, stream

FILE = HERE/"discrepancy.npz"


def fit(records,labels):
    with np.load(MODEL) as arc:
        model = dict(arc)
    net = network()
    physics = physics_arrays(net)
    rows = {c:[] for c in range(1,5)}
    nodes = 1+.3*np.polynomial.legendre.leggauss(3)[0]
    for record,events in zip(records,labels,strict=True):
        if not events:
            continue
        observed,_ = stream(record,model)
        error = observed.copy()
        for pos,event in enumerate(events):
            code,source = event["code"],event["source"]
            g = np.flatnonzero((net["code"]==code)&(net["site"]==source))[0]
            modes = np.flatnonzero(net["group"]==g)
            mode = modes[0] if len(modes)==1 else modes[np.argmin(abs(nodes-event["strength"]))]
            start,end = event["onset"],event["end"]
            raw = response(mode,end-start,len(record)-start,net["a"],net["b"],physics,model["floor"],
                           model["center"],model["scale"])
            signature = innovations(raw,*filter_args(model))
            error[start:] -= signature
            until = events[pos+1]["onset"] if pos+1<len(events) else len(record)
            # Pure recovery and sustained events. The two reports spanning the switch are
            # excluded to avoid training the predictor to cancel genuine new jumps.
            for begin,stop in ((start+2,end),(end+2,until)):
                if stop>begin:
                    sl = slice(begin,stop)
                    rows[code].append((error[sl],error[begin-1:stop-1],error[begin-2:stop-2]))
    ar1,ar2,white,gamma = [],[],[],[]
    for c in range(1,5):
        y,lag1,lag2 = (np.concatenate(col) for col in zip(*rows[c]))
        x = np.column_stack((lag1,lag2))
        scale = np.maximum(np.sqrt(np.mean(x**2,axis=0)),1.)
        xs = x/scale
        # Ridge in standardized coordinates is a Gaussian coefficient prior.
        coef = np.linalg.solve(xs.T@xs+np.eye(xs.shape[1])*len(x)*.001,xs.T@y)/scale[:,None]
        err = y-x@coef
        # Factor a robust Student scale matrix with fixed degrees of freedom.
        covariance = err.T@err/len(err)+np.eye(31)*.05
        nu = float(model["nu"])
        for _ in range(12):
            w = solve_triangular(np.linalg.cholesky(covariance),np.eye(31),lower=True)
            energy = np.sum((err@w.T)**2,axis=1)
            weights = (nu+31)/(nu+energy)
            covariance = err.T@(weights[:,None]*err)/len(err)+np.eye(31)*.05
        w = solve_triangular(np.linalg.cholesky(covariance),np.eye(31),lower=True)
        energy = np.sum((err@w.T)**2,axis=1)
        lag = np.mean((lag1@w.T)**2,axis=1)
        def loss(t):
            v = 1+np.expm1(t)*lag
            return np.mean(31*np.log(v)+(31+nu)*np.log1p(energy/(nu*v)))
        opt = minimize_scalar(loss,bounds=(0.,5.),method="bounded").x
        ar1.append(coef[:31].T)
        ar2.append(coef[31:].T)
        white.append(w)
        gamma.append(np.expm1(min((0.,opt,5.),key=loss)))
    np.savez_compressed(FILE,ar1=ar1,ar2=ar2,white=white,gamma=gamma)
