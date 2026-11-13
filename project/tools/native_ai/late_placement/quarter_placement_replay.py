"""Read-only Quarter lifecycle/selector replay of an archived inactive checkpoint.

The shared controller owns launch, load, autoplay and cleanup. Exact archived
CSC/CE packages retain the policy under test. This adds observations only; it
does not inject a bid, unlock, treasury change or district order.
"""
import argparse
from pathlib import Path
import shutil
from types import SimpleNamespace
import traceback
from ce_bakers_fresh import package_identity,LOGS
from ce_replay import DLL,HOTFIX_EXE_SHA,verify_modules
from driver import (HERE,HOTFIX_SHA,HeldProcess,NativeSession,configure,flags,launch,load,lua,
    make_probe_controller,manifest,native_inventory,read,restore_preferences,sha,write_json)
from full_game_controller.checkpoint import save_inactive_boundary

NAMES=('CSC Bakers Development CE','CSC Bakers Development Mod')


def run(a):
    source=a.source.resolve(strict=True);out=a.output.resolve();home=a.my_games.resolve(strict=True)
    assert load(source/'result.json')['closed']and load(source/'session-closed.json')['verified']
    checkpoint=load(source/('checkpoint-'+str(a.start)+'.json'))
    assert checkpoint['turn']==a.start and checkpoint['verified']and checkpoint['save_complete_event']
    assert 0<a.through-a.start<=30,'Use a short diagnostic window'
    save=Path(checkpoint['native_save']).resolve(strict=True)
    assert save.parent==(home/'Saves/Single').resolve()
    assert sha(save)==checkpoint['sha256']==sha(source/('turn-'+str(a.start)+'.Civ6Save'))
    packages={source/name:home/'Mods'/name for name in NAMES}
    assert not out.exists()and not native_inventory()and not any(p.exists()for p in packages.values())
    ledger=load(source/'packages.json');pins={p:manifest(p)for p in packages}
    for p in packages:
        proof,=[row for row in ledger.values()if Path(row['install']).name==p.name]
        assert pins[p]==proof['files'],'Archived package changed'
    ce,csc=packages;ce_id,_=package_identity(ce);csc_id,_=package_identity(csc)
    binary=Path(load(source/'launch-bootstrap.json')['binary']);assert sha(binary)==HOTFIX_EXE_SHA
    out.mkdir(parents=True)
    write_json(out/'inputs.json',dict(source=str(source),save_sha256=checkpoint['sha256'],
        start=a.start,through=a.through,read_only_observer=True,external_policy=False,
        packages={p.name:pin for p,pin in pins.items()}))
    for name in('quarter_placement_replay.py','quarter_placement_watch.lua'):
        shutil.copyfile(HERE/name,out/name)
    controller=make_probe_controller(out,user_root=a.user_root)
    controller.study_endpoint=a.through
    controller.allow_observer_warning_dismissal=controller.allow_observer_first_meet_dismissal=True
    controller.allow_observer_congress_review=controller.allow_one_more_turn=True
    session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    copied=[]
    def verify():
        assert all(manifest(packages[p])==pins[p]for p in copied),'Runtime package changed'
    try:
        for p,target in packages.items():shutil.copytree(p,target);copied.append(p)
        verify();session.start(lambda:launch(SimpleNamespace(binary=binary),out))
        session.wait_context('MainMenu');configure(controller,out,csc_id=ce_id)
        session.issue_once('enable-csc',"""local selected
for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='"""+csc_id+"""'then assert(not selected);selected=m end end
assert(selected and Modding.CanEnableMod(selected.Handle)=='OK');Modding.EnableMod(selected.Handle,true)
""",'MainMenu')
        assert {k for k,v in flags(controller,'verify-exact-pair')['mods'].items()if v}=={ce_id,csc_id}
        def capture():
            verify_modules(session,(packages[ce]/'Binaries/Win64'/DLL).resolve(),out,HOTFIX_SHA)
            state=controller.state_read('before-placement-watch')
            assert state['turn']==a.start and not state['active']
            raw=controller.cmd(read(out/'quarter_placement_watch.lua'),'CSC_AI_BakersGameplay','install-placement-watch')
            (out/'watch-install.txt').write_text(raw,encoding='utf-8')
            assert 'CSC_QUARTER_WATCH_INSTALLED'in raw and 'CSC_QUARTER_WATCH_FAULT'not in raw
            return True
        session.load_once(save,sha256=checkpoint['sha256'],native_directory=home/'Saves/Single',turn=a.start,
            contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=capture)
        cursor=a.start
        while cursor<a.through:
            cursor=min(cursor+5,a.through);controller.play(cursor)
            write_json(out/'last-boundary.json',dict(turn=cursor,verified=True))
        raw=controller.cmd("CSC_QUARTER_PLACEMENT_WATCH.Drain();print('CSC_QUARTER_WATCH_DRAINED')",
            'CSC_AI_BakersGameplay','drain-final-placement-journal')
        assert 'CSC_QUARTER_WATCH_DRAINED'in raw and 'CSC_QUARTER_WATCH_FAULT'not in raw
        boundary=save_inactive_boundary(controller,turn=a.through,name='CSC_QUARTER_PLACEMENT',
            native_directory=home/'Saves/Single',archive=out/'endpoint.Civ6Save')
        write_json(out/'checkpoint.json',boundary)
    except Exception as error:
        write_json(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    finally:
        if session.owner is not None and session.owner.poll()is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,out)
                if(out/'original-preferences.json').exists()else None,restore_package=verify)
        if session.closed:
            for p in copied:packages[p].rename(out/p.name)
            for name in LOGS:
                log=a.user_root/'Logs'/name
                if log.is_file():shutil.copyfile(log,out/name)
    assert session.closed and sha(save)==checkpoint['sha256']
    log=read(out/'Lua.log')
    assert 'CSC_QUARTER_WATCH_FAULT'not in log and 'CSC_AI_BAKERS_DISTRICTS_FAILED'not in log
    write_json(out/'complete.json',dict(verified=True,start=a.start,through=a.through,
        external_policy=False,read_only_observer=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('source','output','my-games','user-root'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--start',type=int,required=True);parser.add_argument('--through',type=int,required=True)
    run(parser.parse_args())
