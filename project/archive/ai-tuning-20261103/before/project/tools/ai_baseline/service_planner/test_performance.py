"""No sockets: framed discovery, real Lua delta invalidation, bundled exports."""
import copy,json,struct,types,unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from full_game_controller.discovery import query_states
from full_game_controller import controller as core
from .native_adapter import NativeAdapter
from .donation_diagnostic import Diagnostic
from .policy import Planner,Policy
from .test_material import observation
from lupa.lua51 import LuaRuntime

class FakeSocket:
    def __init__(self,chunks):self.chunks=list(chunks);self.sent=[];self.reads=0
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def settimeout(self,t):pass
    def shutdown(self,*a):pass
    def sendall(self,b):self.sent.append(b)
    def recv(self,n):self.reads+=1;return self.chunks.pop(0)
def frame(s):
    b=s.encode();return struct.pack('<II',len(b),1)+b

class DiscoveryTests(unittest.TestCase):
    def test_busy_discovery_retries_before_any_command_transmission(self):
        class Base:
            def __init__(self,out):self.required_state='GameCore_Tuner'
        discover=unittest.mock.Mock(side_effect=[RuntimeError('No responsive tuner states'),RuntimeError('No responsive tuner states'),(4318,{'GameCore_Tuner':10})])
        diag=types.SimpleNamespace(journal=unittest.mock.Mock())
        f=core.make_controller(Base,diagnostics=diag,boundary_decision=None,tuner_port=4318,state_discovery=discover)('.')
        with patch.object(core.time,'sleep')as sleep:self.assertEqual(f.states(),{'GameCore_Tuner':10})
        self.assertEqual(discover.call_count,3);self.assertEqual(sleep.call_count,2)
        self.assertTrue(all(c.kwargs['no_command_sent']for c in diag.journal.call_args_list))
    def test_factory_uses_fresh_discovery_and_matching_port(self):
        class Base:
            def __init__(self,out):self.required_state=None
            def states(self):raise AssertionError('Legacy fixed-window discovery')
        calls=[]
        def discover(required):calls.append(required);return 4319,{'PlotInfo':17}
        f=core.make_controller(Base,diagnostics=None,boundary_decision=None,tuner_port=4318,state_discovery=discover)('.')
        f.required_state='PlotInfo';self.assertEqual(f.states(),{'PlotInfo':17});f.states()
        self.assertEqual(calls,['PlotInfo','PlotInfo']);self.assertEqual(f.discovery_port,4319)
    def test_fragmented_list_finishes_without_fixed_receive_window(self):
        b=frame('L3\0GameCore_Tuner\0'+'4\0PlotInfo\0');s=FakeSocket([b[:3],b[3:12],b[12:]])
        self.assertEqual(query_states(4318,connect=lambda *a,**k:s),{'GameCore_Tuner':3,'PlotInfo':4})
        self.assertEqual(s.reads,3);self.assertEqual(s.sent[0][8:],b'LSQ:\0')
    def test_output_is_not_a_context_list(self):
        s=FakeSocket([frame('O\0unrelated output'),frame('L7\0GameCore_Tuner\0')])
        self.assertEqual(query_states(4318,connect=lambda *a,**k:s),{'GameCore_Tuner':7})
    def test_actual_native_unprefixed_state_list(self):
        s=FakeSocket([frame('0\0Main State\0'+'10\0GameCore_Tuner\0')])
        self.assertEqual(query_states(4318,connect=lambda *a,**k:s),{'Main State':0,'GameCore_Tuner':10})
    def test_truncated_frame_never_yields_partial_ids(self):
        s=FakeSocket([frame('L3\0GameCore_Tuner\0')[:-2],b''])
        with self.assertRaises(EOFError):query_states(4318,connect=lambda *a,**k:s)

