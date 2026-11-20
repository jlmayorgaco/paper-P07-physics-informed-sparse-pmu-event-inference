"""Fit the same scale-mixture observer in the instrument's magnitude and phase coordinates."""
import sys
import numpy as np

from estimator import prepare, publish
from physical import Generator, build_plant, fit_instrument
from robust import SELECTION, calibration_innovations, fit_student, trace_student
from study import (FREEZE, HERE, STORE, digest, evaluate, labels, read, sequences,
                   training_file, verify_freeze, write_json)

LOCK = HERE / "phasor_freeze.json"
MODEL = HERE / "phasor_model.npz"
PRED = HERE / "phasor_predictions.json"
SEAL = HERE / "phasor_seal.json"


def fit():
    if (STORE / "test").exists() or LOCK.exists():
        raise FileExistsError("The successor must be frozen before generating test trajectories")
    gaussian = verify_freeze()
    observations, truth = sequences("dev", True)
    instrument = fit_instrument(np.load(training_file(), mmap_mode="r"), polar=True)
    plant = build_plant(Generator(), instrument[1], polar=True)
    params = {}
    ending = np.array(gaussian["ending"])
    for sigma in (.02, .1, .5, 2.):
        m = prepare(plant, instrument, sigma, gaussian["onset"], ending)
        params[sigma] = fit_student(*calibration_innovations(m, plant, observations, truth))
    sigma = min(params, key=lambda s:params[s][0])
    _, degrees, gamma = params[sigma]
    m = prepare(plant, instrument, sigma, gaussian["onset"], ending)
    m.update(degrees=degrees, gamma=gamma)
    traces = [trace_student(m, r) for r in observations]
    def risk(scores):
        return (scores["quiet_extras"], scores["events"]-scores["joint"]+scores["event_record_extras"],
                -scores["joint"])
    options = []
    for gate in (.9, .99, .999):
        for identify in (.5, .8, .95):
            scores = evaluate(truth, [publish(z, m, gate, identify) for z in traces])
            options.append(((*risk(scores), -gate, -identify), gate, identify, scores))
    _, gate, identify, scores = min(options, key=lambda item:item[0])
    control = read(SELECTION)
    risks = {k:risk(v) for k, v in (("graph", gaussian["dev"]), ("student", control["dev"]), ("phasor", scores))}
    primary = min(risks, key=risks.get)
    np.savez_compressed(MODEL, **m)
    write_json(LOCK, dict(primary=primary, selection_risks=risks, sigma=sigma, degrees=degrees, gamma=gamma,
                          gate=gate, identify=identify, conditional_losses=params, dev=scores,
                          gaussian=digest(FREEZE), student=digest(SELECTION), model=digest(MODEL),
                          source=digest(HERE / "phasors.py"), robust_source=digest(HERE / "robust.py")))
    print("selected", primary, "polar", sigma, degrees, gamma, scores, flush=True)


def predict():
    verify_freeze()
    frozen = read(LOCK)
    inputs = dict(gaussian=digest(FREEZE), student=digest(SELECTION), model=digest(MODEL),
                  source=digest(HERE / "phasors.py"), robust_source=digest(HERE / "robust.py"))
    if any(frozen[k] != v for k, v in inputs.items()):
        raise ValueError("Phasor freeze changed")
    with np.load(MODEL) as file:
        model = dict(file)
    predictions = [publish(trace_student(model, r), model, frozen["gate"], frozen["identify"])
                   for r in sequences("test")]
    write_json(PRED, predictions)
    write_json(SEAL, dict(predictions=digest(PRED), freeze=digest(LOCK), manifest=digest(HERE / "test_manifest.json")))


def score():
    if read(SEAL) != dict(predictions=digest(PRED), freeze=digest(LOCK), manifest=digest(HERE / "test_manifest.json")):
        raise ValueError("Phasor predictions differ from seal")
    result = evaluate(labels("test"), read(PRED), bootstrap=True)
    write_json(HERE / "phasor_scores.json", result)
    print(result, flush=True)


if __name__ == "__main__":
    {"fit": fit, "predict": predict, "score": score}[sys.argv[1]]()
