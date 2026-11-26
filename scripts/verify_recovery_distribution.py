"""Finite enumerations for predictive sufficiency and mixture moments."""
import json
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import math


def normal_pdf(x, mean, variance):
    return math.exp(-0.5*(x-mean)**2/variance) / math.sqrt(2*math.pi*variance)


def main():
    out = Path(__file__).resolve().parents[1] / "generated" / "recovery_distribution_checks.json"
    # A failed rerun must not leave an older PASS artifact looking current.
    out.unlink(missing_ok=True)
    # Explicit two-step finite-state model. Each row is (history, state, mass).
    # Apply a history transition and state transition, condition on Y=1, then
    # predict a binary next report. Compare sum_h sum_s with the marginalized
    # state recursion, using the same enumerated transition and likelihoods.
    initial = [(0, -1, .2), (0, 1, .2), (1, 0, .3), (1, 2, .3)]
    transition = {(0, 0): .8, (0, 1): .2, (1, 0): .3, (1, 1): .7}
    atoms = []
    for h, s, mass in initial:
        for h2 in (0, 1):
            s2 = .5*s + h2
            l_y1 = .2 + .15*(s2+1)
            atoms.append((h2, s2, mass*transition[h, h2], l_y1))
    evidence = sum(m*l for _, _, m, l in atoms)
    joint_posterior = [(h, s, m*l/evidence) for h, s, m, l in atoms]
    # Next-report probability depends only on current state, so the complete
    # state marginal is enough for prediction, irrespective of history labels.
    p_y2_given_state = lambda s: min(.95, max(.05, .5 + .1*s))
    by_state = defaultdict(float)
    for _, s, p in joint_posterior:
        by_state[s] += p
    predict_joint = sum(p*p_y2_given_state(s) for _, s, p in joint_posterior)
    predict_marginal = sum(p*p_y2_given_state(s) for s, p in by_state.items())
    assert abs(predict_joint-predict_marginal) < 1e-15

    # Same state posterior, different coupling to cause labels: prediction
    # remains the same, historical cause posterior changes.
    coupling_a = [(0, -1, .5), (1, 1, .5)]
    coupling_b = [(1, -1, .5), (0, 1, .5)]
    state_marginal = lambda rows: sorted((s, sum(p for _, ss, p in rows if ss == s))
                                         for s in {-1, 1})
    cause0_given_minus1 = lambda rows: (sum(p for h, s, p in rows if h == 0 and s == -1)
                                        / sum(p for _, s, p in rows if s == -1))
    assert state_marginal(coupling_a) == state_marginal(coupling_b)
    assert cause0_given_minus1(coupling_a) != cause0_given_minus1(coupling_b)

    # Enumerate severity and residual-noise atoms to independently verify
    # within-component and between-history moment identities. Conditional
    # severity and noise are symmetric two-point distributions with the stated
    # variances, so weighted finite sums yield the exact moments.
    weights, means, ps, slopes, amus, avs = [0.25, 0.75], [0., 2.], [1., .5], [2., -1.], [1., 3.], [.5, .25]
    rows = []
    for j, w in enumerate(weights):
        for sign_a in (-1, 1):
            a = amus[j] + sign_a*math.sqrt(avs[j])
            for sign_e in (-1, 1):
                e = sign_e*math.sqrt(ps[j])
                z = means[j] + slopes[j]*(a-amus[j]) + e
                rows.append((w*.25, z, a))
    total = sum(w for w, _, _ in rows)
    zbar = sum(w*z for w, z, _ in rows)/total
    abar = sum(w*a for w, _, a in rows)/total
    zvar_enum = sum(w*(z-zbar)**2 for w, z, _ in rows)/total
    avar_enum = sum(w*(a-abar)**2 for w, _, a in rows)/total
    cov_enum = sum(w*(z-zbar)*(a-abar) for w, z, a in rows)/total
    zvar_formula = sum(w*(p+d*d*v+(m-zbar)**2) for w, m, p, d, v in zip(weights, means, ps, slopes, avs))
    abar_formula = sum(w*a for w, a in zip(weights, amus))
    avar_formula = sum(w*(v+(a-abar_formula)**2) for w, a, v in zip(weights, amus, avs))
    cov_formula = sum(w*(d*v+(m-zbar)*(a-abar_formula))
                      for w, m, d, v, a in zip(weights, means, slopes, avs, amus))
    assert abs(zvar_enum-zvar_formula) < 1e-12
    assert abs(avar_enum-avar_formula) < 1e-12
    assert abs(cov_enum-cov_formula) < 1e-12

    # A moment-matched Gaussian generally differs from the finite mixture tails.
    mix_w, mix_m, mix_v = [.3, .7], [-2., 1.], [.4, .8]
    mix_mean = sum(w*m for w, m in zip(mix_w, mix_m))
    mix_var = sum(w*(v+(m-mix_mean)**2) for w, m, v in zip(mix_w, mix_m, mix_v))
    tail_x = 5.
    mixture_tail = sum(w*normal_pdf(tail_x, m, v) for w, m, v in zip(mix_w, mix_m, mix_v))
    gaussian_tail = normal_pdf(tail_x, mix_mean, mix_var)
    assert abs(mixture_tail-gaussian_tail) > 1e-5

    # Equal means with different state variances give different predictive
    # densities after additive observation noise.
    predictive_a = normal_pdf(1.5, 1., .2)
    predictive_b = normal_pdf(1.5, 1., 3.2)
    assert abs(predictive_a-predictive_b) > .1

    # Enumerate joint P(C,Y,Z), Z=g(Y). Conditioning on Z after Y does not
    # alter P(C|Y); fabricating an independent copy of the Y likelihood does.
    prior = {0: .5, 1: .5}
    p_y1 = {0: .2, 1: .8}
    joint = {(c, y, 1 if y == 1 else 0): prior[c]*(p_y1[c] if y else 1-p_y1[c])
             for c in (0, 1) for y in (0, 1)}
    observed_y, observed_z = 1, 1
    den_y = sum(p for (c, y, z), p in joint.items() if y == observed_y)
    post_y = {c: sum(p for (cc, y, z), p in joint.items()
                     if cc == c and y == observed_y)/den_y for c in (0, 1)}
    den_yz = sum(p for (c, y, z), p in joint.items()
                 if y == observed_y and z == observed_z)
    post_yz = {c: sum(p for (cc, y, z), p in joint.items()
                      if cc == c and y == observed_y and z == observed_z)/den_yz
               for c in (0, 1)}
    duplicated = {c: prior[c]*p_y1[c]**2/sum(prior[q]*p_y1[q]**2 for q in (0, 1))
                  for c in (0, 1)}
    assert post_y == post_yz and post_y[1] == .8
    assert abs(duplicated[1]-post_y[1]) > .1

    report = {
        "status": "PASS",
        "checks": ["enumerated_transition_filter_predictive_equals_state_marginal_recursion",
                   "same_state_marginal_can_have_different_historical_cause_posterior",
                   "enumerated_severity_noise_atoms_verify_mixture_variance_and_covariance",
                   "moment_matched_gaussian_can_change_mixture_tail_density",
                   "equal_means_can_produce_different_predictive_densities",
                   "enumerated_deterministic_statistic_preserves_cause_posterior",
                   "independent_duplicate_likelihood_changes_posterior"],
        "predictive_probability_next_report_one": predict_joint,
        "cause_zero_given_state_minus1": [cause0_given_minus1(coupling_a), cause0_given_minus1(coupling_b)],
        "enumerated_moments": {"state_mean": zbar, "state_variance": zvar_enum,
                               "severity_mean": abar, "severity_variance": avar_enum,
                               "state_severity_covariance": cov_enum},
        "deterministic_statistic_posterior": post_yz,
        "duplicate_likelihood_posterior": duplicated,
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "finite exact enumerations of toy models; no estimator or campaign validation"
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