LUA=r'''
state={turn=88,pop=5,can=true,placed=false,tech=false,civic=false,heavy=0}
local function iterator(rows)return function()local i=0;return function()i=i+1;return rows[i]end end end
GameInfo={TypeTags=iterator({}),Resources={[1]={Index=1},[2]={Index=2}},
Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=10,Hash=100},DISTRICT_CSC_TAILORS_QUARTER={Index=11,Hash=101}},
Technologies=iterator({{Index=1}}),Civics=iterator({{Index=1,CivicType='CIVIC_TEST'}}),Yields={YIELD_PRODUCTION={Index=1}},Units={},Buildings={},Projects={}}
Game={GetCurrentGameTurn=function()return state.turn end}
AutoplayManager={IsActive=function()return false end}
UI={GetInterfaceModeParameter=function()return true end}
CityCommandTypes={PARAM_PLOT_PURCHASE=1,PARAM_X=2,PARAM_Y=3,PURCHASE=4}
CityCommandResults={PLOTS=1};CityOperationTypes={PARAM_DISTRICT_TYPE=1,PARAM_X=2,PARAM_Y=3,BUILD=4};CityOperationResults={PLOTS=1}
CityManager={GetOperationTargets=function()return {[1]={0}}end,CanStartOperation=function()return true end,GetCommandTargets=function()return {[1]={0}}end,CanStartCommand=function()return true,{[1]={0}}end}
plots={}
for i=0,2 do local p={index=i,owner=-1,resource=-1,improvement=-1,pillaged=false,feature=-1,district=-1,revealed=true}
function p:GetIndex()return self.index end;function p:GetX()return self.index end;function p:GetY()return 0 end
function p:GetOwner()return self.owner end;function p:GetResourceType()return self.resource end
function p:GetImprovementType()return self.improvement end;function p:IsImprovementPillaged()return self.pillaged end
function p:GetDistrictType()return self.district end;function p:GetFeatureType()return self.feature end
function p:GetTerrainType()return 0 end;function p:IsRiver()return false end
function p:CanHaveDistrict()state.heavy=state.heavy+1;return true end
plots[i]=p end
Map={GetPlotCount=function()return 3 end,GetPlotByIndex=function(i)return plots[i]end,GetPlotDistance=function(x,y,a,b)return math.abs(x-a)end,
GetAdjacentPlots=function(x,y)local rows={};for i,p in pairs(plots)do if i~=x then rows[#rows+1]=p end end;return rows end}
local q={GetSize=function()return 0 end,GetCurrentProductionTypeHash=function()return 0 end,CanProduce=function()return state.can,{}end,HasBeenPlaced=function()return state.placed end}
local ds={HasDistrict=function()return state.placed end}
local culture={HasCivic=function()return state.civic end,GetNextPlot=function()return -1 end,GetTurnsUntilExpansion=function()return 5 end}
local gold={GetPlotPurchaseCost=function()return 25 end}
city={GetID=function()return 10 end,GetX=function()return 0 end,GetY=function()return 0 end,GetPopulation=function()return state.pop end,
GetBuildQueue=function()return q end,GetDistricts=function()return ds end,GetGrowth=function()return {}end,GetYield=function()return 10 end,GetCulture=function()return culture end,GetGold=function()return gold end}
local cities={Members=function()local i=0;return function()i=i+1;if i==1 then return i,city end end end,GetCount=function()return 1 end}
local tr={GetGoldBalance=function()return 50 end,GetGoldYield=function()return 10 end,GetTotalMaintenance=function()return 2 end}
player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,GetCities=function()return cities end,
GetTreasury=function()return tr end,GetEra=function()return 1 end,GetTechs=function()return {HasTech=function()return state.tech end}end,GetCulture=function()return culture end}
Players={[1]=player};PlayersVisibility={[1]={IsRevealed=function(self,x,y)return plots[x].revealed end}}
Events={};function print(s)output=s end
'''

