#!/usr/bin/env python3
"""Fail-closed, single-use C03 import. Default action is read-only --check."""
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCI = ROOT.parent / "SGSMA26-Physics-Informed-AD"
RUN = SCI / "experiments/PAPER_RECOVERY_C03/run"
SNAP = ROOT / "generated/frozen/recovery_c03"
TABLE = ROOT / "tables/generated/recovery_c03.tex"
MACROS = ROOT / "generated/recovery_c03_macros.tex"
ARMS = ("history", "carry", "reset")
PLANTS = ("F01", "P2")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def canonical(value) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def required(run: Path, name: str) -> Path:
    p = run / name
    if not p.is_file():
        raise Pending(f"missing {name}")
    return p


def frozen_path(run: Path, name: str) -> Path:
    p = Path(name)
    if p.is_absolute():
        return p
    for candidate in (run / p, run.parent / p):
        if candidate.is_file():
            return candidate
    return run.parent / p


class Pending(Exception):
    pass


def check_execution(run: Path):
    # Validate frozen inputs by their recorded hashes; never read scenario truth.
    names = ("SCENARIO_FREEZE.json", "EXECUTION_FREEZE.json", "CAL_SELECTION.json",
             "DETECTABILITY_FREEZE.json", "METHOD_FREEZE.json", "TEST_F01_SEAL.json",
             "TEST_P2_SEAL.json", "TEST_PREDICTIONS_SEAL.json", "TEST_RESULTS.json",
             "TEST_EVALUATION_LOCK.json", "DEPENDENCIES.json", "PLANT2_VALIDATION.json",
             "RUNTIME_SMOKE.json")
    files = {n: required(run, n) for n in names}
    scenario, execution = read(files[names[0]]), read(files[names[1]])
    selection, detect, method = read(files[names[2]]), read(files[names[3]]), read(files[names[4]])
    combined, result, lock = read(files[names[7]]), files[names[8]], read(files[names[9]])
    if (run / "execution.lock").exists():
        raise Pending("C03 campaign still holds execution.lock")
    if scenario.get("status") != "FROZEN_BEFORE_OBSERVATIONS":
        raise ValueError("Scenario freeze is not in the expected frozen state")
    for name, expected in scenario.get("sources", {}).items():
        p = frozen_path(run, name)
        if not p.is_file() or sha(p) != expected:
            raise ValueError(f"Frozen scenario input changed or missing: {name}")
    if execution.get("test_access") is not False:
        raise ValueError("Execution freeze does not assert TEST access was withheld")
    for name, expected in execution.get("sources", {}).items():
        p = frozen_path(run, name)
        if not p.is_file() or sha(p) != expected:
            raise ValueError(f"Frozen execution input changed or missing: {name}")
    for key, filename in (("dependency_seal", "DEPENDENCIES.json"),
                          ("scenarios", "SCENARIO_FREEZE.json"),
                          ("plant2", "PLANT2_VALIDATION.json"),
                          ("runtime_smoke", "RUNTIME_SMOKE.json")):
        p = files[filename]
        if sha(p) != execution.get(key):
            raise ValueError(f"Execution seal mismatch: {filename}")
    if method.get("execution") != sha(files["EXECUTION_FREEZE.json"]):
        raise ValueError("METHOD_FREEZE execution hash mismatch")
    if method.get("selection") != sha(files["CAL_SELECTION.json"]):
        raise ValueError("METHOD_FREEZE CAL selection hash mismatch")
    if method.get("detectability") != sha(files["DETECTABILITY_FREEZE.json"]):
        raise ValueError("METHOD_FREEZE detectability hash mismatch")
    if method.get("test_observations_not_accessed_before_freeze") is not True:
        raise ValueError("METHOD_FREEZE lacks the pre-TEST freeze assertion")
    if combined.get("method_freeze") != sha(files["METHOD_FREEZE.json"]):
        raise ValueError("Combined TEST prediction seal points to a different method freeze")
    seal_hashes = {}
    prediction_maps = {}
    for plant in PLANTS:
        seal_name = f"TEST_{plant}_SEAL.json"
        seal = read(files[seal_name])
        expected = combined.get("locks", {}).get(seal_name)
        if expected != sha(files[seal_name]):
            raise ValueError(f"Combined prediction seal mismatch: {seal_name}")
        predmap = seal.get("predictions")
        if not isinstance(predmap, dict) or not predmap:
            raise ValueError(f"Empty prediction manifest: {seal_name}")
        prediction_maps[plant] = predmap
        seal_hashes[seal_name] = sha(files[seal_name])
    if lock.get("status") != "COMPLETE_SINGLE_USE":
        raise Pending("TEST evaluation lock is not COMPLETE_SINGLE_USE")
    if lock.get("result_sha256") != sha(result):
        raise ValueError("TEST result hash does not match its evaluation lock")
    if lock.get("predictions") != sha(files["TEST_PREDICTIONS_SEAL.json"]):
        raise ValueError("Evaluation lock prediction-seal hash mismatch")
    payload = read(result)
    if payload.get("submission_ready") is not False:
        raise ValueError("C03 result must not claim submission readiness")
    return files, payload, selection, prediction_maps, seal_hashes


