"""Inspect a mature saved world's new valuation without playing another turn.

The shared controller owns installation, loading and shutdown. Old source/save
provenance and structural census are checked before adopting a frozen package
whose only changes are main AI Lua, its numeric UI bridge and the CE binary.
This is a diagnostic source update, not another ordinary qualification game.
"""
import argparse
from pathlib import Path
import shutil
from types import SimpleNamespace
import traceback
from planning_continue import prepare,enable,parse_census,compare_structure
from driver import (NativeSession,HeldProcess,make_probe_controller,native_inventory,
    launch,configure,flags,manifest,read,lua,sha,write_json,restore_preferences,require,archive_sources)
from ce_replay import DLL,HOTFIX_SHA,verify_modules
from ce_bakers_fresh import package_identity
from native_valuation_preflight import inspect


def run(args):
    plan=prepare(args.source,args.output,args.at,args.at,args.dependencies,read_only=True)
    replacements={}
    changes={}
    for item in plan.packages:
        new=args.frozen/('CE'if item['role']=='ce'else'CSC')
        require(package_identity(new)[0]==item['id'],'Replacement mod identity changed')
        files=manifest(new)
        different=[k for k in set(files)|set(item['files'])if files.get(k)!=item['files'].get(k)]
        for name in different:
            allowed=(name.replace('\\','/')=='Binaries/Win64/'+DLL)if item['role']=='ce'else(
                name.replace('\\','/').startswith('Lua_UI/AI/')or
                name.replace('\\','/')=='Lua_UI/Adjacencies/CSC_AdjacencyUI.lua')
            require(allowed,'Unexpected non-AI source update: '+name)
        replacements[item['role']]=dict(source=new,files=files,install=item['install'])
        changes[item['role']]=different
    require(not native_inventory(),'Preserve foreign game/Tuner session')
    out=plan.output;out.mkdir(parents=True)
    write_json(out/'diagnostic-source-update.json',dict(source=str(plan.source),turn=plan.at,
        frozen=str(args.frozen),changed_files=changes,read_only=True,game_turns_advanced=0,
        checkpoint=plan.checkpoint))
    scripts=[Path(__file__),Path(__file__).with_name('native_valuation_preflight.py'),
             Path(__file__).with_name('full_game_census.lua'),Path(__file__).with_name('economy_component_probe.lua')]
    pins={str(p.resolve()):sha(p)for p in scripts}
    write_json(out/'implementation-archive.json',archive_sources(pins,out/'implementation-version'))
    controller=make_probe_controller(out,user_root=plan.user_root)
    controller.study_endpoint=plan.at
    controller.allow_observer_warning_dismissal=controller.allow_observer_first_meet_dismissal=True
    controller.allow_observer_congress_review=True
    session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    copied=[]
    def verify():
        for item in replacements.values():require(manifest(item['install'])==item['files'],'Installed package changed')
        for item in plan.extras.values():require(manifest(Path(item['path']))==item['files'],'Optional package changed')
    def gate():
        code=('CSC_ENDPOINT_PLAYERS='+lua(plan.identity['original_ai'])+'\nCSC_ENDPOINT_EXPECTED_TURN='
              +str(plan.at)+'\n'+read(Path(__file__).with_name('full_game_census.lua')))
        raw=controller.cmd(code,'CSC_AI_BakersGameplay','read-only-loaded-census')
        (out/'source-census.txt').write_text(raw,encoding='utf-8')
        actual=parse_census(raw,plan.at)
        proof=compare_structure(plan.expected_census,actual)
        write_json(out/'source-structure-comparison.json',proof)
        require(proof['verified'],'Saved world structure changed')
        return True
    try:
        for item in replacements.values():shutil.copytree(item['source'],item['install']);copied.append(item)
        session.start(lambda:launch(SimpleNamespace(binary=plan.binary),out))
        session.wait_context('MainMenu')
        configure(controller,out,csc_id=plan.protocol['ce'])
        enable(session,plan.protocol['csc'])
        for identity in plan.extras:enable(session,identity)
        require({k for k,v in flags(controller,'verify-valuation-replay-mods')['mods'].items()if v}=={
            plan.protocol['ce'],plan.protocol['csc'],*plan.extras},'Unexpected enabled mod set')
        session.load_once(plan.checkpoint['native_save'],sha256=plan.checkpoint['sha256'],
            native_directory=plan.saves,turn=plan.at,
            contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay','CSC_AdjacencyGameplay'),eligibility=gate)
        verify_modules(session,replacements['ce']['install']/'Binaries/Win64'/DLL,out,HOTFIX_SHA)
        inspect(controller,out)
        state=controller.state_read('read-only-valuation-end-clock')
        require(state['turn']==plan.at and not state['active'],'Diagnostic advanced the game')
        write_json(out/'valuation-complete.json',dict(verified=True,game_turns_advanced=0,turn=plan.at))
    except Exception as error:
        write_json(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    finally:
        if session.owner is not None and session.owner.poll()is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,out),restore_package=verify)
        if session.closed:
            for item in copied:item['install'].rename(out/item['install'].name)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','output','frozen','dependencies'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--at',type=int,required=True)
    run(parser.parse_args())
