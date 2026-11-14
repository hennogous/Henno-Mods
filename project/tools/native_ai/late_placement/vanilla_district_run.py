"""Normal no-CSC district control through the shared controller.

Only CE's passive facilities and the matched optional mods are enabled. No CSC
package, SQL, private yield, AI policy or fixture is installed. Native choice
quotes, before-placement cached totals and physical/UI events are separate
observations. Shared NativeSession owns launch, finite play, saves and cleanup.
"""
import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
from types import SimpleNamespace
import traceback

from ce_bakers_fresh import host,package_identity,check_native_status,LOGS
from ce_replay import DLL,HOTFIX_EXE_SHA,verify_modules
from driver import (HERE,HOTFIX_SHA,HeldProcess,NativeSession,configure,flags,launch,load,lua,
    make_probe_controller,manifest,native_inventory,parse,read,require,restore_preferences,sha,write_json)
from full_game_controller.checkpoint import save_inactive_boundary,SavePermissionUnavailable
from full_game_controller.environment import archive_sources
from planning_continue import enable


def prepare(source,out):
    """Read and hash all inputs before installs, preferences or native work."""
    source=Path(source).resolve(strict=True);out=Path(out).resolve()
    require(not out.exists(),'New baseline output required')
    for name in ('session-closed.json','preferences-restored.json'):
        require(load(source/name)['verified'],'Matched source must be closed/restored')
    protocol=load(source/'protocol.json');identity=load(source/'source.json')
    require(protocol['fresh_game']and protocol['ordinary_setup']and protocol['map_size']=='small'
            and protocol['endpoint']==250,'Require the preselected ordinary planning source')
    packages=load(source/'packages.json')
    ce,= [(Path(p),v)for p,v in packages.items()if str(Path('Binaries/Win64')/DLL)in v['files']]
    ce_path,ce_record=ce
    require(manifest(ce_path)==ce_record['files'],'Pinned CE source changed')
    ce_id,_=package_identity(ce_path)
    extras=load(source/'extra-mods.json')
    for mod_id,item in extras.items():
        require(manifest(Path(item['path']))==item['files'],'Matched optional mod changed: '+mod_id)
    binary=Path(load(source/'session-native-exit.json')['identity']['executable_path'])
    require(sha(binary)==HOTFIX_EXE_SHA,'Qualified DX11 executable changed')
    checkpoints=sorted(source.glob('checkpoint*.json'))
    cp=next(load(p)for p in checkpoints if 'native_save'in load(p))
    saves=Path(cp['native_save']).parent
    mods=Path(ce_record['install']).parent
    install=mods/'CSC Vanilla Observation CE'
    require(not install.exists()and not ce_path.is_relative_to(mods)and not out.is_relative_to(mods),
            'Unused CE-only staging and external output required')
    return SimpleNamespace(source=source,out=out,protocol=protocol,identity=identity,ce=ce_path,
        ce_files=ce_record['files'],ce_id=ce_id,extras=extras,binary=binary,saves=saves,install=install,
        user=Path(load(source/'resource-stack-preflight.json')['database']).parent.parent)


def normal_host(plan):
    # Explicit leader choices are normal setup, not a game-state intervention.
    # Keep the original cohort's unique districts/civs comparable. Removing CSC
    # can change resource generation/RNG, so seed matching is not map identity.
    leaders={r['player']:r['leader']for r in plan.identity['starts']}
    code=host(plan.protocol['map_seed'],plan.protocol['game_seed'],plan.protocol['map'],'small')
    fixed='local leaders='+lua(leaders)+'\nfor id,name in pairs(leaders)do PlayerConfigurations[id]:SetLeaderTypeName(name)end\n'
    return code.replace('ReleasePlayerParameters()',fixed+'ReleasePlayerParameters()')


def check_database(path):
    with closing(sqlite3.connect('file:'+Path(path).as_posix()+'?mode=ro',uri=True))as db:
        districts=[r[0]for r in db.execute("SELECT DistrictType FROM Districts WHERE DistrictType LIKE 'DISTRICT_CSC_%'")]
        yields=[r[0]for r in db.execute("SELECT YieldType FROM Yields WHERE YieldType LIKE 'YIELD_CSC_%'")]
    require(not districts and not yields,'CSC SQL present in no-CSC database')
    return dict(verified=True,database=str(path),sha256=sha(Path(path)),csc_districts=districts,csc_yields=yields)