def verify_predictions(run: Path, maps):
    # Called only after COMPLETE_SINGLE_USE and all result/lock checks pass.
    checked = 0
    for plant, manifest in maps.items():
        for rel, expected in manifest.items():
            p = (run / rel).resolve()
            if not p.is_relative_to(run.resolve()) or not p.is_file():
                raise ValueError(f"Prediction path escapes RUN or is missing: {rel}")
            if sha(p) != expected:
                raise ValueError(f"Sealed prediction changed: {rel}")
            checked += 1
    return checked


def _summary(payload, plant, arm):
    try:
        return payload["results"][plant]["nominal"][arm]
    except (KeyError, TypeError) as e:
        raise ValueError(f"Missing nominal result for {plant}/{arm}") from e


def validate_rows(payload):
    validation = {"plants": {}, "primary_events": 0, "total_events": 0}
    for plant in PLANTS:
        arms = {a: _summary(payload, plant, a) for a in ARMS}
        ids_by_arm = {}
        reference_event_ids = None
        for arm, entry in arms.items():
            rows = entry.get("rows")
            if not isinstance(rows, list) or len(rows) != 72:
                raise ValueError(f"{plant}/{arm}: expected all 72 event+normal parents")
            ids = [r.get("id") for r in rows]
            if None in ids or len(set(ids)) != 72:
                raise ValueError(f"{plant}/{arm}: missing/duplicate parent rows")
            kinds = {k: sum(r.get("kind") == k for r in rows) for k in ("event", "normal")}
            if kinds != {"event": 36, "normal": 36}:
                raise ValueError(f"{plant}/{arm}: expected 36 event and 36 normal parents")
            if any(not isinstance(r.get("available"), bool) for r in rows):
                raise ValueError(f"{plant}/{arm}: unavailable parents are not explicitly retained")
            ids_by_arm[arm] = ids
        if any(ids_by_arm[a] != ids_by_arm["history"] for a in ARMS):
            raise ValueError(f"{plant}: arms are not parent-paired")
        arm_metrics = {}
        for arm, entry in arms.items():
            rows = entry["rows"]
            event_rows = [r for r in rows if r["kind"] == "event"]
            normal_rows = [r for r in rows if r["kind"] == "normal"]
            ev_count = primary = short_timely = all_timely = 0
            event_ids = []
            for row in event_rows:
                events = row.get("rows") or []
                if len(events) != 6:
                    raise ValueError(f"{plant}/{arm}/{row['id']}: expected six scored events")
                if sum(bool(e.get("short_gap")) for e in events) != 4:
                    raise ValueError(f"{plant}/{arm}/{row['id']}: expected four primary short-gap events")
                if any(not isinstance(e.get("timely"), bool) or not isinstance(e.get("short_gap"), bool) for e in events):
                    raise ValueError(f"{plant}/{arm}/{row['id']}: missing scored event outcomes")
                event_ids.extend(e.get("id") for e in events)
                if row.get("id") is None or any(eid is None for eid in event_ids):
                    raise ValueError(f"{plant}/{arm}/{row['id']}: missing event identity")
                ev_count += len(events)
                primary += sum(e["short_gap"] for e in events)
                short_timely += sum(e["short_gap"] and e["timely"] for e in events)
                all_timely += sum(e["timely"] for e in events)
            if reference_event_ids is None:
                reference_event_ids = event_ids
            elif event_ids != reference_event_ids:
                raise ValueError(f"{plant}/{arm}: arms do not contain paired event outcomes")
            if any(r.get("rows") for r in normal_rows):
                raise ValueError(f"{plant}/{arm}: normal parent contains event rows")
            if (ev_count, primary) != (216, 144):
                raise ValueError(f"{plant}/{arm}: event denominators are {ev_count}/{primary}")
            if any(float(r.get("planned_exposure", -1)) != 588 for r in normal_rows):
                raise ValueError(f"{plant}/{arm}: planned normal exposure must be 588 s per parent")
            for row in rows:
                expected_planned = 108 if row["kind"] == "event" else 588
                if float(row.get("planned_exposure", -1)) != expected_planned:
                    raise ValueError(f"{plant}/{arm}/{row['id']}: incorrect planned exposure")
                expected_actual = expected_planned if row["available"] else 0
                if float(row.get("exposure", -1)) != expected_actual:
                    raise ValueError(f"{plant}/{arm}/{row['id']}: availability/exposure mismatch")
                for count in ("alarms", "extras", "open_episodes", "unmatched_restorations"):
                    if int(row.get(count, -1)) < 0:
                        raise ValueError(f"{plant}/{arm}/{row['id']}: missing/invalid {count}")
            extras = sum(int(r.get("extras", -1)) for r in event_rows)
            normal_alarms = sum(int(r.get("alarms", -1)) for r in normal_rows)
            normal_hours = sum(float(r.get("exposure", -1)) for r in normal_rows) / 3600
            planned_normal_hours = sum(float(r.get("planned_exposure", -1)) for r in normal_rows) / 3600
            event_hours = sum(float(r.get("exposure", -1)) for r in event_rows) / 3600
            summary = entry.get("summary", {})
            expected_metrics = {"events": ev_count, "short_events": primary, "short_timely": short_timely,
                "all_timely": all_timely, "extras": extras, "normal_alarms": normal_alarms,
                "unavailable": sum(not r["available"] for r in rows)}
            for key, expected in expected_metrics.items():
                if summary.get(key) != expected:
                    raise ValueError(f"{plant}/{arm}: aggregate {key}={summary.get(key)!r}, rows imply {expected}")
            for key, expected in (("normal_hours", normal_hours), ("planned_normal_hours", planned_normal_hours),
                                  ("event_hours", event_hours)):
                try: actual = float(summary[key])
                except (KeyError, TypeError, ValueError) as e: raise ValueError(f"{plant}/{arm}: missing {key}") from e
                if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9):
                    raise ValueError(f"{plant}/{arm}: aggregate {key} does not match parent exposure")
            if summary.get("extras_per_hour") is None and event_hours > 0:
                raise ValueError(f"{plant}/{arm}: missing event extra rate")
            if event_hours > 0 and not math.isclose(float(summary["extras_per_hour"]), extras/event_hours, rel_tol=0, abs_tol=1e-8):
                raise ValueError(f"{plant}/{arm}: event extra rate does not match rows/exposure")
            arm_metrics[arm] = {"parents": 72, "events": ev_count, "primary_events": primary,
                "timely_primary": short_timely, "timely_all": all_timely, "extras": extras,
                "normal_alarms": normal_alarms, "normal_hours": normal_hours,
                "planned_normal_hours": planned_normal_hours, "event_hours": event_hours}
        for key in ("history_vs_carry", "carry_vs_reset"):
            contrast = payload.get("contrasts", {}).get(plant, {}).get(key)
            if not contrast or not isinstance(contrast.get("coverage"), dict):
                raise ValueError(f"Missing paired coverage interval: {plant}/{key}")
            for field in ("difference", "lower95", "upper95"):
                if not math.isfinite(float(contrast["coverage"][field])):
                    raise ValueError(f"Invalid paired interval value: {plant}/{key}/{field}")
        validation["plants"][plant] = {"parents_per_arm": 72, "event_parents": 36,
            "normal_parents": 36, "arms": arm_metrics,
            "unavailable_by_arm": {a: sum(not r["available"] for r in arms[a]["rows"]) for a in ARMS}}
        validation["primary_events"] += 144
        validation["total_events"] += 216
    if validation["primary_events"] != 288 or validation["total_events"] != 432:
        raise ValueError("Across two plants expected 288 primary and 432 total event rows")
    return validation


