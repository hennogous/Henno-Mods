"""Time the Lua fallback on recorded city reviews with two versus three terrain switches."""
import argparse
from collections import Counter
from contextlib import closing
import json
from pathlib import Path
import sqlite3
from statistics import mean, median
from time import perf_counter_ns

from lupa.lua51 import LuaRuntime
from floor_coverage import decode


def benchmark(log, database):
    vm = LuaRuntime()
    with closing(sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)) as db:
        keys=[r[0] for r in db.execute('SELECT TerrainType FROM Terrains WHERE NOT Water AND NOT Impassable ORDER BY 1')]
    vm.globals().terrainKeys = vm.table_from(keys)
    vm.execute('pairPolicy={}; landscape={}; function rank(s) return s.rank end; profile={district={Index=1,DistrictType="Q"}}')
    vm.execute(Path(__file__).with_name('split_floor_relief.lua').read_text())
    prepare=vm.eval("""function(owned,frontier)
        for _,s in ipairs(owned) do s.plot={GetIndex=function()return s.id end} end
        owned.frontierWeak=frontier
        return function(third)
            pairPolicy.thirdRelief=third
            return pairPolicy.splitRelief(owned,profile)
        end
    end""")
    times={False:[],True:[]}
    targets=Counter()
    cities=set()
    for line in log:
        _,sep,record=line.partition('CSC_LAYOUT_GEOMETRY\t')
        if not sep or len(line.rstrip('\r\n'))>=2047:
            continue
        turn,pid,cid,q,current,data=record.rstrip('\r\n').split('\t')
        sites=decode(data)
        if current!='-1' or not any(s.rank for s in sites) or not any(not s.rank for s in sites):
            continue
        owned=[dict(id=s.plot,rank=s.rank,count=s.counts) for s in sites if s.plot>=0]
        frontier=[dict(unknown=s.unknown,neighbors=sum(s.counts.values())+s.unknown,count=s.counts)
                  for s in sites if s.plot<0]
        pick=prepare(vm.table_from(owned,recursive=True),vm.table_from(frontier,recursive=True))
        for enabled in times:
            samples=[]
            for _ in range(7):
                start=perf_counter_ns()
                cue=pick(enabled)
                samples.append((perf_counter_ns()-start)/1e6)
            times[enabled].append(median(samples))
            if enabled and cue and cue['c']:
                targets[q,int(cue['target'])]+=1
                cities.add((pid,cid))
    return dict(reviews=len(times[False]),selector_ms={
        str(k):dict(mean=mean(v),peak=max(v)) for k,v in times.items()},
        extra_reviews=sum(targets.values()),extra_cities=len(cities),
        extra_targets={f'{q}/{plot}':n for (q,plot),n in targets.items()})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log',type=Path)
    parser.add_argument('gameplay_database',type=Path)
    args=parser.parse_args()
    with args.log.open(encoding='utf-8-sig',errors='replace') as stream:
        print(json.dumps(benchmark(stream,args.gameplay_database),indent=2))
