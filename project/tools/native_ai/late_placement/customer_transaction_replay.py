"""Saved-game main policy plus passive customer-score/forecast inspection.

The shared controller owns a <=25-turn replay and restores every package and
preference. Current model modules run in an isolated Lua environment for quotes;
they never replace the saved world's active policy or publish prototype bids.
All sampled building-cache IDs come from the actual loaded catalogue. An explicit
--policy-package may replace only the main CSC adapter for matched scheduling
tests; gameplay SQL, CE and the other policy modules must remain byte-identical.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace
import traceback

from planning_continue import prepare, enable, parse_census, compare_structure
from driver import (NativeSession, HeldProcess, make_probe_controller, native_inventory,
    launch, configure, flags, manifest, read, lua, sha, write_json, restore_preferences,
    require, archive_sources)
from ce_replay import DLL, HOTFIX_SHA, verify_modules
from ce_bakers_fresh import LOGS, package_identity
from economy_savings_watch import EconomySavingsWatch

HERE=Path(__file__).resolve().parent
AI=HERE.parents[3]/'Civ Supply Chains/Lua_UI/AI'


def policy_packages(plan, replacement):
    """Qualify a main-mod scheduling arm before installing or launching anything.

    Neither arm has a second policy writer. The normal imported adapter runs
    from CSC, and the lexical diagnostic modules below only read/quote facts.
    All non-adapter bytes, including SQL/private yield and CE, are fixed.
    """
    packages=[dict(item) for item in plan.packages]
    changes=[]
    if replacement is not None:
        replacement=Path(replacement).resolve(strict=True)
        item=next(row for row in packages if row['role']=='csc')
        require(package_identity(replacement)[0]==item['id'], 'Policy package identity differs')
        files=manifest(replacement)
        different=[key for key in set(files)|set(item['files']) if files.get(key)!=item['files'].get(key)]
        require(different and all(key.replace('\\','/')=='Lua_UI/AI/CSC_AI_EconomyAdapters.lua'
                                  for key in different), 'Only the scheduling adapter may differ')
        changes=sorted(different);item.update(source=replacement,files=files)
    return packages,changes


def query(cases):
    # Lexical bindings isolate module assignments without setfenv/loadstring.
    # Civ's Havok runtime omits setfenv even though offline Lua51 supplies it.
    # These modules contain no explicit _G assignment; each module's closures
    # capture the preceding private facts/model binding. Native/global readers
    # remain the original functions, and all three active policy tables survive.
    encoder=read(HERE/'economy_component_probe.lua').split('for _,target in ipairs(CSC_COMPONENT_TARGETS)do',1)[0]
    code=encoder[encoder.index('local function encode'):]
    code+='\nlocal function activeModuleTables()return CSC_AI_EconomyFacts,CSC_AI_EconomyModel,CSC_AI_EconomyAdapters end\n'
    code+='local activeModules={activeModuleTables()}\n'
    code+='local CSC_AI_EconomyFacts,CSC_AI_EconomyModel,CSC_AI_EconomyAdapters\n'
    for name in ('CSC_AI_EconomyFacts.lua','CSC_AI_EconomyModel.lua','CSC_AI_EconomyAdapters.lua'):
        source=read(AI/name)
        require(not re.search(r'\b_G\b',source),'Explicit global access requires isolation review')
        code+='\ndo\n'+source+'\nend\n'
    # The closure was compiled before the local shadows. It reads the active
    # global bindings without relying on _G, also absent in Civ's Havok runtime.
    code+='\nlocal afterModules={activeModuleTables()}\n'
    code+='assert(afterModules[1]==activeModules[1]and afterModules[2]==activeModules[2]and afterModules[3]==activeModules[3],"Active policy module replaced")\n'
    code+='local CSC_TRANSACTION_MODULES={CSC_AI_EconomyFacts=CSC_AI_EconomyFacts,CSC_AI_EconomyModel=CSC_AI_EconomyModel,CSC_AI_EconomyAdapters=CSC_AI_EconomyAdapters}\n'
    return code+'\nlocal CSC_TRANSACTION_CASES='+lua(cases)+'\n'+read(HERE/'customer_transaction_survey.lua')


def run(args):
    plan=prepare(args.source,args.output,args.at,args.at,args.dependencies,read_only=True)
    packages,policy_changes=policy_packages(plan,getattr(args,'policy_package',None))
    require(args.at<args.through<=args.at+25,'At most25 diagnostic turns')
    cases=args.case
    require(0<len(cases)<=8,'At most8 diagnostic cases')
    for case in cases:
        case[:4]=map(int,case[:4]);case[5]=int(case[5])
        require(case[0]in plan.identity['original_ai']and case[1]>0 and case[4]in('BAKERS','TAILORS'),
                'Invalid diagnostic case')
    targets=sorted({(c[0],c[1])for c in cases})
    require(not native_inventory(),'Preserve foreign Civ/Tuner session')
    out=plan.output;out.mkdir(parents=True)
    code=query(cases);(out/'diagnostic-query.lua').write_text(code,encoding='utf-8')
    pins={str(p.resolve()):sha(p)for p in [Path(__file__),HERE/'customer_transaction_survey.lua',
        HERE/'economy_savings_watch.py',HERE/'economy_savings_watch.js',
        *(AI/n for n in ('CSC_AI_EconomyFacts.lua','CSC_AI_EconomyModel.lua','CSC_AI_EconomyAdapters.lua'))]}
    write_json(out/'implementation-archive.json',archive_sources(pins,out/'implementation-version'))
    write_json(out/'protocol.json',dict(diagnostic=True,source=str(plan.source),at=args.at,through=args.through,
        cases=cases,targets=targets,checkpoint=plan.checkpoint,active_policy_unchanged=not policy_changes,
        policy_changes=policy_changes,main_csc_is_only_policy=True,
        sql_unchanged=True,services_in_prototype=False,prototype_publishes_bids=False))
    controller=make_probe_controller(out,user_root=plan.user_root)
    controller.study_endpoint=args.through;controller.autoplay_interval_seconds=900
    controller.allow_observer_warning_dismissal=controller.allow_observer_first_meet_dismissal=True
    controller.allow_observer_congress_review=True
    session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    copied=[];watch=None
    def verify():
        for i in copied:
            require(manifest(i['install'])==i['files']and manifest(i['source'])==i['files'],'Package changed')
        for i in plan.extras.values():require(manifest(Path(i['path']))==i['files'],'Optional package changed')
        require(all(sha(Path(p))==h for p,h in pins.items()),'Diagnostic implementation changed')
    def gate():
        raw=controller.cmd('CSC_ENDPOINT_PLAYERS='+lua(plan.identity['original_ai'])+
            '\nCSC_ENDPOINT_EXPECTED_TURN='+str(args.at)+'\n'+read(HERE/'full_game_census.lua'),
            'CSC_AI_BakersGameplay','customer-source-census')
        (out/'source-census.txt').write_text(raw,encoding='utf-8')
        proof=compare_structure(plan.expected_census,parse_census(raw,args.at))
        write_json(out/'source-structure-comparison.json',proof)
        require(proof['verified'],'Saved world differs from source');return True
    def survey():
        turn=controller.state_read('customer-survey-clock')['turn']
        raw=controller.cmd(code,'CSC_AI_BakersGameplay','customer-forecast-'+str(turn))
        (out/('survey-'+str(turn)+'.txt')).write_text(raw,encoding='utf-8')
        records=[json.loads(s)for s in re.findall(r'CSC_TRANSACTION_RECORD=([^\r\n]+)',raw)]
        require('CSC_TRANSACTION_COMPLETE'in raw and len(records)==len(cases),'Incomplete customer survey')
        write_json(out/('survey-'+str(turn)+'.json'),dict(turn=turn,records=records))
    try:
        for item in packages:shutil.copytree(item['source'],item['install']);copied.append(item)
        write_json(out/'installed-manifests.json',{i['role']:i['files']for i in copied})
        session.start(lambda:launch(SimpleNamespace(binary=plan.binary),out));session.wait_context('MainMenu')
        configure(controller,out,csc_id=plan.protocol['ce']);enable(session,plan.protocol['csc'])
        for identity in plan.extras:enable(session,identity)
        require({k for k,v in flags(controller,'customer-mods')['mods'].items()if v}==
                {plan.protocol['ce'],plan.protocol['csc'],*plan.extras},'Unexpected packages')
        session.load_once(plan.checkpoint['native_save'],sha256=plan.checkpoint['sha256'],native_directory=plan.saves,
            turn=args.at,contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay','CSC_AdjacencyGameplay'),eligibility=gate)
        ce=next(i for i in copied if i['role']=='ce')
        verify_modules(session,ce['install']/'Binaries/Win64'/DLL,out,HOTFIX_SHA)
        catalogue=controller.cmd("for d in GameInfo.Districts()do print('CSC_TX_DISTRICT',d.Index,d.DistrictType)end\n"
            "for b in GameInfo.Buildings()do if b.BuildingType=='BUILDING_MARKET'or b.BuildingType=='BUILDING_BANK'or b.BuildingType=='BUILDING_STOCK_EXCHANGE'then print('CSC_TX_BUILDING',b.Index,b.BuildingType)end end",
            'CSC_AI_BakersGameplay','customer-catalogue')
        (out/'catalogue.txt').write_text(catalogue,encoding='utf-8')
        count=max(map(int,re.findall(r'CSC_TX_DISTRICT\s+(\d+)',catalogue)))+1
        buildings=list(map(int,re.findall(r'CSC_TX_BUILDING\s+(\d+)',catalogue)))
        require(buildings,'Missing native customer building IDs')
        for name in ('economy_savings_watch.py','economy_savings_watch.js'):shutil.copyfile(HERE/name,out/name)
        modules=json.loads((out/'loaded-modules.json').read_text(encoding='utf-8'))
        watch=EconomySavingsWatch(directory=plan.dependencies,binary=modules['GameCore_XP2_FinalRelease.dll']['path'],
            output=out,start=args.at,through=args.through,write=write_json,players=plan.identity['original_ai'],
            width=plan.identity['map_signature'][0],height=plan.identity['map_signature'][1],districts=count,
            matrix_targets=targets,matrix_buildings=buildings,capture_placement=True)
        watch.attach(session.owner,modules);watch.window(args.at,args.through)
        for name in ('planning_observer.lua','district_adjacency_watch.lua'):
            raw=controller.cmd(read(HERE/name),'PlotInfo'if name.startswith('district_')else'CSC_AI_BakersGameplay',name)
            (out/(name+'.txt')).write_text(raw,encoding='utf-8')
        survey()
        stops=sorted({*range(args.at+5,args.through+1,5),args.through,*[t for t in (110,122)if args.at<t<args.through]})
        for target in stops:
            controller.play(target);watch.drain();survey()
        state=controller.state_read('customer-final-clock')
        require(state['turn']==args.through and not state['active'],'Wrong diagnostic endpoint')
        write_json(out/'complete.json',dict(verified=True,turn=args.through))
    except Exception as error:
        write_json(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    finally:
        if session.owner is not None and session.owner.poll()is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,out),restore_package=verify,
                before_menu=lambda:watch.freeze()if watch else None,after_native_exit=lambda:watch.after_exit()if watch else None)
        if session.closed:
            for i in copied:i['install'].rename(out/i['install'].name)
            for name in LOGS:
                p=plan.user_root/'Logs'/name
                if p.is_file():shutil.copyfile(p,out/name)
    if watch:watch.qualify()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in('source','output','dependencies'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--at',type=int,default=100);p.add_argument('--through',type=int,default=125)
    p.add_argument('--policy-package',type=Path)
    p.add_argument('--case',nargs=6,action='append',required=True,metavar=('PLAYER','CITY','CHOSEN','ALT','QUARTER','Q_PLOT'))
    run(p.parse_args())
