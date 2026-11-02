from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
root=Path(__file__).resolve().parents[3]
closure=root/"docs"/"closure_luna"
out=closure/"P07_PreA01_Review_Package.zip"
with ZipFile(out,"w",ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(closure.rglob("*")):
        if not p.is_file() or p==out: continue
        rel=p.relative_to(closure)
        if "inputs" in rel.parts or any(x.lower() in {"tmp","cache","__pycache__"} for x in rel.parts): continue
        if p.suffix.lower() in {".aux",".blg",".fls",".log",".pyc"}: continue
        z.write(p,Path("closure_luna")/rel)
print(out)
