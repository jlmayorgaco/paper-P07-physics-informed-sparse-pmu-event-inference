"""Reject tracked files at/above 50 MB before publishing to Overleaf's mirror."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf-8').split('\0')
rows=[((ROOT/n).stat().st_size,n) for n in names if n and (ROOT/n).is_file()]
bad=[(size,n) for size,n in rows if size>=50_000_000]
for size,n in sorted(bad,reverse=True):print(f'OVERLEAF_SIZE_BLOCKER {size} {n}')
if bad:raise SystemExit(1)
size,name=max(rows)
print(f'PASS: {len(rows)} tracked files below 50,000,000 bytes. Largest: {size} {name}')
