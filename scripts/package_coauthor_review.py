"""Package the current verified coauthor review artifacts without changing results."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "output/P07_Para_David_y_Masoud.zip"
FILES = [
    "docs/revision_execution_20261103/RESPONSE_AND_STATUS.md",
    "generated/revision_math_20261103/checks.json",
    "generated/revision_math_20261103/PORTABILITY.json",
    "generated/comparator_lineage.json",
    "scripts/verify_history_partition.py",
    "scripts/build_comparator_lineage.py",
    "docs/P07_VALIDATION_ACTIONS.md",
    "docs/SCIENTIFIC_AUDIT_RESPONSE_20261103.md",
    "generated/monitored_exposure_audit.json",
    "generated/scientific_revision_audit.json",
    "generated/paired_monitored_intervals.csv",
    "scripts/monitored_exposure.py",
    "scripts/build_scientific_revision.py",
    "output/pdf/P07_Event_Attribution_Article.pdf",
    "output/pdf/P07_Event_Attribution_Supplement.pdf",
    "output/pdf/P07_Historical_Technical_Notes.pdf",
    "output/pdf/P07_Coauthor_Brief_David_Masoud.pdf",
    "output/source/P07_Article_Supplement_Source.zip",
    "docs/P07_COAUTHOR_BRIEF.md",
    "docs/P07_COAUTHOR_BRIEF_MANIFEST.json",
    "docs/P07_CLOSURE_FOR_COAUTHORS.md",
    "docs/HACKATHON_TO_C01_METHOD_TRACE.md",
    "docs/METHODS_AND_RESULTS_HANDOFF.md",
    "docs/P07_RESEARCH_CONTRIBUTION.md",
    "docs/SUBMISSION_DECLARATIONS_PENDING.md",
    "docs/CONTROLLED_ABLATION_STATUS.md",
    "scripts/build_review_diagnostics.py",
    "scripts/build_complete_confirmation_tables.py",
    "generated/frozen/c01_20261029/RECORDS.csv",
    "generated/EVIDENCE_BRIDGE_PROVENANCE.json",
    "generated/frozen/SOURCE_MANIFEST.csv",
    "figures/generated/evidence_bridge.png",
    "figures/generated/historical_transfer_confusion.png",
    "scripts/build_evidence_bridge.py",
    "figures/author_photos/PROVENANCE.md",
    "figures/author_photos/source/masoud_barati.jpg",
    "figures/author_photos/source/payman_dehghanian.jpg",
    "figures/author_photos/source/david_celeita.jpg",
    "figures/author_photos/masoud_barati_bw.png",
    "figures/author_photos/payman_dehghanian_bw.png",
    "figures/author_photos/david_celeita_bw.png",
    "docs/c01-confirmatory-results.md",
    "docs/C01_COAUTHOR_STATUS.json",
    "generated/frozen/c01_20261029/MANIFEST.json",
    "generated/frozen/c01_20261029/SUMMARY.csv",
    "generated/frozen/c01_20261029/BY_SOURCE.csv",
    "generated/frozen/c01_20261029/EVENTS.csv",
    "generated/frozen/c01_20261029/EXTRAS.csv",
    "generated/frozen/c01_20261029/PAIRED_INTERVALS.csv",
    "generated/frozen/c01_20261029/EVALUATION_AUDIT.json",
]


def main() -> None:
    readme = (
        "P07 coauthor review package — scientific revision, 3 November 2026\n\n"
        "Read the current scientific-audit response, coauthor brief and main article first; older research notes retain their component-study scopes. "
        "The article focuses on physical recovery, independent load/line attribution and controlled state-carry evidence. The essential supplement contains the implemented-filter derivations and checks, comparator lineage, complete C01/A01 outcomes and separate context/recovery controls. Earlier reconstruction, feature and simultaneous-source studies remain in Historical Technical Notes. Read docs/revision_execution_20261103/RESPONSE_AND_STATUS.md for the latest changes and scientific gaps. "
        "C01 completed 171 physical trajectories and 342 observed records without "
        "method retuning. The source package rebuilds the article. The evidence "
        "concerns the F01 load/line catalog; the out-of-bank R/X alarm burden "
        "is retained. This is a coauthor-review draft, not a journal-ready claim. "
        "No message has been sent to coauthors.\n"
    )
    files = FILES + [str(p.relative_to(ROOT)).replace(chr(92), "/") for p in sorted((ROOT / "generated/frozen/historical_submission_comparison_20261102").glob("*"))]
    for folder in ('generated/review_diagnostics_20261102', 'generated/frozen/ablation_a01_20261102',
                   'generated/frozen/comparator_lineage_20261103',
                   'generated/frozen/revision_math_kernel_20261103'):
        files += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / folder).glob('*')) if p.is_file() and p.suffix in ('.md', '.json', '.csv', '.py')]
    evidence = json.loads((ROOT / "generated/EVIDENCE_BRIDGE_PROVENANCE.json").read_text())
    files += [x["path"].replace(chr(92), "/") for x in evidence["inputs"]]
    files = list(dict.fromkeys(files))
    entries = []
    for name in files:
        data = (ROOT / name).read_bytes()
        entries.append({"path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    manifest = {
        "status": "COAUTHOR_REVIEW_NOT_SUBMISSION_READY",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": entries,
    }
    with ZipFile(TARGET, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("READ_ME.txt", readme)
        archive.writestr("MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
        for name in files:
            archive.write(ROOT / name, name)
    with ZipFile(TARGET) as archive:
        assert archive.testzip() is None
        for entry in entries:
            assert hashlib.sha256(archive.read(entry["path"])).hexdigest() == entry["sha256"]
    print(f"{TARGET}: {len(entries)} files, hashes verified")


if __name__ == "__main__":
    main()