def validate_cal(selection):
    out = {}
    for arm in ARMS:
        choice = selection.get(arm)
        if not isinstance(choice, dict) or not isinstance(choice.get("feasible"), bool):
            raise ValueError(f"Missing CAL feasibility for {arm}")
        cal = choice.get("cal") or {}
        try:
            threshold = float(choice["threshold"])
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(f"Missing selected threshold for {arm}") from e
        if not math.isfinite(threshold):
            raise ValueError(f"Non-finite selected threshold for {arm}")
        if choice["feasible"] and (not math.isfinite(float(cal.get("normal_hours", float("nan"))))
                or not math.isfinite(float(cal.get("planned_normal_hours", float("nan"))))):
            raise ValueError(f"Missing CAL exposure for {arm}")
        out[arm] = {"feasible": choice["feasible"], "threshold": threshold,
                    "normal_hours": cal.get("normal_hours"),
                    "planned_normal_hours": cal.get("planned_normal_hours"),
                    "normal_upper95_poisson": cal.get("normal_upper95_poisson")}
    return out


def tex_escape(x):
    return str(x).replace("_", r"\_")


def fmt_num(x, nd=1):
    return "--" if x is None else f"{float(x):.{nd}f}"


PLANT_MACRO = {"F01": "FOne", "P2": "PTwo"}


