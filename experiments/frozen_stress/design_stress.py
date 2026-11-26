"""Registered common-random-number design for frozen model stress testing."""
from dataclasses import dataclass
from pathlib import Path
import itertools
import csv
import os
import sys
import networkx as nx
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"joint_pmu"))
import cohort_joint as c

DATA=c.ROOT/"tmp/frozen_stress"
RESULT=HERE/"results"
SEED=41572081
BLOCKS=3
QUIET=48


@dataclass(frozen=True)
class Condition:
    name:str
    load:float=1.
    outages:int=0
    timing:str="reference"


CONDITIONS=[Condition("reference"),Condition("topo1",outages=1),Condition("topo2",outages=2)]
CONDITIONS += [Condition("load"+str(pc).replace(".","p"),load=pc/100)
               for pc in (99.5,99,98,95,90,80,100.5,101,102,105,110,115)]
CONDITIONS += [Condition(t,timing=t) for t in ("gap30","gap15","gap6","gap0","over10","over25","over50","synchronous")]
CONDITIONS += [Condition("combined",load=1.1,outages=1,timing="over25")]


def cases():
    rng=np.random.default_rng(SEED)
    sites=c.load(c.RESULT/"test_manifest.json")["sites"]
    sites={int(k):v for k,v in sites.items()}
    pools={k:[] for k in sites}
    with (Path(os.environ["P07_SCIENCE_ARCHIVE"])/"data/topology/ieee39/branches_physical.csv").open() as f:
        graph=nx.Graph((int(r["from_bus"]),int(r["to_bus"])) for r in csv.DictReader(f))
    families=[(i,) for i in sites]+list(itertools.product(sites,repeat=2))
    families+=list(itertools.product((1,2),(1,2),(3,4)))
    schedules=[[] for _ in range(QUIET)]
    for _ in range(BLOCKS):
        for pattern in families:
            row=[]
            start=int(rng.integers(65,241))
            for code in pattern:
                seen={e["source"] for e in row}
                def available(site):
                    if site in seen:
                        return False
                    if code!=2:
                        return True
                    changed=graph.copy()
                    names=[e["source"] for e in row if e["code"]==2]+[site]
                    changed.remove_edges_from(tuple(map(int,s[4:].split("-"))) for s in names)
                    return nx.is_connected(changed)
                if not any(available(s) for s in pools[code]):
                    pools[code]=list(rng.permutation(sites[code]))
                i=next(i for i,s in enumerate(pools[code]) if available(s))
                source=str(pools[code].pop(i))
                end=start+int(rng.integers(*c.SPANS[code]))
                row.append(dict(code=code,source=source,onset=start,end=end,
                                strength=float(rng.uniform(.7,1.3)),sensors=[2,5]))
                start=max(start+46,end+int(rng.integers(30,121)))
            schedules.append(row)
    return [schedules[i] for i in rng.permutation(len(schedules))]


def change_timing(events,timing):
    if timing=="reference" or len(events)<2:
        return events
    row=[events[0]]
    for event in events[1:]:
        last=row[-1]
        duration=event["end"]-event["onset"]
        if timing=="synchronous":
            onset=row[0]["onset"]
        elif timing.startswith("gap"):
            onset=last["end"]+int(timing[3:])
        else:
            overlap=max(1,round(min(duration,last["end"]-last["onset"])*int(timing[4:])/100))
            onset=last["end"]-overlap
        row.append(dict(event,onset=onset,end=onset+duration))
    return row
