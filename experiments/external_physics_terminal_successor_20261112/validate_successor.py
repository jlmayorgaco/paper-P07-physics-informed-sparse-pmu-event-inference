from pathlib import Path
import ast, csv, hashlib, json
import numpy as np
from case39_data import BRANCH,PMU,LINES
from run_corrected import admittance, branch_voltage_current_response, sel, V0, sd, baseI, H, rank

ROOT=Path(__file__).resolve().parent
ZIP=Path('C:/Users/walla/Downloads/PMU_Investigacion_Fisica_IEEE39_Experimentos.zip')
EXPECTED_ZIP='c19f7ed78d3b60bf05e50c6319ba6d196a6b1a43f9141c43b0a6188d1288f048'

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    return h.hexdigest()

# Independent scalar pi stamp at each end, including phase-zero off-nominal tap.
def direct(row,v,end):
    i,j=int(row[0])-1,int(row[1])-1; R,X,B,tap=row[2:]; y=1/(R+1j*X); a=tap if tap else 1.
    if end=='from': return ((y+1j*B/2)/a**2)*v[i]-(y/a)*v[j]
    return -(y/a)*v[i]+(y+1j*B/2)*v[j]

Y,F,T=admittance(BRANCH)
rng=np.random.default_rng(2601); v=rng.normal(size=39)+1j*rng.normal(size=39)
max_stamp_error=0.
for k,row in enumerate(BRANCH):
    max_stamp_error=max(max_stamp_error,abs(F[k]@v-direct(row,v,'from')),abs(T[k]@v-direct(row,v,'to')))
assert max_stamp_error<1e-10
# Nodal KCL: independently sum every branch-end current into its endpoint bus.
nodal=np.zeros(39,complex)
for k,row in enumerate(BRANCH):
    i,j=int(row[0])-1,int(row[1])-1
    nodal[i]+=F[k]@v
    nodal[j]+=T[k]@v
kcl_error=float(np.max(np.abs(nodal-Y@v)))
assert kcl_error<1e-10
# Ensure transformers and nonzero line charging were exercised explicitly.
tap_rows=np.flatnonzero(BRANCH[:,5]!=0); shunt_rows=np.flatnonzero(BRANCH[:,4]!=0)
assert len(tap_rows)>0 and len(shunt_rows)>0
for k in tap_rows:
    assert abs(F[k]@v-direct(BRANCH[k],v,'from'))<1e-10
    assert abs(T[k]@v-direct(BRANCH[k],v,'to'))<1e-10
for k in shunt_rows:
    assert abs(F[k]@v-direct(BRANCH[k],v,'from'))<1e-10
    assert abs(T[k]@v-direct(BRANCH[k],v,'to'))<1e-10
# Each selected terminal is physically local to its PMU bus; seven are TO.
for pm,(k,end) in zip(PMU,sel): assert int(BRANCH[k,0 if end=='from' else 1])-1==pm
assert sum(end=='to' for _,end in sel)==7

# Remove every unique selected branch and check all current channels: affected zero,
# unaffected equal the independently computed local terminal current.
opened_checks=[]
for k in sorted(set(k for k,_ in sel)):
    branch_open=np.delete(BRANCH,k,axis=0)
    currents=branch_voltage_current_response(V0,branch_open)
    affected=[z for z,(selected,_) in enumerate(sel) if selected==k]
    assert affected
    for z,(selected,end) in enumerate(sel):
        if selected==k: assert currents[z]==0
        else: assert abs(currents[z]-direct(BRANCH[selected],V0,end))<1e-10
    opened_checks.append({'opened_branch_index_zero_based':k,'affected_channels':affected,'all_others_match_direct_formula':True})
assert len(sel)==8

# H and base-current noise use corrected local terminal rows and currents.
assert H.shape==(16,39) and rank==np.linalg.matrix_rank(H)
assert np.allclose(sd[:8],.002) and np.allclose(sd[8:],np.maximum(.002,np.abs(baseI)*.002))

# Execute only the seed/RNG/noise assignments from both scripts, then compare arrays.
def recover_noise(path):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    wanted={'SEED','rng','PAIRED_NOISE'}; selected=[]
    for node in tree.body:
        if isinstance(node,(ast.Assign,ast.AnnAssign)):
            targets=node.targets if isinstance(node,ast.Assign) else [node.target]
            names={n.id for t in targets for n in ast.walk(t) if isinstance(n,ast.Name)}
            if names & wanted: selected.append(node)
    ns={'np':np}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),ns)
    assert ns['SEED']==261112 and ns['PAIRED_NOISE'].shape==(18,150,32)
    return ns['PAIRED_NOISE']
noise_original=recover_noise(ROOT/'run_original.py')
noise_corrected=recover_noise(ROOT/'run_corrected.py')
assert np.array_equal(noise_original,noise_corrected)

assert ZIP.exists() and sha256(ZIP)==EXPECTED_ZIP
orig=json.loads((ROOT/'original_results/summary.json').read_text())
fixed=json.loads((ROOT/'results/summary.json').read_text())
for key in ('noise_accuracy.csv','nearest_competitors.csv','catalog_signatures.npz'):
    assert (ROOT/'original_results'/key).exists() and (ROOT/'results'/key).exists()
with (ROOT/'original_results/noise_accuracy.csv').open() as f: old={(int(r['noise_multiplier']),r['channels']):float(r['accuracy']) for r in csv.DictReader(f)}
with (ROOT/'results/noise_accuracy.csv').open() as f: new={(int(r['noise_multiplier']),r['channels']):float(r['accuracy']) for r in csv.DictReader(f)}
report={
 'validation':{
  'all_46_from_to_stamps_vs_independent_pi_formula':'PASS','tap_transformers':'PASS','line_charging_shunts':'PASS',
  'KCL_all_39_buses':'PASS','KCL_max_abs_residual':kcl_error,
  'opened_each_selected_branch_and_checked_all_channels':'PASS','opened_branch_checks':opened_checks,
  'terminal_selection_local_bus':'PASS','to_end_count':sum(e=='to' for _,e in sel),
  'corrected_H_shape':list(H.shape),'corrected_H_complex_rank':int(rank),
  'noise_base_matches_corrected_terminal_currents':'PASS','max_independent_stamp_error':float(max_stamp_error),
  'zip_sha256_matches_source_manifest':sha256(ZIP),'same_seeded_noise_array_programmatic_equality':True,
  'noise_array_shape':list(noise_corrected.shape)},
 'paired_static_comparison':{
  'same_seed':261112,'same_noise_array_sha256':hashlib.sha256(noise_corrected.tobytes()).hexdigest(),
  'complex_observation_rank':{'original':orig['complex_observation_rank'],'corrected':fixed['complex_observation_rank']},
  'median_nearest_abs_cosine_V_plus_I':{'original':orig['median_nearest_shape_similarity_both'],'corrected':fixed['median_nearest_shape_similarity_both']},
  'max_pairwise_abs_cosine_V_plus_I':{'original':orig['max_pairwise_shape_similarity_voltage_current'],'corrected':fixed['max_pairwise_shape_similarity_voltage_current']},
  'accuracy':{f'{n}x/{ch}':{'original':old[(n,ch)],'corrected':new[(n,ch)]} for n in (1,5,20) for ch in ('voltage','voltage+current')}}}
(ROOT/'results/validation_comparison.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
