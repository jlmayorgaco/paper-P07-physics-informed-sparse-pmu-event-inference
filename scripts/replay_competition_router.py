"""Route archived competition windows and optional causal dynamic diagnoses.

The frontend supplies a provisional class, integrity status and affected PMUs.
A unique confirmed physical diagnosis may replace both family and source.
Missing data and a physical event compose code 6. Corruption retains code 7.
This replay consumes predictions, never event annotations.
Each input file represents one record, with times in seconds from its start.
Optional --dynamic JSON rows carry family_code (1 through 4), source, emitted_s,
last_report_used_s and available. Use actual decision times, not fitted onsets.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path


def route(window, diagnoses):
    code = window["legacy_event"]
    if window["available"] and code not in range(9):
        raise ValueError(f"Unknown competition code {code}")
    result = {key: window[key] for key in (
        "window_index", "available", "emitted_s", "integrity_status", "integrity_sources"
    )}
    result.update(event_code=code, physical_family=window["physical_event"],
                  physical_source=window["physical_source"], source_route="frontend")
    if not window["available"]:
        result.update(event_code=None, physical_family=None, physical_source=None,
                      source_route="unavailable")
        return result
    if window["last_report_used_s"] > window["emitted_s"]:
        raise ValueError("Frontend used observations after its decision")
    if code == 7 or window["integrity_status"] == "corrupt":
        return result
    candidates = {(d["family_code"], d["source"]) for d in diagnoses if d["available"]
               and window["window_start_s"] <= d["emitted_s"] < window["window_end_s"]
               and d["emitted_s"] <= window["emitted_s"]}
    if len(candidates) == 1:
        family, source = candidates.pop()
        missing = code in (5, 6) or window["integrity_status"] == "missing"
        result.update(event_code=6 if missing else family, physical_family=family,
                      physical_source=source, source_route="physical_expert")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("windows", type=Path)
    parser.add_argument("--dynamic", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    windows = json.loads(args.windows.read_text())["windows"]
    diagnoses = json.loads(args.dynamic.read_text()) if args.dynamic else []
    for d in diagnoses:
        if d["available"] and (d["family_code"] not in (1, 2, 3, 4) or not d["source"]
                or not math.isfinite(d["emitted_s"]) or not math.isfinite(d["last_report_used_s"])
                or d["last_report_used_s"] > d["emitted_s"]):
            raise ValueError("Invalid dynamic diagnosis or noncausal timestamp")
    predictions = [route(w, diagnoses) for w in windows]
    if args.output:
        args.output.write_text(json.dumps(predictions, indent=2), encoding="utf-8")
    print(json.dumps({"windows": len(predictions),
                      "class_counts": dict(Counter(p["event_code"] for p in predictions)),
                      "source_routes": dict(Counter(p["source_route"] for p in predictions))}))


if __name__ == "__main__":
    main()