def render(payload, validation, cal):
    lines = ["% Generated from the single-use C03 sealed result. Do not edit.",
             r"\begin{tabular}{llrrrrrr}",
             r"Plant & Arm & CAL & Short/144 & Extra & FA & Normal h a/p & U95/h\\", r"\hline"]
    macro = ["% Generated from the single-use C03 sealed result. Do not edit."]
    macro += [r"\newcommand{\CThreeTotalEvents}{432}", r"\newcommand{\CThreePrimaryEvents}{288}"]
    for plant in PLANTS:
        for arm in ARMS:
            entry = _summary(payload, plant, arm)
            s = entry.get("summary", {})
            feasible = "PASS" if cal[arm]["feasible"] else "FAIL"
            row = rf"{plant} & {arm} & {feasible} & {s.get('short_timely', 0)}/144 & {s.get('extras', 0)} & {s.get('normal_alarms', 0)} & {fmt_num(s.get('normal_hours'), 2)}/{fmt_num(s.get('planned_normal_hours'), 2)} & {fmt_num(s.get('normal_upper95_poisson'), 2)}\\"
            lines.append(row)
            prefix = "CThree" + PLANT_MACRO[plant] + arm.title()
            fields = {"ShortTimely": str(s.get("short_timely", 0)), "Extras": str(s.get("extras", 0)),
                      "NormalAlarms": str(s.get("normal_alarms", 0)), "NormalHours": fmt_num(s.get("normal_hours"), 2),
                      "NormalUpper": fmt_num(s.get("normal_upper95_poisson"), 2),
                      "Unavailable": str(s.get("unavailable", 0))}
            for suffix, value in fields.items():
                macro.append(rf"\newcommand{{\{prefix}{suffix}}}{{{value}}}")
        for key, label in (("history_vs_carry", "HistoryCarry"), ("carry_vs_reset", "CarryReset")):
            c = payload["contrasts"][plant][key]
            vals = c["coverage"]
            # Source contrast is a fraction; publish percentage points.
            prefix = "CThree" + PLANT_MACRO[plant] + label
            for suffix, field in (("DifferencePP", "difference"), ("LowerPP", "lower95"), ("UpperPP", "upper95")):
                macro.append(rf"\newcommand{{\{prefix}{suffix}}}{{{100*float(vals[field]):.1f}}}")
            er = c.get("extras_per_hour") or {}
            if er:
                for suffix, field in (("ExtraRateDiff", "difference"), ("ExtraRateLower", "lower95"), ("ExtraRateUpper", "upper95")):
                    macro.append(rf"\newcommand{{\{prefix}{suffix}}}{{{float(er[field]):.1f}}}")
    lines += [r"\hline", r"\multicolumn{8}{l}{CAL FAIL means the arm did not meet the calibration target.}",
              r"\end{tabular}", "% CAL exposure is separate from held-out exposure."]
    for arm, c in cal.items():
        macro.append(rf"\newcommand{{\CThreeCal{arm.title()}Feasible}}{{{str(c['feasible']).lower()}}}")
        if c["threshold"] is not None:
            macro.append(rf"\newcommand{{\CThreeCal{arm.title()}Threshold}}{{{float(c['threshold']):.4f}}}")
        macro.append(rf"\newcommand{{\CThreeCal{arm.title()}Exposure}}{{{fmt_num(c['normal_hours'], 2)}/{fmt_num(c['planned_normal_hours'], 2)}}}")
    return ("\n".join(lines)+"\n").encode(), ("\n".join(macro)+"\n").encode()


