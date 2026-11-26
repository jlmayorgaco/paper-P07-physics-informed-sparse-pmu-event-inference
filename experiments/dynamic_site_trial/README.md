# Dynamic source separation on IEEE-39

The protocol was committed in ff24dfb and the estimator in 79c37ec before scoring. The independent plant here is independent of M9. The readout shares its nominal classical-machine equations with the data generator. Inertia and damping vary in the generated records. Network, operating point, pulse length and assumed noise level are fixed. The experiment contains 264 development trajectories and 138 reserved-site trajectories. Each physical site has six draws. All candidate sites have physics-derived templates. No site-specific labeled training data are used.

| Reserved family | Sources | Frozen rotor | Dynamic | Dynamic supplied onset and intensity | Magnitude only | Angle only |
|---|---:|---:|---:|---:|---:|---:|
| Mechanical generation | 4 | 0/24 | 22/24 | 17/24 | 20/24 | 22/24 |
| Load | 6 | 6/36 | 35/36 | 22/36 | 33/36 | 29/36 |
| Weak conductance pulse | 13 | 0/78 | 10/78 | 16/78 | 0/78 | 14/78 |

Records within each row are paired. The frozen-rotor mechanical generation response is zero by construction, so it abstains on tied assets. It is a physics ablation, not the prior nine-class hybrid. Supplied nuisance parameters do not imply an accuracy ceiling when templates have parameter mismatch. Development dynamic hits were 28/36, 69/72 and 26/156, respectively. The joint 95% gate failed. No nine-class experiment, new false-alarm estimate or update to the production hybrid followed. See the two score files for site-cluster bootstrap intervals for paired differences; especially for the four reserved generation sites the uncertainty is substantial.

## Exploratory resolution bound

For each of 39 nominal weak source trajectories at onset frame 7, stack the eight complex voltage channels as real log magnitudes and angles over 90 frames. The simulation assumes independent Gaussian errors with common SD 0.001 in each coordinate. A pair with whitened separation d has equal-prior optimal binary error Phi(-d/2). Pair the closest remaining sites greedily and allow an oracle to disclose the correct pair (or the unpaired site). This extra information gives an upper bound on multiclass optimal accuracy with uniform source priors. For the 1 MW nominal pulse, fixed operating point and these measurements, that bound is 0.734384. Pairs 11/12 and 16/24 give binary errors 0.4800 and 0.4645. The conditional bound does not apply to larger disturbances, different inputs, different noise or M9. This calculation was added after scoring; it is a model calculation, not a blind performance estimate.

## Reproduction and review

Set P07_SCIENCE_ARCHIVE to the SGSMA scientific archive containing experiments/PAPER_ALLEVENTS_V1/physics/network.py and its original network inputs. Set OPENBLAS_NUM_THREADS=1. From this directory run trial.py predict dev and trial.py predict blind before running trial.py score for each split, then run pair_resolution.py with Python. Prediction hashes detect changes; the experiment was executed by one operator without external label custody. Generator order was verified as ascending bus 30 through 39. The archived per-site predictions allow the counts to be recomputed.

Three GPT-6-Luna reviews covered available measurement sets, compatibility with the registered M9 protocol, and implementation threats to validity. The first two used externally accessible sources after their local read-only subprocesses failed. The implementation reviewer received the protocol and executable source directly. The primary operator verified the NAS source and executed the plant locally. A new physical channel study should first verify monitored branch identity, polarity and noise, then test if measured branch currents separate the weak pairs in development, before spending a new holdout.
