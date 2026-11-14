"""Passive full-run observations using the established baseline census rows.

No production intervention lives here. The shared controller still owns the
session and every game order. Census events read facts every25 turns; health
checks expose missing consumers, while per-turn main CSC logs retain actual
publication/receipt history. A property is labelled separately from a realised
Service effect. The existing Storekeeper watcher supplies that extra evidence.
"""
from pathlib import Path
import re
from driver import lua,read,write_json,require
from customer_adjacency_policy import database_snapshot,qualify_database

HERE=Path(__file__).resolve().parent


def archive_censuses(log,out):
    active=None;rows=[];snapshots={}
    for line in log.splitlines():
        start=re.search(r'CSC_FULL_RUN_CENSUS_BEGIN\s+(\d+)',line)
        if start:
            require(active is None,'Overlapping full-game census')
            active=int(start[1]);rows=[];continue
        end=re.search(r'CSC_ENDPOINT_END\s+(\d+)\s+(\d+)',line)
        if end and active is not None:
            require(int(end[1])==active and int(end[2])==len(rows),'Incomplete full-game census')
            require(active not in snapshots,'Duplicate full-game census turn')
            snapshots[active]=dict(turn=active,phase='turn-start',rows=rows+[['END',end[1]+'\t'+end[2]]])
            active=None;continue
        row=re.search(r'CSC_ENDPOINT_([A-Z_]+)\t([^\r\n]+)',line)
        if row and active is not None:rows.append([row[1],row[2]])
    require(active is None,'Unfinished full-game census')
    for turn,value in snapshots.items():write_json(out/('full-census-'+str(turn)+'.json'),value)
    return snapshots


def install(controller,out,players,user_root,endpoint,*,planning=False,extra_mods=None,csc_path=None,start=1):
    # Short diagnostic qualification uses the same passive observers/policy as
    # the full games; it cannot claim long-run outcome evidence.
    require(endpoint in (25,50,200,250),'Integrated observations end at25/50/200/250')
    scope=lua(dict(players=sorted(players),start=start))
    preflight=read(HERE/'full_game_preflight.lua').replace('__SCOPE__',scope)
    raw=controller.cmd(preflight,'CSC_AI_BakersGameplay','full-game-capability-preflight')
    require('CSC_FULL_RUN_PREFLIGHT_OK' in raw,'Missing capability preflight acknowledgement')
    (out/'full-game-preflight.txt').write_text(raw,encoding='utf-8')
    db=database_snapshot(user_root/'Cache/DebugGameplay.sqlite')
    write_json(out/'loaded-native-customer-database.json',db);qualify_database(db,'on')
    census=read(HERE/'full_game_census.lua')
    code='''-- Read-only trial observer. No bids, queue orders or game-property writes.
local seats=__PLAYERS__
local function collect()
__CENSUS__
end
assert(CSC_FULL_RUN_Observation==nil,'Duplicate observer')
CSC_FULL_RUN_Observation={last=-1}
GameEvents.OnGameTurnStarted.Add(function()
 local turn=Game.GetCurrentGameTurn()
 if turn%25~=0 or turn>250 or CSC_FULL_RUN_Observation.last==turn then return end
 CSC_FULL_RUN_Observation.last=turn
 local ok,error=pcall(function()
  CSC_FULL_RUN_Health()
  CSC_ENDPOINT_PLAYERS=seats;CSC_ENDPOINT_EXPECTED_TURN=turn
  print('CSC_FULL_RUN_CENSUS_BEGIN',turn)
  collect()
 end)
 if not ok then print('CSC_FULL_RUN_OBSERVATION_FAILED',turn,tostring(error))end
end)
print('CSC_FULL_RUN_OBSERVATION_INSTALLED')
'''.replace('__PLAYERS__',lua(sorted(players))).replace('__CENSUS__',census)
    (out/'full-game-observer.lua').write_text(code,encoding='utf-8')
    raw=controller.cmd(code,'CSC_AI_BakersGameplay','install-passive-full-game-observer')
    require('CSC_FULL_RUN_OBSERVATION_INSTALLED'in raw,'Observer did not acknowledge installation')
    placement=read(HERE/'quarter_placement_watch.lua')
    (out/'quarter_placement_watch.lua').write_text(placement,encoding='utf-8')
    raw=controller.cmd(placement,'CSC_AI_BakersGameplay','install-read-only-quarter-lifecycle')
    require('CSC_QUARTER_WATCH_INSTALLED'in raw and 'CSC_QUARTER_WATCH_FAULT'not in raw,
        'Quarter lifecycle observer failed to initialise')
    if planning:
        from resource_stack_preflight import inspect_resource_stack
        resource_stack=inspect_resource_stack(controller,out,user_root,extra_mods or {},csc_path=csc_path)
        origins=resource_stack['origins']
        catalogue=controller.cmd('''
for d in GameInfo.Districts()do
 print('CSC_DISTRICT_CATALOGUE',d.Index,d.DistrictType,tostring(d.RequiresPopulation),tostring(d.Cost),
  tostring(d.PrereqTech),tostring(d.PrereqCivic))
end
for d in GameInfo.DistrictReplaces()do print('CSC_DISTRICT_REPLACEMENT',d.CivUniqueDistrictType,d.ReplacesDistrictType)end
print('CSC_DISTRICT_CATALOGUE_END')
''','CSC_AI_BakersGameplay','loaded-district-catalogue')
        (out/'loaded-district-catalogue.txt').write_text(catalogue,encoding='utf-8')
        require('CSC_DISTRICT_CATALOGUE_END'in catalogue,'District catalogue incomplete')
        planning_code='CSC_PLANNING_RESOURCE_ORIGINS='+lua(origins)+'\n'+read(HERE/'planning_observer.lua')
        (out/'planning_observer.lua').write_text(planning_code,encoding='utf-8')
        raw=controller.cmd(planning_code,'CSC_AI_BakersGameplay','install-passive-planning-observer')
        (out/'planning-observer-install.txt').write_text(raw,encoding='utf-8')
        require('CSC_PLANNING_INSTALLED'in raw and 'CSC_PLANNING_FAULT'not in raw,
                'Planning observer did not initialize cleanly')
        ui_code=read(HERE/'district_adjacency_watch.lua')
        (out/'district_adjacency_watch.lua').write_text(ui_code,encoding='utf-8')
        raw=controller.cmd(ui_code,'PlotInfo','install-passive-ui-district-adjacency')
        require('CSC_DISTRICT_UI_INSTALLED'in raw and 'CSC_DISTRICT_UI_FAULT'not in raw,
                'UI district observer failed to initialize')
    for name in('full_game_census.lua','full_game_preflight.lua','full_game_observation.py','storekeeper_runtime.lua'):
        (out/name).write_bytes((HERE/name).read_bytes())


