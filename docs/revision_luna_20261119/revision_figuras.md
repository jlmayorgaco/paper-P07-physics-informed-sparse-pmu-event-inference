# Initial visual review, article and supplement at e9a80ec

## fig main 0

| Figure | Interpretation | Visual issue and action |
|---|---|---|
| **1** | The flow diagram shows how candidate event histories are propagated, compared with PMU reports, and used to support an alarm, source diagnosis, or restoration report. | Several labels and equations are small at page size. Enlarge the text or simplify the annotations while preserving the sequence and distinctions between the panels. |
| **2** | Nine panels illustrate normal operation, recorded event traces, missing or corrupted PMU data, and the definition of an unknown event. | The multi-panel axes and legends are small, but the figure remains interpretable at the shown size. **Protected: preserve the image byte-for-byte and keep it visible in the main PDF.** |
| **3** | The single-line diagram locates the eight voltage PMUs and candidate line and load events on the IEEE-39 system; the table maps current measurements to branch terminals. | The topology and table are dense at page size. **Protected: keep the figure visible and retain the specified network, connections, and PMU locations; do not replace it with a node graph.** |
| **4** | The plots compare timely attribution and extra alarms for the history bank, continuous GLR, and ExtraTrees, with paired differences below. | The interval labels and small annotations are hard to read at page size. Increase their size or simplify the labels without changing results. |
| **5** | The panels compare attribution coverage and extra alarms for history, carry, and reset across two plants; the second plant’s paired coverage interval includes zero. | The six-panel layout is clear, but count labels and interval annotations are small. Enlarge those annotations while retaining the zero reference and interval. |

## fig supplement 0

| Figure | Concrete interpretation | Visual problem and action |
|---|---|---|
| **1** | A load or line intervention changes the network response; machine state and instrument memory continue, while the measurement history is formed from reported coordinates. | The three panels read as a sequence, but labels and equations are very small at page size. Enlarge key notation and panel text if space permits. |
| **2** *(protected)* | Eight PMU responses compare a load change with a line opening; the shaded interval marks the physical event. | Traces and legend are crowded, and several channel colors are hard to distinguish. Preserve this protected figure; improve contrast or line styles only if allowed without changing the data or image. |
| **3** *(protected)* | The confusion matrices show timely family diagnosis for the fixed continuous test, with omitted or late diagnoses counted as “No timely diagnosis.” | Category labels wrap tightly and the counts are small, though the four-panel comparison is readable. Preserve this protected figure; retain the caption’s scope and caveat. |
| **4** | The left panel compares timely family-and-source decisions; the right shows unmatched alarms, which rise sharply outside the bank for the physical and nominal banks. | The alarm panel’s scale compresses most methods near zero, while the two large values dominate. Consider a clearly marked inset or broken scale; retain the separate method publication rules. |
| **5** | Development methods trade timely attribution against unmatched event-stream alarms; the onset witness has no extras but misses a real BUS16 event. | Point labels and markers are small, and the plotted sample is limited. Keep the paired-realization caveat prominent and enlarge labels where possible. |
| **6** | The sequence shows BUS31 eventually identified under an out-of-bank change, but only after the true OFF time, so attribution is late. | The multi-panel plot is dense: row labels, event markers, and the bottom trace are small. Enlarge the labels and clarify the alignment of the OFF marker with diagnosis timing. |
| **7** | With onset supplied, the left panel compares one-second source separation; the right shows how the reference amplitude threshold changes with assumed noise. | Small labels and closely spaced source curves make individual comparisons difficult. Increase label size and distinguish curves with line styles or direct labels. |
| **8** | The reset’s largest profiled-energy gains are shown by event family; filled points mark cases followed by an unmatched alarm or loss of the next timely diagnosis. | Log-scale values span a wide range, and the legend and filled/open symbols are easy to miss. Make the marker meaning more explicit in the panel and improve the legend’s size and contrast. |

## fig supplement 7

