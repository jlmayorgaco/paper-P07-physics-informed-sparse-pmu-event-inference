"""Compile an extracted source ZIP without the working repository's files."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import zipfile
import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def main():
    archive_path = ROOT / 'output/source/P07_Article_Supplement_Source.zip'
    work = Path(tempfile.mkdtemp(prefix='source-smoke-', dir=ROOT / 'build')).resolve()
    assert work.is_relative_to((ROOT / 'build').resolve())
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            if not (work / name).resolve().is_relative_to(work):
                raise ValueError('Archive path outside smoke directory')
        archive.extractall(work)
        manifest = json.loads(archive.read('SOURCE_MANIFEST.json'))
    for name, expected in manifest.items():
        if hashlib.sha256((work / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Source hash mismatch: ' + name)
    results = {}
    for document in ('main', 'supplement'):
        latex = ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', document + '.tex']
        commands = [latex, ['bibtex', document], latex, latex]
        with (work / (document + '_build.txt')).open('w', encoding='utf-8') as log:
            for command in commands:
                process = subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT)
                if process.returncode:
                    raise RuntimeError(f'{document} isolated build failed; see {log.name}')
        original = pymupdf.open(ROOT / (document + '.pdf'))
        reproduced = pymupdf.open(work / (document + '.pdf'))
        same = len(original) == len(reproduced) and all(
            a.get_text() == b.get_text() for a, b in zip(original, reproduced))
        if not same:
            raise ValueError('Isolated PDF text or pagination differs: ' + document)
        results[document] = dict(pages=len(reproduced), text_and_pagination_match=True)
    output = dict(status='PASS', source_package_sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                  isolated_directory=str(work), input_files=len(manifest), documents=results,
                  system_TeX_dependencies_required=True, scientific_readiness_certified=False)
    (ROOT / 'output/source/SOURCE_PACKAGE_VALIDATION.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(output, indent=2), flush=True)


if __name__ == '__main__':
    main()
