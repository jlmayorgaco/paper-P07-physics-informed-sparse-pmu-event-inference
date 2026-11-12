"""Build the vector-only half-page method figure from editable TikZ."""
from pathlib import Path
import shutil
import subprocess
import pymupdf

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'figures/paper_method'
    build = ROOT / 'build/paper_method'
    build.mkdir(parents=True, exist_ok=True)
    run = subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
        f'-output-directory={build}','main.tex'],cwd=source,capture_output=True,text=True)
    (build/'compile.txt').write_text(run.stdout+run.stderr,encoding='utf-8')
    if run.returncode:
        raise RuntimeError(run.stdout[-5000:])
    dest = ROOT/'figures/generated/paper_method.pdf'
    shutil.copy2(build/'main.pdf',dest)
    with pymupdf.open(dest) as doc:
        if len(doc)!=1 or doc[0].get_images():
            raise ValueError('Expected a single vector-only page')
        doc[0].get_pixmap(matrix=pymupdf.Matrix(3,3),alpha=False).save(dest.with_suffix('.png'))
        print(f'Figure: {doc[0].rect.width:.1f} x {doc[0].rect.height:.1f} pt')
    print(dest)

if __name__=='__main__': main()
