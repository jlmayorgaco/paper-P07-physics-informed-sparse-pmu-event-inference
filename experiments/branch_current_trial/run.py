"""Audit the terminal current operator, then test the frozen voltage/current readout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.linalg import block_diag, cholesky, solve_discrete_lyapunov, solve_triangular
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "dynamic_site_trial"))
from trial import N, ONSETS, SIGMA, dyn, simulate

ARCHIVE = Path(os.environ["P07_SCIENCE_ARCHIVE"])
RUN = ARCHIVE / "experiments/PAPER_CALIBRATION_B01/run"
REF = RUN / "engine_clean/reference"
sys.path.insert(0, str(REF))
from noise import psd
from pmu_operator import report


class CurrentNoise:
    """Frozen common VAR plus local AR. Model units are amperes or degrees."""
    def __init__(self, spec):
        local = np.diag(spec["PMU_local_AR1"])
        self.transition = block_diag(np.asarray(spec["VAR1_transition"]), local)
        self.loading = np.vstack((spec["loadings"], np.eye(8)))
        self.scale = spec["normalization_scale"]
        self.center = np.asarray(spec["normalization_center"])
        self.q = block_diag(psd(spec["innovation_covariance"]), psd(spec["PMU_local_innovation_covariance"]))
        state = solve_discrete_lyapunov(self.transition, self.q)
        lag = state
        cov = np.zeros((N, 8, N, 8))
        for delay in range(N):
            block = self.loading.T @ lag @ self.loading * self.scale**2
            t = np.arange(delay, N)
            cov[t, :, t-delay, :] = block
            cov[t-delay, :, t, :] = block.T
            lag = self.transition @ lag
        self.sd = np.sqrt(np.diag(cov[0,:,0,:]))
        self.chol = cholesky(cov.reshape(N*8, N*8), lower=True)

    def sample(self, rng):
        # Frozen generator exports states 200 onward from a zero state.
        states = rng.multivariate_normal(np.zeros(len(self.q)), self.q, size=199+N)
        for t in range(1, len(states)):
            states[t] += self.transition @ states[t-1]
        return np.clip(states[199:] @ self.loading, -8, 8) * self.scale

    def whiten(self, x):
        shape = x.shape
        matrix = x.reshape(-1, N*8)
        return solve_triangular(self.chol, matrix.T, lower=True).T.reshape(shape)


class Experiment:
    def __init__(self):
        self.plant = dyn.Plant()
        net = json.loads((RUN / "runtime/model/dae/measurement_network.json").read_text())
        self.b = np.array(net["B_real"]) + 1j*np.array(net["B_imag"])
        self.mapping = pd.read_csv(REF / "terminal_mapping.csv")
        cfg = json.loads((REF / "reporting_config.json").read_text())
        kv = pd.read_csv(REF / "data/bus.csv").base_kv.to_numpy()
        branch = pd.read_csv(REF / "data/branch.csv")
        assert list(self.mapping.pmu_bus) == net["pmus"] == cfg["pmus"] == list(dyn.PMU)
        for i, r in enumerate(self.mapping.itertuples()):
            line = branch.iloc[r.edge]
            assert (line.src_bus, line.dst_bus) == (r.src,r.dst)
            assert r.terminal == (r.src if r.side == "src" else r.dst)
            assert line.r_src == 1 and r.effective_native_sign == -r.polarity
            y = 1 / complex(line.R, line.X)
            other = r.dst if r.terminal == r.src else r.src
            stamp = np.zeros(39, complex)
            stamp[other-1] = -y
            stamp[r.terminal-1] = y + complex(getattr(line,"G_"+r.side), getattr(line,"B_"+r.side))
            np.testing.assert_allclose(stamp, self.b[i], atol=1e-5, rtol=1e-5)
        self.factor = (100e6/(np.sqrt(3)*1000*kv[self.mapping.terminal-1])
                       * self.mapping.polarity * self.mapping.gain
                       * np.exp(1j*np.deg2rad(self.mapping.bias_deg)))
        self.factor = self.factor.to_numpy()
        self.v0 = self.plant.zg(()) @ (self.plant.yg*self.plant.E0)
        self.i0 = self.factor * (self.b @ self.v0)
        native = -(self.b @ self.v0)[None,:]
        replay = report(np.array([0.]), self.v0[None,:], native, self.mapping, kv, cfg)
        shift = cfg["common_phase_intercept_deg"] + np.array(cfg["relative_voltage_bias_deg"])
        np.testing.assert_allclose(replay["current_A"][0], self.i0*np.exp(1j*np.deg2rad(shift)))
        model = json.loads((REF / "stochastic_model.json").read_text())
        assert model["pmu_order"] == net["pmus"]
        self.mag, self.ang = [CurrentNoise(model["families"][key]) for key in ("current_magnitude","current_angle")]

    def measure(self, v):
        voltage = (v / self.v0)[self.plant.pm]
        current = self.factor * (self.b @ v)
        return np.r_[np.log(abs(voltage)), np.angle(voltage), abs(current)-abs(self.i0),
                     np.rad2deg(np.angle(current/self.i0))]

    def whiten(self, x):
        return np.concatenate((x[...,:16]/SIGMA, self.mag.whiten(x[...,16:24]),
                               self.ang.whiten(x[...,24:])), axis=-1)

    def bank(self, family, sites):
        result = np.zeros((len(sites), len(ONSETS), N, 32))
        self.plant.H, self.plant.D = dyn.H.copy(), dyn.D
        for k,bus in enumerate(sites):
            signal, _ = simulate(self.plant, family, bus, 1, 0, self.measure)
            for u,onset in enumerate(ONSETS):
                result[k,u,onset:] = signal[:-onset]
        return self.whiten(result)

    def observe(self, family, bus, rng):
        strength = rng.uniform(.7,1.3)
        onset = int(rng.choice(ONSETS))
        self.plant.H = dyn.H * rng.uniform(.8,1.2)
        self.plant.D = dyn.D * rng.uniform(.8,1.2)
        y, _ = simulate(self.plant, family, bus, strength, onset, self.measure)
        y[:,:16] += rng.normal(0,SIGMA,(N,16))
        base = abs(self.i0) + self.mag.center
        y[:,16:24] = np.maximum(0, base + y[:,16:24] + self.mag.sample(rng)) - base
        y[:,24:] = (y[:,24:] + self.ang.sample(rng) + 180) % 360 - 180
        return self.whiten(y)


def run(split):
    exp = Experiment()
    rng = np.random.default_rng({"dev":736182,"blind":9982431}[split])
    families = dict(weak=list(range(1,40)), generation=sorted(dyn.GEN),
                    load=sorted(b for b,s in exp.plant.base_load.items() if s.real>0))
    pred, truth, pair_rows = [], [], []
    for family, sites in families.items():
        bank = exp.bank(family, sites)
        if split == "dev" and family == "weak":
            for a,b in [(11,12),(16,24)]:
                diff = bank[sites.index(a),4] - bank[sites.index(b),4]
                dv, di = np.linalg.norm(diff[:,:16]), np.linalg.norm(diff)
                pair_rows.append(dict(a=a,b=b,d_v=dv,d_vi=di,error_v=norm.sf(dv/2),error_vi=norm.sf(di/2)))
        matrices = [np.ascontiguousarray(bank[...,:n]).reshape(-1,N*n) for n in (16,32)]
        energies = [np.einsum("ij,ij->i",m,m) for m in matrices]
        cases = [(b,split) for k,b in enumerate(sites) if (k%3==0)==(split=="blind")]
        if family=="weak" and split=="blind":
            cases += [(b,"pair_challenge") for b in (11,12,16,24)]
        for b,group in cases:
            for _ in range(6 if split=="dev" else 12):
                y = exp.observe(family,b,rng)
                result = dict(case=len(pred),family=family,group=group)
                for label,n,m,e in zip(("voltage","joint"),(16,32),matrices,energies):
                    c = m @ y[:,:n].ravel()
                    a = np.clip(c/np.maximum(e,1e-24),.7,1.3)
                    scores = ((2*c-a*e)*a).reshape(len(sites),-1).max(axis=1)
                    result[label] = sites[np.argmax(scores)]
                    if group=="pair_challenge":
                        pair = (11,12) if b in (11,12) else (16,24)
                        result[label+"_binary"] = max(pair,key=lambda k:scores[sites.index(k)])
                pred.append(result)
                truth.append(dict(case=result["case"],bus=b))
    if split=="dev":
        pd.DataFrame(pair_rows).to_csv(HERE/"pair_resolution.csv",index=False)
        audit=exp.mapping.copy()
        audit["current_noise_sd_A_unclipped"]=exp.mag.sd
        audit["current_noise_sd_deg_unclipped"]=exp.ang.sd
        audit.to_csv(HERE/"current_audit.csv",index=False)
    path=HERE/f"{split}_predictions.csv"
    pd.DataFrame(pred).to_csv(path,index=False)
    (HERE/f"{split}.sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest())
    pd.DataFrame(truth).to_csv(HERE/f"{split}_truth.csv",index=False)


def score(split):
    path=HERE/f"{split}_predictions.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==(HERE/f"{split}.sha256").read_text()
    data=pd.read_csv(path).merge(pd.read_csv(HERE/f"{split}_truth.csv"),validate="one_to_one")
    rng=np.random.default_rng(7731)
    rows=[]
    for (group,fam),g in data.groupby(["group","family"]):
        v,j=g.voltage==g.bus,g.joint==g.bus
        changes=(j.astype(int)-v.astype(int)).groupby(g.bus).mean().to_numpy()
        ci=np.quantile(rng.choice(changes,(5000,len(changes))).mean(axis=1),[.025,.975])
        rows.append(dict(group=group,family=fam,n=len(g),voltage=int(v.sum()),joint=int(j.sum()),
                         gained=int((j&~v).sum()),lost=int((v&~j).sum()),delta_interval=ci.tolist()))
    if split=="blind":
        pair=data.query("group=='pair_challenge'").copy()
        for label in ("voltage","joint"):
            pair[label+"_binary"]=pair[label+"_binary"]==pair.bus
        print(pair.groupby(pair.bus.isin([11,12]))[["voltage_binary","joint_binary"]].sum())
    (HERE/f"{split}_scores.json").write_text(json.dumps(rows,indent=2))
    print(rows)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=["run","score"])
    parser.add_argument("split",choices=["dev","blind"])
    args=parser.parse_args()
    if args.split=="blind":
        gate=pd.read_csv(HERE/"pair_resolution.csv")
        weak=next(r for r in json.loads((HERE/"dev_scores.json").read_text()) if r["family"]=="weak")
        assert (gate.d_vi>gate.d_v).all() and weak["joint"]>weak["voltage"]
    (run if args.stage=="run" else score)(args.split)
