"""Apply the current pre-A01 editorial staging to an isolated lightweight preview tree."""
from pathlib import Path
import hashlib, json, re, shutil
PAPER=Path(__file__).resolve().parents[4]
STAGE=Path(__file__).resolve().parents[1]
PREVIEW=PAPER/'tmp'/'p07_closure_preview_v6'
MARKER=STAGE/'PREVIEW_PREPARED.json'

if MARKER.is_file():
 manifest=json.loads(MARKER.read_text(encoding='utf-8'))
 for rel,expected in manifest['source_hashes'].items():
  for base in (STAGE,PREVIEW):
   path=base/rel
   if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
    raise RuntimeError(f'Prepared preview source drift: {path}')
 if (PREVIEW/'main.tex').read_text(encoding='utf-8').count(r'\input{sections/article_closure_results}')!=1:
  raise RuntimeError('Prepared preview must include closure results exactly once')
 print('isolated preview sources verified unchanged:',PREVIEW)
 raise SystemExit(0)

def copy(src,dst):
 print('copy',src,'->',dst)
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def replace_once(path,old,new):
 text=path.read_text(encoding='utf-8')
 if text.count(old)!=1: raise RuntimeError(f'Expected one match in {path}: {old[:80]!r}; got {text.count(old)}')
 path.write_text(text.replace(old,new),encoding='utf-8')

# New generated evidence artifacts are isolated from the A01 importer and source directories.
for name in ['closure_restoration.pdf','closure_restoration.png']:
 copy(STAGE/'figures'/'generated'/name,PREVIEW/'figures'/'generated'/name)
for name in ['closure_restoration.tex','closure_compute_cost.tex']:
 copy(STAGE/'tables'/'generated'/name,PREVIEW/'tables'/'generated'/name)

# Revised abstract: accurate, bounded and explicit about comparator weakness and posthoc endpoint.
main=PREVIEW/'main.tex'
text=main.read_text(encoding='utf-8')
new_abstract=r'''\begin{abstract}
Eight PMUs observe only part of an IEEE 39-bus system, so a disturbance can be detected without uniquely identifying its cause. We evaluate a recovery-aware physical hypothesis bank for continuous attribution of load changes and line openings in a fixed simulated catalog. Switched differential-algebraic and oriented PMU-terminal models generate candidate observation paths; a local truncated-Gaussian integral handles unknown load severity, and the finite history bank retains predicted physical and instrumental response after OFF. The full bank remains approximate through plug-in context, shared regime covariances, screening and pruning. Across 18 six-intervention schedules, three network conditions and two noise scales, it assigns the correct family and source before OFF in 644 of 648 event realizations, with 72 unmatched alarms. Two causal ExtraTrees references reach 330/648 with 29 alarms and 352/648 with 16 alarms; both were weak on load attribution during development, so the comparison does not establish general superiority over machine learning. A posthoc audit finds that 0/644 available physical-bank restorations and 0/643 nominal restorations occur more than one report early, versus 52/330 and 26/352 for the learned methods; many learned events have no restoration value. These dependent replays do not isolate the effect of memory. The results support a coverage--alarm tradeoff for this model family and catalog, not calibrated probabilities, field validation or real-time operation.
\end{abstract}'''
text,n=re.subn(r'\\begin\{abstract\}.*?\\end\{abstract\}',lambda _:new_abstract,text,flags=re.S)
if n!=1: raise RuntimeError(f'abstract replacement count={n}')
main.write_text(text,encoding='utf-8')

# The staged main.tex already contains the posthoc section input. Only inject it
# when preparing from an older base; never create a duplicate float/label set.
if not main.read_text(encoding='utf-8').count(r'\input{sections/article_closure_results}'):
 replace_once(main,r'\input{sections/08c_c01_confirmatory}',r'\input{sections/08c_c01_confirmatory}'+'\n'+r'\input{sections/article_closure_results}')
elif main.read_text(encoding='utf-8').count(r'\input{sections/article_closure_results}') != 1:
 raise RuntimeError('Expected exactly one closure-results input in preview main.tex')

