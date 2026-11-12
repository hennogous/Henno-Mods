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


def install(controller,out,players,user_root,endpoint):
    require(endpoint in (200,250),'Integrated trials end at200 or250')
    scope=lua(dict(players=sorted(players)))
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
    for name in('full_game_census.lua','full_game_preflight.lua','full_game_observation.py','storekeeper_runtime.lua'):
        (out/name).write_bytes((HERE/name).read_bytes())


def finish(out,endpoint=250):
    log=read(out/'Lua.log')
    for failure in('CSC_AI_BAKERS_DISTRICTS_FAILED','CSC_AI_INDUSTRY_PLACEMENT_FAILED',
            'CSC_FULL_RUN_OBSERVATION_FAILED'):
        require(failure not in log,'Integrated run logged '+failure)
    snapshots=archive_censuses(log,out)
    require(set(snapshots)==set(range(25,endpoint+1,25)),'Missing full-game milestone')
    write_json(out/'full-game-observation-complete.json',dict(verified=True,turns=sorted(snapshots)))


def play(controller,out,user_root,*,start,endpoint,saves=None):
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
        controller.play(boundary)
        if boundary<endpoint:
            log=read(user_root/'Logs/Lua.log')
            if not re.search(r'CSC_STOREKEEPER_END\t'+str(boundary)+r'\t',log):
                code='CSC_BAKERS_STOREKEEPER_WATCH=false\n'+read(out/'storekeeper_runtime.lua')
                raw=controller.cmd(code,'PlotInfo','storekeeper-inactive-boundary-'+str(boundary))
                require(re.search(r'CSC_STOREKEEPER_END\t'+str(boundary)+r'\t',raw),
                    'Missing inactive-boundary Storekeeper observation')
        write_json(out/'full-game-last-boundary.json',dict(verified=True,turn=boundary,endpoint=endpoint))
        if saves is not None and boundary in(50,100,150,200):
            from full_game_controller.checkpoint import save_inactive_boundary
            checkpoint=save_inactive_boundary(controller,turn=boundary,name='CSC_AI_HARMONISED_'+str(boundary),
                native_directory=saves,archive=out/('turn-'+str(boundary)+'.Civ6Save'))
            write_json(out/('checkpoint-'+str(boundary)+'.json'),checkpoint)
        cursor=boundary
