"""Positive control on the authors' released IEEE-68 features and trained ModelA."""

import argparse
import hashlib
from pathlib import Path
import sys
import urllib.request
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shared import RESULT, TMP, save

COMMIT = "f0e6ea244de74c23392e10202bd30049d5d2faa9"
BASE = (
    "https://raw.githubusercontent.com/Wendy0601/Identifying-Overlapping-Successive-Events-Using-a-Shallow-Convolutional-Neural-Network/"
    + COMMIT
)


def branch(x, weights, prefix):
    for i in (1, 2):
        scope = f"{prefix}_conv{i}/"
        weight, bias = ("weight", "bias") if prefix == "eigen" else ("wE", "bE")
        kernel = weights[scope + weight + str(i)][:, 0]
        x = x[:, :-1] @ kernel[0] + x[:, 1:] @ kernel[1] + weights[scope + bias + str(i)]
        # Their released evaluation notebook explicitly feeds phase_train=True.
        # Use its per-position batch moments ONLY for the external reproduction.
        x = (x - x.mean(0)) / np.sqrt(x.var(0) + 1e-3)
        x = np.maximum(x * weights[scope + "bn/gamma"] + weights[scope + "bn/beta"], 0)
        if i == 1:
            x = np.maximum(x[:, ::2], x[:, 1::2])
    suf = "" if prefix == "eigen" else "e"
    return np.maximum(
        x.reshape(len(x), -1) @ weights["eigen_out/wfc" + suf] + weights["eigen_out/bfc" + suf], 0
    )


def main(converted):
    cache = TMP / "upstream"
    cache.mkdir(exist_ok=True, parents=True)
    model = "modelA_ratio100_set01"
    paths = ["codes/saved_models/ModelA/" + model + ext for ext in (".index", ".data-00000-of-00001")]
    paths += [
        f"data/test/sub_features/one_sec/{field}_{tag}.npy"
        for tag in ("pred", "no")
        for field in ("Energy", "testX", "testY")
    ]
    hashes = {}
    for remote in paths:
        p = cache / Path(remote).name
        if not p.exists():
            urllib.request.urlretrieve(BASE + "/" + remote, p)
        hashes[remote] = hashlib.sha256(p.read_bytes()).hexdigest()
    if converted:
        w = dict(np.load(converted, allow_pickle=False))
    else:
        import tensorflow as tf

        reader = tf.train.load_checkpoint(str(cache / model))
        w = {k: reader.get_tensor(k) for k in reader.get_variable_to_shape_map()}
    out = {}
    for tag in ("pred", "no"):
        eigen = np.load(cache / f"testX_{tag}.npy").astype("float32")
        s = np.load(cache / f"Energy_{tag}.npy").astype("float32")
        truth = np.load(cache / f"testY_{tag}.npy").argmax(1)
        f = np.column_stack((branch(eigen, w, "eigen"), branch(s, w, "Singular")))
        predicted = (f @ w["Final_out/wout"] + w["Final_out/bout"]).argmax(1)
        out[tag] = dict(correct=int(sum(predicted == truth)), n=len(truth))
    save(
        RESULT / "upstream_control.json",
        dict(commit=COMMIT, inputs=hashes, source_checkpoint=model, counts=out),
    )
    print(out)


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--converted", type=Path, help="Exact named tensors exported from ModelA, optional")
    main(cli.parse_args().converted)
