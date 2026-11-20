"""Freeze on development, generate a new physical cohort, seal predictions, then score."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from estimator import mechanical_prediction, physics_arrays, prepare, publish, terminal_prediction, trace
from evaluate import evaluate
from physical import Generator, ROOT, build_plant, fit_instrument, measurements

HERE = Path(__file__).resolve().parent
STORE = ROOT / "tmp/graph_recursive"
FREEZE = HERE / "freeze.json"
SCORES = HERE / "scores.json"
CODE = ("study.py", "estimator.py", "physical.py", "evaluate.py", "PROTOCOL.md",
        "../supervised_stream/plant.py", "../supervised_stream/larger.py", "../supervised_stream/learner.py",
        "../branch_current_trial/run.py", "../history_conditioning/dynamics.py")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf8")


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def training_file():
    return ROOT / "tmp/supervised_stream/larger/train/observations.npy"


def generate(split):
    if split == "test":
        verify_freeze()
    folder = STORE / split
    folder.mkdir(parents=True, exist_ok=False)
    n0, n1, n2, seed = (8, 8, 8, 238411) if split == "dev" else (24, 40, 32, 916437)
    rng = np.random.default_rng(seed)
    sim = Generator()
    sites = {c: [s for i, s in enumerate(sorted(sim.catalog[c])) if (i % 3 == 0) == (split == "test")]
             for c in range(1, 5)}
    sizes = rng.permutation([0] * n0 + [1] * n1 + [2] * n2)
    codes = iter(rng.permutation(np.tile(np.arange(1, 5), (n1 + 2*n2) // 4)))
    records = np.lib.format.open_memmap(folder / "pmu.npy", mode="w+", dtype=np.float32,
                                        shape=(len(sizes), 720, 8, 5))
    truth = []
    for i, count in enumerate(sizes):
        events = []
        on = int(rng.integers(65, 316))
        for _ in range(count):
            code = int(next(codes))
            low, high = {1: (5, 13), 2: (22, 59), 3: (27, 66), 4: (27, 66)}[code]
            end = on + int(rng.integers(low, high))
            events.append(dict(code=code, source=str(rng.choice(sites[code])), onset=on, end=end,
                               strength=float(rng.uniform(.7, 1.3)), sensors=[2, 5]))
            on = end + int(rng.integers(30, 121))
        records[i] = sim.simulate(events, rng)
        truth.append(events)
    records.flush()
    write_json(folder / "truth.json", truth)
    write_json(HERE / f"{split}_manifest.json", dict(seed=seed, records=len(sizes), sites=sites,
               observations=digest(folder / "pmu.npy"), truth=digest(folder / "truth.json")))


def sequences(split, with_labels=False):
    folder = STORE / split
    manifest = read(HERE / f"{split}_manifest.json")
    if digest(folder / "pmu.npy") != manifest["observations"]:
        raise ValueError("Measurements differ from the generation manifest")
    observations = np.load(folder / "pmu.npy", mmap_mode="r")
    return (observations, labels(split)) if with_labels else observations


def labels(split):
    path = STORE / split / "truth.json"
    if digest(path) != read(HERE / f"{split}_manifest.json")["truth"]:
        raise ValueError("Truth differs from the generation manifest")
    return read(path)


def fit_transitions(truth):
    events = [e for record in truth for e in record]
    quiet = len(truth) * 690 - sum(e["end"] - e["onset"] for e in events)
    # Bernoulli MLE on actual transition opportunities, including quiet record boundaries.
    ending = np.zeros(5)
    for code in range(1, 5):
        lengths = [e["end"] - e["onset"] for e in events if e["code"] == code]
        ending[code] = len(lengths) / sum(lengths)
    return len(events) / quiet, ending


def labeled_loss(model, plant, observations, truth):
    # Conditional calibration uses the closest force node and the known development path only.
    physics = physics_arrays(model)
    norms, departures, penalties = [], [], []
    for record, events in zip(observations, truth):
        y = (measurements(record) - model["mean"]) / model["scale"]
        y -= y[:30].mean(axis=0)
        modes = np.zeros(len(y), dtype=int)
        for e in events:
            allowed = np.flatnonzero((plant["code"] == e["code"]) & (plant["site"] == e["source"]))
            mode = allowed[np.argmin(abs(plant["strength"][allowed] - e["strength"]))]
            modes[e["onset"]:e["end"]] = mode
        state = np.zeros(30)
        error = y[29]
        departure = 0.
        for k in range(30, len(y)):
            j = modes[k]
            prior = mechanical_prediction(j, state, model["a"], model["b"], physics)
            residual = y[k] - terminal_prediction(j, prior, physics) - model["ar"] @ error
            z = model["white"][j] @ residual
            norms.append(z @ z)
            penalties.append(model["penalty"][j])
            departures.append(departure)
            state = prior + model["gain"][j] @ z
            error = y[k] - terminal_prediction(j, state, physics)
            voltage = y[k, :16] * model["scale"][:16]
            departure = voltage @ voltage / 8
    norms, departures = np.asarray(norms), np.asarray(departures)
    def loss(log_gamma):
        variance = 1 + np.expm1(log_gamma) * departures
        return float(np.mean(penalties) + .5 * np.mean(31*np.log(variance) + norms/variance))
    upper = np.log1p(1e12)
    interior = minimize_scalar(loss, method="bounded", bounds=(0., upper)).x
    best = min((0., interior, upper), key=loss)
    return loss(best), float(np.expm1(best))


def train():
    if FREEZE.exists() or (STORE / "test").exists():
        raise FileExistsError("Use a fresh study directory to repeat development")
    observations, truth = sequences("dev", True)
    onset, ending = fit_transitions(truth)
    instrument = fit_instrument(np.load(training_file(), mmap_mode="r"))
    plant = build_plant(Generator(), instrument[1])
    losses = {}
    for sigma in (.02, .1, .5, 2.0):
        model = prepare(plant, instrument, sigma, onset, ending)
        losses[sigma] = labeled_loss(model, plant, observations, truth)
    sigma = min(losses, key=lambda s: losses[s][0])
    model = prepare(plant, instrument, sigma, onset, ending)
    model["gamma"] = losses[sigma][1]
    traces = [trace(model, x) for x in observations]
    choices = []
    for gate in (.9, .99, .999):
        for identify in (.5, .8, .95):
            scored = evaluate(truth, [publish(z, model, gate, identify) for z in traces])
            episode_loss = scored["events"] - scored["joint"] + scored["event_record_extras"]
            choices.append((scored["quiet_extras"], episode_loss, -scored["joint"],
                            -gate, -identify, gate, identify, scored))
    *_, gate, identify, best = min(choices, key=lambda c: c[:5])
    np.savez_compressed(HERE / "model.npz", **model)
    write_json(FREEZE, dict(sigma=sigma, gamma=model["gamma"], onset=onset, ending=ending.tolist(), gate=gate, identify=identify,
               labeled_dev_nll_without_constant=losses, dev=best, codes={p:digest(HERE / p) for p in CODE},
               dev_manifest=digest(HERE / "dev_manifest.json"), model=digest(HERE / "model.npz"),
               training_observations=digest(training_file()), trees=digest(ROOT / "experiments/supervised_stream/successor/model.joblib")))
    print("frozen", sigma, gate, identify, best, flush=True)


def verify_freeze():
    frozen = read(FREEZE)
    if frozen["codes"] != {p:digest(HERE / p) for p in CODE} or frozen["model"] != digest(HERE / "model.npz"):
        raise ValueError("Frozen source or model changed")
    return frozen


def supervised(record, trees):
    import larger
    z = larger.first.normalized(record, trees["scales"])
    tau, cf = trees["thresholds"]
    outputs = []
    for start, when in larger.candidates(larger.telemetry(z, trees["trigger"], trees["clock"]), tau):
        prefix = z[:when + 1]
        prob = trees["family"].predict_proba(larger.family_features(prefix, start)[None, :])[0]
        if 1 - prob[0] >= cf:
            code = int(np.argmax(prob[1:]) + 1)
            rank = trees["rankers"][code].predict_proba(larger.ranking(prefix, start, code, trees))[:, 1]
            outputs.append(dict(detected=int(when), published=int(when), code=code,
                                source=trees["catalog"][code][int(np.argmax(rank))]))
    return outputs


def predict():
    from online import load_model
    frozen = verify_freeze()
    if digest(ROOT / "experiments/supervised_stream/successor/model.joblib") != frozen["trees"]:
        raise ValueError("Comparator changed")
    trees = load_model()
    with np.load(HERE / "model.npz") as stored:
        model = dict(stored)
    result = dict(graph=[], trees=[])
    for record in sequences("test"):
        result["graph"].append(publish(trace(model, record), model, frozen["gate"], frozen["identify"]))
        result["trees"].append(supervised(record, trees))
    path = HERE / "predictions.json"
    write_json(path, result)
    write_json(HERE / "seal.json", dict(predictions=digest(path), freeze=digest(FREEZE),
                                       manifest=digest(HERE / "test_manifest.json")))


def score():
    path = HERE / "predictions.json"
    seal = read(HERE / "seal.json")
    if seal != dict(predictions=digest(path), freeze=digest(FREEZE), manifest=digest(HERE / "test_manifest.json")):
        raise ValueError("Invalid prediction seal")
    truth = labels("test")
    report = {name:evaluate(truth, alarms, bootstrap=True) for name, alarms in read(path).items()}
    write_json(SCORES, report)
    print(report, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("dev", "train", "test", "predict", "score"))
    stage = parser.parse_args().stage
    if stage in ("dev", "test"):
        generate(stage)
    else:
        {"train": train, "predict": predict, "score": score}[stage]()