class DeltaLuaTests(unittest.TestCase):
    def setUp(self):
        self.e=LuaRuntime(unpack_returned_tuples=True);self.e.execute(LUA)
        here=Path(__file__).parent
        for f in ('native_delta.lua','native_observer.lua'):self.e.execute((here/f).read_text())
        self.e.execute('CSC_SERVICE_NATIVE.delta_mode=true;CSC_SERVICE_NATIVE.material_first=true;CSC_SERVICE_NATIVE.external_venues={};CSC_SERVICE_NATIVE.venues_turn=88;CSC_SERVICE_NATIVE.external_quarters={};CSC_SERVICE_NATIVE.quarters_turn=88')
    def read(self,turn=88):
        self.e.execute(f'state.turn={turn};CSC_SERVICE_NATIVE.quarters_turn={turn};CSC_SERVICE_NATIVE.venues_turn={turn};CSC_SERVICE_NATIVE.Read()')
        return json.loads(self.e.globals().output.split('=',1)[1])
    def test_unchanged_scope_skips_all_native_placement_projection(self):
        self.assertEqual(len(self.read()['cities']),1);n=self.e.globals().state.heavy
        r=self.read(89);self.assertEqual(len(r['cities']),0);self.assertEqual(len(r['unchanged']),1)
        self.assertEqual(self.e.globals().state.heavy,n)
    def test_all_relevant_deltas_refresh_immediately(self):
        for change in ('plots[0].owner=1','plots[1].resource=1','plots[1].improvement=2','plots[1].pillaged=true','plots[0].district=3','plots[0].feature=2','plots[1].revealed=false','state.pop=6','state.tech=true','state.civic=true','state.can=false','state.placed=true'):
            self.setUp();self.read();self.e.execute(change)
            self.assertEqual(len(self.read(89)['cities']),1,change)
    def test_periodic_reconciliation_and_force_refresh(self):
        self.read();self.assertEqual(len(self.read(113)['cities']),1)
        self.e.execute('CSC_SERVICE_NATIVE.delta_force_refresh=true')
        self.assertEqual(len(self.read(114)['cities']),1)

class CandidateCacheTests(unittest.TestCase):
    def test_changed_city_invalidates_marks_and_scan_timestamp_together(self):
        o=observation();o['district_state']={};o['broad_scan']=True
        responses=[dict(turn=88,cities=[copy.deepcopy(o)],players=[{'player':1,'gold':5}]),dict(turn=89,cities=[copy.deepcopy(o)],players=[{'player':1,'gold':9}])]
        runner=types.SimpleNamespace(cmd=lambda *a,**kw:'CSC_SERVICE_NATIVE='+json.dumps(responses.pop(0)))
        a=NativeAdapter(runner,'.',lambda *x:None,lambda v:'{}',material_first=True);a.delta_mode=True;a.planner=Planner(Policy.material_first_v2())
        a.collect(88);a.planner.update(1,10,88,[])
        a.collect(89)
        self.assertTrue(a.planner.wide_due(1,10,89));self.assertNotIn((1,10),a.planner.cache)
    def test_unchanged_candidates_reuse_routes_but_refresh_clock(self):
        d=object.__new__(Diagnostic);a=types.SimpleNamespace(delta_mode=True,cities={(1,10):observation()})
        with patch('service_planner.donation_diagnostic.candidates',return_value=[])as f:
            d.city_candidates(a,(1,10),88);d.city_candidates(a,(1,10),89);self.assertEqual(f.call_count,1)
            a.cities[1,10]['tiles']=copy.deepcopy(a.cities[1,10]['tiles'])
            d.city_candidates(a,(1,10),89);self.assertEqual(f.call_count,2)
    def test_adapter_rehydrates_unchanged_cities_without_candidate_rebuild(self):
        o=observation();o['district_state']={};o['broad_scan']=True
        responses=[dict(turn=88,cities=[o],players=[{'player':1,'gold':5}]),dict(turn=89,cities=[],unchanged=[{'player':1,'city':10}],players=[{'player':1,'gold':9}])]
        runner=types.SimpleNamespace(cmd=lambda *a,**kw:'CSC_SERVICE_NATIVE='+json.dumps(responses.pop(0)))
        writes=[];a=NativeAdapter(runner,'.',lambda *x:writes.append(x),lambda v:'{}',material_first=True)
        a.delta_mode=True;a.candidates=unittest.mock.Mock(return_value={})
        a.collect(88);a.collect(89)
        self.assertIn((1,10),a.cities);self.assertEqual(a.candidates.call_count,1)
        self.assertEqual(a.players[1]['gold'],9);self.assertEqual(a.cities[1,10]['delta_full_read_turn'],88)
        self.assertEqual(len(a.data['cities']),1)

