"""Bounded-severity successor of the frozen nominal channel diagnostic."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import numpy as np
from scipy.linalg import solve_triangular
from scipy.optimize import minimize_scalar

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = HERE.parent / 'channel_information_20261112'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    design = json.loads((HERE / 'design.json').read_text())
    if digest(BASE / 'input_snapshot.npz') != design['snapshot_sha256']:
        raise ValueError('Frozen nominal snapshot changed')
    spec = importlib.util.spec_from_file_location('channel_base', BASE / 'run_channel_diagnostic.py')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    bank, assets = base.load_snapshot(), base.read_assets()
    hs = design['horizons_reports']; horizon = max(hs)
    lo, hi = design['rival_load_interval']; amplitude = design['true_load_amplitude']
    if not lo <= amplitude <= hi:
        raise ValueError('Fixed comparison amplitude must be feasible under profiling')
    gamma, _ = base.raw_covariance(bank, horizon)
    # Each trajectory is affine in amplitude; topology-specific constants stay.
    offsets = np.empty((18, horizon, 47)); slopes = np.empty_like(offsets)
    for i, asset in enumerate(assets):
        for a, target in ((0., offsets), (1., slopes)):
            x = np.zeros(bank['T'].shape[1])
            for k in range(horizon):
                op = base.operator_index(i, 'on0' if k == 0 else 'stay')
                group = int(bank['group'][op])
                target[i, k] = bank['J'][group] @ x + bank['j'][op] + bank['v'][op]*a - bank['j'][0]
                x = bank['T'][group] @ x + bank['g'][op] + bank['u'][op]*a
        slopes[i] -= offsets[i]
        if asset['family'] == 'line' and np.max(np.abs(slopes[i])) != 0:
            raise ValueError('Line means must not have a fitted amplitude')
    truth = offsets + amplitude * slopes
    old = base.event_mean(bank, assets, horizon)
    if not np.allclose(truth, old, rtol=1e-10, atol=1e-10):
        raise ValueError('True trajectories differ from fixed-mean predecessor')
    rows, nearest = [], []
    optimization_error = 0.
    for h in hs:
        local = {}
        for name in design['channels']:
            channels = base.CHANNELS[name]; idx = base.channel_indices(h, channels)
            cov = gamma[np.ix_(idx, idx)]
            factor, scale = base.stable_factor(cov)
            def white(x):
                m = x[:, :h, list(channels)].reshape(18, -1)
                return solve_triangular(factor, (m/scale).T, lower=True).T
            wtruth, woffsets, wslopes = white(truth), white(offsets), white(slopes)
            for i in range(18):
                scores = []
                fixed_scores = []
                for j in range(18):
                    if i == j: continue
                    d, s = wtruth[i]-woffsets[j], wslopes[j]
                    a = float(np.clip((d@s)/(s@s), lo, hi)) if assets[j]['family']=='load' else 0.
                    residual = d-s*a
                    profiled = float(residual@residual)
                    fixed = wtruth[i]-wtruth[j]
                    fixed_d2 = float(fixed@fixed)
                    if assets[j]['family']=='load':
                        # Independent scalar minimizer including both interval boundaries.
                        objective = lambda b: float((d-s*b)@(d-s*b))
                        opt = minimize_scalar(objective,bounds=(lo,hi),method='bounded',options={'xatol':1e-12})
                        numerical = min(objective(lo),objective(hi),opt.fun)
                        optimization_error = max(optimization_error,abs(profiled-numerical)/max(1.,profiled))
                    elif abs(profiled-fixed_d2)>1e-10*max(1.,fixed_d2):
                        raise ArithmeticError('Fixed line candidate changed under profiling')
                    if profiled > fixed_d2+1e-10*max(1.,fixed_d2):
                        raise ArithmeticError('Profiling increased distance despite feasible fixed amplitude')
                    local.setdefault((i,j),{})[name] = (profiled,a,fixed_d2)
                    scores.append((profiled,assets[j]['id'],a))
                    fixed_scores.append((fixed_d2,assets[j]['id']))
                best = min(scores); fixed_best = min(fixed_scores)
                nearest.append(dict(source=assets[i]['id'],family=assets[i]['family'],reports=h,channels=name,
                    nearest=best[1],D2_profile=best[0],rival_amplitude=best[2],
                    fixed_nearest=fixed_best[1],D2_fixed=fixed_best[0]))
        for (i,j), values in local.items():
            v, vi, all_ = (values[n][0] for n in ('V','VI','all'))
            if vi < v-1e-10*max(1.,vi) or all_ < vi-1e-10*max(1.,all_):
                raise ArithmeticError('Marginal channel profiling violates monotonicity')
            row = dict(source=assets[i]['id'],competitor=assets[j]['id'],reports=h)
            for name,(score,a,fixed) in values.items():
                row.update({f'D2_{name}':score,f'rival_amplitude_{name}':a,f'fixed_D2_{name}':fixed})
            rows.append(row)
    if len(rows)!=918 or len(nearest)!=162 or optimization_error>1e-8:
        raise ArithmeticError('Unexpected result count or analytic/numerical profiling mismatch')
    for name, table in (('pairwise.csv',rows),('nearest.csv',nearest)):
        with (HERE/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
    one = {(r['source'],r['channels']):r for r in nearest if r['reports']==30}
    ratios = [one[a['id'],'VI']['D2_profile']/one[a['id'],'V']['D2_profile'] for a in assets]
    retention = [one[a['id'],'VI']['D2_profile']/one[a['id'],'VI']['D2_fixed'] for a in assets]
    summary = dict(scope=design, checks=dict(all_gates_pass=True, independent_optimizer_max_relative_error=optimization_error),
        inputs={str(p.relative_to(ROOT)):digest(p) for p in [HERE/'design.json',BASE/'input_snapshot.npz',BASE/'run_channel_diagnostic.py',BASE/'r11_assets.json']},
        script_sha256=digest(Path(__file__)),
        results=dict(pairwise_rows=len(rows),nearest_rows=len(nearest),
            nearest_profile_VI_over_V=dict(min=min(ratios),median=float(np.median(ratios)),max=max(ratios)),
            nearest_profile_VI_over_fixed_VI=dict(min=min(retention),median=float(np.median(retention)),max=max(retention)),
            nearest_changes_fixed_vs_profile_VI=sum(one[a['id'],'VI']['nearest']!=one[a['id'],'VI']['fixed_nearest'] for a in assets)),
        outputs={name:digest(HERE/name) for name in ['pairwise.csv','nearest.csv']})
    (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary['results'],indent=2))


if __name__=='__main__': main()
