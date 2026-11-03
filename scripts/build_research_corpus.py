"""Build a traceable research corpus; never consume partial C01 outcomes."""
from pathlib import Path
import csv
import datetime as dt
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "generated/frozen"
OUT = ROOT / "docs/corpus"
SGSMA = ROOT.parent / "SGSMA26-Physics-Informed-AD"
SOURCES = {}
ROWS = []
MASTER = {r["imported_name"]: r for r in csv.DictReader(
    (FROZEN / "SOURCE_MANIFEST.csv").open(encoding="utf-8-sig", newline=""))}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register(path, expected=None):
    path = path.resolve()
    digest = sha(path)
    if expected is not None:
        assert digest == expected, f"Frozen input changed: {path}"
    label = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    SOURCES[label] = {"sha256": digest, "bytes": path.stat().st_size}
    return path


def archived(name):
    return register(FROZEN / name, MASTER[name]["sha256"])


def records(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def add(group, method, metric, value, unit, denominator, independent, path, boundary):
    label = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    ROWS.append(dict(evidence=group, method=method, metric=metric,
                     value=float(value), unit=unit, denominator=denominator,
                     independent_unit=independent, source=label,
                     source_sha256=sha(path), boundary=boundary))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Protect immutable visual assets, including the approved block diagram.
    protected = {
        "figures/generated/event_signatures.pdf": "a85d23376f5f94c6956502553f424b5800ad66d262a0f042b579b1af6052c80d",
        "figures/generated/event_signatures.png": "8e8d78d043f68a154a64e588a28b638c7d6d3b3e1c7e03f1d3a866c33e3928da",
        "figures/narrative_architecture.tex": "b43a90a653cbeefb12f8dc843f143d47288583f922fa268a1a2a3b9a13d142c9",
    }
    for name, digest in protected.items():
        register(ROOT / name, digest)

    state = archived("e04a_b0_b1_b2_summary.csv")
    state_rows = records(state)
    assert all(int(r["n_trajectories"]) == 100 for r in state_rows)
    for r in state_rows:
        add("state_nominal", r["method"], "hidden_voltage_relative_error_mean",
            r["TVE_percent"], "%", 100, "test trajectory", state,
            "HVRE label; historical TVE_percent field is not PMU-compliance TVE. Matched short nominal simulation; not source accuracy.")

    recenter = archived("e06h_summary.csv")
    rec = records(recenter)[0]
    add("AC_recenter", "regularized_AC", "oracle_gap_closure_median",
        float(rec["closure_median"]) * 100, "%", rec["test_cases"],
        "test case", recenter,
        "M6 operating shift only; point recovery does not prove joint calibration or unique nuisance identification.")

    legacy = archived("legacy_replayed_summary.csv")
    with legacy.open(encoding="utf-8-sig", newline="") as stream:
        raw = list(csv.reader(stream))
    # The historical CSV has a two-level header with duplicated metric names.
    # DictReader would silently select standard deviations instead of means.
    means = next(r for r in raw[3:] if r[0] == "hierarchical_448_availability")
    for metric, col in [("detection_f1", 1), ("family_macro_f1", 3),
                        ("physical_top1", 5), ("physical_top3", 7),
                        ("integrity_top1", 11)]:
        assert raw[1][col] == "mean"
        add("legacy_known_sources", means[0], metric, means[col], "fraction",
            "historical grouped evaluation", "trajectory / grouped seed protocol",
            legacy, "Historical supervised replay; not official leaderboard or directly comparable to H04/C01 timely attribution.")

    unseen = archived("legacy_unseen_sources_recomputed.csv")
    u = records(unseen)
    correct = sum(r["correct"].lower() == "true" for r in u)
    assert len(u) == 303 and len({r["scenario_id"] for r in u}) == 101
    add("legacy_source_holdout", "historical_supervised", "exact_source_correct",
        correct, "count", len(u), "101 parents repeated with three seeds", unseen,
        "Family supplied; closed-label reachability must be considered. Not a claim that all ML fails on unseen sources.")

    support = archived("global137_support_summary.csv")
    for r in records(support):
        assert int(r["n"]) % 3 == 0
        for metric in ["top1", "top3"]:
            boundary = "Archived effective-prior implementation; known onset/context, loads only. "
            boundary += ("Joint K and support decision." if metric == "top1" else
                         "Pair-only rank conditional on K=2; not the joint Top-1 decision space.")
            add("GLOBAL137_archived", r["regime"], metric, 100 * float(r[metric]),
                "%", r["n"], f"{int(r['n']) // 3} physical trajectories, three noise seeds", support, boundary)
    run = archived("global137_run_manifest.csv")
    rm = records(run)[0]
    for metric in ["unique_physical_trajectories", "noise_rows", "hypotheses_per_case"]:
        add("GLOBAL137_archived", "GH31", metric, rm[metric], "count", "campaign",
            "physical trajectory, not each noise replay", run,
            "Metadata counts; do not equate decisions with independent physical trajectories.")

    fidelity = archived("likelihood120_physical_validation.csv")
    f = [r for r in records(fidelity) if int(r["T"]) == 120]
    for model in sorted({r["model"] for r in f}):
        selected = [r for r in f if r["model"] == model]
        assert len(selected) == 32
        add("T120_representation", model, "median_whitened_response_error",
            statistics.median(float(r["whitened_norm"]) for r in selected),
            "whitened norm", len(selected), "32 physical trajectories", fidelity,
            "Response fidelity only; not a localization-accuracy ablation, not a calibrated physical limit.")

    cont = FROZEN / "continuous_20261029"
    cm = json.loads((cont / "MANIFEST.json").read_text())
    cmap = {r["path"]: r["sha256"] for r in cm["files"]}
    events = register(cont / "H04/EVENTS.csv", cmap["H04/EVENTS.csv"])
    summary = register(cont / "H04/SUMMARY.csv", cmap["H04/SUMMARY.csv"])
    es, ss = records(events), records(summary)
    def truth(row, key):
        return row[key].lower() == "true"
    for method in ["R11", "R11_NOMINAL", "ET_REFERENCE", "ET_CANDIDATE", "R12"]:
        e = [r for r in es if r["method"] == method]
        s = [r for r in ss if r["method"] == method]
        assert len(e) == 54 and len({r["event"] for r in e}) == 18
        boundary = "H04 development; 18 interventions repeated across three R/X conditions, not independent confirmation."
        for metric, key in [("detected", "detected"), ("eventual_joint", "joint_top1"),
                            ("timely_joint", "diagnosis_before_off")]:
            add("H04_development", method, metric, sum(truth(r, key) for r in e),
                "count", len(e), "physical parent trajectory", events, boundary)
        for family in ["load", "line"]:
            selected = [r for r in e if r["family"] == family]
            add("H04_development", method, family + "_timely", sum(truth(r, "diagnosis_before_off") for r in selected),
                "count", len(selected), "physical parent trajectory", events, boundary)
        for metric, key in [("extras", "extras"), ("normal_FA", "normal_FA"),
                            ("normal_exposure_s", "normal_available_s")]:
            add("H04_development", method, metric, sum(float(r[key]) for r in s),
                "s" if metric.endswith("_s") else "count", "full H04 exposure",
                "physical parent trajectory", summary,
                boundary + " Only 204 s of normal exposure per arm; no strong low-FA-rate inference.")

    xroot = FROZEN / "shared_review_x01_20261030"
    xm = json.loads((xroot / "MANIFEST.json").read_text())
    # Keep the copied candidate's provenance rather than rerunning a benchmark
    # under the concurrent C01 workload.
    xp = xroot / "run/RESULTS.json"
    xentry = next(r for r in xm["files"] if r["path"] == "run/RESULTS.json")
    register(xp, xentry["sha256"])
    x = json.loads(xp.read_text())
    assert not x["IEEE39_physical_replay_executed"]
    for t in x["timings"]:
        for metric in ["p50_ms", "p95_ms", "p99_ms"]:
            add("X01_local_synthetic", t["method"], metric, t[metric], "ms",
                t["repetitions"], "interleaved kernel repetitions", xp,
                "Six synthetic fixtures; not IEEE-39 accuracy, R11 runtime, or end-to-end 30-fps performance.")
    add("X01_local_synthetic", "batched_GH31", "maximum_log_evidence_error",
        max(r["batched_log_evidence_error"] for r in x["equivalence"]),
        "absolute error", len(x["equivalence"]), "synthetic fixture", xp,
        "All 137 supports; equivalence to legacy arithmetic, not a correction of physical accuracy.")

    # A completed, separately sealed signature experiment has its own contract.
    ei = FROZEN / "ei_x02_20261030"
    if (ei / "MANIFEST.json").exists():
        em = json.loads((ei / "MANIFEST.json").read_text())
        expected = {x["path"]: x["sha256"] for x in em["files"]}
        ep = register(ei / "results/SUMMARY.csv", expected["results/SUMMARY.csv"])
        for row in records(ep):
            for metric in ["joint_correct", "conditional_source_correct", "normal_selected_event", "median_incremental_error"]:
                add("X02_IEEE39_signature", row["method"], metric, row[metric],
                    "fraction" if metric == "median_incremental_error" else "count",
                    15 if metric == "normal_selected_event" else 80 if metric == "median_incremental_error" else 240,
                    "85 physical cases; three common noise realizations", ep,
                    "Known family/onset/OFF, four load buses, scalar context. Not causal detection or C01; no extra localization gain over recentering.")
        ap = ROOT / "generated/ei_x02_amplitude_analysis.json"
        if ap.exists():
            register(ap)
            amplitude_data = json.loads(ap.read_text())
            register(ROOT / amplitude_data['source'], amplitude_data['source_sha256'])
            for row in amplitude_data["rows"]:
                add("X02_IEEE39_signature", row["method"], "median_relative_amplitude_error",
                    row["median_relative_amplitude_error_pct"], "%", row["records"],
                    "physical test case, three common noise seeds", ap,
                    "Severity evaluated under the generating source; both corrected arms select that source in all cases. No calibration claim.")

    # Verify the frozen executor without reading its partial predictions or
    # reserved event truth. Leave C01 entirely outside this result table.
    ef = SGSMA / "experiments/PAPER_CONFIRMATORY_C01/protocol/EXECUTION_FREEZE.json"
    register(ef)
    executor_checked = 0
    for row in json.loads(ef.read_text())["files"]:
        if "/execution/" in row["path"]:
            register(SGSMA / row["path"], row["sha256"])
            executor_checked += 1
    register(ROOT / "scripts/build_research_corpus.py")
    fields = list(ROWS[0])
    with (OUT / "RESULTS.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ROWS)
    text = ["# Resultados verificados del corpus", "",
            "Generados desde archivos con hashes. C01 está excluida hasta su cierre; "
            "no se leen sus predicciones parciales. Los resultados externos del chat "
            "no se mezclan con los ejecutados localmente.", "",
            "El CSV adjunto conserva fuente, hash, denominador y límite de cada cifra. "
            "Una comparación entre contratos diferentes no es una mejora porcentual válida.", "",
            "| Evidencia | Método / régimen | Métrica | Valor | Denominador |",
            "|---|---|---|---:|---|"]
    for row in ROWS:
        v = row["value"]
        display = f"{v:.6g}" if v else "0"
        text.append(f"| {row['evidence']} | {row['method']} | {row['metric']} | {display} {row['unit']} | {row['denominator']} |")
    text += ["", "## Lectura correcta", "",
             "- Estado: el error de voltaje no mide localización ni calibra la incertidumbre conjunta.",
             "- E_B: exactitud histórica bajo un prior efectivo auditado; Top-3 usa K=2 conocido.",
             "- T120: mejor ajuste físico no demuestra mejor decisión de soporte.",
             "- H04: desarrollo, catálogo restringido y 204 s normales; no score oficial de hackathon.",
             "- X01: equivalencia sintética y coste local; no nuevas simulaciones IEEE-39.",
             "- C01: incorporar solo tras verificar finalización, denominadores e importación de P07.", ""]
    (OUT / "RESULTS.md").write_text("\n".join(text), encoding="utf-8")
    # Bind the adjudication to its source inventory and all local corpus pages.
    ideas = records(OUT / "IDEAS.csv")
    assert len({r["id"] for r in ideas}) == len(ideas) == 32
    for name in ["README.md", "CONVERSATION_SYNTHESIS.md", "REVIEW_6ae55d7c.md",
                 "EQUATIONS_AND_STATUS.md", "EXPERIMENT_DECISIONS.md",
                 "IDEAS.csv", "review_source.json"]:
        register(OUT / name)
    for name in ["RESULTS.csv", "RESULTS.md"]:
        register(OUT / name)
    manifest = dict(created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                    result_rows=len(ROWS), adjudicated_ideas=len(ideas), sources=SOURCES,
                    protected_visuals_verified=True,
                    frozen_C01_executor_files_verified=executor_checked,
                    C01_partial_outcomes_read=False, C01_modified=False,
                    external_DICE_artifact_reproduced=False, RAW0002_opened=False)
    (OUT / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "sources"}, indent=2))


if __name__ == "__main__":
    main()