# Focus the three contribution claims on the procedure/evidence; do not claim an isolated component effect.
intro=PREVIEW/'sections'/'article_intro.tex'
old='''The paper makes three contributions:
\\begin{enumerate}
\\item Network-conditioned state reconstruction, physical feature ablations
and mixed-source sensitivity experiments measure how network equations
recover unmeasured voltages and distinguish candidate inputs. Each
experiment retains its own data and evaluation conditions.
\\item The continuous procedure compares new interventions with retained
recovery histories, integrates local load severity, and separates active
mass $M$ from originating-cause mass $\\Gamma$. Its $\\Delta M$ records the
changing attribution. These quantities summarize the hypothesis weights;
the physical information enters through the candidate trajectories.
\\item A direct historical transfer of the submitted system and a new
same-stream comparison with causal ExtraTrees distinguish feature failure,
source attribution and alarm cost. The latter also compares a published
outage detector on its eligible persistent-line task.
\\end{enumerate}'''
new='''The paper makes three bounded contributions:
\\begin{enumerate}
\\item It specifies an executable physical measurement contract in which a
switched DAE and oriented terminal map generate the candidate PMU paths.
\\item It evaluates a continuous history bank that compares new load or line
interventions with retained recovery, integrates local load severity, and
reports active mass $M$ separately from originating-cause mass $\\Gamma$.
These are summaries of an approximate, screened hypothesis bank.
\\item It measures timely family/source attribution, unmatched alarms and
restoration behavior on a prespecified catalog, and states exactly how that
evidence differs from two frozen ExtraTrees procedures and historical
window-based results.
\\end{enumerate}'''
replace_once(intro,old,new)
# Scope and outcome framing at the introduction's headline.
replace_once(intro,'A subsequent\ncontrolled study separates amplitude-evidence scoring from physical-state\ncarry at closure. Its design and completion status are reported separately\nfrom the original comparison.','A separate posthoc component study tests amplitude-evidence scoring and\nphysical-state carry at inferred closure. It is not an independent confirmation\nand cannot establish a benefit until all four arms and their intervals are\nreviewed.')

# Explicit history-mass bridge, null mass, implicit admitted transitions and suffix replacement.
method=PREVIEW/'sections'/'article_method.tex'
old='''The rolling screen proposes histories; it is not another independent
observation. Replaying a suffix replaces its original no-new-event suffix
likelihood. The sequential update therefore counts each report once,
rather than repeatedly accumulating overlapping ten-second windows.'''
new='''The rolling screen proposes histories; it is not another independent
observation. Replaying a suffix replaces its original no-new-event suffix
likelihood. The sequential update therefore counts each report once,
rather than repeatedly accumulating overlapping ten-second windows.

Within each fixed network hypothesis $\\ell$, let $\\mathcal H_{\\ell,k}$
denote its screened non-null histories and
$\\mathcal A_{\\ell,k}=\\mathcal H_{\\ell,k}\\cup\\{0\\}$ include the
null history $0$ (no intervention). The predicted masses apply the
implementation's birth and OFF hazards to survivors and children; these
transitions are generated on demand and are not a materialized transition
matrix over all possible histories. Within network hypothesis $\\ell$,
\\begin{align}
\\bar\\pi_{\\ell,h,k}&=\\sum_{g\\in\\mathcal A_{\\ell,k-1}}
  T^{(\\ell)}_{g\\to h,k}\\pi_{\\ell,g,k-1},\\nonumber\\\\
\\widetilde\\pi_{\\ell,h,k}&=L_{\\ell,h,k}\\bar\\pi_{\\ell,h,k},\\qquad
\\widetilde\\pi_{\\ell,0,k}=L_{\\ell,0,k}\\bar\\pi_{\\ell,0,k},\\nonumber\\\\
\\pi_{\\ell,h,k}&=\\frac{\\widetilde\\pi_{\\ell,h,k}}
 {\\sum_{j\\in\\mathcal A_{\\ell,k}}\\widetilde\\pi_{\\ell,j,k}}.
\\label{eq:history-mass-update}
\\end{align}
The birth hazard supplies the prior mass for a proposed intervention from
the null history. A retrospective birth replaces the old null suffix score
with the candidate suffix score; the supplement states the corresponding
suffix-replacement identity. It does not add the same reports twice. After
each update, the screen and beam prune hypotheses
and the retained masses are renormalized jointly with the null. Thus the
equation describes the flow of the currently admitted bank within one
fixed network hypothesis. The outer weights $w_{\\ell,k}$ are updated from
network-level predictive densities and combine these conditional masses in
$M$ and $\\Gamma$; they are not part of the within-bank normalizer. The
equation does not enumerate all histories or define a calibrated posterior.'''
replace_once(method,old,new)
replace_once(method,'Its frozen\nbirth screen searches lags of 0--18 reports and proposes selected onsets;\nit does not enumerate every onset in the 300-report history.','Its frozen birth screen proposes selected onsets at 19 candidate lags,\n0--18, within a 20-report candidate window. It does not enumerate every\nonset in the 300-report history.')
replace_once(method,'\\item Screen onsets in the latest 18 reports. Start each proposed history','\\item Screen 19 candidate onset lags (0--18) within the 20-report window. Start each proposed history')
replace_once(method,'The internal observer proposes an alarm after six reports above the 0.99\nactive-mass threshold.','The internal observer proposes an alarm after the six-report persistence\nrule above the 0.99 active-mass threshold.')

