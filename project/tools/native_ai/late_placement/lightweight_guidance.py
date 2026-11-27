"""Replay CSC stock, ordinary-database guidance and advanced planning on shared starts."""
import argparse
from contextlib import closing
import hashlib
from pathlib import Path
import shutil
import sqlite3
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from ce_replay import DLL, verify_modules
from driver import (HERE, HeldProcess, NativeSession, launch, load, lua, make_probe_controller,
                    native_inventory, read, require, restore_preferences, sha, write_json)
from economy_factorial import read_opening, select_stack
from economy_guidance_timing import install_clocks, observed_turns
from full_game_controller.checkpoint import save_inactive_boundary
from full_game_observation import archive_censuses
from mature_guidance_replay import replace
from shortlist_pair import prepare


def stock_controls(database):
    """Read Firaxis's gameplay export after load, before the next game replaces it."""
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        return dict(
            builder_priority=db.execute("""SELECT Favored,Value FROM AiFavoredItems
                WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'""").fetchall(),
            recruiting_city=db.execute("""SELECT n.NodeId,t.DefaultData FROM BehaviorTreeNodes n
                LEFT JOIN TreeData t ON t.TreeName=n.TreeName AND t.NodeId=n.NodeId AND t.DefnId=2
                WHERE n.TreeName='Build City Improvement' AND n.NodeType='Build Unit'
                ORDER BY n.NodeId""").fetchall(),
            placements=db.execute("""SELECT d.DistrictType,a.AdjacentDistrict,a.AdjacentImprovement,
                a.YieldChange,a.TilesRequired,a.AdjacentResourceClass FROM District_Adjacencies d
                JOIN Adjacency_YieldChanges a ON a.ID=d.YieldChangeId
                WHERE a.YieldType='YIELD_CSC_AI_PLACEMENT' ORDER BY d.DistrictType,a.ID""").fetchall())


def observers(c,seats):
    # The stock arms have no advanced publisher. Load only read-only fact
    # readers in its existing Lua context for the same physical census in all arms.
    helpers="""
if not CSC_Adjacency then include('CSC_AdjacencyCore') end
CSC_Adjacency.Initialize()
if not CSC_AI_QuarterSiteForecasts then include('CSC_AI_AdjacencyScan') end
if not CSC_AI_QuarterPlacement then include('CSC_AI_QuarterPlacement') end
if not CSC_AI_DistrictBridge then include('CSC_AI_DistrictBridge') end
local CSC_LIFECYCLE_ONLY=true
"""
    context='CSC_AI_BakersGameplay'
    watched='local CSC_OBSERVE_SUPPLIER_LOSS='+lua({i:True for i in seats})+'\n'
    raw=c.cmd(watched+helpers+read(HERE/'quarter_placement_watch.lua'),context,'observe-foundations')
    require('CSC_QUARTER_WATCH_INSTALLED' in raw,'Foundation observer failed')
    raw=c.cmd('local CSC_ENDPOINT_PLAYERS='+lua(list(seats))+'''
GameEvents.OnGameTurnStarted.Add(function()
    local CSC_ENDPOINT_EXPECTED_TURN=Game.GetCurrentGameTurn()
    if CSC_ENDPOINT_EXPECTED_TURN%25~=0 then return end
    print('CSC_FULL_RUN_CENSUS_BEGIN',CSC_ENDPOINT_EXPECTED_TURN)
'''+read(HERE/'full_game_census.lua')+"\nend)\nprint('CSC_NATIVE_CENSUS_READY')",context,'observe-quarter-census')
    require('CSC_NATIVE_CENSUS_READY' in raw,'Quarter census failed')
    raw=c.cmd('CSC_MILESTONE_INCLUDE_HANDOFFS=true\nCSC_MILESTONE_SERVICE_EVERY_TURN=true\nCSC_MILESTONE_SERVICE_PLAYERS='+
              lua({i:True for i in seats})+'\n'+read(HERE/'later_stage_service_watch.lua'),'PlotInfo','observe-service-effects')
    require('CSC_MILESTONE_SERVICE_INSTALLED' in raw,'Service observer failed')
    install_clocks(c,stock=True)


