import hashlib,json
from pathlib import Path
root=Path('experiments/external_physics_terminal_successor_20261112')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
files={str(p.relative_to(root)).replace('\\','/'):digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts}
manifest={'task':'external static prototype terminal-end correction','source_zip_sha256':'c19f7ed78d3b60bf05e50c6319ba6d196a6b1a43f9141c43b0a6188d1288f048','source_run_original_local_change':'Only OUT redirected from results/ to original_results/; numerical algorithm unchanged (validated against extracted source).','source_extracted_files':{'case39_data.py':'e49d31f90bebdc0edcb3afc5061c68ca5be58ba55c31105e8d5dd4985ada2793','run_experiment.py':'8ffb78d321453d86034ad5e8c992549232593f4081bcfd284f48990f9dc33a51'},'random_seed':261112,'paired_noise_shape':[18,150,32],'files_sha256':files}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