class BundleTests(unittest.TestCase):
    def test_single_command_preserves_raw_current_and_observer_prefixes(self):
        from .boundary_bundle import capture
        payloads={'CSC_QUARTER_SITES':{'turn':88,'cities':{}},'CSC_CHAIN_METRICS':{'turn':88,'errors':[]},'CSC_CURRENT_PRIMARY':{'turn':88},'CSC_SERIES_RESEARCH':{'turn':88,'errors':[],'history':[1]},'CSC_BUILDERS_SNAPSHOT':{'turn':88,'events':[2]}}
        cmd=unittest.mock.Mock(return_value='\n'.join(k+'='+json.dumps(v)for k,v in payloads.items()));writes={}
        result=capture(types.SimpleNamespace(cmd=cmd),'.',lambda p,v:writes.update({p.name:v}),88)
        self.assertEqual(cmd.call_count,1);self.assertEqual(writes['research-latest.json']['history'],[1])
        self.assertEqual(writes['failure-preserved-builders-current.json']['events'],[2])
        self.assertEqual(result['primary']['turn'],88)
        self.assertNotIn('checkpoints={}',cmd.call_args.args[0])

class WarmHistoryTests(unittest.TestCase):
    def test_reporter_and_watchdog_metadata_required_before_native_work(self):
        from full_game_controller.run_metadata import validate
        from full_game_controller.renderer_evidence import review
        with tempfile.TemporaryDirectory(dir=Path.cwd())as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(AssertionError,'Missing run metadata'):validate(root)
            values={'run-start.json':{'time':1},'game-process.json':{'pid':123},'original-preferences.json':{},'original-installed-manifest.json':{},'installed-original-hashes.json':{},'settings.json':{},'log-offsets.json':{}}
            for name,value in values.items():(root/name).write_text(json.dumps(value))
            (root/'diagnostics').mkdir();validate(root)
            self.assertIsNone(review(root)['at_or_after_run_start_events'])
    def test_confirmed_history_restores_counts_without_native_actions(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd())as tmp:
            p=Path(tmp)/'parent';p.mkdir();r=Path(tmp)/'current';r.mkdir()
            request=dict(token='old:88',player=1,city=10,quarter='TAILORS')
            receipt=dict(status='confirmed',original_gold=5,final_gold=5,donated=20,spent=20,steps=[{}])
            site=dict(player=1,city=10,quarter='TAILORS',plot=42)
            rows=[dict(event='donated-acquisition-begin',request=request),dict(event='donated-acquisition-confirmed',request=request,receipt=receipt),dict(event='foundation-begin',**site),dict(event='foundation-confirmed',proof={'verified':True},**site)]
            (p/'service-actions.ndjson').write_text('\n'.join(json.dumps(x)for x in rows)+'\n')
            runner=types.SimpleNamespace(cmd=unittest.mock.Mock(side_effect=AssertionError('No native replay')))
            d=Diagnostic(runner,r,lambda *a:None,lambda x:'{}');x=d.inherit_confirmed(p)
            self.assertEqual((d.grants,d.spent,d.tiles,d.foundations),(20,20,1,1));self.assertIn((1,10,'TAILORS'),d.completed)
            runner.cmd.assert_not_called();self.assertEqual(x['replayed_native_actions'],0)
    def test_unconfirmed_begin_blocks_warm_replay(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd())as tmp:
            p=Path(tmp)/'parent';p.mkdir();r=Path(tmp)/'current';r.mkdir()
            (p/'service-actions.ndjson').write_text(json.dumps(dict(event='donated-acquisition-begin',request={'token':'pending'}))+'\n')
            d=Diagnostic(None,r,lambda *a:None,lambda x:'{}')
            with self.assertRaisesRegex(AssertionError,'Unconfirmed acquisition'):d.inherit_confirmed(p)