def bundle(run: Path, dry=False):
    files, payload, selection, maps, seal_hashes = check_execution(run)
    validation = validate_rows(payload)
    cal = validate_cal(selection)
    # --check validates the manifest chain only; touch prediction payloads
    # only during an explicit import after the single-use result lock closes.
    checked = verify_predictions(run, maps) if not dry else sum(len(v) for v in maps.values())
    rendered_table, rendered_macros = render(payload, validation, cal)
    audit = {"status": "IMPORTED_SINGLE_USE_C03", "source_run": str(run.resolve()),
             "result_sha256": sha(files["TEST_RESULTS.json"]), "prediction_seal_sha256": sha(files["TEST_PREDICTIONS_SEAL.json"]),
             "plant_prediction_seals": seal_hashes, "prediction_files_verified": checked,
             "execution_freeze_sha256": sha(files["EXECUTION_FREEZE.json"]),
             "method_freeze_sha256": sha(files["METHOD_FREEZE.json"]),
             "scenario_freeze_sha256": sha(files["SCENARIO_FREEZE.json"]),
             "selection_sha256": sha(files["CAL_SELECTION.json"]), "validation": validation,
             "calibration": cal, "decision": payload.get("decision"), "submission_ready": False}
    if dry:
        return audit
    if SNAP.exists() or TABLE.exists() or MACROS.exists():
        raise FileExistsError("C03 destination already exists; immutable import will not replace it")
    SNAP.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="recovery_c03_import_", dir=SNAP.parent))
    try:
        # Compact, self-contained evidence only; no raw truth or predictions copied.
        for name in ("TEST_RESULTS.json", "TEST_EVALUATION_LOCK.json", "TEST_PREDICTIONS_SEAL.json",
                     "TEST_F01_SEAL.json", "TEST_P2_SEAL.json", "CAL_SELECTION.json",
                     "METHOD_FREEZE.json", "EXECUTION_FREEZE.json", "SCENARIO_FREEZE.json",
                     "DETECTABILITY_FREEZE.json", "DEPENDENCIES.json",
                     "PLANT2_VALIDATION.json", "RUNTIME_SMOKE.json"):
            shutil.copyfile(files[name], stage / name)
        (stage / "VALIDATION.json").write_bytes(canonical(audit))
        (stage / "TABLE.tex").write_bytes(rendered_table)
        (stage / "MACROS.tex").write_bytes(rendered_macros)
        manifest = {p.name: sha(p) for p in stage.iterdir() if p.is_file()}
        (stage / "BUNDLE_MANIFEST.json").write_bytes(canonical({"status": "IMMUTABLE_COMPACT_IMPORT", "files": manifest}))
        os.replace(stage, SNAP)
        TABLE.parent.mkdir(parents=True, exist_ok=True)
        MACROS.parent.mkdir(parents=True, exist_ok=True)
        # Both outputs are derived from the compact snapshot, never from RUN.
        TABLE.write_bytes(rendered_table)
        MACROS.write_bytes(rendered_macros)
    except Exception:
        if stage.exists(): shutil.rmtree(stage)
        raise
    return audit


