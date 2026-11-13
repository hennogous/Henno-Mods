"""Read-only Quarter lifecycle/selector replay of an archived inactive checkpoint.

The shared controller owns launch, load, autoplay and cleanup. Defaults use
exact archived CSC/CE policy; explicit paired --ce/--csc inputs qualify a new
integrated candidate against that checkpoint. Input identities/differences are
recorded. The observer injects no bid, unlock, gold or district order.
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
from district_admission_watch import AdmissionWatch,validate_options

NAMES=('CSC Bakers Development CE','CSC Bakers Development Mod')


def run(a):
    admission_enabled=getattr(a,'admission_probe',False)
    validate_options(admission_enabled,getattr(a,'frida_deps',None),getattr(a,'admission_binary',None))
    source=a.source.resolve(strict=True);out=a.output.resolve();home=a.my_games.resolve(strict=True)
    assert load(source/'result.json')['closed']and load(source/'session-closed.json')['verified']
    checkpoint=load(source/('checkpoint-'+str(a.start)+'.json'))
    assert checkpoint['turn']==a.start and checkpoint['verified']and checkpoint['save_complete_event']
    inspect_capacity=getattr(a,'inspect_capacity',False)
    # A saved-state inspection advances no turns. Keep it explicit rather than
    # silently treating a zero-length replay as a successful AI observation.
    assert (a.through==a.start if inspect_capacity else 0<a.through-a.start<=30),'Use a short diagnostic window'
    assert not(inspect_capacity and admission_enabled),'Capacity inspection uses shipped UI queries, not request hooks'
    save=Path(checkpoint['native_save']).resolve(strict=True)
    assert save.parent==(home/'Saves/Single').resolve()
    assert sha(save)==checkpoint['sha256']==sha(source/('turn-'+str(a.start)+'.Civ6Save'))
    archived={source/name:home/'Mods'/name for name in NAMES}
    assert not out.exists()and not native_inventory()and not any(p.exists()for p in archived.values())
    ledger=load(source/'packages.json');archive_pins={p:manifest(p)for p in archived}
    for p in archived:
        proof,=[row for row in ledger.values()if Path(row['install']).name==p.name]
        assert archive_pins[p]==proof['files'],'Archived package changed'
    assert bool(a.ce)==bool(a.csc),'Candidate override requires both explicit packages'
    inputs=[a.ce.resolve(strict=True),a.csc.resolve(strict=True)]if a.ce else list(archived)
    packages=dict(zip(inputs,archived.values()));pins={p:manifest(p)for p in packages}
    for old,new in zip(archived,packages):
        assert package_identity(old)[0]==package_identity(new)[0],'Candidate save identity differs'
    differences={new.name:[name for name in sorted(set(archive_pins[old])|set(pins[new]))
        if archive_pins[old].get(name)!=pins[new].get(name)]for old,new in zip(archived,packages)}
    ce,csc=packages;ce_id,_=package_identity(ce);csc_id,_=package_identity(csc)
    binary=Path(load(source/'launch-bootstrap.json')['binary']);assert sha(binary)==HOTFIX_EXE_SHA
    out.mkdir(parents=True)
    write_json(out/'inputs.json',dict(source=str(source),save_sha256=checkpoint['sha256'],
        start=a.start,through=a.through,read_only_observer=True,external_policy=False,
        inspect_capacity=inspect_capacity,turns_advanced=a.through-a.start,
        packages={str(p):pin for p,pin in pins.items()},candidate_override=bool(a.ce),
        changed_from_archived=differences))
    for name in('quarter_placement_replay.py','quarter_placement_watch.lua','quarter_economy_facts_probe.lua'):
        shutil.copyfile(HERE/name,out/name)
    if inspect_capacity:shutil.copyfile(HERE/'district_capacity_inspect.lua',out/'district_capacity_inspect.lua')
    admission=None
    if admission_enabled:
        # Diagnostic only: the same archived main CSC policy still supplies all
        # bids. Reuse explicit existing Frida dependencies; do not install them.
        # No attachment happens until the controller qualifies the loaded save.
        for name in('district_admission_watch.py','district_admission_watch.js'):
            shutil.copyfile(HERE/name,out/name)
        admission=AdmissionWatch(directory=a.frida_deps,binary=a.admission_binary,
            output=out,start=a.start,through=a.through,write=write_json)
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
            if a.facts_probe:
                facts=controller.cmd('CSC_QUARTER_FACTS_REQUIRE_READY='+str(a.require_ready).lower()+'\n'+read(out/'quarter_economy_facts_probe.lua'),'CSC_AI_BakersGameplay','read-economic-readiness-facts')
                (out/'economic-readiness-facts.txt').write_text(facts,encoding='utf-8')
                assert 'CSC_QUARTER_FACT_PROBE_COMPLETE'in facts
            if admission:
                admission.attach(session.owner,load(out/'loaded-modules.json'))
            if inspect_capacity:
                # PlotInfo is a UI-cache context. The ordinary ProductionPanel
                # uses these same CanProduce/requirements and capacity queries.
                # Gameplay's similarly named binding is not interchangeable.
                raw=controller.cmd(read(out/'district_capacity_inspect.lua'),'PlotInfo','inspect-saved-capacity')
                (out/'saved-capacity.txt').write_text(raw,encoding='utf-8')
                assert 'CSC_CAPACITY_FACTS_COMPLETE'in raw
            return True
        session.load_once(save,sha256=checkpoint['sha256'],native_directory=home/'Saves/Single',turn=a.start,
            contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=capture)
        cursor=a.start
        while cursor<a.through:
            endpoint=min(cursor+5,a.through)
            # RPC labels only bound the observational interval; they do not
            # advance Civ. The shared controller remains the sole turn driver.
            if admission:admission.window(cursor,endpoint)
            cursor=endpoint;controller.play(cursor)
            write_json(out/'last-boundary.json',dict(turn=cursor,verified=True))
        status=controller.cmd("print('CSC_QUARTER_REPLAY_NATIVE '..CE_AIDistrictScoresStatus())",'CSC_AI_BakersGameplay','native-delivery-health')
        (out/'native-health.txt').write_text(status,encoding='utf-8')
        assert '\"ready\":1'in status and '\"enabled\":1'in status and '\"faults\":0'in status
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
                if(out/'original-preferences.json').exists()else None,restore_package=verify,
                before_menu=admission.freeze if admission else lambda:None,
                after_native_exit=admission.after_exit if admission else lambda:None)
        if session.closed:
            for p in copied:packages[p].rename(out/p.name)
            for name in LOGS:
                log=a.user_root/'Logs'/name
                if log.is_file():shutil.copyfile(log,out/name)
    assert session.closed and sha(save)==checkpoint['sha256']
    if admission:admission.qualify()
    log=read(out/'Lua.log')
    assert 'CSC_QUARTER_WATCH_FAULT'not in log and 'CSC_AI_BAKERS_DISTRICTS_FAILED'not in log
    write_json(out/'complete.json',dict(verified=True,start=a.start,through=a.through,
        external_policy=False,read_only_observer=True,admission_probe=admission_enabled,
        inspect_capacity=inspect_capacity,turns_advanced=a.through-a.start))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('source','output','my-games','user-root'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--facts-probe',action='store_true')
    parser.add_argument('--require-ready',action='store_true')
    parser.add_argument('--ce',type=Path);parser.add_argument('--csc',type=Path)
    parser.add_argument('--admission-probe',action='store_true',
        help='Observe Quarter request admission; never changes bids or decisions')
    parser.add_argument('--frida-deps',type=Path,help='Explicit existing Frida 17.24.3 package directory')
    parser.add_argument('--admission-binary',type=Path,help='Explicit original patched XP2 DLL (SHA092abfbb)')
    parser.add_argument('--inspect-capacity',action='store_true',
        help='Read saved-city capacity and native production failure reasons; requires through=start and advances no turns')
    parser.add_argument('--start',type=int,required=True);parser.add_argument('--through',type=int,required=True)
    run(parser.parse_args())
