"""Finish the same preselected campaign after its recorded Pangaea interruption.

No game interface lives here. Child drivers own their complete shared-controller
sessions. Continue the verified200 save, then run the still-unplayed Fractal
seed. The abandoned205 branch and all errors remain archived and labelled.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from planning_continue import prepare

HERE=Path(__file__).resolve().parent


def main(root,dependencies):
    root=Path(root).resolve(strict=True)
    state=json.loads((root/'campaign-progress.json').read_text(encoding='utf-8'))
    if state['completed']!=['Continents']or state.get('failure',{}).get('map')!='Pangaea':
        raise ValueError('Require the recorded first-arm success and interrupted Pangaea')
    # Every failed attempt stays in place. A reviewed, explicit rerun selects a
    # new folder; this is not an automatic retry loop after a child failure.
    recovery=next(root/('pangaea250-recovery200-'+str(n).zfill(2))for n in range(1,100)
                  if not(root/('pangaea250-recovery200-'+str(n).zfill(2))).exists())
    plan=prepare(root/'pangaea250-01',recovery,200,250,Path(dependencies))
    def record():
        path=root/'campaign-progress.json';tmp=path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
    def execute(command,name):
        with (root/name).open('w',encoding='utf-8')as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:
            state['failure']=dict(map=state['active'],exit_code=result.returncode);record()
            raise RuntimeError('Recovered campaign stopped after '+state['active'])
    state.setdefault('interrupted_attempts',[]).append(dict(map='Pangaea',path=str(plan.source),
        last_boundary=205,resume_at=200,reason='Observer spy-warning conversation blocked finite autoplay'))
    state.pop('failure');state.update(active='Pangaea',active_segment=str(recovery));record()
    execute([sys.executable,str(HERE/'planning_continue.py'),'--source',str(plan.source),
        '--output',str(recovery),'--at','200','--through','250','--dependencies',str(plan.dependencies)],
        recovery.name+'-console.txt')
    state['completed'].append('Pangaea');state.update(active='Fractal',active_segment=None);record()
    by_role={p['role']:p for p in plan.packages}
    command=[sys.executable,str(HERE/'ce_bakers_fresh.py'),'--output',str(root/'fractal250-01'),
        '--mods',str(by_role['ce']['install'].parent),'--user-root',str(plan.user_root),
        '--binary',str(plan.binary),'--ce',str(by_role['ce']['source']),'--csc',str(by_role['csc']['source']),
        '--ce-sha256','400e675522916ce54a17a6765132da89ee23c90304a89e721c6289c31327394f',
        '--map','Fractal','--map-seed','19672039','--game-seed','29812257',
        '--through','250','--interval-minutes','15','--saves',str(plan.saves),
        '--harmonised-observation','--planning-observation','--economy-preflight',
        '--savings-dependencies',str(plan.dependencies)]
    for item in plan.extras.values():command+=['--extra-mod',item['path']]
    execute(command,'fractal250-01-console.txt')
    state['completed'].append('Fractal');state['active']=None;record()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--dependencies',type=Path,required=True)
    args=parser.parse_args();main(args.root,args.dependencies)
