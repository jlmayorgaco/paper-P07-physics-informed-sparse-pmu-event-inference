"""Fit, freeze, seal and score a graph episode confirmation at its causal deadline."""
import argparse

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from episode_cohort import DATA, OUT
from episode_gate import Confirmation, Signatures, log_odds
from episode_trace import evidence, trace_path
from estimator import publish
from evaluate import evaluate
from phasors import LOCK, MODEL
from study import CODE, HERE, ROOT, digest, read, supervised, write_json


FREEZE = OUT / "freeze.json"
TREES = ROOT / "experiments/supervised_stream/successor/model.joblib"
PROPOSALS = (.98, .999)


def dependencies():
    names = (*CODE, "episode_gate.py", "episode_cohort.py", "episode_trial.py", "episode_trace.py",
             "phasors.py", "robust.py", "monitor.py", "model.npz")
    files = {name: digest(HERE / name) for name in names}
    files.update(polar=digest(MODEL), graph=digest(LOCK), trees=digest(TREES))
    return files


def verify():
    config = read(FREEZE)
    if config["dependencies"] != dependencies():
        raise ValueError("Frozen observer, comparison or cohort code changed")
    return config


def arrays(split):
    evidence(split)
    return (np.load(DATA / split / "pmu.npy", mmap_mode="r"),
            np.load(trace_path(split), mmap_mode="r"))


def truth(split):
    path = DATA / split / "truth.json"
    if digest(path) != read(OUT / f"{split}_manifest.json")["truth"]:
        raise ValueError("Invalid truth")
    return read(path)


def candidates(records, traces, signatures, graph, proposal):
    rows = []
    for stream, scores in zip(records, traces, strict=True):
        gate = Confirmation(signatures, graph, proposal)
        rows.append([pair for frame, score in zip(stream, scores, strict=True)
                     for pair in gate.step(frame, score)])
    return rows


def match(events, alarms):
    used, indices = set(), []
    for e in events:
        index = next((i for i, a in enumerate(alarms) if i not in used
                      and 0 <= a["detected"] - e["onset"] <= 45), None)
        if index is not None:
            used.add(index)
        indices.append(index)
    return indices


def fit_logistic(rows, labels):
    features, targets = [], []
    for record, events in zip(rows, labels, strict=True):
        matched = set(match(events, [a for a, _ in record]))
        for i, (_, x) in enumerate(record):
            features.append(x)
            targets.append(i in matched)
    scaler = StandardScaler().fit(features)
    model = LogisticRegression(C=1., max_iter=500).fit(scaler.transform(features), targets)
    return dict(center=scaler.mean_.tolist(), scale=scaler.scale_.tolist(),
                coef=model.coef_[0].tolist(), intercept=float(model.intercept_[0]),
                fitted_candidates=len(features), fitted_new_events=sum(targets))


def filtered(rows, config):
    return [[a for a, x in record if log_odds(x, config) >= config["cut"]] for record in rows]


def fit():
    if FREEZE.exists() or (DATA / "test").exists():
        raise FileExistsError("Fit must precede generation of the fresh test streams")
    train, dev = arrays("train"), arrays("dev")
    train_labels, dev_labels = truth("train"), truth("dev")
    signatures = Signatures()
    with np.load(MODEL) as archive:
        graph = dict(archive)
    baseline = evaluate(dev_labels, [publish(z, graph, .999, .95) for z in dev[1]])
    choices = []
    for proposal in PROPOSALS:
        train_rows = candidates(*train, signatures, graph, proposal)
        model = fit_logistic(train_rows, train_labels)
        dev_rows = candidates(*dev, signatures, graph, proposal)
        for probability in (.05, .1, .2, .3, .4, .5, .6, .7, .8, .9, .95):
            cut = float(np.log(probability / (1-probability)))
            config = dict(**model, proposal=proposal, cut=cut, threshold=probability)
            metric = evaluate(dev_labels, filtered(dev_rows, config))
            rank = (metric["quiet_extras"], max(0, baseline["joint"]-metric["joint"]),
                    -metric["macro_f1"], -metric["joint"], metric["extras"], -probability)
            choices.append((rank, config, metric))
    _, best, metric = min(choices, key=lambda x: x[0])
    write_json(FREEZE, dict(**best, development=metric, original_development=baseline,
                            selection=[dict(proposal=c["proposal"], threshold=c["threshold"],
                                            joint=m["joint"], extras=m["extras"], macro_f1=m["macro_f1"])
                                       for _, c, m in choices],
                            dependencies=dependencies(),
                            manifests={s: digest(OUT / f"{s}_manifest.json") for s in ("train","dev")}))
    print("frozen on development", best["proposal"], best["threshold"], metric, flush=True)