| Fig. | Concrete interpretation | Visual issue and action |
|---|---|---|
| 9 | Timely attribution falls sharply for load events at the widest startup noise scales; the diagnostic panel separates timely detections from misses by matched-signature energy. | The log-scale scatter and small markers make the diagnostic harder to read than the bars. Enlarge markers and clarify the dashed reference in the panel. |
| 10 | At 1 s, the plots compare pairwise source separation with voltage alone versus voltage plus current, then show the effect of fitting rival load amplitudes. | Many bus and line labels are small. Increase label size or simplify the y-axis labels while retaining source identities. |
| 11 | The curves show how quickly each method accumulates correct diagnoses over time; incorrect or absent diagnoses do not add mass. | Several curves overlap near the start and at saturation. Use stronger line styles or markers to keep methods distinguishable. |
| 12 | In six paired strata, the physical bank’s timely-attribution and unmatched-alarm differences are shown relative to ExtraTrees; orange rows identify out-of-bank conditions. | The zero reference and interval endpoints are visually easy to miss. Make the zero line and point/interval marks more prominent. |
| 13 | The timeline contrasts diagnoses against true ON/OFF intervals; a bus-31 diagnosis after OFF misses the timely endpoint. | Labels and false-alarm annotations crowd the later timeline events. Offset them and use leader lines for clearer associations. |
| 14 | The three panels show a PMU 2 parity trace, balanced voltage changes against network-coupling bounds, and information under one missing or corrupted PMU. | The multi-panel labels and panel C categories are small; panel A’s dense trace also obscures individual spikes. Enlarge the panels and annotate the key thresholds/events. |
| 15 | The ablation compares nominal, recentered, and conditioned signatures while keeping the data and decision calculation shared. | Box text and equations are too small at page scale. Increase type size and simplify equations where possible. |
| 16 | Recentring and conditioning affect response error, source/presence decisions, and severity error differently; nominal and recentered response predictions coincide. | The three outcomes use separate scales, which the caption explains but the graphic does not emphasize. Add compact panel subtitles or a shared legend spanning all panels. |
| 17 | This fixed example shows observed PMU channels, physical truth, and each method’s selected-source estimate over the ON/OFF interval. | Gray observations compete with thin colored predictions, especially in the left panels. Increase prediction line weight and distinguish truth with a clearer stroke. |
| 18 | With the previous trajectory treated as known, recovery separation stays near equilibrium; adding uncertain prior severity reduces separation across the displayed cases. | Cell values are readable but row labels are tight. Add a little row spacing or enlarge the labels. |
| 19 | The solid upper path is the reported physical bank; dashed lower modules are proposed extensions, with cyber outputs kept outside the physical likelihood path. | The schematic is dense, and the solid/dashed boundary is easy to lose at this size. Enlarge text and visually separate the reported and proposed paths. |

Protected main figures 2–3 should remain included and visible as instructed; they are not among the attached rendered pages reviewed here.

## fig supplement 14

| Figure | Interpretation | Visual issue and action |
|---|---|---|
| **20** | Rotor deviation energy spikes after the 2 s event; network active-power loss changes with switching and load recovery. | Near-zero traces are hard to distinguish, and event timing is not equally explicit across panels. Add subtle guides at 2, 3, and 6 s in both panels and strengthen the near-zero traces. |
| **21** | Reduced polar observations track phase response fairly closely; the complex-voltage path produces a large spurious magnitude response during load recovery. | The fine dotted trace and compact legend are difficult to parse at this size. Increase line weight or use direct labels so the three methods remain distinguishable. |
| **22** | The observation-only control nearly overlaps the fixed predictor; refreshing every three reports lowers recovery RMSE in all four line cases. | In panel (b), only the lower-error values are annotated, leaving the fixed-versus-refreshed comparison to be estimated from the log axis. Label both values per case or show the exact pairs. |
| **23** | Median separation stays near 99% across gap settings, while lower-tail separation falls more at the shortest and longest gaps, especially at the larger prior scale. | The vertical axis begins at 94%, which visually magnifies small median differences. Keep the focused range but make the truncated scale explicit and add a full-range reference or inset. |

Protected main Figures 2–3 remain preserved.
