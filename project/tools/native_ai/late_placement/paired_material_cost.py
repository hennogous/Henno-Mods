"""Time the Lua selector on real radius-three terrain patterns outside Civ.

A sample is one Quarter in one hypothetical city with both supplied and
unsupplied tiles. Native map reads and modifier updates are measured by
the separate matched game; the clock here covers the Lua choice only.
"""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from statistics import mean, median
from time import perf_counter_ns

from lupa.lua51 import LuaRuntime


def samples(world):
    plots={p['index']:p for p in world['plots']}
    bonus={r['type'] for r in world['resources'] if r['class']=='RESOURCECLASS_BONUS'}
    removable={f['type'] for f in world['features'] if f.get('removable')}
    clear={i for i,p in plots.items() if not (p['water'] or p['impassable'] or p.get('district'))
           and (not p.get('resource') or p['resource'] in bonus)
           and (not p.get('feature') or p['feature'] in removable or p['feature'].startswith('FEATURE_FLOODPLAINS'))}
    for quarter in ('BAKERS','TAILORS'):
        base={r['type'] for r in world['material_tags'] if r['tag']==f'CLASS_CSC_{quarter}_BASE'}
        for center in sorted(clear):
            if center%3:
                continue
            reach={center}
            for _ in range(3):
                reach.update({j for i in reach for j in plots[i]['neighbors']})
            rows=[]
            for i in sorted((reach&clear)-{center}):
                neighbors=[plots[j] for j in plots[i]['neighbors']]
                amount=sum(p.get('resource') in base and p['index']!=center for p in neighbors)
                counts=dict(Counter(p['terrain'] for p in neighbors))
                rows.append((i,amount,counts))
            if any(r[1] for r in rows) and any(not r[1] for r in rows):
                yield rows


def main(paths):
    vm=LuaRuntime()
    vm.execute("GameInfo={CSC_AdjacencyRules=function()return function()end end};print=function()end")
    vm.execute((Path(__file__).parent/'paired_material_layout.lua').read_text())
    prepare=vm.eval("""function(rows)
      for _,s in ipairs(rows) do
        s.materialTerrain=s.baseCount>0 and {base=true} or {}
        s.customerRank=0
        s.plot={GetIndex=function()return s.id end,IsHills=function()return false end,GetRiverCrossingCount=function()return 0 end}
      end
      local city={GetID=function()return 1 end}
      local profile={district={Index=1,DistrictType='TEST'}}
      return function()return pairPolicy.choose(rows,city,1,profile,1) end
    end""")
    elapsed=[]
    for path in paths:
        with gzip.open(path,'rt') as stream:
            world=json.load(stream)
        for rows in samples(world):
            data=[dict(id=i,baseCount=b,count=t) for i,b,t in rows]
            choose=prepare(vm.table_from(data,recursive=True))
            times=[]
            for _ in range(5):
                start=perf_counter_ns()
                choose()
                times.append((perf_counter_ns()-start)/1e6)
            elapsed.append(median(times))
    elapsed.sort()
    print(json.dumps(dict(reviews=len(elapsed),mean_ms=mean(elapsed),p95_ms=elapsed[int(.95*len(elapsed))],
                          maximum_ms=elapsed[-1],repeats_per_review=5)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('maps',nargs='+',type=Path)
    main(parser.parse_args().maps)
