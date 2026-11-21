"""Published HYDRA multivariate transform with a source-only classification head.

This arm has no detector. ``label`` is called at the shared trigger and consumes
the 84 reports ending at trigger + 29, matching the consolidated ROCKET arm.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys

import joblib
import numpy as np
import sklearn
import torch
from sklearn.linear_model import RidgeClassifierCV

from robust import TMP, RESULT, CONDITIONS, Errors, study, observations


UPSTREAM_REV = "144bb7aa3186654042f00f36b078370c620acb06"
HYDRA_SHA256 = "CE7181887D8696F270C979B91F555AE4ED59607DDC5FEA2701FE9A021C958C67"
SCALER_SHA256 = "56DE99EB1723567EE0A2B3763513ECB4A645D8B1732116C50A07AF2B2E3A2D4F"
GROUPS = 8
KERNELS_PER_GROUP = 4
FIT_BATCH = 16
ALPHAS = np.logspace(-3, 3, 10)


def upstream():
    """Import the hash-pinned authors' transform and sparse scaler."""
    root = TMP
    paths = {
        "hydra_multivariate.py": HYDRA_SHA256,
        "hydra_univariate.py": SCALER_SHA256,
    }
    for name, expected in paths.items():
        path = root / name
        if not path.exists():
            from urllib.request import urlopen
            upstream_name="hydra.py" if name=="hydra_univariate.py" else name
            url=f"https://raw.githubusercontent.com/angus924/hydra/{UPSTREAM_REV}/code/{upstream_name}"
            payload=urlopen(url,timeout=40).read()
            assert sha256(payload).hexdigest().upper()==expected
            root.mkdir(parents=True,exist_ok=True)
            path.write_bytes(payload)
        actual = sha256(path.read_bytes()).hexdigest().upper()
        if actual != expected:
            raise RuntimeError(f"Upstream source hash mismatch for {name}: {actual}")
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import hydra_multivariate
    import hydra_univariate
    return hydra_multivariate.HydraMultivariate, hydra_univariate.SparseScaler


def series(y):
    z = observations(y)
    return z - z[:30].mean(axis=0)


def block(z, end, length=84):
    if end < length - 1 or end >= len(z):
        raise ValueError("requested window is outside the available reports")
    return np.ascontiguousarray(z[end + 1 - length:end + 1].T, dtype=np.float32)


def transform(x, head, batch_size=FIT_BATCH):
    transform_model, scaler, _ = head
    tensor = torch.from_numpy(np.ascontiguousarray(x, dtype=np.float32))
    with torch.inference_mode():
        raw = transform_model.batch(tensor, batch_size=batch_size)
        return scaler.transform(raw).cpu().numpy()


def train_head(x, y):
    HydraMultivariate, SparseScaler = upstream()
    torch.set_num_threads(4)
    torch.manual_seed(381109)
    np.random.seed(381109)
    x = np.ascontiguousarray(x, dtype=np.float32)
    kernel_transform = HydraMultivariate(
        input_length=x.shape[-1], num_channels=x.shape[1],
        k=KERNELS_PER_GROUP, g=GROUPS, max_num_channels=8,
    ).cpu().eval()
    tensor = torch.from_numpy(x)
    with torch.inference_mode():
        raw = kernel_transform.batch(tensor, batch_size=FIT_BATCH)
    scaler = SparseScaler(mask=True, exponent=4)
    scaled = scaler.fit_transform(raw)
    classifier = RidgeClassifierCV(alphas=ALPHAS, class_weight="balanced")
    classifier.fit(scaled.cpu().numpy(), np.asarray(y))
    return kernel_transform, scaler, classifier


def fit():
    """Train only from the disclosed catalog records used by rocket_arm.py."""
    torch.set_num_threads(4)
    manifest = study.read(study.ROOT / "experiments/modal_recovery/clock_stress/results/inputs.json")
    truth = study.read(study.ROOT / "experiments/modal_recovery/clock_stress/results/truth.json")
    windows, labels, groups = [], [], []
    conditions = list(CONDITIONS.values())
    rng = np.random.default_rng(8036501)
    n_records = 0
    for key, target in sorted(truth.items()):
        if target["panel"] != "catalog":
            continue
        path = study.ROOT / "tmp/clock_stress/pmu" / (key + ".npz")
        assert study.digest(path) == manifest["records"][key]["sha"]
        y, clearance = study.unpack(path)
        error = Errors(510000 + target["parent"], len(y), clearance)
        for condition_index in (0, 1 + target["parent"] % 3):
            z = series(error.apply(y, conditions[condition_index]))
            if target["on"] is None:
                continue
            onset = int(np.ceil(30 * target["on"] - 1e-7))
            ends = np.maximum(clearance + 59, onset + rng.integers(0, 15, size=2)) + 29
            windows.extend(block(z, int(end)) for end in ends)
            labels.extend([target["source"]] * len(ends))
            groups.extend([target["parent"]] * len(ends))
        n_records += 1
    assert set(labels) and len(set(labels)) == 18, (len(set(labels)), sorted(set(labels)))
    head = train_head(np.stack(windows), labels)
    TMP.mkdir(parents=True, exist_ok=True)
    result_path = RESULT / "hydra.joblib"
    joblib.dump(head, result_path, compress=3)
    joblib.dump(head, TMP / "hydra_fitted.joblib", compress=3)
    metadata = {
        "source": "catalog panel only; paired positive/control records",
        "catalog_traces": n_records,
        "catalog_pairs": len(set(groups)),
        "source_windows": len(windows),
        "parent_groups": len(set(groups)),
        "classes": sorted(set(labels)),
        "upstream_repository": "https://github.com/angus924/hydra",
        "upstream_commit": UPSTREAM_REV,
        "multivariate_source_sha256": HYDRA_SHA256.lower(),
        "authors_sparse_scaler_sha256": SCALER_SHA256.lower(),
        "groups": GROUPS,
        "kernels_per_group": KERNELS_PER_GROUP,
        "batch_size": FIT_BATCH,
        "n_features": int(head[0].batch(torch.from_numpy(np.asarray(windows[:1])), batch_size=1).shape[1]),
        "classifier": "RidgeClassifierCV; alphas=logspace(-3,3,10); class_weight=balanced",
        "torch_seed": 381109,
        "numpy_window_seed": 8036501,
        "torch_version": torch.__version__,
        "numpy_version": np.__version__,
        "scikit_learn_version": sklearn.__version__,
    }
    (TMP / "hydra_fit.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf8")
    return head


def load_head():
    """Load the frozen source classifier from consolidated/results/hydra.joblib."""
    upstream()  # Ensure the original pickled transform class can be imported and verified.
    return joblib.load(RESULT / "hydra.joblib")


def label(y, b, model):
    """Return ``[family, site]`` at a common trigger, or None if unavailable."""
    if b is None or int(b) < 0 or int(b) + 29 >= len(y):
        return None
    z = series(y)
    sample = block(z, int(b) + 29)[None]
    prediction = str(model[2].predict(transform(sample, model, batch_size=1))[0])
    family = "load" if prediction.startswith("BUS") else "line"
    return [family, prediction]


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] != "fit":
        raise SystemExit("usage: python hydra_arm.py fit")
    fit()
