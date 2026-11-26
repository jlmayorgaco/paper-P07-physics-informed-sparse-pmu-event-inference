"""Compile the editable TikZ recovery overview diagram and export its preview."""
from pathlib import Path
import shutil
import subprocess
import fitz
ROOT = Path(__file__).resolve().parents[1]
def main():
    source = ROOT / 'figures/recovery_overview'
    build = ROOT / 'build/recovery_overview'
    build.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', f'-output-directory={build}', 'main.tex'], cwd=source, capture_output=True, text=True)
    (build / 'compile.log.txt').write_text(run.stdout + run.stderr, encoding='utf-8')
    if run.returncode:
        raise RuntimeError(run.stdout[-4000:])
    target = ROOT / 'figures/generated/recovery_overview.pdf'
    shutil.copy2(build / 'main.pdf', target)
    with fitz.open(target) as pdf:
        if len(pdf) != 1 or pdf[0].get_images():
            raise ValueError('Expected one vector-only figure page')
        pdf[0].get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False).save(target.with_suffix('.png'))
    print(target)
if __name__ == '__main__':
    main()
