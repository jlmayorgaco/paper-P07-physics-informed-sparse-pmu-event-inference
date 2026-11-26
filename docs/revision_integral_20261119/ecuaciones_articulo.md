# Main article, equations 1 through 17


### Equations 1–2 — switched DAE and switch continuity

- **(1), `eq:narrative-dae`:** The DAE is a model statement, not a closed specification. Its use depends on the stated local nonsingularity and angle-reference assumptions; the excerpt does not specify what happens if the algebraic solution ceases to be locally unique.
- **(2), `eq:narrative-switch`:** Continuity of \(x\) and solving the post-switch algebraic constraint are consistent with the accompanying text. The equation does not itself specify the admissible switch timing, the convention for \(u(s^+)\), or how a report exactly at the switch is assigned. The prose supplies the post-switch reporting convention.

### Equations 3–4 — PMU set and measurement model

- **(3), `eq:narrative-pmus`:** The set has eight buses, as stated. The excerpt flags unresolved current-terminal conventions for some measurements; those conventions affect the selected phasors and therefore the implementation of \(H_q\) and \(G_M\).
- **(4), `eq:narrative-measurement`:** The filter state is updated using the current \(\zeta_k\), then the report is formed from \(\eta_k\) and \(\zeta_k\). This is causal if that is the intended ordering. The extract does not specify startup values or whether the instrument noise is independent across reports. The 47 report coordinates are stated in prose but not enumerated here.

### Equations 5–7 — recovery response, DAE reduction, and predictor

- **(5), `eq:recovery-response`:** This is a first-order state-to-output approximation after restoration. It assumes the two trajectories share the intact dynamics and that the output difference is captured by \(C_0\Phi_0\delta x(\kappa)\). It does not include a direct input difference; the prose’s “same kind of initial condition” assertion is needed for the restored-load case. The excerpt does not define whether \(C_0\) is constant or time-varying.
- **(6), `eq:narrative-reduction`:** The Schur-complement signs are correct for eliminating \(\delta z=-g_z^{-1}(g_x\delta x+g_u\delta u)\). Implementation requires a nonsingular, consistently gauged \(g_z\), as stated. The displayed derivatives must all be evaluated at the same operating point and topology.
- **(7), `eq:implemented-predictor`:** The affine report and state equations are internally consistent as a one-report model. The excerpt does not show the construction of \(T,J,g,u,j,v\), the covariance of \(w_k\), or how “including any switch within it” is encoded. Those are implementation details needed to reproduce the predictor.

### Equations 8–11 — innovation, severity, evidence, and state correction

- **(8), `eq:innovation`:** \(S=JP_\rho J^\top+R\) and \(K=TP_\rho J^\top S^{-1}\) are consistent with scoring the current report and then updating the next state, provided the report and transition noises follow the assumed timing and covariance model. The excerpt requires \(S\) to be invertible; it does not state this separately here.
- **(9), `eq:severity-update`:** Completing the square gives the displayed Gaussian posterior parameters. This requires \(v_a>0\) and \(S\succ0\). The symbols \(v_a\) and \(v\) elsewhere should not be conflated.
- **(10), `eq:narrative-evidence`:** The Gaussian predictive factor and truncation-normalizer ratio are the correct integrated evidence for the stated truncated Gaussian prior. The interval \(I\) and its endpoints must be the same in the numerator and denominator. The excerpt does not specify numerical handling when either normalizer is extremely small.
- **(11), `eq:implemented-conditional-correction`:** The signs in \(d_h^+=Td_h+u-Ks\) follow from applying \(K(e-sa)\). The correction gives a conditional mean trajectory; it is not by itself a covariance update. The text’s later use of a shared \(P_\rho\) is important to interpreting it.

### Equations 12–13 — history weights and cause masses

- **(12), `eq:history-bayes-update`:** This is a proportional weight update. A reproducible implementation needs the transition weights \(p(h\mid h')\), the normalization rule, and a clear account of how pruning changes the retained mass. The excerpt says the weights are renormalized after pruning.
- **(13), `eq:active-cause-masses`:** The definitions correctly distinguish active mass \(M_{c,k}\) from total source mass \(\Gamma_{c,k}\). They rely on normalized history weights and an unambiguous active/restored status for each history.

### Equations 14–17 — recovery covariance, score, and source separation

- **(14), `eq:recovery-report-variance`:** The total-covariance expression is correct if \(\omega_h\) sum to one, all report means use the same \(J\), and \(V_{a,h}\) is the conditional severity variance. It omits any variation in \(J\), \(S\), or the network hypothesis across components; the prose limits the claim to the shared report operator.
- **(15), `eq:recovery-log-loss`:** The expected Gaussian negative log-density has the displayed trace and mean-error terms, up to a constant independent of \((z,U)\). The scoring distribution must have finite covariance \(V\), and \(U\succ0\).
- **(16), `eq:recovery-log-projection`:** The eigenvalue expression is nonnegative for positive eigenvalues. It requires \(V\succ0\) as well as \(U\succ0\); the preceding text explicitly states \(S\succ0\), which would ensure this for the defined \(V\).
- **(17), `eq:signature-information`:** This is a known-onset, best-fitting-rival residual score. The minimization interval \(I_j\) and the rival’s \(s_{j,r},S_{j,r}\) must correspond to the same candidate model across reports. It is not an integrated severity likelihood. The line/no-intervention special case is described in prose.

