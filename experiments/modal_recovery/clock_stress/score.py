"""Unblind all prespecified stress levels together and compute the paired endpoints."""
import csv
from dataclasses import asdict
import gzip
import json
import shutil
from stress_plan import GRID,RESULT,TMP,SIZES,study,verify
from metrics import outcomes
from scipy.stats import beta


def unpack(pair):
    return dict(alarm=pair[0],label=pair[1])


def seal_calls():
    verify()
    files = ("inputs.json","protocol_seal.json","calls.json.gz","quiet.json")
    study.save(RESULT/"prediction_seal.json",dict(results={k:study.digest(RESULT/k) for k in files},
               harness={k:study.digest(RESULT.parent/k) for k in ("predict.py","score.py")}))


def exact95(k,n):
    return [float(beta.ppf(.05,k,n-k+1)) if k else 0.,float(beta.ppf(.95,k+1,n-k)) if k<n else 1.]


def summarize(cases,split,level):
    n = SIZES[split]
    keys = ("detection","family","exact","early","control_alarm")
    totals = {k:0 for k in keys}
    baseline = {k:0 for k in keys}
    new_false = removed_false = magnitudes_detected_31 = detected_31 = n31 = 0
    natives = []
    by_parent = {}
    for t,v in cases:
        a,b = outcomes(t,unpack(v["magnitude"])), outcomes(t,unpack(v["phase"][level]))
        for k in b:
            totals[k] += b[k]
            baseline[k] += a[k]
        by_parent.setdefault(t["parent"],[]).append(t)
        if t["on"] is None:
            new_false += b["control_alarm"] and not a["control_alarm"]
            removed_false += a["control_alarm"] and not b["control_alarm"]
        elif t["source"]=="BUS31":
            n31+=1
            detected_31 += b["detection"]
            magnitudes_detected_31 += a["detection"]
        if t["on"] is not None:
            natives.append(("line" if t["first"].startswith("LINE") else "load",t["family"]))
    assert len(cases)==2*n and len(by_parent)==n
    for pair in by_parent.values():
        assert len(pair)==2 and sum(t["on"] is None for t in pair)==1
        assert pair[0]["first"]==pair[1]["first"] and pair[0]["clearance"]==pair[1]["clearance"]
    if split=="catalog":
        assert all(natives.count((x,y))==n//4 for x in ("line","load") for y in ("line","load"))
    else:
        assert n31==n and natives.count(("line","load"))==n//2
    return dict(n=n,angular=totals,magnitude=baseline,new_false=new_false,removed_false=removed_false,
                n31=n31,detected31=detected_31,baseline31=magnitudes_detected_31,
                bounds={k:exact95(v,n) for k,v in totals.items()},excess_false_upper95=exact95(new_false,n)[1])


def write_csv(rows):
    dest = RESULT/"operating_points.csv"
    fields = ("axis","angle_deg","jitter_us","offset_us","drift_us_s","step_us","det","family","exact",
              "false","early","magnitude_false","gained_false","relieved_false","bus31_det","bus31_exact","bus31_false",
              "quiet_episodes","quiet_records","primary_pass","including_quiet_pass")
    with dest.open("x",newline="",encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(fields)
        for v in rows:
            s,cat,focus,q = v["setting"],v["catalog"],v["bus31"],v["quiet"]
            a,b = cat["angular"],focus["angular"]
            writer.writerow([s["name"],s["angle"],s["jitter"],s["offset"],s["drift"],s["step"],
                a["detection"],a["family"],a["exact"],a["control_alarm"],a["early"],cat["magnitude"]["control_alarm"],
                cat["new_false"],cat["removed_false"],b["detection"],b["exact"],b["control_alarm"],
                q["angular_episodes"],q["angular_records"],v["primary_pass"],v["including_quiet_pass"]])


def score():
    verify()
    seal = study.read(RESULT/"prediction_seal.json")
    assert all(study.digest(RESULT/k)==v for k,v in seal["results"].items())
    assert all(study.digest(RESULT.parent/k)==v for k,v in seal["harness"].items())
    manifest = study.read(RESULT/"inputs.json")
    truth_path = RESULT/"truth.json" if (RESULT/"truth.json").exists() else TMP/"targets.json"
    assert study.digest(truth_path)==manifest["targets_sha"]
    truth = study.read(truth_path)
    calls = json.loads(gzip.decompress((RESULT/"calls.json.gz").read_bytes()))
    assert calls.keys()==truth.keys()==manifest["records"].keys()
    normals = study.read(RESULT/"quiet.json")
    rows = []
    panels = {p:[(t,calls[k]) for k,t in truth.items() if t["panel"]==p] for p in SIZES}
    for i,s in enumerate(GRID):
        cat,focus = (summarize(panels[p],p,i) for p in ("catalog","bus31"))
        hours = sum(r["reports"] for r in normals.values())/108000
        quiet = dict(hours=hours,angular_episodes=sum(r["phase"][i] for r in normals.values()),
                     angular_records=sum(r["phase"][i]>0 for r in normals.values()),
                     magnitude_episodes=sum(r["magnitude"] for r in normals.values()))
        a = cat["angular"]
        passed = (all(a[k]*100>95*cat["n"] for k in ("detection","family","exact"))
                  and focus["detected31"]*100>95*focus["n"] and a["control_alarm"]*100<5*cat["n"]
                  and a["control_alarm"]<=cat["magnitude"]["control_alarm"])
        rows.append(dict(setting=asdict(s),catalog=cat,bus31=focus,quiet=quiet,primary_pass=passed,
                         including_quiet_pass=passed and quiet["angular_episodes"]<=quiet["magnitude_episodes"]))
    result = dict(prediction_seal=study.digest(RESULT/"prediction_seal.json"),points=rows)
    if (RESULT/"scores.json").exists():
        assert result==study.read(RESULT/"scores.json")
    else:
        shutil.copyfile(truth_path,RESULT/"truth.json")
        study.save(RESULT/"scores.json",result)
        write_csv(rows)
    for family in dict.fromkeys(s.name for s in GRID):
        points = [r for r in rows if r["setting"]["name"]==family]
        print(family, [r["primary_pass"] for r in points], [r["including_quiet_pass"] for r in points])


if __name__=="__main__":
    import sys
    {"seal":seal_calls,"score":score}[sys.argv[1]]()
