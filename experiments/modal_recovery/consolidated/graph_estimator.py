"""Frozen MET_BAYES_GRAFO_ADAPTATIVO estimator for successive P2 load/line events."""
from dataclasses import dataclass
from robust import RESULT, phase_data, study, joblib
from adaptive import is_quiet
from odds import weak_decision
from benchmark import call
import numpy as np


@dataclass
class GraphEstimator:
    nominal: tuple
    invariant: tuple
    conditional: tuple
    correction: object
    quality: list
    thresholds: tuple

    @classmethod
    def load(cls):
        """Verify the archives required by this estimator and load only its weights."""
        freeze=study.read(RESULT/"freeze.json")
        selected=freeze["winner"]
        if selected["name"]!="odds":
            raise ValueError("This entry point requires the published adaptive weights")
        angular=phase_data.RESULT
        if study.digest(angular/"freeze.json")!=freeze["upstream"]:
            raise ValueError("Angular component manifest mismatch")
        upstream=study.read(angular/"freeze.json")

        def checked(folder,name,hashes):
            path=folder/(name+".joblib")
            if study.digest(path)!=hashes[path.name]:
                raise ValueError(f"Weight checksum mismatch for {path}")
            return joblib.load(path)

        nominal=tuple(checked(angular,n,upstream["weights"]) for n in ("background","detector","source"))
        local,joint,correction=(checked(RESULT,n,freeze["weights"]) for n in ("local","history_joint","odds"))
        return cls(nominal,local,joint,correction,selected["quality"],
                   (upstream["threshold"],selected["strong_tau"],selected["tau"]))

    def predict(self,measurements,clearance):
        """Return absolute first alarm report and the family/site available by the last report.

        Supply arrays (reports, eight PMUs) under voltage_magnitude in V phase-neutral,
        current_magnitude in A, voltage_angle and current_angle in degrees. PMU order is
        2, 5, 6, 10, 19, 22, 29, 39. Supply the first restoration report and the quiet
        opening second. The caller may pass each longer prefix as reports arrive.
        """
        y=phase_data.channels(measurements)
        if y.ndim!=2 or y.shape[1]!=32 or not np.isfinite(y).all():
            raise ValueError("Expected 32 finite phasor channels in eight-PMU order")
        c=int(clearance)
        if c!=clearance or c<30:
            raise ValueError("Invalid first restoration report index")
        if len(y)<c+60:
            return dict(alarm=None,label=None)
        nominal,local,weak=self.thresholds
        if is_quiet(y,self.quality):
            bg,gate,source=self.nominal
            return call(bg.residual(y,c),c,gate,source,nominal)
        bg,gate,source=self.invariant
        ordinary=call(bg.residual(y,c),c,gate,source,local)
        return weak_decision(y,c,self.conditional,self.correction,weak,ordinary)
