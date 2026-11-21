"""Independently check paired macro-F1, false alarms, and missed physical assets."""
from collections import Counter
from sklearn.metrics import f1_score
from robust import RESULT, study

CODE={"none":0,"line":2,"load":4}


def audit():
    summary=study.read(RESULT/"summary.json")
    truth=study.read(RESULT/"truth.json")
    calls=study.read(RESULT/"predictions.json")
    missed={}
    for panel,row in summary["primary"].items():
        keys=[k for k,t in truth.items() if t["panel"]==panel]
        missed[panel]={}
        for condition,counts in row.items():
            missed[panel][condition]={}
            for arm,expected in counts["arms"].items():
                target,pred=[],[]
                failures=Counter()
                false=detected=family=exact=early=0
                for k in keys:
                    t=truth[k]
                    decision=calls[k][condition][arm]
                    b,label=decision["alarm"],decision["label"]
                    target.append(CODE[t["family"]])
                    prediction=0
                    if t["on"] is None:
                        false+=b is not None
                        if b is not None:
                            prediction=CODE[label[0]] if label else -1
                    else:
                        first,last=[round(t[z]*60) for z in ("on","off")]
                        active=b is not None and first<=2*b<last
                        valid=active and 2*(b+29)<last
                        detected+=active
                        early+=int(b is not None and 2*b<first)
                        if valid:
                            prediction=CODE[label[0]] if label else -1
                        family+=int(valid and label is not None and label[0]==t["family"])
                        correct=valid and label==[t["family"],t["source"]]
                        exact+=int(correct)
                        if not correct:
                            failures[t["source"]]+=1
                    pred.append(prediction)
                assert abs(f1_score(target,pred,labels=[0,2,4],average="macro",zero_division=0)-expected["macro_f1"])<1e-12
                assert (false,detected,family,early)==tuple(expected[k] for k in ("control_alarm","detection","family","early"))
                if arm!="li_wang":
                    assert exact==expected["exact"]
                if arm=="graph":
                    missed[panel][condition]=dict(failures)
    if (RESULT/"source_errors.json").exists():
        assert study.read(RESULT/"source_errors.json")==missed
    else:
        study.save(RESULT/"source_errors.json",missed)
    print("All 48 primary rows match independent counting and sklearn macro-F1.")


if __name__=="__main__":
    audit()
