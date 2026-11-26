"""Render non-substitution layout proposals for P07's protected figures.

Only reads the active protected PDFs and writes a new script plus temporary
LaTeX/PDF/raster outputs under build/ and output/previews/. It does not edit
the manuscript, protected sources, or protected image files.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "protected_proposals_20261113"
OUT = ROOT / "output" / "previews" / "proposals_20261113"
EVENTS = ROOT / "figures" / "generated" / "event_signatures.pdf"
TOPOLOGY = ROOT / "figures" / "generated" / "narrative_topology.pdf"


def tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"Required rendering tool not found: {name}")
    return found


def write_event_proposal(path: Path) -> None:
    # Source page is 510.46 x 279.67 bp, with a 3 x 2 panel grid. The trim
    # rectangles retain each complete title, legend, axes, and plotted data.
    # Each cell stores trim left,bottom,right,top. The top-row and bottom-row
    # cells use the shared panel boundaries in the original PDF.
    cells = [
        ("Fault at bus 39", "0 139 340 0"),
        ("Line outage 23--24", "170 139 170 0"),
        ("Generation change at bus 2", "340 139 0 0"),
        ("Load change at bus 7", "0 0 340 139"),
        ("Missing data at PMU 29", "170 0 170 139"),
        ("Corrupted voltage at PMU 2", "340 0 0 139"),
    ]
    def grid(selection: list[tuple[str, str]]) -> str:
        rows = []
        for offset in range(0, len(selection), 2):
            pair = selection[offset : offset + 2]
            images = [
                rf"\includegraphics[trim={trim}bp,clip,width=5.35in]{{{EVENTS.as_posix()}}}"
                for _name, trim in pair
            ]
            rows.append(" & ".join(images) + r"\\[0.02in]")
        return "\n".join(rows)

    physical = grid(cells[:4])
    integrity = grid(cells[4:])
    path.write_text(
        r"""\documentclass[10pt]{article}
\usepackage[paperwidth=11.5in,paperheight=14.7in,margin=0.3in]{geometry}
\usepackage{graphicx,xcolor}
\pagestyle{empty}
\setlength{\tabcolsep}{0pt}
\definecolor{Pblue}{HTML}{2276A0}
\definecolor{Pslate}{HTML}{23343F}
\definecolor{Pteal}{HTML}{087F78}
\definecolor{Porange}{HTML}{C46B2C}
\begin{document}
\sffamily
{\color{Pblue}\bfseries\Large PHYSICAL INTERVENTIONS}\hfill
{\color{Pslate!65}\small Layout concept}\\[-0.06in]
\\[-0.10in]
\noindent\begin{tabular}{@{}cc@{}}
"""
        + physical
        + r"""\end{tabular}\\[-0.02in]
\vspace{0.12in}
{\color{Porange}\bfseries\Large MEASUREMENT-INTEGRITY EVENTS}\\[-0.06in]
\\[-0.10in]
\noindent\begin{tabular}{@{}cc@{}}
"""
        + integrity
        + r"""\end{tabular}
\end{document}
""",
        encoding="utf-8",
    )


def write_topology_proposal(path: Path) -> None:
    path.write_text(
        rf"""\documentclass[10pt]{{article}}
\usepackage[paperwidth=11.7in,paperheight=6.8in,margin=0.30in]{{geometry}}
\usepackage{{graphicx,xcolor}}
\pagestyle{{empty}}
\definecolor{{Pblue}}{{HTML}}{{2276A0}}
\definecolor{{Pslate}}{{HTML}}{{23343F}}
\definecolor{{Pteal}}{{HTML}}{{087F78}}
\begin{{document}}
\sffamily
{{\color{{Pslate}}\bfseries\Large IEEE 39-BUS STUDY MODEL}}\\[-0.04in]
{{\color{{Pslate!65}}\small PMU voltage locations and separately mapped current terminals}}\\[-0.02in]
\noindent\begin{{minipage}}[c]{{6.05in}}
\centering
\includegraphics[width=5.75in]{{{TOPOLOGY.as_posix()}}}
\end{{minipage}}\hfill
\begin{{minipage}}[c]{{4.45in}}
\color{{black!85}}
{{\color{{Pblue}}\bfseries\large Voltage location}}\\[0.02in]
{{\color{{Pslate}}P marks the PMU voltage bus.}}\\[0.12in]
{{\color{{Pteal}}\bfseries\large Current measurement}}\\[0.02in]
{{\color{{Pslate}}Branch and terminal are mapped separately.}}\\[0.12in]
{{\color{{Pteal}}\bfseries\large Provisional mapping}}\\[0.02in]
{{\color{{Pslate}}BUS5: branch 5--6, terminal 5.}}\\[0.18in]
{{\color{{Pslate!65}}\small Layout concept $\bullet$ original topology unchanged.}}
\end{{minipage}}
\end{{document}}
""",
        encoding="utf-8",
    )


def render(stem: str, source: Path) -> None:
    work = BUILD / stem
    work.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, work / "proposal.tex")
    subprocess.run(
        [tool("pdflatex"), "-interaction=nonstopmode", "-halt-on-error", "proposal.tex"],
        cwd=work,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        [tool("pdftoppm"), "-png", "-r", "110", "-singlefile", "proposal.pdf", str(OUT / stem)],
        cwd=work,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    event_tex = BUILD / "events_proposal.tex"
    topology_tex = BUILD / "topology_proposal.tex"
    write_event_proposal(event_tex)
    write_topology_proposal(topology_tex)
    render("events_grouping_proposal", event_tex)
    render("topology_margin_legend_proposal", topology_tex)
    print(f"Rendered PNG proposals to {OUT}")


if __name__ == "__main__":
    main()
