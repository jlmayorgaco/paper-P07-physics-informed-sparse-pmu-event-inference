"""Generate the exploratory coverage contrasts from the reproduced runs."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NAMES = {
    "moment_gaussian_minus_shared_covariance": "Moment",
    "mixture_minus_moment_gaussian": "Mixture",
}


def main():
    lines = []
    for i, seed in enumerate((20261114, 20261115)):
        data = json.loads((HERE / f"SEED_{seed}.json").read_text())
        if data["seed"] != seed:
            raise ValueError("Seed mismatch")
        metrics = data["per_scenario"]["base_unknown_onset"]["metrics"]
        for name, macro in NAMES.items():
            value = metrics["paired_bootstrap"][name]
            delta = value["delta_percentage_points"]
            lo, hi = value["bootstrap_95_pp"]
            arm = macro + ("One" if i == 0 else "Two")
            lines.append(rf"\newcommand{{\Bridge{arm}}}{{${delta:+.2f}$}}")
            lines.append(rf"\newcommand{{\Bridge{arm}CI}}{{[${lo:.2f}$, ${hi:.2f}$]}}")
    (ROOT / "generated/unknown_onset_bridge_macros.tex").write_text(
        "\n".join(lines) + "\n", encoding="ascii"
    )


if __name__ == "__main__":
    main()
