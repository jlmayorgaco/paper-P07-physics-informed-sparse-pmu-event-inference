"""Calibrate voltage responses at every eligible M9 asset in a separate process."""

import argparse
import json
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import least_squares
from scipy.signal import periodogram

from competition_electrical_localizer import network_signatures
from competition_response_bank import BUSES


def frequencies(values, t):
    values = values - values.mean()
    frequencies = []
    residual = values.copy()
    for _ in range(2):
        freq, power = periodogram(residual, fs=30, nfft=65536, window="hann")
        band = (freq >= 0.012) & (freq <= 0.35)
        frequencies.append(freq[band][power[band].argmax()])

        def error(f):
            z = 2 * np.pi * t[:, None] * f
            a = np.column_stack([np.ones(len(t)), np.sin(z), np.cos(z)])
            return values - a @ np.linalg.lstsq(a, values, rcond=None)[0]

        frequencies = least_squares(error, frequencies, bounds=(0.01, 0.36)).x.tolist()
        residual = error(frequencies)
    return frequencies


def build(archive, data, out):
    sys.path.insert(0, str(archive / "V5"))
    from src.simulation.m9.generator import (
        generate_physical_truth,
        get_template,
        list_templates,
    )

    names = sorted(n for n in list_templates() if n.startswith("TEMPLATE_EVENT"))
    meta = archive / "data/metadata"

    def simulate(spec, duration):
        state = generate_physical_truth(
            meta / "IEEE_39_Bus_Power_System.raw",
            meta / "PMUbus_ Location.txt",
            spec,
            seed=610881,
            duration_s=duration,
        )
        ix = [state.bus_order.index(f"BUS{b}") for b in BUSES]
        return state.voltage_complex_pu[:, ix]

    quiet = simulate(get_template(names[0]), 34)
    ambient = simulate(get_template(names[0]), 200)
    t = np.arange(len(ambient)) / 30
    freq = np.array(
        [
            [frequencies(series, t) for series in component.T]
            for component in (abs(ambient), np.angle(ambient))
        ]
    )
    bundle = {"freq": freq}
    for family, sites in network_signatures(data).items():
        responses = []
        for site in sites:
            spec = get_template(names[family])
            event = spec["physical_events"][0]
            if family == 2:
                a, b = site.removeprefix("LINE").split("-")
                event["target_line"] = f"BUS{a}-BUS{b}"
            else:
                event["target_bus"] = site
            z = (simulate(spec, 34) / quiet)[120:1020]
            responses.append(np.stack([abs(z) - 1, np.angle(z)], axis=0))
        # Separate a common waveform from each sensor's relative response.
        response = np.array(responses)
        wave, weight = [], []
        for plane in response.transpose(1, 0, 2, 3):
            residual = plane.copy()
            hs, coeff = [], []
            for _ in range(2):
                if np.max(abs(residual)) < 1e-8:
                    hs.append(np.zeros(plane.shape[1]))
                    coeff.append(np.zeros((plane.shape[0], plane.shape[2])))
                    continue
                index = np.unravel_index(np.argmax(abs(residual)), residual.shape)
                h = residual[index[0], :, index[2]].copy()
                h /= np.max(abs(h))
                a = np.einsum("stb,t->sb", residual, h) / np.dot(h, h)
                residual -= a[:, None, :] * h[None, :, None]
                hs.append(h)
                coeff.append(a)
            assert np.max(abs(residual)) < 1e-8, family
            wave.append(hs)
            weight.append(coeff)
        bundle[f"wave{family}"] = wave
        bundle[f"weight{family}"] = weight
        bundle[f"sites{family}"] = list(sites)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "bank.npz", **bundle)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "data", "out"):
        p.add_argument(name, type=Path)
    a = p.parse_args()
    build(a.archive.resolve(), a.data, a.out)