def replay(root,seed,mode,end,label=None,ce_opening=False,deposit_cues=False):
    study=load(root/'study.json')
    pins=study['pins'];game=pins['seeds'][str(seed)]
    source=root/str(seed)/'opening'
    if mode=='prepare':
        return prepare(pins,seed,game,source,stack=('csc',))
    if mode in ('verify-off','prepare-advanced'):
        enabled=mode=='prepare-advanced'
        folder=source.parent/mode
        prepare(pins,seed,game,folder,stack=('csc','ce'),advanced_option=enabled,
                save_name=f'CSC_LIGHT_{seed}_{mode.upper()}_START')
        require(load(source/'source.json')==load(folder/'source.json'),'Seeded opening map or seats differ')
        return
    if ce_opening:
        require(mode=='advanced','Only the CE arm may need its own seeded opening')
        source=source.parent/'prepare-advanced'
    record=load(source/'checkpoint.json')
    arm_name=label or (mode+'-deposits' if deposit_cues else mode)
    out=source.parent/arm_name
    require(not native_inventory() and not out.exists(),'Game in use or output exists')
    out.mkdir()
    ce=mode=='advanced'
    enabled=['csc','ce'] if ce else ['csc']
    user=Path(pins['userdata']);saves=Path(pins['saves'])
    c=make_probe_controller(out,user_root=user);c.study_endpoint=end
    c.observer_warning_senders=range(1,len(game['roster']));c.autoplay_interval_seconds=2700
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    c.allow_observer_congress_review=c.allow_one_more_turn=True
    session=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    manifest=next(Path(pins['packages']['csc']['path']).glob('*.modinfo'))
    original=manifest.read_bytes()
    require(original==(root/'candidate.modinfo').read_bytes(),'Installed manifest changed before replay')
    staged_path=manifest
    active=original
    if mode=='stock':
        doc=ET.fromstring(original)
        actions=doc.find('InGameActions');connectors=actions.find("UpdateDatabase[@id='CSC_AI_Connectors']")
        require(connectors is not None,'Expected native action')
        actions.remove(connectors)
        active=ET.tostring(doc,encoding='utf-8',xml_declaration=True)
    if deposit_cues:
        require(mode in ('native','advanced'),'The stock control must keep ordinary AI')
        staged_path=manifest.parent/'Data/CSC_Q_ALL_AI_Connectors.sql'
        require(sha(staged_path)==load(root/'material-candidate.json')['full'],'Underlying connector revision changed')
        original=staged_path.read_bytes()
        addition=(HERE/'undeveloped_material_candidate.sql').read_bytes()
        active=original+b'\n'+addition
        (out/'deposit-treatment.sql').write_bytes(addition)
    write_json(out/'protocol.json',dict(seed=seed,turn=end,mode=mode,shared_save=record['sha256'],
        opening=source.name,deposit_cues=deposit_cues,active_file=staged_path.name,
        active_sha256=hashlib.sha256(active).hexdigest()))
    try:
        if active!=original:replace(staged_path,active)
        session.start(lambda:launch(SimpleNamespace(binary=Path(pins['binary'])),out))
        session.wait_context('MainMenu')
        select_stack(session,out,[pins['packages'][key]['id'] for key in enabled])
        def eligible():
            return read_opening(c,out,game['roster'],csc=True,cl=False,ce=ce)
        session.load_once(record['native_save'],sha256=record['sha256'],native_directory=saves,turn=1,
            contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=eligible,timeout=600)
        require(load(source/'source.json')==load(out/'source.json'),'Map or seats differ')
        fork=Path(pins['packages']['ce']['path'])/'Binaries/Win64'/DLL if ce else None
        verify_modules(session,fork,out,pins['core_sha256'])
        code=f"local native={lua(mode!='stock')};local advanced={lua(ce)};local deposits={lua(deposit_cues)}\n"+"""
assert((GameInfo.Yields.YIELD_CSC_AI_PLACEMENT~=nil)==native)
assert((CSC_AI_EconomyAdapters~=nil)==advanced)
local edges,materialRules,depositRules=0,0,0
for r in GameInfo.District_Adjacencies() do
 if string.find(r.YieldChangeId,'CSC_AI_QUARTER_',1,true)==1 then edges=edges+1 end
 if string.find(r.YieldChangeId,'CSC_AI_SUPPLIER_',1,true)==1 then materialRules=materialRules+1 end
 if string.find(r.YieldChangeId,'CSC_AI_DEPOSIT_',1,true)==1 then depositRules=depositRules+1 end
end
assert((edges>0)==native and (materialRules>0)==native and (depositRules>0)==deposits)
print('CSC_LIGHT_MODE_OK',edges,tostring(GameConfiguration.GetValue('CSC_ADVANCED_AI_PLANNING')),materialRules,depositRules)
"""
        raw=c.cmd(code,'CSC_AI_BakersGameplay','verify-running-treatment')
        require('CSC_LIGHT_MODE_OK' in raw,'Runtime tuning mode differs')
        (out/'mode.txt').write_text(raw,encoding='utf8')
        controls=stock_controls(user/'Cache/DebugGameplay.sqlite')
        write_json(out/'stock-controls.json',controls)
        if mode!='stock':
            require(controls['builder_priority']==[(1,10)] and controls['recruiting_city']==[(13,None),(23,None)],
                    'Expected the stock city bindings and the standalone Builder request preference')
        observers(c,range(1,len(game['roster'])))
        for turn in range(5,end+1,5):c.play(turn)
        ck=save_inactive_boundary(c,turn=end,name=f'CSC_LIGHT_{seed}_{arm_name.upper()}_T{end}',
                                  native_directory=saves,archive=out/'endpoint.Civ6Save')
        write_json(out/'checkpoint.json',ck)
    finally:
        try:
            if session.owner is not None and session.owner.poll() is None:
                session.close(restore_preferences=lambda:restore_preferences(c,out) if
                    (out/'original-preferences.json').is_file() else None,menu_timeout=600)
        finally:
            if session.closed:
                shutil.copyfile(user/'Logs/Lua.log',out/'Lua.log')
            if active!=original and not native_inventory():
                require(staged_path.read_bytes()==active,'Installed benchmark input changed during replay')
                replace(staged_path,original)
    log=read(out/'Lua.log')
    require('CSC_MILESTONE_SERVICE_FAULT' not in log and 'CSC_QUARTER_WATCH_FAULT' not in log,'Observer fault')
    require(set(archive_censuses(log,out))==set(range(25,end+1,25)),'Incomplete physical census')
    times,excluded,direct=observed_turns(out,end,2)
    require(bool(direct['published_packets'])==ce,'Unexpected advanced publications')
    write_json(out/'measured.json',dict(clean=times,direct=direct['publisher_wall'],
        excluded={t:sorted(v) for t,v in excluded.items()}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('seed',type=int)
    p.add_argument('mode',choices=['prepare','verify-off','prepare-advanced','native','stock','advanced'])
    p.add_argument('--ce-opening',action='store_true',help='Use the separately verified same-seed CE opening')
    p.add_argument('--deposit-cues',action='store_true',help='Test the undeveloped-resource class cue on this seed')
    p.add_argument('--end',type=int,default=250);p.add_argument('--label')
    a=p.parse_args();replay(a.root,a.seed,a.mode,a.end,a.label,a.ce_opening,a.deposit_cues)
