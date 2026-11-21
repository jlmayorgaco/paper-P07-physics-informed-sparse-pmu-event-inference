"""Independently recount the paired decisions and emit the manuscript table."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = HERE / "results"


def read(name):
    return json.loads((RESULT / name).read_text(encoding="utf-8-sig"))


def checksum(name):
    return hashlib.sha256((RESULT / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main():
    scores, pred, truth, freeze = [read(f + ".json") for f in ("scores", "predictions", "truth", "freeze")]
    assert scores["prediction_sha"] == checksum("predictions.json")
    assert scores["truth_sha"] == checksum("truth.json") == pred["target_sha"]
    assert pred["freeze_sha"] == checksum("freeze.json")
    counts = scores["outcomes"]
    rows = []
    macros = {}
    names = {"mean": "Mean", "modal": "Mean + sine and cosine", "quadratic": "Mean + slope and curvature"}
    for arm, name in names.items():
        alarms = [(truth[k], a["arms"][arm]) for k, a in pred["calls"].items()]
        timely = [(t, a) for t, a in alarms if a and t["on"] is not None
                  and 30*t["on"] <= a["report"] < 30*t["off"]]
        values = [len(timely), sum(t["family"] == a["family"] for t, a in timely),
                  sum(t["source"] == a["source"] for t, a in timely),
                  sum(a is not None and t["on"] is None for t, a in alarms)]
        assert values == [counts[key][arm] for key in ("timely", "family", "site", "recovery_false_alarm")]
        rows.append(" & ".join([name, *map(str, values)]) + r" \\")
        macros[arm.title()+"Family"] = values[1]
        macros[arm.title()+"Quiet"] = scores["quiet"][arm]["alarms"]
    family = counts["family"]
    macros.update(Rows="\n".join(rows), Frequency=f"{freeze['mode_hz']:.2f}",
                  QuietHours=f"{scores['quiet']['modal']['hours']:.2f}",
                  QuietUpper=f"{scores['quiet']['modal']['poisson_upper95_h']:.2f}",
                  PMean=f"{family['exact_p']:.3g}", PQuadratic=f"{family['exact_p_vs_quad']:.3g}")
    second = RESULT.parent / "fixed_lag/results"
    conf = json.loads((second / "scores.json").read_text())
    calls = json.loads((second / "predictions.json").read_text())["calls"]
    targets = json.loads((second / "truth.json").read_text())
    for label, file in (("predictions_sha", "predictions"), ("truth_sha", "truth")):
        raw = (second / (file + ".json")).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == conf[label]
    labels = {"immediate": ("Sine and cosine","Immediate"),
              "mean_fixed": ("Mean","At alarm"), "modal_fixed": ("Sine and cosine","At alarm"),
              "quadratic_fixed": ("Slope and curvature","At alarm"),
              "mean_mixed": ("Mean","Averaged"), "modal_mixed": ("Sine and cosine","Averaged"),
              "quadratic_mixed": ("Slope and curvature","Averaged")}
    details = []
    for rule, (name, onset) in labels.items():
        nfamily = nsite = 0
        for k, a in calls.items():
            t = targets[k]
            if t["on"] is None or rule not in a["labels"]:
                continue
            b = a["alarm"]
            last = b if rule == "immediate" else b + 29
            if 30*t["on"] <= b and last < 30*t["off"]:
                fam, asset = a["labels"][rule]
                nfamily += int(fam == t["family"])
                nsite += int(asset == t["source"])
        assert (nfamily, nsite) == tuple(conf["totals"][rule][k] for k in ("family","site"))
        details.append(f"{name} & {onset} & {nfamily} & {nsite}" + r" \\")
    totals = conf["totals"]
    macros.update(ConfirmRows="\n".join(details), ConfirmNull=conf["normal_twins_with_alarm"],
                  ImmediateFamily=totals["immediate"]["family"], ConfirmFamily=totals["modal_mixed"]["family"],
                  ConfirmMean=totals["mean_mixed"]["family"], ConfirmQuad=totals["quadratic_mixed"]["family"],
                  TriggerCount=totals["immediate"]["in_time"], ConfirmSite=totals["modal_mixed"]["site"],
                  ConfirmP=f"{conf['paired_family']['immediate']['exact_p']:.2g}",
                  HolmMean=f"{conf['holm']['mean_mixed']:.3g}",
                  HolmQuad=f"{conf['holm']['quadratic_mixed']:.3g}")
    out = ["% Generated from the paired post-restoration decisions."]
    out += [r"\newcommand{\Modal"+key+"}{"+str(value)+"}" for key, value in macros.items()]
    (HERE.parents[1] / "generated/modal_recovery.tex").write_text("\n".join(out)+"\n", encoding="utf8")
    print("Recounted 96 paired histories and regenerated article macros.")


if __name__ == "__main__":
    main()
