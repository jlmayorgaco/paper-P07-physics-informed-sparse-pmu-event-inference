"""Generate article numbers from the archived, single-use comparison."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "generated/frozen/recovery_c02_20261105"
EXPECTED = "4f19cb72a2cf1929b5e68805c41fb00703fa88bdc365b726ed408fd57423349a"


def main():
    data = (SNAPSHOT / "TEST_EVALUATION.json").read_bytes()
    lock = json.loads((SNAPSHOT / "TEST_EVALUATION_LOCK.json").read_bytes())
    seal = json.loads((SNAPSHOT / "RESULTS_SEAL.json").read_bytes())
    if (hashlib.sha256(data).hexdigest() != EXPECTED
            or lock["result_sha256"] != EXPECTED or lock["status"] != "COMPLETE_SINGLE_USE"
            or seal["files"]["run/TEST_EVALUATION.json"] != EXPECTED):
        raise ValueError("Recovery result seal mismatch")
    report = json.loads(data)
    fields = {}
    for label, key in (("Bank", "PHYSICAL_HISTORY"), ("Glr", "PHYSICAL_CONTINUOUS_GLR"),
                       ("Trees", "EXTRATREES_ALL_SOURCES")):
        arm = report["arms"][key]
        fields.update({
            label + "Timely": f"{arm['timely_joint']}/{arm['events']}",
            label + "Extras": arm["event_extras"],
            label + "ExtrasRate": f"{arm['event_extras_per_h']:.1f}",
            label + "NormalAlarms": arm["normal_false_alarms"],
        })
    bank = report["arms"]["PHYSICAL_HISTORY"]
    fields.update(Parents=bank["event_parents"], NormalParents=bank["normal_parents"],
                  NormalHours=f"{bank['normal_monitored_s']/3600:.2f}",
                  NormalUpper=f"{bank['normal_Poisson_upper95_per_h']:.2f}")
    for label, key in (("Glr", "PHYSICAL_CONTINUOUS_GLR"), ("Trees", "EXTRATREES_ALL_SOURCES")):
        diff = report["paired_intervals"]["PHYSICAL_HISTORY-minus-" + key]
        d = diff["coverage_difference"]
        fields.update({label + "Diff": f"{100*d['point']:.1f}",
                       label + "CI": f"[{100*d['lower95']:.2f}, {100*d['upper95']:.2f}]"})
    lines = ["% Generated from the sealed recovery comparison. Do not edit."]
    lines += [fr"\newcommand{{\Rec{key}}}{{{value}}}" for key, value in fields.items()]
    (ROOT / "generated/recovery_comparison_macros.tex").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
