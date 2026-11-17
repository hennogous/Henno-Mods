"""Run the preselected customer-placement comparisons with the shared controller.

This is serial orchestration, never gameplay policy or another console client.
Each existing fresh-game driver owns launch, normal Online play, observations,
exit and restoration. Both arms use integrated main CSC; only its frozen adapter
differs. Compare current tuning, not disabled tuning. Retire only exact duplicate
closed package archives and retain all outcomes, saves and immutable inputs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from driver import load,manifest,require,sha,write_json
from planning_results import parse

HERE=Path(__file__).resolve().parent


def qualify_gate(root):
    """Predetermined current-world combined-edge test; no fixture orders.

    Amount0 also removes the edge from Lua's positive-rule candidate graph.
    This is combined relationship-guidance ablation, not isolated SQL causality.
    Production coefficients/ordinary gameplay remain identical between arms.
    """
    proof=[]
    for amount,expected in((0,2377),(1,2227)):
        path=root/('magdeburg-sql'+str(amount)+'-150-155')
        complete,closed=load(path/'complete.json'),load(path/'session-closed.json')
        require(complete['verified']and complete['observation_qualified']and
                closed['verified']and closed['native_exit_code']==0,'Positive construction gate incomplete')
        protocol=load(path/'protocol.json')
        require(protocol['amount']==amount and protocol['start']==150 and protocol['through']==155,
                'Construction gate protocol differs')
        rows=[json.loads(s)for s in(path/'economy-savings.ndjson').read_text().splitlines()]
        choices=[r for r in rows if r['kind']=='district-selection'and r.get('player')==3
                 and r.get('city')==262144 and r['turn']==150]
        require(len(choices)==1 and choices[0]['district']==6 and choices[0]['plot']==expected,
                'Construction gate did not switch the predetermined close choice')
        physical=[r for r in parse((path/'Lua.log').read_text(encoding='utf-8-sig'),'CSC_PLANNING_')
                  if r['kind']=='FOUNDATION'and r.get('player')==3 and r.get('city')==262144
                  and r.get('district')==6 and r.get('plot')==expected and r.get('source')=='added']
        require(physical and physical[0]['turn']<=155,'Chosen footprint did not reach foundation')
        choice={key:choices[0][key]for key in('turn','player','city','district','plot','totalQ8','sequence')}
        proof.append(dict(amount=amount,choice=choice,foundation=physical[0],
                          complete_sha256=sha(path/'complete.json'),protocol_sha256=sha(path/'protocol.json')))
    require(load(root/'magdeburg-sql0-150-155/protocol.json')['checkpoint']==
            load(root/'magdeburg-sql1-150-155/protocol.json')['checkpoint'],'Gate save differs')
    return proof


def retire_duplicates(out):
    """After clean exit, remove named archives only against retained sources."""
    require(load(out/'session-closed.json')['verified'],'Never retire a live package')
    before=shutil.disk_usage(out).free;retired=[]
    for source,row in load(out/'packages.json').items():
        keeper=Path(source).resolve(strict=True)
        target=(out/Path(row['install']).name).resolve()
        if not target.exists():continue
        require(target.parent==out.resolve()and target.name in
                ('CSC Bakers Development CE','CSC Bakers Development Mod'),'Unexpected package archive')
        require(not keeper.is_relative_to(target),'Archive is its own retained source')
        require(not any(p.is_symlink()or getattr(p,'is_junction',lambda:False)()
                       for p in[target,*target.rglob('*')]),'Archive has a link/junction')
        if manifest(target)!=row['files']or manifest(keeper)!=row['files']:continue
        retired.append(dict(path=str(target),keeper=str(keeper),
                            logical_bytes=sum(p.stat().st_size for p in target.rglob('*')if p.is_file())))
        shutil.rmtree(target)
    ledger=out/'storage-retirement.json'
    if ledger.exists():
        if not retired:return
        ledger=next(out/('storage-retirement-'+str(n)+'.json')for n in range(2,1000)
                    if not(out/('storage-retirement-'+str(n)+'.json')).exists())
    write_json(ledger,dict(retired=retired,free_before_bytes=before,
        free_after_bytes=shutil.disk_usage(out).free,scope='Exact duplicate closed package copies only'))


def run(root):
    root=Path(root).resolve(strict=True);plan=load(root/'plan.json');source=Path(plan['source'])
    gate=qualify_gate(root)
    control,candidate=Path(plan['baseline_package']),Path(plan['candidate_package'])
    ca,cb=manifest(control),manifest(candidate)
    changes=[p for p in set(ca)|set(cb)if ca.get(p)!=cb.get(p)]
    require(len(changes)==1 and changes[0].replace('\\','/')=='Lua_UI/AI/CSC_AI_EconomyAdapters.lua',
            'Freeze differs outside the reviewed adapter')
    require(sha(candidate/'Lua_UI/AI/CSC_AI_EconomyAdapters.lua')==plan['adapter_sha256'],'Candidate changed')
    packages=load(source/'packages.json');ce=next(Path(p)for p in packages if(Path(p)/'Binaries').is_dir())
    require(ca==packages[str(control)]['files'],'Original comparison control changed')
    ce_files=manifest(ce)
    require(ce_files==packages[str(ce)]['files'],'Original qualified CE package changed')
    ce_dll,=(ce/'Binaries/Win64').glob('GameCore_XP2_CE*.dll')
    proof=load(root/'buffalo-pairs150-160-02/loaded-modules.json')
    require(sha(ce_dll)==proof[ce_dll.name]['sha256'],'Qualified CE changed')
    extras=load(source/'extra-mods.json')
    for item in extras.values():require(manifest(Path(item['path']))==item['files'],'Optional content changed')
    frozen=dict(packages={str(control):ca,str(candidate):cb,str(ce):ce_files},extras=extras,
                plan_sha256=sha(root/'plan.json'))
    frozen_digest=hashlib.sha256(json.dumps(frozen,sort_keys=True).encode()).hexdigest()
    campaign=root/'final-comparisons';campaign.mkdir(exist_ok=True)
    state=dict(schema='csc-customer-campaign-v1',preselected_worlds=plan['fresh_games'],
        gate=gate,control=str(control),candidate=str(candidate),changes=changes,
        ce_sha256=sha(ce_dll),frozen_inputs_sha256=frozen_digest,completed=[],active=None)
    if(campaign/'campaign-progress.json').exists():
        previous=load(campaign/'campaign-progress.json')
        require(previous.get('frozen_inputs_sha256')==frozen_digest,'Resumed campaign inputs differ')
        require(load(campaign/'frozen-inputs.json')==frozen,'Resumed campaign manifests differ')
        state=previous
    else:
        require(not any(campaign.iterdir()),'Existing unqualified campaign output requires reconciliation')
        write_json(campaign/'frozen-inputs.json',frozen)
        write_json(campaign/'campaign-progress.json',state)
    mods=Path(packages[str(ce)]['install']).parent
    user_root=Path(load(source/'resource-stack-preflight.json')['database']).parent.parent
    for world in plan['fresh_games']:
        for arm,csc in(('control',control),('treatment',candidate)):
            out=campaign/(world['map'].lower()+'-'+arm+'250')
            require(shutil.disk_usage(root).free>=10*2**30,'Insufficient free disk for next game')
            for path,files in frozen['packages'].items():require(manifest(Path(path))==files,'Frozen package drift before child')
            for item in extras.values():require(manifest(Path(item['path']))==item['files'],'Optional content drift before child')
            command=[sys.executable,str(HERE/'ce_bakers_fresh.py'),'--output',str(out),
                '--mods',str(mods),'--user-root',str(user_root),'--main-mod-package',
                '--binary',load(source/'session-owner.json')['executable_path'],
                '--ce',str(ce),'--csc',str(csc),'--ce-sha256',sha(ce_dll),
                '--map',world['map'],'--map-seed',str(world['map_seed']),'--game-seed',str(world['game_seed']),
                '--through','250','--interval-minutes','15','--saves',str(mods.parent/'Saves/Single'),
                '--harmonised-observation','--planning-observation','--economy-preflight',
                '--savings-dependencies',str(root.parent/'csc-ce-ai-tooling-probe-20261028/dependencies')]
            reference=campaign/(world['map'].lower()+'-control250/source.json')if arm=='treatment'else(
                source/'source.json'if world['map']=='Continents'else None)
            if reference:command+=['--reference-source',str(reference)]
            for item in extras.values():command+=['--extra-mod',item['path']]
            state['active']=dict(map=world['map'],arm=arm,output=str(out),started=time.time(),
                free_bytes=shutil.disk_usage(root).free)
            write_json(campaign/'campaign-progress.json',state)
            if not out.exists():
                with(campaign/(out.name+'-console.txt')).open('w',encoding='utf-8')as console:
                    result=subprocess.run(command,stdout=console,stderr=subprocess.STDOUT)
                if result.returncode:
                    state['failure']=dict(output=str(out),exit_code=result.returncode)
                    write_json(campaign/'campaign-progress.json',state);raise RuntimeError('Campaign child failed; preserve its session')
            # A restart may reuse a fully closed/qualified child and repeat only
            # offline analysis. Existing partial/live outcomes require explicit
            # reconciliation; never overwrite them or silently launch again.
            require((out/'session-closed.json').exists()and(out/'result.json').exists()
                    and(out/'full-game-observation-complete.json').exists(),
                    'Existing child is partial/live; reconcile it before resuming')
            require(load(out/'session-closed.json')['verified']and load(out/'result.json')['reached']==250,
                    'Campaign child lacks a clean250 outcome')
            require(load(out/'full-game-observation-complete.json')['verified'],'Child observation unqualified')
            watcher=load(out/'economy-savings-frozen.json')
            require(watcher['frozen']and watcher['active']==0 and not(watcher['faults']or watcher['stopReason'])
                    and not load(out/'economy-savings-messages.json'),'Child native capture unqualified')
            expected={str(ce):ce_files,str(csc):ca if arm=='control'else cb}
            actual=load(out/'packages.json')
            require(set(actual)==set(expected)and all(actual[p]['files']==files for p,files in expected.items()),
                    'Child package manifest differs from campaign freeze')
            require(load(out/'extra-mods.json')==extras,'Child optional manifests differ from campaign freeze')
            timing=load(out/'ai-processing-time.json')
            require(not(timing['unobserved_turns']or timing['missing_wall_attempts']or timing['failed_attempts']),
                    'Guidance timing coverage incomplete')
            # Analysis stays outside native ownership. The existing driver's
            # closed observation already writes planning/timing summaries.
            from customer_coordination_results import analyse as connections
            from customer_opportunity_results import analyse as opportunities
            from planning_results import analyse as chronology
            chronology(out)
            write_json(out/'customer-coordination-results.json',connections(out))
            write_json(out/'customer-opportunity-results.json',opportunities(out))
            retire_duplicates(out)
            if not any(r['map']==world['map']and r['arm']==arm for r in state['completed']):
                state['completed'].append(dict(map=world['map'],arm=arm,output=str(out),finished=time.time()))
            state.pop('failure',None)
            state['active']=None;write_json(campaign/'campaign-progress.json',state)
    write_json(campaign/'complete.json',dict(verified=True,games=state['completed']))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True)
    run(parser.parse_args().root)
