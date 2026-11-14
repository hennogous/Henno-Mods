"""Run the three preselected no-CSC controls serially, stopping on a failure.

No game commands live here. Each child owns a complete shared-controller session
and exact preference restoration. Seeds/cohorts come from the completed treated
sources before any control outcomes are observed; no outcome-based retries.
"""
import argparse
from pathlib import Path
import subprocess
import sys
from driver import load,require,write_json
from vanilla_district_run import prepare


def run(args):
    root=args.output.resolve(strict=True);treated=args.treated.resolve(strict=True)
    state_path=root/'campaign-progress.json'
    require(not state_path.exists(),'A campaign already exists; review its state before resuming')
    sources=[('Continents','continents250-01'),('Pangaea','pangaea250-01'),('Fractal','fractal250-01')]
    plans=[]
    # Qualify all package/source identities first, including the interrupted
    # Pangaea parent. Its matched outcome is the explicitly segmented derivative.
    for name,folder in sources:
        p=prepare(treated/folder,root/(name.lower()+'250-01'))
        plans.append((name,p))
    state=dict(csc_enabled=False,completed=[],active=None,seeds=[dict(map=name,
        map_seed=p.protocol['map_seed'],game_seed=p.protocol['game_seed'],
        matched_source=str(p.source),output=str(p.out))for name,p in plans])
    write_json(state_path,state)
    for name,p in plans:
        state['active']=name;write_json(state_path,state)
        with (root/(p.out.name+'-console.txt')).open('w',encoding='utf-8')as stream:
            child=subprocess.run([sys.executable,str(Path(__file__).with_name('vanilla_district_run.py')),
                '--source',str(p.source),'--output',str(p.out),'--dependencies',str(args.dependencies),
                '--through','250'],stdout=stream,stderr=subprocess.STDOUT)
        if child.returncode:
            state['failure']=dict(map=name,exit_code=child.returncode);write_json(state_path,state)
            raise RuntimeError('No-CSC campaign stopped; inspect '+str(p.out))
        require(load(p.out/'session-closed.json')['verified'],'Child did not close cleanly')
        state['completed'].append(name);state['active']=None;write_json(state_path,state)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('output','treated','dependencies'):parser.add_argument('--'+name,type=Path,required=True)
    run(parser.parse_args())
