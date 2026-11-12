# Bounded rival-severity diagnostic

This successor asks whether the earlier current contribution survives fitting
the rival load magnitude. It uses the same frozen nominal operators and common
raw-report covariance from `../channel_information_20261112`, with known onset
and zero initial deviation. No observations or campaign results are read.

`design.json` was written before execution. True loads remain +0.10; candidate
load amplitudes can vary over [-0.20, 0.20], the implemented total prior support.
Line operators are discrete and never rescaled. The optimization uses the
exact clipped scalar least-squares solution and checks every load comparison
against a separate bounded scalar optimizer. All 18 sources and 17 distinct
rivals are included at 3, 15 and 30 reports. The null is not a source rival.

From the paper root, with NumPy and SciPy:

```
python experiments/channel_profile_20261112/run.py
```

The figure and macros additionally require Matplotlib and pandas:

```
python scripts/build_channel_profile_figure.py
```

These are deterministic profiled distances under a common covariance. The
diagnostic does not integrate a prior, run a detector, measure FAR, or quantify
the effect of uncertain recovery states. In particular, no extra state
covariance is appended to the reference innovation-induced covariance.
Directed profile distances need not be symmetric. Nearest rivals can change
both when selecting channels and when allowing amplitude adjustment.