# Four-column capability comparison gains the directly relevant PF/DAE paper and bounded contrast.
related=PREVIEW/'sections'/'article_related.tex'
replace_once(related,'''Warner \\emph{et al.} compare simulated voltage/current paths across an
unknown-onset window for short-circuit line identification
\\cite{warner2023highfidelity}. Our load/line task continues through
restoration and successive events; their method has not been run on this
cohort. Multiple-model filters and adaptive history banks already retain
conditional modes \\cite{blom1988imm,boers2005m3h}; sequential diagnosis
has established error/delay theory under specified observation laws
\\cite{warner2024matrix}. Our screened, pruned bank inherits none of those
general optimality or delay guarantees.''','''Warner \\emph{et al.} compare simulated voltage/current paths across an
unknown-onset window for short-circuit line identification
\\cite{warner2023highfidelity}. Yang, Chen and Zhai combine partial-PMU
algebraic measurements with particle-filter estimates of generator dynamic
states, then monitor outage signatures with an EWMA on the IEEE-39 system
\\cite{yang2021particle}. This is a close physical precedent for line
outage detection; the present evaluation instead attributes load and line
interventions through OFF and successive recovery. Neither study is run as a
same-data benchmark here. Multiple-model filters and adaptive history banks
already retain conditional modes \\cite{blom1988imm,boers2005m3h}; sequential
diagnosis has established error/delay theory under specified observation
laws \\cite{warner2024matrix}. Our screened, pruned bank inherits none of
those general optimality or delay guarantees.''')
replace_once(related,r'''Warner high-fidelity & Simulated V/I paths and onset search & Short-circuit line candidates & Closest trajectory precedent; no common-data run\\
Adaptive Matrix CuSum''',r'''Warner high-fidelity & Simulated V/I paths and onset search & Short-circuit line candidates & Closest trajectory precedent; no common-data run\\
Yang--Chen--Zhai (2021) & Particle filter for generator states; EWMA outage monitoring & Line-outage detection with partial PMUs on IEEE-39 & Closely related line detector; no continuous load/restoration comparison\\
Adaptive Matrix CuSum''')

# Add exact arXiv reference metadata only after primary-source verification.
bib=PREVIEW/'references.bib'
bibtext=bib.read_text(encoding='utf-8')
if 'yang2021particle' not in bibtext:
 bib.write_text(bibtext.rstrip()+'''\n\n@misc{yang2021particle,
  author       = {Xiaozhou Yang and Nan Chen and Chao Zhai},
  title        = {Dynamic Power Systems Line Outage Detection Using Particle Filter and Partially Observed States},
  year         = {2021},
  eprint       = {2107.06754},
  archivePrefix= {arXiv},
  primaryClass = {eess.SY},
  note         = {Version 3, revised 27 October 2021}
}\n''',encoding='utf-8')