def predict():
    from online import load_model
    config = verify()
    path = OUT / "predictions.json"
    if path.exists():
        raise FileExistsError("Predictions already sealed")
    trees = load_model()
    records, traces = arrays("test")
    with np.load(MODEL) as archive:
        graph = dict(archive)
    rows = candidates(records, traces, Signatures(), graph, config["proposal"])
    forecasts = dict(confirmed=filtered(rows, config),
                     original=[publish(z, graph, .999, .95) for z in traces],
                     candidates_only=[[a for a, _ in record] for record in rows],
                     trees=[supervised(r, trees) for r in records])
    write_json(path, forecasts)
    write_json(OUT / "seal.json", dict(predictions=digest(path), development=digest(FREEZE),
                                       manifest=digest(OUT / "test_manifest.json")))


def summarize(labels, forecasts):
    result = evaluate(labels, forecasts)
    first = second = first_n = second_n = 0
    post = 0
    for events, alarms in zip(labels, forecasts, strict=True):
        matched = match(events, alarms)
        for order, (e, i) in enumerate(zip(events, matched)):
            a = None if i is None else alarms[i]
            right = bool(a and a["published"] is not None and a["published"] <= e["onset"] + 45
                         and (a["code"], a["source"]) == (e["code"], e["source"]))
            if order == 0:
                first += right
                first_n += 1
            else:
                second += right
                second_n += 1
        for i, a in enumerate(alarms):
            preceding = [e for e in events if e["onset"] <= a["detected"]]
            if i not in matched and preceding and preceding[-1]["end"] <= a["detected"]:
                post += 1
    return dict(**result, post_restoration_extras=post, first_joint=[first, first_n],
                second_joint=[second, second_n])


def intervals(labels, forecasts, clusters):
    # Keep both counterfactual arms of a trajectory together in each paired draw.
    _, groups = np.unique(clusters, return_inverse=True)
    samples = np.random.default_rng(852019).integers(groups.max()+1, size=(4000, groups.max()+1))
    def draws(alarms):
        stats = np.zeros((groups.max()+1, 5, 6))
        joint = np.zeros((len(stats), 2))
        for g, events, actions in zip(groups, labels, alarms, strict=True):
            r = evaluate([events], [actions])
            stats[g] += r["confusion"]
            joint[g] += (r["joint"], len(events))
        tables = stats[samples].sum(axis=1)
        f1s = []
        for c in range(1,5):
            denom = tables[:, c, :].sum(axis=1) + tables[:, :, c].sum(axis=1)
            f1s.append(np.divide(2*tables[:,c,c], denom, where=denom>0, out=np.zeros_like(denom)))
        j = joint[samples].sum(axis=1)
        return np.column_stack((np.mean(f1s, axis=0), j[:,0]/j[:,1]))
    new = draws(forecasts["confirmed"])
    return {name: dict(zip(("macro_f1", "joint_fraction"),
                           np.quantile(new-draws(forecasts[name]), [.025,.975], axis=0).T.tolist()))
            for name in ("original", "trees")}


def score():
    verify()
    if read(OUT / "seal.json") != dict(predictions=digest(OUT / "predictions.json"),
                                       development=digest(FREEZE), manifest=digest(OUT / "test_manifest.json")):
        raise ValueError("Broken prediction seal")
    labels = truth("test")
    forecasts = read(OUT / "predictions.json")
    clusters = read(OUT / "test_manifest.json")["clusters"]
    scores = {m:summarize(labels, a) for m, a in forecasts.items()}
    scores["paired_difference_ci95"] = intervals(labels, forecasts, clusters)
    write_json(OUT / "scores.json", scores)
    write_json(OUT / "test_truth.json", labels)
    print({m: (s["joint"], s["macro_f1"], s["extras"]) for m,s in scores.items() if "joint" in s})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("fit","predict","score"))
    stage = parser.parse_args().stage
    {"fit": fit, "predict": predict, "score": score}[stage]()
