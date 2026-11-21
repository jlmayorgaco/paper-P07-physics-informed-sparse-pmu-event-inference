"""Fit angular likelihoods and select a threshold before any prospective simulation."""
from phase_data import TMP,RESULT,folder,study
from phase_model import train_recovery,train_switch
from benchmark import quiet,call,report
import joblib
import numpy as np


def records(split):
    manifest = study.read(TMP/split/"manifest.json")
    for k,expected in sorted(manifest["hashes"].items()):
        path = folder(split)/(k+".npz")
        assert study.digest(path)==expected
        yield k,*study.unpack(path)


def fit():
    records_fit = [(y,c) for _,y,c in records("fit")]
    with np.load(TMP/"recovery.npz") as z:
        bg = train_recovery(z,records_fit)
    joblib.dump(bg,TMP/"background.joblib",compress=3)
    residuals = [bg.residual(y,c) for y,c in records_fit]
    with np.load(TMP/"switch.npz") as z:
        gate = train_switch(residuals,z,60,4,(5,12,20,32,42))
        joblib.dump(gate,TMP/"detector.joblib",compress=3)
        readout = train_switch(residuals,z,84,4,np.arange(29,72))
        joblib.dump(readout,TMP/"source.joblib",compress=3)
    print("Fitted network responses, recovery estimator, detector and source readout.",flush=True)


def calibrate_quiet():
    bg,gate = [joblib.load(TMP/(n+".joblib")) for n in ("background","detector")]
    study.save(TMP/"quiet_cal.json",quiet("F01","CAL",bg,gate))


def select():
    bg,gate,readout = [joblib.load(TMP/(n+".joblib")) for n in ("background","detector","source")]
    peaks = [float(gate.scores(bg.residual(y,c)).max()) for _,y,c in records("cal")]
    quiet_max = max(v["peak"] for v in study.read(TMP/"quiet_cal.json").values())
    public = study.HERE/"conditional_switch/results"
    truth = study.read(TMP/"dev/targets.json")
    assert truth==study.read(public/"truth.json")
    baseline = {k:v["adjusted"] for k,v in study.read(public/"predictions.json")["calls"].items()}
    dev = [(k,c,bg.residual(y,c)) for k,y,c in records("dev")]
    # Include the strictest observed calibration recovery as a conservative operating point.
    bounds = sorted(set(max(quiet_max, sorted(peaks)[j]) for j in (312,317,319)))
    summaries = []
    for threshold in bounds:
        calls = {k:dict(magnitudes=baseline[k],angles=call(r,c,gate,readout,threshold)) for k,c,r in dev}
        value = report(truth,calls)
        summaries.append(dict(threshold=threshold,totals=value["totals"],bus31=value["sources"]["BUS31"],
                              qualifies=value["improved_in_development"]))
    viable = [row for row in summaries if row["qualifies"]]
    pick = max(viable,key=lambda v:(v["totals"]["exact"]["angles"],v["bus31"]["angles_detection"],
                -v["totals"]["control_alarm"]["angles"],-v["totals"]["early"]["angles"],v["threshold"])) if viable else None
    RESULT.mkdir(exist_ok=True)
    study.save(RESULT/"development.json",dict(quiet_max=quiet_max,calibration_peaks=peaks,grid=summaries,selected=pick))
    print(summaries,flush=True)


if __name__=="__main__":
    import sys
    {"fit":fit,"quiet":calibrate_quiet,"select":select}[sys.argv[1]]()