def archive_checkpoint(controller,out,saves,turn):
    # Checkpoints support later inspection; the live censuses and district
    # journals supply this campaign's measurements. If the shipped UI declines
    # saving before a request is sent, retain that fact and keep observing.
    # A timeout AFTER a save request remains an error with uncertain completion.
    try:
        cp=save_inactive_boundary(controller,turn=turn,name='CSC_NO_CSC_CONTROL_'+str(turn),
            native_directory=saves,archive=out/('turn-'+str(turn)+'.Civ6Save'))
    except SavePermissionUnavailable as error:
        write_json(out/('checkpoint-unavailable-'+str(turn)+'.json'),
            dict(turn=turn,save_requests=0,reason=str(error),optional_artifact=True))
        return
    write_json(out/('checkpoint-'+str(turn)+'.json'),cp)


def run(args):
    p=prepare(args.source,args.output)
    require(args.through in(25,250),'Bounded diagnostic25 or full250 only')
    require(not native_inventory(),'Foreign Civ/Tuner owner; preserve it')
    out=p.out;out.mkdir(parents=True)
    protocol=dict(map=p.protocol['map'],map_seed=p.protocol['map_seed'],game_seed=p.protocol['game_seed'],
        endpoint=args.through,map_size='small',speed='online',difficulty='prince',csc_enabled=False,
        matched_source=str(p.source),fixed_original_leaders=True,identical_map_claim=False,
        ordinary_setup=True,fresh_game=True,external_policy=False,gameplay_interventions=False,
        interval_minutes=15,ce=p.ce_id,extra_mods=list(p.extras),capture_placement=True)
    write_json(out/'protocol.json',protocol)
    write_json(out/'packages.json',{str(p.ce):dict(install=str(p.install),files=p.ce_files)})
    write_json(out/'extra-mods.json',p.extras)
    runtime=[Path(__file__),HERE/'economy_savings_watch.py',HERE/'economy_savings_watch.js',
        HERE/'vanilla_district_observer.lua',HERE/'vanilla_district_ui.lua',HERE/'district_adjacency_watch.lua',
        HERE/'ce_bakers_fresh.py',HERE/'planning_continue.py',
        *sorted((HERE.parents[1]/'ai_baseline/full_game_controller').glob('*.py')),
        *sorted((HERE.parents[1]/'ai_baseline/full_game_controller').glob('*.lua'))]
    pins={str(path.resolve()):sha(path)for path in runtime}
    write_json(out/'implementation-pins.json',pins)
    write_json(out/'implementation-archive.json',archive_sources(pins,out/'implementation-version'))
    c=make_probe_controller(out,user_root=p.user);c.study_endpoint=args.through
    c.autoplay_interval_seconds=900
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    c.allow_observer_congress_review=c.allow_one_more_turn=True
    session=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    watch=None;copied=False;players=set()

    def verify():
        require(manifest(p.ce)==p.ce_files,'Frozen CE changed')
        if copied:require(manifest(p.install)==p.ce_files,'Installed CE changed')
        for item in p.extras.values():require(manifest(Path(item['path']))==item['files'],'Optional mod changed')
        require(all(sha(Path(k))==v for k,v in pins.items()),'Executed observer/controller source changed')

    def source_gate():
        expected={r['player']:r['leader']for r in p.identity['starts']}
        code='local expected='+lua(expected)+'\n'+'''
assert(Game.GetCurrentGameTurn()==1 and Players[0]:IsHuman())
assert(not GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER and not GameInfo.Yields.YIELD_CSC_AI_PLACEMENT)
assert(not CSC_AI_QuarterPlacement and not CSC_AI_BAKERS_RUNTIME)
local speed=GameConfiguration.GetGameSpeedType()
assert(speed=='GAMESPEED_ONLINE'or GameInfo.GameSpeeds[speed].GameSpeedType=='GAMESPEED_ONLINE')
local ids={}
for _,player in ipairs(PlayerManager.GetAliveMajors())do
 local pid=player:GetID();assert(PlayerConfigurations[pid]:GetLeaderTypeName()==expected[pid])
 if not player:IsHuman()then
  assert(not player:GetCulture():HasCivic(GameInfo.Civics.CIVIC_CRAFTSMANSHIP.Index))
  ids[#ids+1]=pid
 end
 local plot=player:GetStartingPlot()
 print('CSC_CONTROL_START='..table.concat({pid,expected[pid],plot and plot:GetIndex()or -1},','))
end
print('CSC_CONTROL_AI=['..table.concat(ids,',')..']')
local width,height=Map.GetGridSize();print('CSC_CONTROL_GRID=['..width..','..height..']')
print('CSC_CONTROL_CE='..CE_AIDistrictScoresStatus())
'''
        raw=c.cmd(code,'GameCore_Tuner','verify-no-CSC-normal-start')
        (out/'source-identity.txt').write_text(raw,encoding='utf-8')
        players.update(parse(raw,'CSC_CONTROL_AI'))
        require(players==set(p.identity['original_ai']),'Changed AI cohort')
        native=parse(raw,'CSC_CONTROL_CE');check_native_status(native,True)
        starts=[dict(player=int(pid),leader=leader,plot=int(plot))for pid,leader,plot in
            re.findall(r'CSC_CONTROL_START=(\d+),([A-Za-z0-9_]+),(-?\d+)',raw)]
        require(len(starts)==6,'Incomplete actual-start roster')
        write_json(out/'source.json',dict(original_ai=sorted(players),native=native,
            map_signature=parse(raw,'CSC_CONTROL_GRID'),starts=starts,
            expected_starts=p.identity['starts'],identical_starting_plots_claim=False))
        write_json(out/'no-csc-database.json',check_database(p.user/'Cache/DebugGameplay.sqlite'))
        database=p.user/'Cache/DebugGameplay.sqlite'
        before=sha(database);shutil.copyfile(database,out/'DebugGameplay.sqlite')
        require(before==sha(database)==sha(out/'DebugGameplay.sqlite'),'Loaded rule snapshot changed during copy')
        return True

    try:
        shutil.copytree(p.ce,p.install);copied=True;verify()
        session.start(lambda:launch(SimpleNamespace(binary=p.binary),out))
        session.wait_context('MainMenu');configure(c,out,csc_id=p.ce_id)
        for mod_id in p.extras:enable(session,mod_id)
        require({k for k,v in flags(c,'verify-no-CSC-mod-stack')['mods'].items()if v}==
            {p.ce_id,*p.extras},'Expected CE and matched optional mods only')
        session.issue_once('host-no-CSC-control',normal_host(p),'MainMenu')
        session.ready_after_issue(1,('GameCore_Tuner','PlotInfo'),eligibility=source_gate)
        verify_modules(session,p.install/'Binaries/Win64'/DLL,out,HOTFIX_SHA)
        catalogue=c.cmd("for d in GameInfo.Districts()do print('CSC_DISTRICT_CATALOGUE',d.Index,d.DistrictType,tostring(d.RequiresPopulation),d.Cost)end;print('CSC_DISTRICT_CATALOGUE_END')",'GameCore_Tuner','baseline-district-catalogue')
        (out/'loaded-district-catalogue.txt').write_text(catalogue,encoding='utf-8')
        indices=[int(i)for i in re.findall(r'CSC_DISTRICT_CATALOGUE\t(\d+)\t',catalogue)]
        require(indices and 'CSC_DISTRICT_CATALOGUE_END'in catalogue,'Missing catalogue')
        scope=lua(dict(players=sorted(players),through=args.through))
        core='CSC_VANILLA_SCOPE='+scope+'\n'+read(HERE/'vanilla_district_observer.lua')
        raw=c.cmd(core,'GameCore_Tuner','install-passive-no-CSC-district-observer')
        require('CSC_VANILLA_DISTRICT_INSTALLED'in raw and 'CSC_VANILLA_DISTRICT_FAULT'not in raw,'Core observer failed')
        ui=read(HERE/'vanilla_district_ui.lua')+'\n'+read(HERE/'district_adjacency_watch.lua')
        raw=c.cmd(ui,'PlotInfo','install-passive-no-CSC-ui-adjacency')
        require('CSC_DISTRICT_UI_INSTALLED'in raw and 'CSC_DISTRICT_UI_FAULT'not in raw,'UI observer failed')
        for name in('economy_savings_watch.js','economy_savings_watch.py'):shutil.copyfile(HERE/name,out/name)
        from economy_savings_watch import EconomySavingsWatch
        modules=load(out/'loaded-modules.json');width,height=load(out/'source.json')['map_signature']
        watch=EconomySavingsWatch(directory=args.dependencies,binary=modules['GameCore_XP2_FinalRelease.dll']['path'],
            output=out,start=1,through=args.through,write=write_json,players=sorted(players),
            width=width,height=height,districts=max(indices)+1,capture_placement=True)
        watch.attach(session.owner,modules)
        cursor=1
        while cursor<args.through:
            boundary=min(cursor+5,args.through,25*(cursor//25+1))
            watch.window(cursor,boundary);c.play(boundary);watch.drain()
            write_json(out/'full-game-last-boundary.json',dict(verified=True,turn=boundary,endpoint=args.through))
            if boundary%25==0:
                raw=c.cmd("CSC_VANILLA_DISTRICTS.Health();print('CSC_CONTROL_CE='..CE_AIDistrictScoresStatus())",'GameCore_Tuner','baseline-health-'+str(boundary))
                check_native_status(parse(raw,'CSC_CONTROL_CE'),True)
            if boundary in(50,100,150,200,250):
                archive_checkpoint(c,out,p.saves,boundary)
            cursor=boundary
        raw=c.cmd("CSC_VANILLA_DISTRICTS.Finish()",'GameCore_Tuner','finish-passive-no-CSC-observer')
        require('CSC_VANILLA_DISTRICT_FINISHED'in raw and 'CSC_VANILLA_DISTRICT_FAULT'not in raw,'Observer incomplete')
    except Exception as error:
        write_json(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    finally:
        if session.owner is not None and session.owner.poll()is None:
            session.close(restore_preferences=lambda:restore_preferences(c,out)if(out/'original-preferences.json').exists()else None,
                restore_package=verify,before_menu=lambda:watch.freeze()if watch else None,
                after_native_exit=lambda:watch.after_exit()if watch else None)
        elif session.owner is not None:
            # A crash cannot restore menu preferences. Preserve the installed
            # package and mark the incomplete lifecycle instead of fabricating
            # successful cleanup or automatically starting another game.
            code=session.owner.poll()
            if watch:watch.after_exit()
            write_json(out/'unexpected-native-exit.json',dict(identity=session.owner.identity,
                exit_code=code,preferences_restored=False,successful_run=False))
            session.owner.close()
        if session.closed or session.owner is None and not native_inventory():
            if copied:p.install.rename(out/p.install.name)
            if session.closed:
                for name in LOGS:
                    path=p.user/'Logs'/name
                    if path.is_file():shutil.copyfile(path,out/name)
    watch.qualify()
    log=read(out/'Lua.log')
    require(not any(s in log for s in('CSC_VANILLA_DISTRICT_FAULT','CSC_DISTRICT_UI_FAULT',
        'CSC_AI_BAKERS_DISTRICTS turn=','CSC_AI_BAKERS_PLACEMENT turn=')),'Control contaminated or observer faulted')
    from full_game_observation import archive_censuses
    censuses=archive_censuses(log,out)
    require(set(censuses)==set(range(25,args.through+1,25)),'Missing baseline census')
    write_json(out/'full-game-observation-complete.json',dict(verified=True,turns=sorted(censuses),csc_enabled=False))
    from planning_results import analyse
    write_json(out/'district-summary.json',analyse(out))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('source','output','dependencies'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--through',type=int,default=250)
    run(parser.parse_args())
