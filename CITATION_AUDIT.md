# Citation Audit Report

Generated: 2026-11-01T04:02:13.946145+00:00

**Overall verdict: WARN.** All 77 bibliography entries have live existence evidence. The active main article and supplement cite 28 keys in 38 source occurrences; 49 entries are uncited in this scope. Six metadata corrections and one contextual wording correction remain. No entry is classified REPLACE or REMOVE.

| Scope | KEEP | FIX | REPLACE | REMOVE |
|---|---:|---:|---:|---:|
| All 77 entries | 70 | 7 | 0 | 0 |
| Active 28 entries | 27 | 1 | 0 | 0 |

## Priority corrections

### FIX: chen2016quickest (active)

At sections/narrative_protocol.tex:33, single-line incorrectly narrows the description of the published method. The original includes single- and double-line outages; the manuscript adapter is the restricted component.

Recommended: Use: "The published physical comparator is Chen et al.'s persistent-line quickest-change detector ... Our declared F01 adapter restricts the catalog to single-line hypotheses ..."

Evidence: [author-hosted original paper](https://people.ece.ubc.ca/chen/papers/journal/07041234.pdf).

### FIX: zhang2025functional (uncited)

The DOI is real, but the entry mixes a different title formulation with an incorrect first-author initial.

Recommended: Set title to "Functional Observability, Structural Functional Observability, and Optimal Sensor Placement" and first author to "Y. Zhang" (Yuan Zhang). Retain 2025, 70(3):1592-1607 and DOI.

Evidence: [primary/institutional metadata corroboration](https://research-repository.uwa.edu.au/en/publications/functional-observability-structural-functional-observability-and-/).

### FIX: yuan2023gnn (uncited)

The second and third authors are reversed in the bibliography.

Recommended: Use "Y. Yuan and Z. Wang and Y. Wang" (Yuxuan Yuan; Zhaoyu Wang; Yanchao Wang).

Evidence: [primary/institutional metadata corroboration](https://wzy.ece.iastate.edu/CV/c201.pdf).

### FIX: azizi2021log (uncited)

The second author is Mohammad Rezaei Jegarluei. "M. R. Rezaei Jegarluei" duplicates the Rezaei initial when Rezaei is retained as part of the surname.

Recommended: Use "Rezaei Jegarluei, Mohammad" or the correctly abbreviated "M. Rezaei Jegarluei".

Evidence: [primary/institutional metadata corroboration](https://eprints.whiterose.ac.uk/id/eprint/169323/).

### FIX: azizi2023line (uncited)

The second-author name has the same duplicated Rezaei initial. The publisher/author early-access record retrieved in this audit is incomplete for final volume/pages, so do not replace the existing 2023 final citation with its stale 2022, 1-11 values.

Recommended: Use "Rezaei Jegarluei, Mohammad"; confirm final issue/page fields against the final IEEE PDF before changing them.

Evidence: [primary/institutional metadata corroboration](https://eprints.whiterose.ac.uk/id/eprint/190192/).

### FIX: moshtagh2025topology (uncited)

Final journal volume, issue and pages are now available but absent.

Recommended: Add volume={40}, number={6}, pages={4547--4560}; retain year={2025}.

Evidence: [primary/institutional metadata corroboration](https://asu.elsevierpure.com/en/publications/topology-aware-graph-neural-network-based-state-estimation-for-pm/).

### FIX: hu2026openset (uncited)

The early-access note is stale; a final September 2026 issue record is available.

Recommended: Add volume={22}, number={9}, pages={8104--8115}; remove note={Early access}.

Evidence: [primary/institutional metadata corroboration](https://ieeexplore.ieee.org/document/11527391/).

## Scope and execution

Inputs were references.bib and the existing recursive TeX graph rooted at main.tex and supplement.tex. Legacy/historical-note files and previous reviews were excluded. No datasets, RAW files or author contact ledgers were opened. The extracted contexts include file, line and complete surrounding sentences in `.aris/citation-audit/contexts.txt`. The exact input hashes are in the JSON ledger; all were rechecked at completion.

**Tooling deviation:** the required `mcp__codex__codex` tool and gpt-5.4 reviewer were unavailable. This run used a fresh collaboration subagent and live primary web/DOI/arXiv/publisher lookups. The exact inherited model/effort and cross-model independence are not certified. No claim is made that the original cross-model workflow ran. Required shared-reference documents were not found by a local filename search; the embedded SKILL.md schema was used.

Each entry has an isolated trace and registry response. The registry batch was retried after rate limits; all 72 DOI records were eventually retrieved. Three arXiv records, the publisher ISBN record for Kay, and the official Codex page cover the five entries without a DOI. Context judgments use the source itself or its publisher/author abstract; source scope was not inferred from titles alone.

The final Chen wording correction uses FIX/CONTEXT because the source remains appropriate: only the manuscript's scope attribution needs repair. WARN therefore records a contextual qualification as well as metadata drift.

## Uncertainty and resolved apparent discrepancies

- Azizi 2023: the accessible primary metadata remains an early-access record. The existing final 2023 volume/pages should not be overwritten with the stale registry values; final primary issue verification remains open.
- Warner 2023: the original paper text supports the moving onset window, V/I trajectories, before-clearing target and load-change false-alarm test. Primary-host PDF access failed; the full-text mirror was checked, without certifying exact byte identity with v1.
- Cover 2006: the publisher confirms the cited second print edition/year despite conflicting electronic-registry year/edition fields.
- Wang 2024: the publisher confirms 121(8):2275–2291; registry volume/issue zero and 1–10 pages are obsolete placeholders.
- Rotnitzky 2000: the author publication list confirms pages 243–284; the registry records only the first page.
- Codex citations identify the disclosed tool. The product page cannot authenticate the authors' actual usage or historical access date.

## Per-entry ledger

| Key | Active | Existence | Metadata | Context | Verdict |
|---|---|---|---|---|---|
| [albustami2026dae](.aris/traces/citation-audit/20261101_run01/albustami2026dae.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [anguluri2023group](.aris/traces/citation-audit/20261101_run01/anguluri2023group.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [blom1988imm](.aris/traces/citation-audit/20261101_run01/blom1988imm.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [boers2005m3h](.aris/traces/citation-audit/20261101_run01/boers2005m3h.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [chen2016quickest](.aris/traces/citation-audit/20261101_run01/chen2016quickest.md) | yes | YES | CORRECT | WEAK | FIX |
| [conte2023fault](.aris/traces/citation-audit/20261101_run01/conte2023fault.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [ensaf2023kernel](.aris/traces/citation-audit/20261101_run01/ensaf2023kernel.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [eriksson2013diagnosability](.aris/traces/citation-audit/20261101_run01/eriksson2013diagnosability.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [fernando2010functional](.aris/traces/citation-audit/20261101_run01/fernando2010functional.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [gillijns2007input](.aris/traces/citation-audit/20261101_run01/gillijns2007input.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [jamei2020limits](.aris/traces/citation-audit/20261101_run01/jamei2020limits.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [katanic2024recursive](.aris/traces/citation-audit/20261101_run01/katanic2024recursive.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [li2024knowledge](.aris/traces/citation-audit/20261101_run01/li2024knowledge.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [montanari2022functional](.aris/traces/citation-audit/20261101_run01/montanari2022functional.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [nagi2022trajectory](.aris/traces/citation-audit/20261101_run01/nagi2022trajectory.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [nugroho2022dae](.aris/traces/citation-audit/20261101_run01/nugroho2022dae.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [openaiCodex2026](.aris/traces/citation-audit/20261101_run01/openaiCodex2026.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [pandey2020realtime](.aris/traces/citation-audit/20261101_run01/pandey2020realtime.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [rovatsos2017outage](.aris/traces/citation-audit/20261101_run01/rovatsos2017outage.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [sarkka2013bayesian](.aris/traces/citation-audit/20261101_run01/sarkka2013bayesian.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [scharf1994matched](.aris/traces/citation-audit/20261101_run01/scharf1994matched.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [tartakovsky2023gp](.aris/traces/citation-audit/20261101_run01/tartakovsky2023gp.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [tate2008outage](.aris/traces/citation-audit/20261101_run01/tate2008outage.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [warner2023highfidelity](.aris/traces/citation-audit/20261101_run01/warner2023highfidelity.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [warner2024matrix](.aris/traces/citation-audit/20261101_run01/warner2024matrix.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [yildiz2024few](.aris/traces/citation-audit/20261101_run01/yildiz2024few.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [yildiz2025sparse](.aris/traces/citation-audit/20261101_run01/yildiz2025sparse.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [zhao2014outages](.aris/traces/citation-audit/20261101_run01/zhao2014outages.md) | yes | YES | CORRECT | SUPPORTS | KEEP |
| [Mayorga2026FrequencyBenchmark](.aris/traces/citation-audit/20261101_run01/Mayorga2026FrequencyBenchmark.md) | no | YES | CORRECT | N/A | KEEP |
| [abdelhai2021transfer](.aris/traces/citation-audit/20261101_run01/abdelhai2021transfer.md) | no | YES | CORRECT | N/A | KEEP |
| [azizi2021log](.aris/traces/citation-audit/20261101_run01/azizi2021log.md) | no | YES | FIX | N/A | FIX |
| [azizi2023line](.aris/traces/citation-audit/20261101_run01/azizi2023line.md) | no | YES | FIX | N/A | FIX |
| [bell1994ieks](.aris/traces/citation-audit/20261101_run01/bell1994ieks.md) | no | YES | CORRECT | N/A | KEEP |
| [biswas2025quality](.aris/traces/citation-audit/20261101_run01/biswas2025quality.md) | no | YES | CORRECT | N/A | KEEP |
| [chatterjee2020robust](.aris/traces/citation-audit/20261101_run01/chatterjee2020robust.md) | no | YES | CORRECT | N/A | KEEP |
| [cheng2022bigan](.aris/traces/citation-audit/20261101_run01/cheng2022bigan.md) | no | YES | CORRECT | N/A | KEEP |
| [cover2006elements](.aris/traces/citation-audit/20261101_run01/cover2006elements.md) | no | YES | CORRECT | N/A | KEEP |
| [cui2021hybrid](.aris/traces/citation-audit/20261101_run01/cui2021hybrid.md) | no | YES | CORRECT | N/A | KEEP |
| [foggo2024pmubage](.aris/traces/citation-audit/20261101_run01/foggo2024pmubage.md) | no | YES | CORRECT | N/A | KEEP |
| [hou1998input](.aris/traces/citation-audit/20261101_run01/hou1998input.md) | no | YES | CORRECT | N/A | KEEP |
| [hu2026openset](.aris/traces/citation-audit/20261101_run01/hu2026openset.md) | no | YES | FIX | N/A | FIX |
| [kalman1960](.aris/traces/citation-audit/20261101_run01/kalman1960.md) | no | YES | CORRECT | N/A | KEEP |
| [kay1993estimation](.aris/traces/citation-audit/20261101_run01/kay1993estimation.md) | no | YES | CORRECT | N/A | KEEP |
| [kummerow2022siamese](.aris/traces/citation-audit/20261101_run01/kummerow2022siamese.md) | no | YES | CORRECT | N/A | KEEP |
| [kummerow2023nuisance](.aris/traces/citation-audit/20261101_run01/kummerow2023nuisance.md) | no | YES | CORRECT | N/A | KEEP |
| [kummerow2023sigmoid](.aris/traces/citation-audit/20261101_run01/kummerow2023sigmoid.md) | no | YES | CORRECT | N/A | KEEP |
| [li2018subspace](.aris/traces/citation-audit/20261101_run01/li2018subspace.md) | no | YES | CORRECT | N/A | KEEP |
| [li2019cnn](.aris/traces/citation-audit/20261101_run01/li2019cnn.md) | no | YES | CORRECT | N/A | KEEP |
| [li2022transfer](.aris/traces/citation-audit/20261101_run01/li2022transfer.md) | no | YES | CORRECT | N/A | KEEP |
| [li2023eventtriggered](.aris/traces/citation-audit/20261101_run01/li2023eventtriggered.md) | no | YES | CORRECT | N/A | KEEP |
| [moshtagh2025topology](.aris/traces/citation-audit/20261101_run01/moshtagh2025topology.md) | no | YES | FIX | N/A | FIX |
| [ngo2024pignn](.aris/traces/citation-audit/20261101_run01/ngo2024pignn.md) | no | YES | CORRECT | N/A | KEEP |
| [nguyen2021unknown](.aris/traces/citation-audit/20261101_run01/nguyen2021unknown.md) | no | YES | CORRECT | N/A | KEEP |
| [nyberg2002detectability](.aris/traces/citation-audit/20261101_run01/nyberg2002detectability.md) | no | YES | CORRECT | N/A | KEEP |
| [pasqualetti2013attack](.aris/traces/citation-audit/20261101_run01/pasqualetti2013attack.md) | no | YES | CORRECT | N/A | KEEP |
| [phadke2008synchronized](.aris/traces/citation-audit/20261101_run01/phadke2008synchronized.md) | no | YES | CORRECT | N/A | KEEP |
| [plietzsch2022powerdynamics](.aris/traces/citation-audit/20261101_run01/plietzsch2022powerdynamics.md) | no | YES | CORRECT | N/A | KEEP |
| [pomarico2026shred](.aris/traces/citation-audit/20261101_run01/pomarico2026shred.md) | no | YES | CORRECT | N/A | KEEP |
| [qi2015placement](.aris/traces/citation-audit/20261101_run01/qi2015placement.md) | no | YES | CORRECT | N/A | KEEP |
| [qu2023joint](.aris/traces/citation-audit/20261101_run01/qu2023joint.md) | no | YES | CORRECT | N/A | KEEP |
| [rauch1965smoothing](.aris/traces/citation-audit/20261101_run01/rauch1965smoothing.md) | no | YES | CORRECT | N/A | KEEP |
| [rimkus2025gnn](.aris/traces/citation-audit/20261101_run01/rimkus2025gnn.md) | no | YES | CORRECT | N/A | KEEP |
| [rotnitzky2000singular](.aris/traces/citation-audit/20261101_run01/rotnitzky2000singular.md) | no | YES | CORRECT | N/A | KEEP |
| [sarkka2020linesearch](.aris/traces/citation-audit/20261101_run01/sarkka2020linesearch.md) | no | YES | CORRECT | N/A | KEEP |
| [showkatbakhsh2020secure](.aris/traces/citation-audit/20261101_run01/showkatbakhsh2020secure.md) | no | YES | CORRECT | N/A | KEEP |
| [stuart2010inverse](.aris/traces/citation-audit/20261101_run01/stuart2010inverse.md) | no | YES | CORRECT | N/A | KEEP |
| [sun2016observability](.aris/traces/citation-audit/20261101_run01/sun2016observability.md) | no | YES | CORRECT | N/A | KEEP |
| [sun2026secure](.aris/traces/citation-audit/20261101_run01/sun2026secure.md) | no | YES | CORRECT | N/A | KEEP |
| [tsybakov2009nonparametric](.aris/traces/citation-audit/20261101_run01/tsybakov2009nonparametric.md) | no | YES | CORRECT | N/A | KEEP |
| [wang2024group](.aris/traces/citation-audit/20261101_run01/wang2024group.md) | no | YES | CORRECT | N/A | KEEP |
| [yuan2021learning](.aris/traces/citation-audit/20261101_run01/yuan2021learning.md) | no | YES | CORRECT | N/A | KEEP |
| [yuan2023gnn](.aris/traces/citation-audit/20261101_run01/yuan2023gnn.md) | no | YES | FIX | N/A | FIX |
| [yue2024graph](.aris/traces/citation-audit/20261101_run01/yue2024graph.md) | no | YES | CORRECT | N/A | KEEP |
| [zhai2025partial](.aris/traces/citation-audit/20261101_run01/zhai2025partial.md) | no | YES | CORRECT | N/A | KEEP |
| [zhang2025functional](.aris/traces/citation-audit/20261101_run01/zhang2025functional.md) | no | YES | FIX | N/A | FIX |
| [zhao2018gmukf](.aris/traces/citation-audit/20261101_run01/zhao2018gmukf.md) | no | YES | CORRECT | N/A | KEEP |
| [zhao2019dse](.aris/traces/citation-audit/20261101_run01/zhao2019dse.md) | no | YES | CORRECT | N/A | KEEP |

## Per-use assessment

### albustami2026dae

- `sections/article_related.tex:58` — **SUPPORTS**. The abstract explicitly treats joint Bayesian estimation of generator inertia/damping and branch resistance/reactance in a power-system DAE.

Source: [arXiv abstract and author/version record](https://arxiv.org/abs/2604.15686).

### anguluri2023group

- `sections/article_related.tex:19` — **SUPPORTS**. The abstract explicitly recovers sparse input locations, forcing signals and an unknown initial state with group LASSO for linear dynamics. The journal author order differs from the preprint: the bibliography correctly follows the journal record.

Source: [author preprint abstract; publisher-deposited metadata](https://arxiv.org/abs/2201.07907).

### blom1988imm

- `sections/article_related.tex:37` — **SUPPORTS**. The paper develops approximate Bayesian filtering and hypothesis merging for Markovian switching linear systems, supporting the stated multiple-model precedent.

Source: [author institution abstract](https://research.tudelft.nl/en/publications/the-interacting-multiple-model-algorithm-for-systems-with-markovi/).

### boers2005m3h

- `sections/article_related.tex:39` — **SUPPORTS**. The source explicitly combines pruning and merging, permits variable merging depth, and adapts computational load through a changing hypothesis count.

Source: [publisher abstract and method/conclusion excerpts](https://www.sciencedirect.com/science/article/pii/S0005109804003243).

### chen2016quickest

- `sections/article_intro.tex:26` — **SUPPORTS**. The source uses stochastic injection changes, phasor-angle increments, network hypotheses and sequential quickest-change tests. Its abstract explicitly includes single- and double-line outages; the manuscript must identify single-line restriction as belonging to its adapter.
- `sections/article_related.tex:17` — **SUPPORTS**. The source uses stochastic injection changes, phasor-angle increments, network hypotheses and sequential quickest-change tests. Its abstract explicitly includes single- and double-line outages; the manuscript must identify single-line restriction as belonging to its adapter.
- `sections/narrative_protocol.tex:33` — **WEAK**. At sections/narrative_protocol.tex:33, single-line incorrectly narrows the description of the published method. The original includes single- and double-line outages; the manuscript adapter is the restricted component.

Source: [author-hosted original paper](https://people.ece.ubc.ca/chen/papers/journal/07041234.pdf).

### conte2023fault

- `sections/article_related.tex:22` — **SUPPORTS**. Reduced PMU placement produces fault-localization clusters and the placement algorithm controls localization resolution; this supports source distinguishability dependence on sensor placement.

Source: [publisher abstract and author-institution full-paper excerpts](https://ieeexplore.ieee.org/document/9751367/).

### ensaf2023kernel

- `sections/article_related.tex:57` — **SUPPORTS**. The abstract uses stochastic swing equations and Gaussian/kernel regression for observed and unobserved state estimation and forecasting under sparse measurements; no source-localization guarantee is attributed to it.

Source: [arXiv abstract and author/version record](https://arxiv.org/abs/2309.10200).

### eriksson2013diagnosability

- `sections/article_related.tex:12` — **SUPPORTS**. The source quantifies fault-mode distinguishability in stochastic descriptor models through KL divergence and links it to fault-to-noise ratio. It supports the qualitative source-separation argument, not a universal calibrated error formula.
- `sections/article_information.tex:33` — **SUPPORTS**. The source quantifies fault-mode distinguishability in stochastic descriptor models through KL divergence and links it to fault-to-noise ratio. It supports the qualitative source-separation argument, not a universal calibrated error formula.

Source: [publisher abstract and method excerpts](https://www.sciencedirect.com/science/article/pii/S0005109813001349).

### fernando2010functional

- `sections/article_related.tex:9` — **SUPPORTS**. The source defines functional observability/detectability and functional observers, supporting recovery of selected functions without demanding full-state observability.

Source: [publisher abstract and original-paper excerpt](https://ieeexplore.ieee.org/document/5409605/).

### gillijns2007input

- `sections/article_related.tex:7` — **SUPPORTS**. The paper jointly estimates unknown input and state in linear discrete-time systems. It is a general estimation foundation; the accompanying Nugroho and Katanic references establish the electrical-network application in the grouped sentence.

Source: [author-hosted original paper abstract](https://ftp.esat.kuleuven.be/pub/pub/stadius/gillijns/reports/TR-05-228-a.pdf).

### jamei2020limits

- `sections/article_related.tex:22` — **SUPPORTS**. The source analyzes KL separation of fault hypotheses with insufficient PMUs and derives placement for localization resolution, directly supporting the placement/discrimination claim.

Source: [author-hosted original paper](https://www.cs.ucdavis.edu/~peisert/research/2020-JSAC-PMULocalization).

### katanic2024recursive

- `sections/article_intro.tex:24` — **SUPPORTS**. The source recursively estimates algebraic/dynamic states using incomplete nonlinear DAE models and phasor data; both manuscript uses match that scope.
- `sections/article_related.tex:7` — **SUPPORTS**. The source recursively estimates algebraic/dynamic states using incomplete nonlinear DAE models and phasor data; both manuscript uses match that scope.

Source: [publisher full text and abstract](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/gtd2.13308).

### li2024knowledge

- `sections/article_related.tex:50` — **SUPPORTS**. The source combines a spatiotemporal graph network with type/topology constraints to localize disturbances using sparse PMU measurements.

Source: [publisher abstract/full-text search excerpt and registry abstract](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/gtd2.13331).

### montanari2022functional

- `sections/article_related.tex:9` — **SUPPORTS**. The source generalizes functional observability to nonlinear systems and reconstructs chosen state functions, supporting the statement about requested state quantities.

Source: [author institution published-version abstract](https://www.repository.cam.ac.uk/items/45d8001b-afb7-422a-9042-3e486b823491).

### nagi2022trajectory

- `sections/article_related.tex:62` — **SUPPORTS**. The abstract explicitly combines trajectory-sensitive DAE linearization, a Gaussian prior, parameter posterior and closed-form model evidence. The manuscript accurately treats it as a parameter-inference precedent.

Source: [publisher abstract; author-hosted original-paper excerpt](https://ieeexplore.ieee.org/document/9512471/).

### nugroho2022dae

- `sections/article_related.tex:7` — **SUPPORTS**. The source jointly estimates dynamic and algebraic network states with an observer designed to accommodate noise, unknown inputs and input sensor failures.

Source: [author preprint abstract](https://arxiv.org/abs/2202.13254).

### openaiCodex2026

- `main.tex:81` — **SUPPORTS**. The page identifies Codex as an OpenAI coding agent and is appropriate for identifying disclosed assistance. The authors' actual usage and responsibility are author declarations, not facts authenticated by the product webpage.
- `preamble.tex:54` — **SUPPORTS**. The page identifies Codex as an OpenAI coding agent and is appropriate for identifying disclosed assistance. The authors' actual usage and responsibility are author declarations, not facts authenticated by the product webpage.
- `author_biographies.tex:8` — **SUPPORTS**. The page identifies Codex as an OpenAI coding agent and is appropriate for identifying disclosed assistance. The authors' actual usage and responsibility are author declarations, not facts authenticated by the product webpage.
- `supplement.tex:66` — **SUPPORTS**. The page identifies Codex as an OpenAI coding agent and is appropriate for identifying disclosed assistance. The authors' actual usage and responsibility are author declarations, not facts authenticated by the product webpage.

Source: [official product page](https://openai.com/codex/).

### pandey2020realtime

- `sections/article_related.tex:50` — **SUPPORTS**. The source combines statistical/clustering anomaly detection, DBSCAN, physics-based rules/decision trees and topology-based localization. It supports the broad learned-and-knowledge-driven grouping, not a claim that its full method is a supervised learner.

Source: [publisher abstract and introduction](https://doi.org/10.1109%2FTPWRS.2020.2986019).

### rovatsos2017outage

- `sections/article_intro.tex:26` — **SUPPORTS**. The source propagates demand statistics through a network model and develops dynamic composite quickest-change detection including transients; the two general descriptions are supported.
- `sections/article_related.tex:17` — **SUPPORTS**. The source propagates demand statistics through a network model and develops dynamic composite quickest-change detection including transients; the two general descriptions are supported.

Source: [author-hosted original paper and institutional abstract](https://aledan.ece.illinois.edu/files/2017/04/TSP_2017.pdf).

### sarkka2013bayesian

- `supplement/appendix_causal_walkthrough.tex:20` — **SUPPORTS**. The first edition covers Bayesian filtering, Gaussian filtering and smoothing. It supports the cited standard conditional Gaussian filtering identities; citing this edition is valid even though a second edition now exists.

Source: [publisher Gaussian-filtering chapter record; author edition listing and registry description](https://www.cambridge.org/core/product/97BF7ECDEA1C808257A0CBDB21A711A6).

### scharf1994matched

- `sections/article_related.tex:12` — **SUPPORTS**. The source derives GLRTs for signals in subspace interference and noise, providing the nuisance-profiled detection precedent. The manuscript correctly limits its use to qualitative noise sensitivity and disclaims a universal error certificate.
- `sections/article_information.tex:33` — **SUPPORTS**. The source derives GLRTs for signals in subspace interference and noise, providing the nuisance-profiled detection precedent. The manuscript correctly limits its use to qualitative noise sensitivity and disclaims a universal error certificate.

Source: [original-paper full-text excerpt](https://www.mssc.mu.edu/~daniel/mscs6960/spring2010/ScharfFriedlanderTSP94.pdf).

### tartakovsky2023gp

- `sections/article_related.tex:57` — **SUPPORTS**. The source constructs prior state statistics from stochastic swing equations and estimates/forecasts unobserved states, supporting the latent-state-estimation statement. The final journal issue is 2023 despite the DOI/online year 2022.

Source: [publisher full-text excerpt and author-lab abstract](https://www.sciencedirect.com/science/article/pii/S0169207022000474).

### tate2008outage

- `sections/article_related.tex:15` — **SUPPORTS**. The paper detects line outages from topology information and sparse phasor-angle measurements, exactly the scope stated.

Source: [original paper from research consortium](https://documents.pserc.wisc.edu/documents/publications/papers/2007_general_publications/tate_overbye_pes_nov2007.pdf).

### warner2023highfidelity

- `sections/article_intro.tex:27` — **SUPPORTS**. The original paper uses simulated voltage/current paths, maximizes over onset positions t-M <= k < t, and returns candidate lines. The evaluated target is short circuits with clearing assumed after the detection window (Section IV.C); load changes are tested for induced false alarms (Section IV.D). Both uses are supported. Direct TechRxiv/PDF access failed, so the full-text mirror and registry were used; byte identity to v1 was not certified.
- `sections/article_related.tex:27` — **SUPPORTS**. The original paper uses simulated voltage/current paths, maximizes over onset positions t-M <= k < t, and returns candidate lines. The evaluated target is short circuits with clearing assumed after the detection window (Section IV.C); load changes are tested for induced false alarms (Section IV.D). Both uses are supported. Direct TechRxiv/PDF access failed, so the full-text mirror and registry were used; byte identity to v1 was not certified.

Source: [original preprint text mirrored online; TechRxiv registry; repository PDF indexed excerpts](https://www.researchgate.net/publication/371657943_Quick_Line_Fault_Detection_and_Identification_Using_High-Fidelity_Models_of_Transient_Dynamics).

### warner2024matrix

- `sections/article_related.tex:35` — **SUPPORTS**. The source analyzes sequential change diagnosis with a finite family of post-change laws, unknown onset, error control and delay; the manuscript appropriately withholds transfer of those guarantees to its approximate bank.

Source: [publisher original-paper abstract](https://www.imstat.org/publications/bej/bej_30_3/bej_30_3.pdf).

### yildiz2024few

- `sections/article_related.tex:50` — **SUPPORTS**. The source combines a CNN-assisted method and strategic sparse PMUs for fault detection/location, supporting the representation-based diagnosis claim.

Source: [publisher abstract and method excerpt](https://www.sciencedirect.com/science/article/abs/pii/S0378779624005911).

### yildiz2025sparse

- `sections/article_related.tex:22` — **SUPPORTS**. The paper explicitly optimizes sparse PMU placement to improve line-outage/fault identification accuracy, supporting the sensor-placement statement.

Source: [publisher abstract](https://ieeexplore.ieee.org/document/10640266/).

### zhao2014outages

- `sections/article_related.tex:16` — **SUPPORTS**. The source develops joint Bayesian outage/state inference using Gaussian state priors and posterior-based detection, matching the manuscript statement.

Source: [author institution abstract](https://collaborate.princeton.edu/en/publications/identification-of-outages-in-power-systems-with-uncertain-states-/).

## Completion check

Declared input hashes unchanged: **True**. Changed files: none.
No manuscript/bibliography corrections were applied by this reviewer. No compilation was run because only audit artifacts changed. The parent reviewer is responsible for authorized fixes and the subsequent manuscript build.
