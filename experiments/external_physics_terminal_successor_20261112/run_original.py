"""Physics-only, STATIC AC linear-circuit screening experiment on public MATPOWER case39.
Explicitly NOT a reproduction of the dynamic DAE/historical source attribution paper.
No genuine PMU measurements are available. Everything scored is synthetic.
"""
from pathlib import Path
import json, csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from case39_data import BRANCH,BUS,PMU,LOADS,LINES

OUT=Path(__file__).resolve().parent/'original_results'; OUT.mkdir(exist_ok=True)
SEED=261112
rng=np.random.default_rng(SEED)
PAIRED_NOISE=rng.standard_normal((18,150,32))
N=39
V0=BUS[:,3]*np.exp(1j*np.deg2rad(BUS[:,4]))

def admittance(branch):
    Y=np.zeros((N,N),complex)
    Yterm=np.zeros((len(branch),N),complex)
    for r,(ii,jj,R,X,B,tap) in enumerate(branch):
        i,j=int(ii)-1,int(jj)-1
        y=1/(R+1j*X); a=tap if tap else 1.
        # complex tap phase=0 for case39; full pi model with half charging
        Y[i,i]+=(y+1j*B/2)/a**2
        Y[j,j]+=y+1j*B/2
        Y[i,j]+=-y/a;Y[j,i]+=-y/a
        Yterm[r,i]=(y+1j*B/2)/a**2
        Yterm[r,j]=-y/a
    return Y,Yterm
Y0,Yterm0=admittance(BRANCH)
j0=Y0@V0
# Explicit stabilized model: all injections are held as constant current on event;
# no nonlinear constant-power power-flow and no generator dynamics.
# Synthetic terminal-current channel: first deterministic incident FROM branch or TO branch
# with measured orientation as a branch-end current; NOT the real competition mapping.
def terminals(V, branch=BRANCH):
    pairs=[]
    for pm in PMU:
        ix=next(k for k,x in enumerate(branch) if int(x[0])-1==pm or int(x[1])-1==pm)
        pairs.append(ix)
    # For unique complete-case rows same fixed indices across line-opening models
    Y,Yfrom=admittance(branch)
    return pairs,Yfrom
sel, T0=terminals(V0)

def branch_voltage_current_response(new_v,branch):
    _,Ti=admittance(branch)
    currents=np.zeros(len(PMU),complex)
    for z,pm in enumerate(PMU):
        r=sel[z]
        # same branch index, but report removed terminal current as zero if branch opened
        if r>=len(branch) or not np.array_equal(BRANCH[r,:2],branch[r,:2]):
            # choose by endpoint pair; if original branch removed, value=0
            matching=[k for k,x in enumerate(branch) if tuple(x[:2])==tuple(BRANCH[r,:2])]
            if matching: currents[z]=Ti[matching[0]]@new_v
        else:currents[z]=Ti[r]@new_v
    return currents

baseI=branch_voltage_current_response(V0,BRANCH)
# current power source proxy for loads: deltaI=-conj(deltaS/V0); 10% P/Q change.
sources=[]; signatures=[]; full_dv=[]
for bus in LOADS:
    i=bus-1
    injection=np.zeros(N,complex)
    dS=.10*(BUS[i,1]+1j*BUS[i,2])/100
    injection[i]=-np.conj(dS/V0[i])
    Vnew=np.linalg.solve(Y0,j0+injection)
    Inew=branch_voltage_current_response(Vnew,BRANCH)
    sources.append(f'LOAD {bus}')
    signatures.append(np.r_[Vnew[PMU]-V0[PMU], Inew-baseI])
    full_dv.append(Vnew-V0)
for pair in LINES:
    idx=next(k for k,v in enumerate(BRANCH) if tuple(map(int,v[:2]))==pair)
    newbranch=np.delete(BRANCH,idx,axis=0)
    Y1,_=admittance(newbranch)
    Vnew=np.linalg.solve(Y1,j0)
    Inew=branch_voltage_current_response(Vnew,newbranch)
    sources.append(f'LINE {pair[0]}-{pair[1]}')
    signatures.append(np.r_[Vnew[PMU]-V0[PMU],Inew-baseI])
    full_dv.append(Vnew-V0)
S=np.array(signatures);DV=np.array(full_dv)
# One fixed source-aware scale for each complex coordinate. noise is synthetic,
# with sd magnitude chosen as a FRACTION OF EACH BASELINE MAGNITUDE, subject to floor.
# Current sensors have a different scale; baseline zeros are floored to avoid infinite SNR.
sdV=np.full(len(PMU), .002)
sdI=np.maximum(.002,np.abs(baseI)*.002)
sd=np.r_[sdV,sdI]

# Group labels, pairwise scalar severity profiled for comparison, including same-source ratio.
# For line fixed switch effect (no amplitude fit), but to evaluate pure spatial identifiability
# all 18 signatures are normalized; this is a conservative shape-only test independent of magnitude.
def profile_matrix(ids, whiten_sd=sd):
    X=np.concatenate((S[:,ids].real/whiten_sd[ids],S[:,ids].imag/whiten_sd[ids]),axis=1)
    norm=np.linalg.norm(X,axis=1)
    Z=X/np.maximum(norm[:,None],1e-15)
    # full signed amplitude profiling, allowing sign reversal; ambiguity is |cosine|
    abs_cos=np.abs(Z@Z.T)
    np.fill_diagonal(abs_cos,np.nan)
    return X,norm,abs_cos