def finish(out,endpoint=250,*,start=1):
    log=read(out/'Lua.log')
    for failure in('CSC_AI_BAKERS_DISTRICTS_FAILED','CSC_AI_INDUSTRY_PLACEMENT_FAILED',
            'CSC_FULL_RUN_OBSERVATION_FAILED','CSC_QUARTER_WATCH_FAULT','CSC_PLANNING_FAULT',
            'CSC_PLANNING_LIMIT','CSC_DISTRICT_UI_FAULT'):
        require(failure not in log,'Integrated run logged '+failure)
    snapshots=archive_censuses(log,out)
    require(set(snapshots)==set(range(25*(start//25+1),endpoint+1,25)),'Missing full-game milestone')
    write_json(out/'full-game-observation-complete.json',dict(verified=True,start=start,turns=sorted(snapshots)))


def observe_inactive_storekeeper(controller,out,turn):
    """Observe the exact UI clock or defer to its passive TurnBegin watcher.

    Core can reach an inactive boundary before the UI publishes that clock.
    The first200 trial observed Core55/UI54; the retry showed that this lag
    can persist while inactive. Waiting cannot make the UI start its next
    turn. Keep a separate deferral receipt, then allow ordinary play to publish
    that UI clock. The terminal Service audit still verifies actual coverage.
    Never relabel54 as55 or resend any gameplay order to settle observation.
    A later UI clock or malformed reply remains a hard failure.
    """
    reader=read(out/'storekeeper_runtime.lua')
    code=("if Game.GetCurrentGameTurn()=="+str(turn)+" then\n"
        +'CSC_BAKERS_STOREKEEPER_WATCH=false\n'+reader
        +"\nelse print('CSC_FULL_RUN_UI_CLOCK_DEFERRED',Game.GetCurrentGameTurn()) end")
    raw=controller.cmd(code,'PlotInfo','storekeeper-inactive-boundary-'+str(turn))
    if re.search(r'CSC_STOREKEEPER_END\t'+str(turn)+r'\t',raw):return True
    pending=re.search(r'CSC_FULL_RUN_UI_CLOCK_DEFERRED\s+(\d+)',raw)
    require(pending and int(pending[1])<turn,'Unexpected inactive-boundary Storekeeper reply')
    write_json(out/('deferred-ui-boundary-'+str(turn)+'.json'),
        dict(core_turn=turn,ui_turn=int(pending[1]),deferred=True,relabeled=False))
    return False


def observe_purchase_contexts(controller,out,batch,boundary):
    """Join native XY to later live map facts without inventing native intent.

    Native events retain their original turn and measured funds. These facts
    are explicitly at the inactive drain boundary (up to five turns later), so
    a resource subsequently harvested cannot be described as absent at payment.
    Actual SetOwner before/after and debit evidence remain in the native journal.
    """
    targets=set()
    for row in batch['records']:
        if 'plot'in row and 'player'in row:targets.add((row['player'],row['plot']))
        for candidate in row.get('candidates',[]):
            if candidate.get('cached'):targets.add((candidate['player'],candidate['cached']['plot']))
    if not targets:return
    require(len(targets)<=512,'Purchase-context observation bound exceeded')
    code='local targets='+lua([list(t)for t in sorted(targets)])+'''
local A=assert(CSC_Adjacency)
for _,target in ipairs(targets)do
 local pid,index=target[1],target[2];local plot=assert(Map.GetPlotByIndex(index))
 local resource=GameInfo.Resources[plot:GetResourceType()]
 local improvement=GameInfo.Improvements[plot:GetImprovementType()]
 for _,family in ipairs({'BAKERS','TAILORS'})do
  local base=resource and A.HasTag('CLASS_CSC_'..family..'_BASE',resource.ResourceType)or false
  local spec=resource and A.HasTag('CLASS_CSC_'..family..'_SPEC',resource.ResourceType)or false
  local adjacent={}
  for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
   if near:GetOwner()==pid and near:GetDistrictType()==GameInfo.Districts['DISTRICT_CSC_'..family..'_QUARTER'].Index then
    adjacent[#adjacent+1]=near:GetIndex()
   end
  end
  print('CSC_PURCHASE_CONTEXT',Game.GetCurrentGameTurn(),pid,index,plot:GetOwner(),plot:GetDistrictType(),
   resource and resource.ResourceType or'NONE',improvement and improvement.ImprovementType or'NONE',
   family,tostring(base),tostring(spec),table.concat(adjacent,','),'laterBoundaryFacts')
 end
end
print('CSC_PURCHASE_CONTEXT_END',Game.GetCurrentGameTurn(),#targets)
'''
    raw=controller.cmd(code,'CSC_AI_BakersGameplay','purchase-context-'+str(boundary))
    (out/('purchase-context-'+str(boundary)+'.txt')).write_text(raw,encoding='utf-8')
    require('CSC_PURCHASE_CONTEXT_END'in raw,'Incomplete purchase map context')


def play(controller,out,user_root,*,start,endpoint,saves=None,savings=None):
    """Use the shared controller's guarded five-turn operations throughout.

    Observer-popup and victory handlers require a remaining budget <=5. Do
    not bypass their guards with one250-turn activation. TurnBegin's passive
    Storekeeper watcher skips the inactive handoff clock, so read that same
    clock once when its END row is absent. This repairs observation coverage,
    never a chain, score, queue, treasury or native operation.
    """
    controller.allow_one_more_turn=True
    cursor=start
    while cursor<endpoint:
        # Land on each25-turn milestone as well as respecting the five-turn
        # budget. This permits exact inactive200/250 evidence and useful
        # natural checkpoints for a later matched SQL replay.
        boundary=min(cursor+5,endpoint,25*(cursor//25+1))
        if savings:savings.window(cursor,boundary)
        controller.play(boundary)
        if savings:
            batch=savings.drain()
            observe_purchase_contexts(controller,out,batch,boundary)
        if boundary<endpoint:
            log=read(user_root/'Logs/Lua.log')
            if not re.search(r'CSC_STOREKEEPER_END\t'+str(boundary)+r'\t',log):
                observe_inactive_storekeeper(controller,out,boundary)
        write_json(out/'full-game-last-boundary.json',dict(verified=True,turn=boundary,endpoint=endpoint))
        if saves is not None and boundary in(50,100,150,200):
            from full_game_controller.checkpoint import save_inactive_boundary
            checkpoint=save_inactive_boundary(controller,turn=boundary,name='CSC_AI_HARMONISED_'+str(boundary),
                native_directory=saves,archive=out/('turn-'+str(boundary)+'.Civ6Save'))
            write_json(out/('checkpoint-'+str(boundary)+'.json'),checkpoint)
        cursor=boundary
    raw=controller.cmd("CSC_QUARTER_PLACEMENT_WATCH.Drain();print('CSC_QUARTER_WATCH_DRAINED')",
        'CSC_AI_BakersGameplay','drain-final-placement-journal')
    require('CSC_QUARTER_WATCH_DRAINED'in raw and 'CSC_QUARTER_WATCH_FAULT'not in raw,
        'Final Quarter journal read failed')
    if (out/'planning_observer.lua').exists():
        raw=controller.cmd("CSC_AI_PLANNING_WATCH.Finish();print('CSC_PLANNING_FINISHED')",
            'CSC_AI_BakersGameplay','finish-passive-planning-observer')
        require('CSC_PLANNING_FINISHED'in raw and 'CSC_PLANNING_FAULT'not in raw,
                'Final passive planning observation failed')
