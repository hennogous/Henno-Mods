"""One normal queued repair in the preserved Mill study; no hooks or fresh map.

Only the initial pillage uses the Debug setter. Repair is requested through the
stock ProductionPanel BUILD operation and paid by ordinary turn production.
Never grant/recreate the Mill, clear pillage directly, or accelerate production.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(ROOT / 'project/tools/ai_baseline'), str(HERE)]
from driver import lua, parse, sha, stable_sample
from full_game_controller.environment import (launch, configure, flags, manifest,
    restore_preferences, write_json, archive_sources)
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory

GP = 'CSC_AdjacencyGameplay'
ID = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a09'

# Captures native payout and independent eligibility, rather than assuming that
# a correct property means the modifier actually pays. The second city remains
# an unchanged control. Event arguments are retained without interpreting their
# undocumented order as a completion receipt.
READER = r'''
assert(not CSC_REPAIR_CHECK,'Do not redefine an active repair check')
CSC_REPAIR_CHECK={events={}}
for _,name in ipairs({'CityProductionCompleted','DistrictPillageChanged','CityProductionChanged'}) do
 if Events[name] then Events[name].Add(function(...)
  local args={};for i=1,select('#',...) do args[i]=tostring(select(i,...)) end
  CSC_REPAIR_CHECK.events[#CSC_REPAIR_CHECK.events+1]={name=name,turn=Game.GetCurrentGameTurn(),args=args}
 end) end
end
function CSC_REPAIR_CHECK.Read()
 local rows={}
 for _,binding in ipairs({{65536,1986},{131073,2434}}) do
  local city=assert(CityManager.GetCity(0,binding[1]));local plot=assert(Map.GetPlotByIndex(binding[2]))
  local d=assert(city:GetDistricts():GetDistrictAtLocation(plot:GetX(),plot:GetY()))
  local w=GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL.Index;local b=city:GetBuildings()
  local prefix='CSC_ADJ_CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS_'
  rows[#rows+1]={city=city:GetID(),plot=plot:GetIndex(),district=d:GetID(),
   pillaged=d:IsPillaged(),complete=d:IsComplete(),hill=plot:IsHills(),
   production=d:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index),
   wind=b:HasBuilding(w),windPillaged=b:IsPillaged(w),windPlot=b:GetBuildingLocation(w),
   step=plot:GetProperty(prefix..'STEP_1') or 0,actual=plot:GetProperty(prefix..'ACTUAL_AMOUNT') or 0}
 end
 return {facts=rows,turn=Game.GetCurrentGameTurn(),events=CSC_REPAIR_CHECK.events}
end
'''

# ProductionPanel's queue accessors belong to the UI city interface. Keep them
# out of the gameplay reader: the gameplay object does not expose the same API.
QUEUE_READ = r'''
local c=assert(CityManager.GetCity(0,65536));local q=c:GetBuildQueue()
local d=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER
print('CSC_REPAIR_QUEUE={"hash":'..tostring(q:GetCurrentProductionTypeHash() or -1)..
 ',"size":'..tostring(q:GetSize())..',"progress":'..tostring(q:GetDistrictProgress(d.Index))..'}')
'''

# This is the stock non-placement ZoneDistrict branch, including replacement at
# queue position zero when the production manager is closed. UI legality is
# checked before issuing exactly one asynchronous request.
QUEUE = r'''
local city=assert(CityManager.GetCity(0,65536));local d=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER
assert(Game.GetLocalPlayer()==0 and Players[0]:IsHuman())
assert(city:GetBuildQueue():HasBeenPlaced(d.Hash))
local args={};args[CityOperationTypes.PARAM_DISTRICT_TYPE]=d.Hash
args[CityOperationTypes.PARAM_INSERT_MODE]=CityOperationTypes.VALUE_REPLACE_AT
args[CityOperationTypes.PARAM_QUEUE_DESTINATION_LOCATION]=0
local legal=CityManager.CanStartOperation(city,CityOperationTypes.BUILD,args,true)
local producible,reasons=city:GetBuildQueue():CanProduce(d.Hash,false,true)
print('CSC_REPAIR_CAN_PRODUCE',tostring(producible));for k,v in pairs(reasons or {}) do print('CSC_REPAIR_REASON',tostring(k),tostring(v)) end
print('CSC_REPAIR_QUEUE_LEGAL',tostring(legal));assert(legal,'Normal district repair operation unavailable')
CityManager.RequestOperation(city,CityOperationTypes.BUILD,args)
'''


def run(a):
    study, out = a.study.resolve(), a.output.resolve()
    retired = study / 'retired-study-package'
    installed = a.mods.resolve() / 'CSC Mill Building Study'
    if out.exists() or installed.exists() or native_inventory():
        raise RuntimeError('Require fresh output, absent test install and no native/Tuner owner')
    checkpoint = json.loads((study / 'run-03/source-checkpoint.json').read_text())
    source = Path(checkpoint['native_save'])
    if sha(source) != checkpoint['sha256'] or sha(checkpoint['archive']) != checkpoint['sha256']:
        raise RuntimeError('Preserved source checkpoint identity changed')
    expected = json.loads((study / 'run-03/content-before.json').read_text())
    package = manifest(retired)
    if package != expected[str(installed)]:
        raise RuntimeError('Retired package differs from original study')
    roots = [Path(p) for p in expected if Path(p) != installed]
    untouched = {str(p): manifest(p) for p in roots}
    out.mkdir(parents=True)
    sources = [Path(__file__), HERE / 'driver.py', HERE / 'fixture.lua']
    sources += list((ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*'))
    pins = {str(p.resolve()): sha(p) for p in sources if p.is_file()}
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    write_json(out / 'protocol.json', dict(fresh_worlds=0,loads=1,hooks=0,
        production_acceleration=False,maximum_turn=16,normal_BUILD_requests=1))
    shutil.copytree(retired, installed)
    def verify():
        assert manifest(installed) == package
        assert all(manifest(p) == untouched[str(p)] for p in roots)
        assert all(sha(p) == value for p, value in pins.items())
    c = make_probe_controller(out, user_root=a.user_root)
    c.study_endpoint=16
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    c.allow_observer_congress_review=True
    s = NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    error=None; result=None
    def read(label):
        value=parse(c.cmd('CSC_MillFixture.Print(CSC_REPAIR_CHECK.Read())',GP,label,wait=20),'CSC_MILL_FIXTURE')
        queue=parse(c.cmd(QUEUE_READ,'PlotInfo',label+'-queue',wait=20),'CSC_REPAIR_QUEUE')
        value['facts'][0].update(queueHash=queue['hash'],queueSize=queue['size'],progress=queue['progress'])
        write_json(out / (label+'.json'),value)
        return value
    try:
        verify();s.start(lambda:launch(a,out));s.wait_context('MainMenu')
        configure(c,out,'BASIC',csc_id=ID)
        assert {k for k,v in flags(c,'exclusive')['mods'].items() if v}=={ID}
        def eligible():
            c.cmd("assert(Game.GetCurrentGameTurn()==1 and Players[0]:IsHuman());assert(type(CE_AIDistrictScoresBegin)=='nil')",'GameCore_Tuner','eligibility')
            return True
        s.load_once(source,sha256=checkpoint['sha256'],native_directory=source.parent,
            turn=1,contexts=('GameCore_Tuner','PlotInfo',GP),eligibility=eligible)
        s.issue_once('define-reader',(HERE/'fixture.lua').read_text()+READER,GP)
        descriptor=json.loads((study/'run-03/source-fixture-descriptor.json').read_text())
        raw=c.cmd('CSC_MillFixture.Print(CSC_MillFixture.VerifyReload('+lua(descriptor)+'))',GP,'exact-source-parity')
        write_json(out/'exact-source-parity.json',parse(raw,'CSC_MILL_FIXTURE'))
        initial=stable_sample(lambda:read('initial'))
        assert initial['facts'][0]['production']==0 and not initial['facts'][0]['pillaged']
        # The old human yield fixture force-created its Quarter without research
        # grants. Unlike the two AI forecast cities it never unlocked the host
        # district. Grant only that civic to make an ordinary repair queue legal;
        # do not grant Mill technology, production, buildings or modifier state.
        s.issue_once('unlock-host-district',"local d=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER;assert(d.PrereqTech==nil and d.PrereqCivic=='CIVIC_CRAFTSMANSHIP');local culture=Players[0]:GetCulture();local index=GameInfo.Civics.CIVIC_CRAFTSMANSHIP.Index;print('CSC_REPAIR_CIVIC_BEFORE',culture:HasCivic(index));if not culture:HasCivic(index) then culture:SetCivic(index,true) end;assert(culture:HasCivic(index))",GP)
        # Re-pillage the retained objects so normal production has a real repair
        # job. No geometry, building or native modifier is replaced.
        s.issue_once('pillage',"local c=assert(CityManager.GetCity(0,65536));local p=Map.GetPlotByIndex(1986);local d=assert(c:GetDistricts():GetDistrictAtLocation(p:GetX(),p:GetY()));assert(not d:IsPillaged());d:SetPillaged(true)",GP)
        before=stable_sample(lambda:read('pillaged'))
        assert before['facts'][0]['pillaged'] and before['facts'][0]['production']==0
        s.issue_once('queue-normal-repair',QUEUE,'PlotInfo')
        queued=stable_sample(lambda:read('queued'))
        raw=c.cmd("print('CSC_REPAIR_HASH',GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Hash)",GP,'district-hash')
        import re
        district_hash=int(re.search(r'CSC_REPAIR_HASH\s+(-?\d+)',raw)[1])
        assert queued['facts'][0]['queueHash']==district_hash,'Repair not admitted at queue head'
        samples=[queued]
        for turn in range(2,17):
            verify();c.play(turn)
            current=stable_sample(lambda:read('turn-'+str(turn)))
            samples.append(current)
            write_json(out/'progress.json',dict(turn=turn,facts=current['facts']))
            if not current['facts'][0]['pillaged']:
                break
            if current['facts'][0]['queueHash']!=district_hash:
                raise RuntimeError('Native AI replaced repair before completion; no repair verdict')
        final=samples[-1]['facts'][0]
        completed=not final['pillaged']
        healthy=final['complete'] and final['wind'] and not final['windPillaged'] and final['windPlot']==1986 and final['hill']
        result=dict(completed=completed,turn=samples[-1]['turn'],healthy=healthy,
            expectedProduction=1,actualProduction=final['production'],step=final['step'],
            passed=completed and healthy and final['step']==1 and abs(final['production']-1)<1e-6,
            fresh_worlds=0,hooks=0,production_acceleration=False)
        write_json(out/'verdict.json',result)
    except BaseException as failure:
        error=failure
        write_json(out/'failure.json',dict(error=str(failure),traceback=traceback.format_exc(),no_replay=True))
    finally:
        if s.owner is not None and s.owner.poll() is None:
            s.close(restore_preferences=lambda:restore_preferences(c,out)
                if (out/'original-preferences.json').exists() else None,restore_package=verify)
        if native_inventory():
            raise RuntimeError('Owner remains; preserve installed package')
        verify()
        destination=out/'retired-study-copy'
        assert installed.resolve().parent==a.mods.resolve() and destination.parent==out
        installed.rename(destination)
        write_json(out/'restoration.json',dict(verified=manifest(destination)==package,
            closed=s.closed,untouched=all(manifest(p)==untouched[str(p)] for p in roots)))
    if error:raise error
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('study','output','mods','user-root','binary'):
        p.add_argument('--'+name,type=Path,required=True)
    run(p.parse_args())
