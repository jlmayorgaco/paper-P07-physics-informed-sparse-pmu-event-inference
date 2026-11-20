"""A causal test of whether a graph proposal has the signature of a new intervention."""
from collections import deque

import numpy as np

from estimator import EpisodeDecision, mechanical_prediction, physics_arrays, terminal_prediction
from physical import measurements
from study import HERE


WAIT = 6
HORIZON = 24
LOOKBACK = 24
PRE = 18


class Signatures:
    def __init__(self):
        # Rectangular coordinates retain the complex-current equivalence at zero amplitude.
        with np.load(HERE / "model.npz", allow_pickle=False) as archive:
            model = dict(archive)
        physics = physics_arrays(model)
        self.scale = model["scale"]
        self.code = model["code"]
        self.site = model["site"]
        self.rows = np.zeros((len(self.code), HORIZON, len(self.scale)))
        for group in range(1, len(self.code)):
            modes = np.flatnonzero(model["group"] == group)
            mode = modes[len(modes) // 2]
            state = np.zeros(30)
            for k in range(HORIZON):
                state = mechanical_prediction(mode, state, model["a"], model["b"], physics)
                self.rows[group, k] = terminal_prediction(mode, state, physics)
        self.energy = np.cumsum(np.sum(self.rows**2, axis=2), axis=1)
        self.index = {(int(c), str(s)): j for j, (c, s) in enumerate(zip(self.code, self.site))}

    def features(self, window, detected, group):
        """The window ends at the actual confirmation tick. detected is local to this window."""
        # Forecast smooth continuation from the pre-onset phasors. Each candidate onset
        # uses identical reports for continuation, a new step, and a signed return step.
        best = np.full(8, -np.inf)
        for onset in range(max(PRE, detected - LOOKBACK), min(detected + 2, len(window) - 3) + 1, 2):
            before = window[onset - PRE:onset]
            length = min(HORIZON, len(window) - onset)
            t = np.arange(PRE, dtype=float) - (PRE-1)/2
            slope = (t @ before) / (t @ t)
            residual = (window[onset:onset+length] - before.mean(axis=0)
                        - (np.arange(length) + (PRE+1)/2)[:, None] * slope)
            norm = np.sum(residual**2)
            dot = np.einsum("gtc,tc->g", self.rows[:, :length], residual)
            energy = self.energy[:, length - 1]
            # Profile a bounded positive strength. A reverse step approximates clearing
            # in the local model. Both signs are assessed in the same observation space.
            def improvement(alignment):
                strength = np.clip(alignment / np.maximum(energy, 1e-12), .5, 1.5)
                return 2 * strength * alignment - strength**2 * energy
            forward, reverse = improvement(dot), improvement(-dot)
            restore = max(0., reverse[1:].max())
            candidate = forward[group]
            any_event = forward[1:].max()
            values = np.array([candidate, any_event, candidate-restore, any_event-restore])
            # Size and fractional fit discriminate a large but mismatched switching transient.
            signed = np.sign(values) * np.log1p(abs(values) / length)
            fraction = np.clip(values / max(norm, 1.), -1., 1.)
            best = np.maximum(best, np.r_[signed, fraction])
        if not np.isfinite(best).all():
            raise ValueError("Insufficient pre-onset or post-onset PMU history")
        pre = window[max(0, detected - PRE):detected]
        pre_rms = np.sqrt(np.mean(pre**2, axis=0))
        pre_change = np.sqrt(np.mean(np.diff(pre, axis=0)**2, axis=0))
        # The baseline is the quiet prefix. Expose disturbance and slope separately
        # in voltage, terminal real current and terminal quadrature current.
        context = [np.log1p(np.max(v[indices])) for v in (pre_rms, pre_change)
                   for indices in (slice(0, 16), slice(16, 23), slice(23, 31))]
        family = self.code[group] == np.arange(1, 5)
        return np.r_[best, context, family]


class Confirmation:
    """Return diagnosed candidate features at their real publication times."""
    def __init__(self, signatures, graph, proposal):
        self.signatures = signatures
        self.decision = EpisodeDecision(graph, proposal, .95)
        self.frames = deque(maxlen=128)
        self.center = None
        self.pending = []
        self.tick = -1

    def step(self, report, graph_score):
        self.tick += 1
        k = self.tick
        coordinate = measurements(report) / self.signatures.scale
        self.frames.append(coordinate)
        if k == 29:
            self.center = np.mean(self.frames, axis=0)
        for action in self.decision.step(k, graph_score):
            if action["published"] is not None:
                # A stale proposal cannot be retrospectively backdated.
                if k - action["detected"] <= 45:
                    self.pending.append((max(k, action["detected"] + WAIT), action))
        updates = []
        while self.pending and self.pending[0][0] <= k:
            _, action = self.pending.pop(0)
            history = np.asarray(self.frames) - self.center
            detected = action["detected"] - (k + 1 - len(history))
            group = self.signatures.index[(action["code"], action["source"])]
            x = self.signatures.features(history, detected, group)
            updates.append((dict(detected=k, published=k, code=action["code"], source=action["source"]), x))
        return updates


class ConfirmedMonitor:
    """Online graph observer with the frozen shared episode-confirmation model."""
    def __init__(self):
        from monitor import PhysicalMonitor
        from episode_trial import verify
        self.config = verify()
        self.graph = PhysicalMonitor().filter
        self.confirm = Confirmation(Signatures(), self.graph.model, self.config["proposal"])

    def step(self, report):
        rows = self.confirm.step(report, self.graph.step(report))
        return [action for action, features in rows
                if log_odds(features, self.config) >= self.config["cut"]]


def log_odds(features, config):
    z = (features - config["center"]) / config["scale"]
    return float(z @ config["coef"] + config["intercept"])
