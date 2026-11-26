"""Publish main.tex as a standalone article; supporting material stays separate."""
from pathlib import Path
import os, shutil
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
def main():
    source=ROOT/'main.pdf'
    with pymupdf.open(source) as pdf:
        n=len(pdf)
        if n<1:raise ValueError('Empty article')
        if any('APPENDIX A.' in p.get_text() for p in pdf):
            raise ValueError('Supporting appendices must not be appended to the main article')
    dest=ROOT/'output/pdf/P07_Event_Attribution_Article.pdf'
    temp=dest.with_suffix('.tmp.pdf');shutil.copy2(source,temp);os.replace(temp,dest)
    assert source.read_bytes()==dest.read_bytes()
    print('STANDALONE_ARTICLE',n,'pages',dest)
if __name__=='__main__':main()
