"""Build the architecture and its explicit implementation boundaries."""
from pathlib import Path
import subprocess, shutil
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
def main():
    build=ROOT/'build/layered_architecture';build.mkdir(parents=True,exist_ok=True)
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'-output-directory={build}','main.tex'],cwd=ROOT/'figures/layered_architecture',capture_output=True,text=True)
    (build/'compile.txt').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError(result.stdout[-4000:])
    dest=ROOT/'figures/generated/layered_architecture.pdf';shutil.copy2(build/'main.pdf',dest)
    with pymupdf.open(dest) as d:
        assert len(d)==1 and not d[0].get_images()
        d[0].get_pixmap(matrix=pymupdf.Matrix(3,3)).save(dest.with_suffix('.png'))
    print(dest)
if __name__=='__main__':main()
