"""Optimistic bound for equal-prior weak sources at nominal strength and supplied onset."""
import csv
from pathlib import Path

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import norm

from trial import dyn, simulate, SIGMA


def main():
    plant = dyn.Plant()
    sites = list(range(1, 40))
    means = np.array([simulate(plant, "weak", bus, 1, 7)[0].ravel() for bus in sites])
    distances = pdist(means / SIGMA)
    pairs = zip(*np.triu_indices(len(sites), 1))
    used = set()
    records = []
    for distance, (a, b) in sorted(zip(distances, pairs)):
        if a in used or b in used:
            continue
        used.update((a, b))
        error = norm.sf(distance / 2)
        records.append((sites[a], sites[b], distance, error))
    path = Path(__file__).with_name("weak_pairs.csv")
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["bus_a", "bus_b", "whitened_distance", "binary_error"])
        writer.writerows(records)
    # A genie reveals the disjoint pair containing the source (or the singleton).
    print("Equal-prior accuracy upper bound", 1 - 2 * sum(r[3] for r in records) / len(sites))


if __name__ == "__main__":
    main()
