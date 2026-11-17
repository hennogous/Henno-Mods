"""Run three preselected normal games serially with the shared controller.

Each child owns its complete launch-to-restoration lifecycle. Stop on any
failure; never overlap native ownership or continue after incomplete telemetry.
This runner adds no gameplay policy and never opens its own console connection.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
SEEDS=(('Continents',18461107,29461107),('Pangaea',18431267,28681391),
       ('Fractal',19672039,29812257))


def main(root,*,frozen=None,ce_sha=None,policy_qualification=None):
    root=Path(root).resolve(strict=True)
    frozen=Path(frozen).resolve(strict=True)if frozen else root/'frozen02'
    ce_sha=ce_sha or '400e675522916ce54a17a6765132da89ee23c90304a89e721c6289c31327394f'
    proxy,=(frozen/'CE/Binaries/Win64').glob('GameCore_XP2_CE*.dll')
    if hashlib.sha256(proxy.read_bytes()).hexdigest()!=ce_sha:
        raise ValueError('Frozen CE hash does not match the qualified build')
    mods=Path("C:/Users/Shadow/Documents/My Games/Sid Meier's Civilization VI/Mods")
    workshop=Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/289070')
    args=[sys.executable,str(HERE/'ce_bakers_fresh.py'),
        '--mods',str(mods),'--user-root',"C:/Users/Shadow/AppData/Local/Firaxis Games/Sid Meier's Civilization VI",
        '--binary',"C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI/Base/Binaries/Win64Steam/CivilizationVI.exe",
        '--ce',str(frozen/'CE'),'--csc',str(frozen/'CSC'),
        '--ce-sha256',ce_sha,
        '--through','250','--interval-minutes','15',
        '--saves',str(mods.parent/'Saves/Single'),'--harmonised-observation',
        '--planning-observation','--economy-preflight','--savings-dependencies',
        'C:/Users/Shadow/Desktop/Codex/csc-ce-ai-tooling-probe-20261028/dependencies']
    for folder in ('2190389813','1369684991','1150492115'):
        args+=['--extra-mod',str(workshop/folder)]
    state=dict(seeds=SEEDS,completed=[],active=None,frozen=str(frozen),ce_sha256=ce_sha,
               policy_qualification=str(policy_qualification)if policy_qualification else None)
    def record():
        path=root/'campaign-progress.json';tmp=path.with_suffix('.tmp')
        tmp.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
    if policy_qualification:
        # Current economic integration reuses the previously qualified full-game
        # observer/controller. Its new model is checked on a mature zero-turn
        # world, never enabled as a second policy during outcome games.
        smoke=Path(policy_qualification).resolve(strict=True)
        closed=json.loads((smoke/'session-closed.json').read_text(encoding='utf-8'))
        policy=json.loads((smoke/'integrated-economy/result.json').read_text(encoding='utf-8'))
        protocol=json.loads((smoke/'protocol.json').read_text(encoding='utf-8'))
        if (not closed['verified']or closed['native_exit_code']or not policy['verified']
                or protocol['ce_overlay_sha256']!=ce_sha
                or any(row.get('wallMicros',-1)<0 for p in policy['players']for row in p['rows'])):
            raise ValueError('Economic policy qualification lacks clean closure or precise timing')
    else:
        # Preserve the older campaign's short savings/payment qualification.
        smoke=root/'smoke50-03'
        if not (smoke/'full-game-observation-complete.json').is_file():
            raise ValueError('Short observer qualification must finish first')
        closed=json.loads((smoke/'session-closed.json').read_text(encoding='utf-8'))
        savings=json.loads((smoke/'economy-savings-frozen.json').read_text(encoding='utf-8'))
        if (not closed['verified']or not savings['frozen']or savings['faults']or savings['active']
                or not savings['totals']['targetedSavings']or not savings['totals']['commandDebits']):
            raise ValueError('Short qualification lacks clean restoration or actual savings/payment observations')
    for name,map_seed,game_seed in SEEDS:
        output=root/(name.lower()+'250-01')
        if output.exists():raise ValueError('Fresh campaign outputs required')
        state['active']=name;record()
        command=args+['--output',str(output),'--map',name,'--map-seed',str(map_seed),'--game-seed',str(game_seed)]
        with (root/(name.lower()+'250-01-console.txt')).open('w',encoding='utf-8')as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:
            state['failure']=dict(map=name,exit_code=result.returncode);record()
            raise RuntimeError('Campaign stopped after failed '+name+' run')
        if policy_qualification:
            timing=json.loads((output/'ai-processing-time.json').read_text(encoding='utf-8'))
            clock=json.loads((output/'economy-preflight.json').read_text(encoding='utf-8'))
            if (not clock.get('profiling_clock')or timing['missing_wall_attempts']
                    or timing['unobserved_turns']or timing['failed_attempts']):
                state['failure']=dict(map=name,timing_coverage=timing);record()
                raise RuntimeError('Campaign stopped for missing or failed ordinary guidance timing')
        state['completed'].append(name);state['active']=None;record()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--frozen',type=Path)
    parser.add_argument('--ce-sha')
    parser.add_argument('--policy-qualification',type=Path)
    main(**vars(parser.parse_args()))
