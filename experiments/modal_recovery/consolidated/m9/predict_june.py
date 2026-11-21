"""Predict only the original June submission on the frozen spatial264 records."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
import competition_held_locations as wrapper  # noqa: E402


def initialize(submitted: Path) -> None:
    # This is the same June model loader used by the held-location wrapper.
    wrapper.native.init_model(submitted)


def infer(folder: Path) -> tuple[str, list[int | str]]:
    api = wrapper.native.api
    frames = api._load_frames(folder)
    start, end = api._window_bounds(frames, 30)[-1]
    if start != 60 or end >= 90:
        raise ValueError(f"Unexpected decision window in {folder.name}: {(start, end)}")
    features = api._build_feature_rows(api._slice_frames(frames, start, end, True))
    row = wrapper.native.model.predict_from_features(*features).iloc[0]
    return folder.name, [int(row.pred_event), str(row.pred_location)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort", type=Path, default=REPO / "tmp/spatial264")
    parser.add_argument("--submitted", type=Path,
                        default=REPO / "tmp/competition_zip_verified")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("june_predictions.json"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("workers must be between 1 and 4")
    if not (args.submitted / "SUBMISSION_MANIFEST.md").is_file():
        parser.error("submission must be tmp/competition_zip_verified extraction")

    folders = [folder for split in ("primary", "quiet")
               for folder in sorted((args.cohort / split / "observations").iterdir())]
    with ProcessPoolExecutor(max_workers=args.workers,
                             initializer=initialize,
                             initargs=(args.submitted.resolve(),)) as pool:
        predictions = dict(pool.map(infer, folders))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(predictions, sort_keys=True, separators=(",", ":")) + "\n",
                           encoding="utf-8")
    print(f"Saved {len(predictions)} June decisions to {args.output}")


if __name__ == "__main__":
    main()
