"""Build the small LaTeX handoff from the actual compiler dependencies."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TRANSIENT = {".aux", ".out", ".toc", ".lof", ".lot", ".log", ".fls", ".blg", ".fdb_latexmk"}
LIMIT = 40_000_000


def main():
    sources = {ROOT/"references.bib", ROOT/"IEEEtran.bst"}
    for name in ("main", "supplement"):
        recorder = ROOT/(name+".fls")
        for line in recorder.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("INPUT "):
                continue
            path = (ROOT/line[6:].strip('"')).resolve()
            if path.is_relative_to(ROOT) and path.suffix.lower() not in TRANSIENT:
                if not path.is_file():
                    raise FileNotFoundError(path)
                sources.add(path)
    for name in ("Article", "Supplement"):
        pdf = ROOT/"output/pdf"/f"P07_Event_Attribution_{name}.pdf"
        if pdf.stat().st_size >= LIMIT:
            raise ValueError(f"PDF exceeds editorial size target: {pdf}")
    target = ROOT/"output/source/P07_IEEE_Access_Editorial_Source.zip"
    temp = target.with_suffix(".tmp")
    manifest = {}
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(sources):
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            manifest[relative] = hashlib.sha256(data).hexdigest()
            info = zipfile.ZipInfo(relative, date_time=(2026, 11, 13, 0, 0, 0))
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED)
    if temp.stat().st_size >= LIMIT:
        raise ValueError(f"Editorial source exceeds size target: {temp}")
    with zipfile.ZipFile(temp) as archive:
        for name, expected in manifest.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected, name
    temp.replace(target)
    print(json.dumps(dict(file=str(target), files=len(manifest), bytes=target.stat().st_size,
                          sha256=hashlib.sha256(target.read_bytes()).hexdigest()), indent=2))


if __name__ == "__main__":
    main()
