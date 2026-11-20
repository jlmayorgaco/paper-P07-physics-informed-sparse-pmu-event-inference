"""Refit the historical nine-class ExtraTrees recipe on physically disjoint records."""
import joblib
import numpy as np

from common import DATA, FREEZE, FROZEN_TREES, HELD, REFIT, RESULT, ROOT, SUP, load, save, sha
import larger


def fit():
    if FREEZE.exists() or (DATA/"test").exists():
        raise FileExistsError("Cannot fit after freeze")
    DATA.mkdir(exist_ok=True, parents=True)
    history = ROOT/"tmp/supervised_stream/larger/train"
    rows = load(history/"truth.json")
    obs = np.load(history/"observations.npy", mmap_mode="r")
    manifest = load(SUP/"successor/train_manifest.json")
    import hashlib
    if sha(history/"observations.npy") != manifest["sha256_observations"] or hashlib.sha256(
            (history/"truth.json").read_bytes()).hexdigest() != manifest["sha256_truth"]:
        raise ValueError("Archived training stream changed")
    if sha(FROZEN_TREES) != load(SUP/"successor/model_freeze.json")["model_sha256"]:
        raise ValueError("Historical classifier changed")
    # The deterministic template bank and instrument calibration are physical inputs to both trees.
    archive = joblib.load(FROZEN_TREES)
    model = {k:archive[k] for k in ("scales","bank","catalog","spatial")}
    del archive
    ids = [i for i, events in enumerate(rows) if all(e["source"] not in HELD for e in events)]
    truth = [rows[i] for i in ids]
    zs = [larger.first.normalized(obs[i], model["scales"]) for i in ids]
    shuffled = np.random.default_rng(4711).permutation(len(ids))
    cutoff = len(ids)*4//5
    train, cal = shuffled[:cutoff], shuffled[cutoff:]
    trigger, clock = larger.gate_fit(zs, truth, train)
    tele = [larger.telemetry(z,trigger,clock) for z in zs]
    family = larger.fit_family(zs,truth,train,tele)
    counts = {(t,c):np.zeros(3,int) for t in larger.TAUS for c in larger.CONF}
    for i in cal:
        cache = {}
        for tau in larger.TAUS:
            proposals = list(larger.candidates(tele[i],tau))
            for start, _ in proposals:
                if start not in cache:
                    cache[start] = family.predict_proba(larger.family_features(zs[i],start)[None])[0,0]
            for cf in larger.CONF:
                actions = [a for a in proposals if 1-cache[a[0]] >= cf]
                counts[tau,cf] += larger.first.gate_counts(truth[i],actions)
    def objective(key):
        tp,fp,fn = counts[key]
        return 2*tp/max(1,2*tp+fp+fn), -fp
    model["thresholds"] = max(counts, key=objective)
    model["family"] = larger.fit_family(zs,truth,shuffled,tele)
    model["trigger"], model["clock"] = larger.gate_fit(zs,truth,shuffled)
    model["rankers"] = {}
    for code, sites in model["catalog"].items():
        valid = np.array([site not in HELD for site in sites])
        features, labels = [], []
        for i, events in enumerate(truth):
            for event in events:
                if event["code"] != code:
                    continue
                for shift in (-3,0,3):
                    features.append(larger.ranking(zs[i], event["onset"]+shift, code, model)[valid])
                    labels.extend(np.asarray(sites)[valid] == event["source"])
        ranker = larger.first.forest(64,18,2).fit(np.vstack(features), labels)
        ranker.n_jobs = 1
        model["rankers"][code] = ranker
    joblib.dump(model, REFIT, compress=3)
    seen = {str(c):sorted({e["source"] for r in truth for e in r if e["code"]==c}) for c in range(1,9)}
    save(RESULT/"tree_fit.json", dict(records=len(ids), training_record_ids=ids, held=sorted(HELD),
         labels_by_family=seen, threshold=model["thresholds"], historical=sha(FROZEN_TREES),
         refit=sha(REFIT), training_observations=sha(history/"observations.npy"),
         history_truth=sha(history/"truth.json")))
    print("Source-held-out comparator frozen", len(ids), flush=True)


if __name__ == "__main__":
    fit()