Xv,Nv,Cv=profile_matrix(np.arange(8))
Xvi,Nvi,Cvi=profile_matrix(np.arange(16))
# Pooled low-level experiment: each sample generated from same known network model.
# Compare voltage alone vs voltage+synthetic terminal currents; no calibration to real PMU.
def classify(keep,noise_level=1.,drop=None, trials=100):
    ids=np.arange(8 if keep=='voltage' else 16)
    if drop is not None:
        ids=np.array([i for i in ids if i%8!=drop])
    x,n,_=profile_matrix(ids,sd*noise_level)
    samples=0; correct=0; confusion=np.zeros((18,18),int)
    # amplitude is known for this *shape-only* test? profile over real scalar coefficient.
    # choose unit *signal*, do GLR with unknown signed real amplitude and nonnegative gain.
    for c in range(18):
        target=x[c]
        for trial in range(trials):
            paired_indices=np.r_[ids,ids+16]
            y=target + PAIRED_NOISE[c,trial,paired_indices]
            # maximize generalized likelihood ratio under unbounded real amplitude
            score=(x@y)**2/np.maximum(np.einsum('ij,ij->i',x,x),1e-15)
            pred=int(np.argmax(score)); confusion[c,pred]+=1
            correct+=pred==c; samples+=1
    return correct/samples,confusion

rows=[]
for nscale in [1,5,20]:
    for observation in ['voltage','voltage+current']:
        acc,conf=classify('voltage' if observation=='voltage' else 'both',nscale,trials=150)
        rows.append({'noise_multiplier':nscale,'channels':observation,'accuracy':round(acc,4),'n_synthetic':int(conf.sum())})
for d in range(8):
    acc,_=classify('both',1.,drop=d,trials=150)
    rows.append({'noise_multiplier':1,'channels':f'voltage+current minus PMU {PMU[d]+1}','accuracy':round(acc,4),'n_synthetic':2700})

near=[]
for C,kind in [(Cv,'voltage'),(Cvi,'voltage+current')]:
    for i in range(18):
        j=np.nanargmax(C[i])
        near.append({'channels':kind,'source':sources[i],'nearest_source':sources[j],
                    'abs_profile_cosine':round(float(C[i,j]),6),
                    'sin_angle':round(float(np.sqrt(max(0,1-C[i,j]**2))),6)})
# rank and conditional uncertainty of recovering 39 states from sensor outputs
# fixed-topology linear map H from all states to first-terminal currents and bus voltages
H=np.vstack([np.eye(N,dtype=complex)[PMU],T0[sel]])
rank=int(np.linalg.matrix_rank(H))
# condition hypothetical known current sources: if model correct, full states from Y solve;
# if current injections unknown, there are N-rank ambiguous complex directions.

with open(OUT/'noise_accuracy.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with open(OUT/'nearest_competitors.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(near[0]));w.writeheader();w.writerows(near)
with open(OUT/'catalog_signatures.npz','wb') as f:
 np.savez_compressed(f,sources=np.array(sources),signatures=S,voltage_39=DV,pmu=PMU+1,baseV=V0,
                     current_terminal_proxy=sel,sd=sd)

plt.figure(figsize=(10,7))
plt.imshow(Cvi,vmin=0,vmax=1,cmap='viridis')
plt.xticks(range(18),sources,rotation=90,fontsize=8)
plt.yticks(range(18),sources,fontsize=8)
plt.title('Absolute similarity of physical response signatures\npublic IEEE-39 topology; static synthetic circuit (not dynamic PMU data)')
plt.colorbar(label='|cosine| after amplitude normalization')
plt.tight_layout();plt.savefig(OUT/'signature_similarity.png',dpi=165);plt.close()
plt.figure(figsize=(10,4.5))
plt.plot(range(1,40),np.abs(DV[LOADS.index(24)]),marker='.',label='Load at bus 24')
plt.scatter(PMU+1,np.abs(DV[LOADS.index(24),PMU]),marker='x',s=75,label='Observed PMU bus positions')
plt.xlabel('Bus');plt.ylabel('Predicted |delta V| (p.u.)')
plt.title('Predicted impact, conditional on static known current source (10% load)')
plt.legend();plt.tight_layout();plt.savefig(OUT/'hidden_bus_impact.png',dpi=165);plt.close()
summary={'model':'PUBLIC MATPOWER case39 static pi-network/constant-current-injection idealization; NOT a DAE, not SGSMA data',
         'buses':39,'branches':46,'pmu_buses':(PMU+1).tolist(),'hypotheses':len(sources),
         'complex_observation_rank':rank,'complex_unobservable_dimension_lower_bound':39-rank,
         'max_pairwise_shape_similarity_voltage':float(np.nanmax(Cv)),
         'max_pairwise_shape_similarity_voltage_current':float(np.nanmax(Cvi)),
         'median_nearest_shape_similarity_voltage':float(np.nanmedian(np.nanmax(np.where(np.eye(18,dtype=bool),-1,Cv),axis=1))),
         'median_nearest_shape_similarity_both':float(np.nanmedian(np.nanmax(np.where(np.eye(18,dtype=bool),-1,Cvi),axis=1))),
         'noise_accuracy':rows,
         'limitations':['Same linear network generates data and templates: favorable same-model test',
          'No generator dynamics, restoration, frequency/ROCOF, PMU measurement filters, or time-series',
          'Current terminal mapping is a transparent deterministic proxy, not competition mapping',
          'True plant uses constant-power/ZIP loads, not constant-current injection',
          'Current noise levels chosen hypothetically; no calibration to real PMUs',
          'Full bus responses derived from a fully known model, not uniquely inferred from PMUs alone']}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='noise_accuracy' and k!='limitations'},indent=2))
for x in rows:print(x)
print('Most confusable pairs:')
for x in sorted([z for z in near if z['channels']=='voltage+current'],key=lambda z:-z['abs_profile_cosine'])[:8]:print(x)