def verify_bundle():
    if not SNAP.is_dir(): raise FileNotFoundError(SNAP)
    manifest = read(SNAP / "BUNDLE_MANIFEST.json")
    listed = manifest.get("files")
    if manifest.get("status") != "IMMUTABLE_COMPACT_IMPORT" or not isinstance(listed, dict) or not listed:
        raise ValueError("Invalid or empty compact bundle manifest")
    expected_files = {"TEST_RESULTS.json", "TEST_EVALUATION_LOCK.json", "TEST_PREDICTIONS_SEAL.json",
        "TEST_F01_SEAL.json", "TEST_P2_SEAL.json", "CAL_SELECTION.json", "METHOD_FREEZE.json",
        "EXECUTION_FREEZE.json", "SCENARIO_FREEZE.json", "DETECTABILITY_FREEZE.json",
        "DEPENDENCIES.json", "PLANT2_VALIDATION.json", "RUNTIME_SMOKE.json", "VALIDATION.json",
        "TABLE.tex", "MACROS.tex"}
    if set(listed) != expected_files:
        raise ValueError("Compact bundle manifest has missing or unexpected entries")
    for name, expected in listed.items():
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError(f"Unsafe compact bundle path: {name}")
        p = SNAP / name
        if not p.is_file() or sha(p) != expected: raise ValueError(f"Bundle file hash mismatch: {name}")
    payload = read(SNAP / "TEST_RESULTS.json")
    lock = read(SNAP / "TEST_EVALUATION_LOCK.json")
    combined = read(SNAP / "TEST_PREDICTIONS_SEAL.json")
    method = read(SNAP / "METHOD_FREEZE.json")
    execution = read(SNAP / "EXECUTION_FREEZE.json")
    if lock.get("status") != "COMPLETE_SINGLE_USE" or lock.get("result_sha256") != sha(SNAP / "TEST_RESULTS.json"):
        raise ValueError("Compact result/evaluation-lock chain is invalid")
    if lock.get("predictions") != sha(SNAP / "TEST_PREDICTIONS_SEAL.json"):
        raise ValueError("Compact evaluation lock does not seal prediction manifests")
    if combined.get("method_freeze") != sha(SNAP / "METHOD_FREEZE.json"):
        raise ValueError("Compact combined prediction seal points to another method freeze")
    for plant in PLANTS:
        name = f"TEST_{plant}_SEAL.json"
        if combined.get("locks", {}).get(name) != sha(SNAP / name):
            raise ValueError(f"Compact plant prediction seal mismatch: {plant}")
        if not read(SNAP / name).get("predictions"):
            raise ValueError(f"Compact plant prediction manifest is empty: {plant}")
    if method.get("execution") != sha(SNAP / "EXECUTION_FREEZE.json"):
        raise ValueError("Compact method freeze execution hash mismatch")
    if method.get("selection") != sha(SNAP / "CAL_SELECTION.json"):
        raise ValueError("Compact method freeze selection hash mismatch")
    if method.get("detectability") != sha(SNAP / "DETECTABILITY_FREEZE.json"):
        raise ValueError("Compact method freeze detectability hash mismatch")
    for key, filename in (("dependency_seal", "DEPENDENCIES.json"), ("scenarios", "SCENARIO_FREEZE.json"),
                          ("plant2", "PLANT2_VALIDATION.json"), ("runtime_smoke", "RUNTIME_SMOKE.json")):
        if execution.get(key) != sha(SNAP / filename): raise ValueError(f"Compact execution seal mismatch: {filename}")
    if payload.get("submission_ready") is not False:
        raise ValueError("Compact C03 result must not claim submission readiness")
    validation_record = read(SNAP / "VALIDATION.json")
    validation = validate_rows(payload)
    if validation_record.get("validation") != validation:
        raise ValueError("Compact validation record no longer matches result rows")
    cal = validate_cal(read(SNAP / "CAL_SELECTION.json"))
    table, macros = render(payload, validation, cal)
    if table != (SNAP / "TABLE.tex").read_bytes() or macros != (SNAP / "MACROS.tex").read_bytes():
        raise ValueError("Compact bundle does not regenerate its derived TeX")
    if table != TABLE.read_bytes() or macros != MACROS.read_bytes():
        raise ValueError("Workspace TeX does not match the compact C03 snapshot")
    return len(manifest.get("files", {}))


