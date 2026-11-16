"""Reload the completed Online250 save for disposable supplier payout checks.

The ordinary full-game record is sealed first. This session uses its exact
packages/save and never advances an AI turn. Human fixture grants measure
real incoming Food/Culture; their construction is not included in run results.
All game/console access belongs to the existing shared controller lifecycle.
"""
import argparse
from pathlib import Path
import shutil
import traceback
from types import SimpleNamespace

from driver import (HERE,HOTFIX_SHA,HeldProcess,NativeSession,configure,flags,
                    launch,load,make_probe_controller,manifest,native_inventory,
                    parse,read,require,restore_preferences,sha,write_json)
from ce_replay import DLL,HOTFIX_EXE_SHA,verify_modules
from planning_continue import enable
from material_coverage_fixture import run as fixture
from material_lifecycle_fixture import run as lifecycle_fixture


def prepare(source,output):
    source,output=Path(source).resolve(strict=True),Path(output).resolve()
    require(not output.exists(),'Use a new diagnostic output directory')
    closed=load(source/'session-closed.json')
    require(all(closed.get(k)for k in('verified','owners_absent','preferences_verified','package_callback_completed'))
            and closed['native_exit_code']==0,'Complete/close the ordinary run first')
    protocol=load(source/'protocol.json');checkpoint=load(source/'checkpoint.json')
    require(protocol['fresh_game']and protocol['endpoint']==250 and not protocol['untuned']
            and not protocol['external_policy']and not protocol['gameplay_interventions'],
            'Expected the ordinary main-policy Online250 source')
    require(load(source/'full-game-observation-complete.json')['verified'],
            'Seal the ordinary observation before fixture changes')
    require(load(source/'coverage-preflight.json')['verified'],'Loaded coverage was not qualified')
    require(checkpoint['verified']and checkpoint['turn']==250 and checkpoint['save_complete_event']
            and checkpoint['native_phase_unchanged'],'Verified inactive250 save required')
    save=Path(checkpoint['native_save']).resolve(strict=True)
    require(sha(save)==sha(source/'endpoint.Civ6Save')==checkpoint['sha256'],'Source save differs')
    packages=[]
    for path,item in load(source/'packages.json').items():
        path=Path(path).resolve(strict=True);install=Path(item['install'])
        require(manifest(path)==item['files']and not install.exists(),'Source package drift or occupied install')
        packages.append(dict(source=path,install=install,files=item['files']))
    require(len(packages)==2,'Expected CE and CSC only')
    extras=load(source/'extra-mods.json')
    for item in extras.values():
        require(manifest(Path(item['path']))==item['files'],'Optional package changed')
    binary=Path(load(source/'launch-bootstrap.json')['binary']).resolve(strict=True)
    require(sha(binary)==HOTFIX_EXE_SHA,'Executable changed since qualification')
    return source,output,protocol,checkpoint,save,packages,extras,binary


def run(args):
    source,out,protocol,checkpoint,save,packages,extras,binary=prepare(args.source,args.output)
    require(not native_inventory(),'Shared console/native session already owned')
    out.mkdir(parents=True)
    for name in ('material_coverage_replay.py','material_coverage_fixture.py',
                 'material_coverage_fixture.lua','material_coverage_plan.lua','material_lifecycle_fixture.py'):
        shutil.copyfile(HERE/name,out/name)
    write_json(out/'protocol.json',dict(diagnostic_only=True,fixture_grants=True,
        ai_turns_advanced=0,source=str(source),source_checkpoint=checkpoint,
        ordinary_game_unchanged=True))
    controller=make_probe_controller(out,user_root=args.user_root)
    controller.allow_observer_warning_dismissal=controller.allow_observer_first_meet_dismissal=True
    session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    copied=[]

    def verify_packages():
        for item in copied:
            require(manifest(item['install'])==item['files'],'Installed diagnostic package changed')
        for item in extras.values():
            require(manifest(Path(item['path']))==item['files'],'Optional package changed during diagnostic')

    def source_gate():
        raw=controller.cmd('''
assert(Game.GetCurrentGameTurn()==250 and not AutoplayManager.IsActive())
assert(Players[0]:IsHuman())
print('CSC_MATERIAL_SOURCE_OK')
''','GameCore_Tuner','verify-material-source')
        require('CSC_MATERIAL_SOURCE_OK'in raw,'Wrong payout diagnostic source')
        return True

    try:
        for item in packages:
            shutil.copytree(item['source'],item['install']);copied.append(item)
        verify_packages()
        session.start(lambda:launch(SimpleNamespace(binary=binary),out))
        session.wait_context('MainMenu')
        configure(controller,out,csc_id=protocol['ce'])
        enable(session,protocol['csc'])
        for identity in extras:enable(session,identity)
        enabled={k for k,v in flags(controller,'verify-material-packages')['mods'].items()if v}
        require(enabled=={protocol['ce'],protocol['csc'],*extras},'Source mod selection differs')
        session.load_once(save,sha256=checkpoint['sha256'],native_directory=save.parent,turn=250,
            contexts=('GameCore_Tuner','PlotInfo','CSC_AdjacencyGameplay'),eligibility=source_gate)
        ce=next(p['install']for p in packages if(p['install']/'Binaries/Win64'/DLL).is_file())
        verify_modules(session,ce/'Binaries/Win64'/DLL,out,HOTFIX_SHA)
        code='CSC_MATERIAL_COVERAGE_TURN=250\n'+read(HERE/'material_coverage_plan.lua')
        raw=controller.cmd(code,'CSC_AdjacencyGameplay','select-material-fixture')
        (out/'plan.txt').write_text(raw,encoding='utf-8')
        config=parse(raw,'CSC_MATERIAL_COVERAGE_PLAN')
        result=fixture(controller,out/'payouts',config)
        if args.lifecycle:
            result['lifecycle']=lifecycle_fixture(controller,out/'lifecycle',config)
        write_json(out/'result.json',result)
    except Exception as error:
        write_json(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()))
        raise
    finally:
        if session.owner is not None and session.owner.poll()is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,out)
                if(out/'original-preferences.json').exists()else None,restore_package=verify_packages)
        if session.closed or session.owner is None and not native_inventory():
            for item in copied:item['install'].rename(out/item['install'].name)
    require(session.closed and result['verified']and sha(save)==checkpoint['sha256'],
            'Payout qualification incomplete or source save changed')
    write_json(out/'complete.json',dict(verified=True,ai_turns_advanced=0,source_save_unchanged=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('source','output','user-root'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--lifecycle',action='store_true',help='Observe supplier/producer/district pillage and repair without advancing turns')
    run(parser.parse_args())
