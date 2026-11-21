"""Apply both frozen methods to the twelve motivating, previously disclosed failures."""
from cohort import HERE
from run import RESULT, infer, models, trial, verify
from metrics import outcomes
import study


def main():
    frozen = verify()
    estimators = models()
    diagnosis = study.read(HERE/"diagnosis.json")
    truth = study.read(trial.RESULT/"truth.json")
    old = study.read(trial.RESULT/"predictions.json")["calls"]
    controls = {t["parent"]:k for k,t in truth.items() if t["on"] is None}
    cases = []
    for case in diagnosis["cases"]:
        key = case["id"]
        twin = controls[case["parent"]]
        calls = {}
        for k in (key,twin):
            path = trial.TMP/"test"/(k+".npz")
            assert study.digest(path)==old[k]["sha"]
            calls[k] = infer(*study.unpack(path),*estimators,frozen)
            assert calls[k]["current"]["alarm"]==old[k]["alarm"]
        r = calls[key]["adjusted"]
        cases.append(dict(id=key, previous_failure=case["category"], asset=case["second"],
                          adjusted_alarm=r["alarm"], **outcomes(truth[key],r),
                          twin_alarm=calls[twin]["adjusted"]["alarm"]))
    result = dict(freeze_sha=study.digest(RESULT/"freeze.json"),cases=cases)
    path = RESULT/"retrospective.json"
    if path.exists():
        assert study.read(path)==result
    else:
        study.save(path,result)
    for category in ("early","miss"):
        group = [c for c in cases if c["previous_failure"]==category]
        print(category, "timely, exact, early, control",
              [sum(c[k] for c in group) for k in ("detection","exact","early")],
              sum(c["twin_alarm"] is not None for c in group))


if __name__ == "__main__":
    main()
