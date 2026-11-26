import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from competition_electrical_localizer import network_signatures

SEED = 746191
DRAWS = 256
FAMILIES = (1, 2, 3, 4, 6, 8)
CONDITIONS = (("0 dB", 1.0), ("10 dB", 10.0), ("20 dB", 100.0), ("Noiseless", None))
TIE_TOL = 1e-10


def direction_roof(matrix):
    matrix = matrix - matrix.mean(axis=1, keepdims=True)
    unit = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    unique = []
    for direction in unit:
        if not any(abs(np.vdot(old, direction)) ** 2 >= 1 - 1e-10 for old in unique):
            unique.append(direction)
    return len(unique) / len(matrix)


def score_hits(matrix, observation, true_index):
    """Fractional hits for each column (one realization) of observation."""
    centered = matrix - matrix.mean(axis=1, keepdims=True)
    centered_y = observation - observation.mean(axis=0)
    gains = np.abs(centered.conj() @ centered_y) ** 2 / np.sum(np.abs(centered) ** 2, axis=1)[:, None]
    tied = gains >= gains.max(axis=0) * (1 - TIE_TOL)
    return tied[true_index] / tied.sum(axis=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    signatures = network_signatures(args.data_path)
    rng = np.random.default_rng(SEED)
    grouped = []
    roofs = {}
    for family in FAMILIES:
        sites = sorted(signatures[family])
        physical = np.asarray([signatures[family][site] for site in sites], dtype=complex)
        if physical.shape[1] != 8:
            raise ValueError(f"Family {family} must have eight PMU channels")
        configs = [("Full", np.arange(8))]
        configs += [(f"Leave out {(2,5,6,10,19,22,29,39)[i]}", np.delete(np.arange(8), i)) for i in range(8)]
        centered_full = physical - physical.mean(axis=1, keepdims=True)
        norms = np.linalg.norm(centered_full, axis=1)
        if np.any(norms == 0):
            raise ValueError(f"Family {family} contains a constant signature")
        for label, channels in configs:
            roofs[family, label] = direction_roof(physical[:, channels])

        for source_index, site in enumerate(sites):
            phases = rng.uniform(0, 2 * np.pi, DRAWS)
            noise = (rng.standard_normal((8, DRAWS)) + 1j * rng.standard_normal((8, DRAWS))) / np.sqrt(2)
            offsets = rng.standard_normal(DRAWS) + 1j * rng.standard_normal(DRAWS)
            for condition, snr in CONDITIONS:
                amplitude = 1.0 / norms[source_index] if snr is None else np.sqrt(7 * snr) / norms[source_index]
                scale = 0.0 if snr is None else 1.0
                counts = {label: 0.0 for label, _ in configs}
                signal = amplitude * physical[source_index, :, None] * np.exp(1j * phases)
                noisy = signal + scale * noise + offsets
                rotated = noisy * np.exp(0.731j) + (0.37 - 0.29j)
                for label, channels in configs:
                    matrix = physical[:, channels]
                    hit = score_hits(matrix, noisy[channels], source_index)
                    check = score_hits(matrix, rotated[channels], source_index)
                    np.testing.assert_array_equal(hit, check)
                    counts[label] = float(hit.sum())
                for label, _ in configs:
                    fraction = counts[label] / DRAWS
                    roof = roofs[family, label]
                    grouped.append({
                        "family": family, "condition": condition, "source": site,
                        "configuration": label, "correct_count": counts[label],
                        "draws": DRAWS, "accuracy": fraction, "noiseless_roof": roof,
                    })

    grouped_path = args.out / "grouped_counts.csv"
    fields = list(grouped[0])
    with grouped_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(grouped)

    summary = []
    for family in FAMILIES:
        for condition, _ in CONDITIONS:
            for label in ["Full"] + [f"Leave out {(2,5,6,10,19,22,29,39)[i]}" for i in range(8)]:
                rows = [r for r in grouped if r["family"] == family and
                        r["condition"] == condition and r["configuration"] == label]
                if condition == "Noiseless":
                    np.testing.assert_allclose(np.mean([r["accuracy"] for r in rows]), roofs[family,label], atol=1e-12)
                summary.append({
                    "family": family, "condition": condition, "configuration": label,
                    "accuracy": np.mean([r["accuracy"] for r in rows]),
                    "noiseless_roof": roofs[family, label],
                    "sources": len(rows), "draws_per_source": DRAWS,
                })
    summary_path = args.out / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    fig, axes = plt.subplots(1, 4, figsize=(10, 3.2), sharey=True)
    family_x = np.arange(len(FAMILIES))
    for ax, (condition, _) in zip(axes, CONDITIONS):
        full_values, loo_low, loo_high, roof_low, roof_high = [], [], [], [], []
        for family in FAMILIES:
            rows = [r for r in summary if r["family"] == family and r["condition"] == condition]
            full_values.append(next(r["accuracy"] for r in rows if r["configuration"] == "Full"))
            loo = [r["accuracy"] for r in rows if r["configuration"].startswith("Leave out")]
            loo_low.append(min(loo))
            loo_high.append(max(loo))
            ceilings = [roofs[family, "Full"]] + [roofs[family, f"Leave out {(2,5,6,10,19,22,29,39)[i]}"] for i in range(8)]
            roof_low.append(min(ceilings))
            roof_high.append(max(ceilings))
        ax.errorbar(family_x - 0.12, full_values, fmt="o", color="#245b8f",
                    label="Full-array accuracy")
        ax.vlines(family_x, loo_low, loo_high, color="#d07a24", linewidth=4,
                  label="Leave-one-out accuracy range")
        ax.vlines(family_x + 0.12, roof_low, roof_high, color="#39845a", linewidth=3,
                  linestyles="dashed", label="Noiseless direction ceiling range")
        ax.set_title(condition)
        ax.set_xticks(family_x, ["Fault", "Line", "Gen.", "Load", "Mixed", "Comp."], rotation=40, ha="right")
        ax.set_ylim(-0.03, 1.03)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Fraction correctly resolved")
    axes[0].set_xlabel("Physical family")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0,.14,1,1))
    figure_path = args.out / "resolution.pdf"
    fig.savefig(figure_path, bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)

    tex = []
    for family, tag in ((1, "Bus"), (2, "Branch"), (3, "Gen"), (4, "Load")):
        row = next(r for r in summary if r["family"] == family and r["configuration"] == "Full" and r["condition"] == "Noiseless")
        resolved = round(row["accuracy"] * row["sources"])
        tex.append(r"\newcommand{\Resolution" + tag + "}{" + f"{resolved}/{row['sources']}" + "}")
    (args.out / "macros.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")

    dictionary_hash = hashlib.sha256()
    for family in FAMILIES:
        for site in sorted(signatures[family]):
            dictionary_hash.update(str(family).encode())
            dictionary_hash.update(site.encode())
            dictionary_hash.update(np.asarray(signatures[family][site], dtype=np.complex128).tobytes())
    code_hash = hashlib.sha256(Path(__file__).read_text(encoding="utf-8").encode("utf-8")).hexdigest()
    figure_hash = hashlib.sha256(figure_path.read_bytes()).hexdigest()
    fingerprint = {
        "seed": SEED, "draws_per_source": DRAWS,
        "dictionary_sha256": dictionary_hash.hexdigest(),
        "code_sha256": code_hash, "figure_sha256": figure_hash,
        "grouped_csv": grouped_path.name, "summary_csv": summary_path.name,
        "figure": figure_path.name,
    }
    (args.out / "fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()