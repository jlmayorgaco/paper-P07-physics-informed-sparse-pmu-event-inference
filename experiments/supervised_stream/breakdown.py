"""Give per-record bootstrap intervals and episode-level breakdowns without changing decisions."""
import json
import numpy as np
import pandas as pd
from larger import OUT, STORE
from plant import FS



def confusion_plot(matrix):
    import matplotlib.pyplot as plt
    labels=["Normal","Falla","Línea","Generación","Carga","Datos ausentes",
            "Generación + ausencia","Datos sesgados","Pulso compuesto"]
    ratios=matrix/matrix.sum(axis=1,keepdims=True)
    fig,ax=plt.subplots(figsize=(8.5,6.3),layout="constrained")
    show=ax.imshow(ratios,vmin=0,vmax=1,cmap="Blues")
    ax.set_xticks(range(9),labels,rotation=40,ha="right")
    ax.set_yticks(range(9),labels)
    ax.set_xlabel("Clase anunciada")
    ax.set_ylabel("Clase verdadera")
    ax.set_title("Prueba ciega de 900 trayectorias")
    for i,j in np.ndindex(matrix.shape):
        if matrix[i,j]:
            ax.text(j,i,str(matrix[i,j]),ha="center",va="center",
                    color="white" if ratios[i,j]>.55 else "black")
    fig.colorbar(show,ax=ax,shrink=.8,label="Fracción de cada fila")
    fig.savefig(OUT/"confusion.png",dpi=160)
    plt.close(fig)

def main():
    ledger=pd.read_csv(OUT/"event_ledger.csv")
    truth=json.loads((OUT/"test_truth.json").read_text())
    preds=json.loads((OUT/"predictions.json").read_text())
    counts=np.zeros((len(truth),9,9),int)
    for row in ledger.itertuples():
        counts[row.record,row.true_class,row.pred_class]+=1
    for i,(events,alarms) in enumerate(zip(truth,preds)):
        occupied={frame//FS for e in events for frame in range(e["onset"],e["end"])}
        occupied.update(a["published"]//FS for a in alarms)
        counts[i,0,0]=24-len(occupied)
    score=json.loads((OUT/"scores.json").read_text())
    assert np.array_equal(counts.sum(axis=0),score["confusion"])
    confusion_plot(counts.sum(axis=0))
    rng=np.random.default_rng(41197)
    weights=rng.multinomial(len(truth),np.full(len(truth),1/len(truth)),size=3000)
    cm=(weights@counts.reshape(len(truth),-1)).reshape(-1,9,9)
    f1=(2*np.diagonal(cm,axis1=1,axis2=2)/np.maximum(1,cm.sum(axis=1)+cm.sum(axis=2))).mean(axis=1)
    fam=np.diagonal(cm,axis1=1,axis2=2)[:,1:].sum(1)/cm[:,1:].sum(axis=(1,2))
    events=ledger.query('true_class>0').copy()
    events['order']=events.groupby('record').cumcount()+1
    results={}
    for k,g in events.groupby('order'):
        results[int(k)]=dict(n=len(g),joint=int(((g.true_class==g.pred_class)&(g.true_site==g.pred_site)).sum()))
    details=dict(macro_f1_ci=np.quantile(f1,[.025,.975]).tolist(),family_ci=np.quantile(fam,[.025,.975]).tolist(),
                 by_event_position=results,quiet_minutes=sum(not x for x in truth)*24/60)
    (OUT/"breakdown.json").write_text(json.dumps(details,indent=2))
    print(details)


if __name__=="__main__":
    main()