# Clarify parent-resampling denominators in the article's protocol.
protocol=PREVIEW/'sections'/'narrative_protocol.tex'
text=protocol.read_text(encoding='utf-8')
text=text.replace('Confidence intervals use 10,000\npaired parent-cluster resamples, not independent PMU samples.','Confidence intervals use 10,000\npaired parent-cluster resamples, not independent PMU samples. For metrics\nwith zero event denominators on normal parents, those parents remain in the\npaired resample but contribute no event denominator; the effective event\nparent count can therefore vary by bootstrap draw.')
protocol.write_text(text,encoding='utf-8')

# Main results section: report restoration omissions distinctly and use existing stage timings only.
result=STAGE/'sections'/'article_closure_results.tex'
result.write_text(r'''\\section{Episode Restoration and Computational Cost}
\\label{sec:closure-results}

Restoration timing gives a second view of continuous attribution. Figure~\\ref{fig:closure-restoration} shows the signed OFF delay among available associated restorations, alongside intended events without a restoration value. Under the posthoc threshold of more than one 30-Hz report early ($d_{\\rm OFF}<-1/30$ s), the physical bank has 0/644 early restorations and the nominal bank 0/643. The reference and short-window ExtraTrees have 52/330 and 26/352, respectively. The corresponding missing-restoration counts are 4, 5, 318 and 296 out of 648 intended event realizations. Missing values include omissions and are not necessarily open episodes. Replays are dependent; this descriptive criterion is not a new confirmatory endpoint and does not isolate the memory component.

\\begin{figure}[t]\\centering
\\includegraphics[width=\\columnwidth]{figures/generated/closure_restoration.pdf}
\\caption{Posthoc restoration timing and events without an associated restoration value. Panel A shows signed OFF delay only where available; the dashed line marks the threshold at one report early. Panel B reports missing restoration values over 648 intended events, including omissions, not a count of episodes open at record end.}
\\label{fig:closure-restoration}\\end{figure}

Recorded stage timings from the continuous evaluation are summarized in Table~\\ref{tab:closure-compute-cost}. For 120-s records, median physical-history inference took 358.7 s across 270 records, compared with 9.5 s for the combined ExtraTrees adapter stage; physical bank construction had a separate 80.1-s median. Dividing total time by 3,601 reports gives amortized averages of 99.6 ms/report for physical inference and 2.6 ms/report for the combined learned stage. These totals include full-record work and do not measure per-report latency. The physical stage is slower in this recorded implementation and does not support a real-time claim. Timers span stages recorded under concurrent campaign workload; memory use and frame-level latency were not recorded. The 600-s normal controls are summarized separately in the machine-readable cost file.

\\input{tables/generated/closure_restoration}
\\input{tables/generated/closure_compute_cost}
''' .replace('\\\\','\\'),encoding='utf-8')
copy(result,PREVIEW/'sections'/'article_closure_results.tex')
# Copy candidate source files into the durable staging folder for later guarded integration.
for rel in ['main.tex','references.bib','sections/article_intro.tex','sections/article_related.tex','sections/article_method.tex','sections/narrative_protocol.tex','sections/article_closure_results.tex','scripts/c01_main_tables.py','supplement.tex']:
 copy(PREVIEW/rel,STAGE/rel)
# Fix the generator source, not just a generated output label.
gen=PREVIEW/'scripts'/'c01_main_tables.py'
replace_once(gen,"false restorations and open episodes.","unmatched-episode restorations and open episodes.")
replace_once(gen,"& False OFF & Open at end","& Unmatched episode restorations & Open at end")
copy(gen,STAGE/'scripts'/'c01_main_tables.py')
# Correct the pre-A01 preview label while keeping controlled study clearly pending.
# Include new supplementary contracts and profile; do not edit or regenerate frozen figures.
supp=PREVIEW/'supplement.tex'
replace_once(supp,r'\input{supplement/appendix_causal_walkthrough}',r'\input{supplement/appendix_causal_walkthrough}'+'\n'+r'\input{supplement/measurement_contract}'+'\n'+r'\input{supplement/domain_profile}')
copy(supp,STAGE/'supplement.tex')
for rel in ['supplement/measurement_contract.tex','supplement/domain_profile.tex']:
 copy(STAGE/rel,PREVIEW/rel)

print('isolated preview sources prepared:',PREVIEW)