def self_test():
    """Tooling-only fixture; synthetic numbers are never manuscript evidence."""
    global SNAP, TABLE, MACROS
    with tempfile.TemporaryDirectory(prefix="p07_c03_import_test_") as td:
        base = Path(td); run = base / "run"; run.mkdir()
        out_before = {p: (p.exists(), sha(p) if p.is_file() else None) for p in (SNAP, TABLE, MACROS)}
        # Pending check: no run artifact or output path may be created/changed.
        try:
            bundle(run, dry=True)
            raise AssertionError("incomplete fixture unexpectedly passed")
        except Pending:
            pass
        assert not list(run.iterdir())
        assert out_before == {p: (p.exists(), sha(p) if p.is_file() else None) for p in (SNAP, TABLE, MACROS)}

        def put(name, value):
            p = run / name; p.write_bytes(canonical(value)); return p
        source = base / "frozen_input.txt"; source.write_text("fixed", encoding="utf-8")
        put("SCENARIO_FREEZE.json", {"status": "FROZEN_BEFORE_OBSERVATIONS", "sources": {str(source): sha(source)}})
        for name, body in (("DEPENDENCIES.json", {}), ("PLANT2_VALIDATION.json", {"valid": True}),
                           ("RUNTIME_SMOKE.json", {"cal_only": True})):
            put(name, body)
        execution = {"test_access": False, "sources": {str(source): sha(source)},
                     "dependency_seal": sha(run/"DEPENDENCIES.json"),
                     "scenarios": sha(run/"SCENARIO_FREEZE.json"),
                     "plant2": sha(run/"PLANT2_VALIDATION.json"),
                     "runtime_smoke": sha(run/"RUNTIME_SMOKE.json")}
        ex = put("EXECUTION_FREEZE.json", execution)
        cal = {a: {"feasible": True, "threshold": 1.0, "cal": {"normal_hours": 6.0,
               "planned_normal_hours": 6.0, "normal_upper95_poisson": 0.5}} for a in ARMS}
        cal["reset"] = {"feasible": False, "threshold": 6.9}
        selection = put("CAL_SELECTION.json", cal)
        detect = put("DETECTABILITY_FREEZE.json", {"fixture": True})
        method = put("METHOD_FREEZE.json", {"execution": sha(ex), "selection": sha(selection),
                     "detectability": sha(detect), "test_observations_not_accessed_before_freeze": True})
        combined_locks, plant_maps = {}, {}
        for plant in PLANTS:
            pred = run / f"{plant}_prediction.json"; pred.write_text("synthetic tooling fixture", encoding="utf-8")
            seal_name = f"TEST_{plant}_SEAL.json"
            seal = put(seal_name, {"predictions": {pred.name: sha(pred)}})
            combined_locks[seal_name] = sha(seal); plant_maps[plant] = {pred.name: sha(pred)}
        combined = put("TEST_PREDICTIONS_SEAL.json", {"method_freeze": sha(method),
                        "locks": combined_locks})
        contrasts, results = {}, {}
        for plant in PLANTS:
            arms = {}
            base_rows = []
            for i in range(36):
                base_rows.append({"id": f"{plant}_E{i}", "kind": "event", "available": True,
                    "exposure": 108, "planned_exposure": 108, "alarms": 1, "extras": 1,
                    "open_episodes": 0, "unmatched_restorations": 0,
                    "rows": [{"id": f"{plant}_E{i}_e{j}", "short_gap": j < 4, "timely": j < 3} for j in range(6)]})
            base_rows.extend({"id": f"{plant}_N{i}", "kind": "normal", "available": True,
                              "exposure": 588, "planned_exposure": 588, "alarms": 0, "extras": 0,
                              "open_episodes": 0, "unmatched_restorations": 0, "rows": []} for i in range(36))
            for arm in ARMS:
                arms[arm] = {"rows": base_rows, "summary": {"events": 216, "short_events": 144,
                    "short_timely": 108, "all_timely": 108, "extras": 36, "normal_alarms": 0,
                    "normal_hours": 5.88, "planned_normal_hours": 5.88, "event_hours": 1.08,
                    "extras_per_hour": 36/1.08, "normal_upper95_poisson": 0.51, "unavailable": 0}}
            results[plant] = {"nominal": arms}
            contrast = {"difference": 0.0, "lower95": -0.1, "upper95": 0.1}
            contrasts[plant] = {k: {"coverage": contrast, "extras_per_hour": contrast}
                                for k in ("history_vs_carry", "carry_vs_reset")}
        result = put("TEST_RESULTS.json", {"submission_ready": False, "decision": "TOOLING_FIXTURE",
                          "results": results, "contrasts": contrasts})
        lock = put("TEST_EVALUATION_LOCK.json", {"status": "COMPLETE_SINGLE_USE",
                          "result_sha256": sha(result), "predictions": sha(combined)})
        files, payload, selected, maps, _ = check_execution(run)
        validation = validate_rows(payload); checked_cal = validate_cal(selected); verify_predictions(run, maps)
        table, macros = render(payload, validation, checked_cal)
        assert b"FAIL" in table and b"5.88/5.88" in table
        assert b"\\CThreeFOneHistoryShortTimely" in macros and b"\\CThreePTwoHistoryShortTimely" in macros
        pdflatex = shutil.which("pdflatex")
        if not pdflatex:
            raise RuntimeError("pdflatex is required for the importer TeX self-test")
        texdir = base / "tex"; texdir.mkdir()
        (texdir / "table.tex").write_bytes(table); (texdir / "macros.tex").write_bytes(macros)
        (texdir / "check.tex").write_text("\\documentclass{article}\n\\usepackage[margin=1in]{geometry}\n"
            "\\input{macros.tex}\n\\begin{document}\n\\CThreeFOneHistoryShortTimely\\par\n"
            "\\input{table.tex}\n\\end{document}\n", encoding="utf-8")
        proc = __import__("subprocess").run([pdflatex, "-interaction=nonstopmode", "-halt-on-error", "check.tex"],
            cwd=texdir, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if proc.returncode != 0 or not (texdir / "check.pdf").is_file():
            raise RuntimeError("Generated TeX fixture failed to compile:\n" + proc.stdout[-4000:])
        # Exercise regeneration and the compact snapshot chain without source RUN access.
        old_paths = SNAP, TABLE, MACROS
        SNAP, TABLE, MACROS = base/"snapshot", base/"table.tex", base/"macros.tex"
        try:
            SNAP.mkdir()
            compact_names = ("TEST_RESULTS.json", "TEST_EVALUATION_LOCK.json", "TEST_PREDICTIONS_SEAL.json",
                "TEST_F01_SEAL.json", "TEST_P2_SEAL.json", "CAL_SELECTION.json", "METHOD_FREEZE.json",
                "EXECUTION_FREEZE.json", "SCENARIO_FREEZE.json", "DETECTABILITY_FREEZE.json",
                "DEPENDENCIES.json", "PLANT2_VALIDATION.json", "RUNTIME_SMOKE.json")
            for name in compact_names: shutil.copyfile(files[name], SNAP/name)
            (SNAP/"VALIDATION.json").write_bytes(canonical({"validation": validation}))
            (SNAP/"TABLE.tex").write_bytes(table); (SNAP/"MACROS.tex").write_bytes(macros)
            TABLE.write_bytes(table); MACROS.write_bytes(macros)
            listed = {p.name: sha(p) for p in SNAP.iterdir() if p.is_file()}
            (SNAP/"BUNDLE_MANIFEST.json").write_bytes(canonical({"status": "IMMUTABLE_COMPACT_IMPORT", "files": listed}))
            assert verify_bundle() == len(listed)
            broken = json.loads(json.dumps(payload))
            broken["results"]["F01"]["nominal"]["reset"]["summary"]["short_timely"] += 1
            try:
                validate_rows(broken)
                raise AssertionError("summary/row disagreement unexpectedly passed")
            except ValueError as e:
                assert "short_timely" in str(e)
        finally:
            SNAP, TABLE, MACROS = old_paths
        # A post-lock mutation must be rejected before validation/import.
        result.write_bytes(result.read_bytes() + b"tamper\n")
        try:
            check_execution(run)
            raise AssertionError("tampered result unexpectedly passed")
        except ValueError as e:
            assert "result hash" in str(e)
        print("SELF_TEST_OK pending-no-writes; tampered-result-rejected; summary/denominators; TeX compile; bundle-chain verification; synthetic fixture only")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="read-only validation (default)")
    ap.add_argument("--import", dest="do_import", action="store_true", help="import only after complete lock validation")
    ap.add_argument("--verify-bundle", action="store_true", help="verify/regenerate check from imported compact data")
    ap.add_argument("--self-test", action="store_true", help="run synthetic tooling-only fail-closed checks")
    ap.add_argument("--source-run", type=Path, default=RUN)
    args = ap.parse_args()
    try:
        if args.self_test:
            self_test()
        elif args.verify_bundle:
            print(f"BUNDLE_OK {verify_bundle()} files")
        elif args.do_import:
            result = bundle(args.source_run.resolve())
            print("IMPORTED", json.dumps(result, sort_keys=True))
        else:
            result = bundle(args.source_run.resolve(), dry=True)
            print("COMPLETE_VALID", json.dumps(result, sort_keys=True))
    except Pending as e:
        print(f"PENDING: {e}")
        return 2
    except Exception as e:
        print(f"INVALID: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
