"""Qualify buyer/cash ambiguities before a source-identified live replay."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lupa.lua51 import LuaRuntime

from nicopolis_replay import CASES, WATCHER, SZEGED_SEAT_PROVENANCE, seed_source_seats, qualify_purchase, qualify_integrated_policy, ablate_frontier_offer, bypass_szeged_quote_screen
from driver import lua

FIXTURE = '''
prices={85,130,-1};bank=719;owner=-1;output={}
print=function(...)local args={...};for i=1,select('#',...)do args[i]=tostring(args[i])end
 output[#output+1]=table.concat(args,'\t')end
local ids={589829,524292,393216}
local cities={}
for i,id in ipairs(ids)do
 cities[i]={GetID=function()return id end,GetName=function()return i==1 and 'LOC_CITY_NAME_SZEGED' or 'Other' end,
  GetGold=function()return {GetPlotPurchaseCost=function(_,target)assert(target==1365);return prices[i]end}end,
  GetBuildQueue=function()return {CanProduce=function()return true end,GetCurrentProductionTypeHash=function()return 321 end}end,
  GetDistricts=function()return {GetNumAllowedDistrictsRequiringPopulation=function()return 2 end,
   GetNumZonedDistrictsRequiringPopulation=function()return 2 end}end}
end
local player={IsHuman=function()return false end,
 GetTreasury=function()return {GetGoldBalance=function()return bank end}end,
 GetCities=function()return {Members=function()local i=0;return function()i=i+1;if cities[i]then return i,cities[i]end end end}end}
Players={[2]=player};CityManager={GetCity=function(pid,id)assert(pid==2 and id==589829);return cities[1]end}
Map={GetPlotByIndex=function(id)assert(id==1365);return {GetOwner=function()return owner end,GetDistrictType=function()return -1 end}end}
GameInfo={Districts={[37]={Hash=10037}}};Game={GetCurrentGameTurn=function()return 200 end}
'''


class Controller:
    def __init__(self, change=''):
        self.vm=LuaRuntime()
        self.vm.execute(FIXTURE+change)

    def cmd(self, code, state, label):
        assert state=='PlotInfo'
        self.vm.execute(code)
        return '\n'.join(self.vm.globals().output.values())


class Qualification(unittest.TestCase):
    def test_qualification_uses_declared_checkpoint_clock(self):
        with tempfile.TemporaryDirectory()as folder:
            controller=Controller('Game.GetCurrentGameTurn=function()return 202 end')
            qualify_purchase(controller,Path(folder),dict(CASES['szeged'],turn=202))
            record=json.loads((Path(folder)/'source-purchase-qualification.json').read_text())
            self.assertTrue(record['verified'])

    def test_policy_gate_logs_zero_return_property_without_masking_inactivity(self):
        class PolicyController(Controller):
            def cmd(self,code,state,label):
                assert state=='CSC_AI_BakersGameplay'
                self.vm.execute(code)
                return '\n'.join(self.vm.globals().output.values())
        c=PolicyController()
        c.vm.execute('''
PlayerManager={GetAliveMajors=function()return {{GetID=function()return 2 end,IsHuman=function()return false end}}end}
Game.GetProperty=function()end -- native absent-property binding returns NO values
ExposedMembers={CSC_Adjacency={IsSinglePlayer=function()return true end}}
CSC_AI_DistrictBridge={Available=function()return true end,Status=function()return '{"ready":1,"faults":0,"enabled":0,"version":0}' end}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {{key='TAILORS',base='CLASS_CSC_TAILORS_BASE'}}end}
CSC_Adjacency={Tags={}}
''')
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaisesRegex(AssertionError,'inactive or unqualified'):
                qualify_integrated_policy(c,Path(path),CASES['szeged'])
            record=json.loads((Path(path)/'policy-qualification.json').read_text())
            self.assertEqual(record['seats'],[dict(player=2,originalHuman=None,human=False)])
            self.assertEqual(record['native']['enabled'],0)

    def test_seat_migration_validates_all_provenance_and_is_atomic_on_conflicts(self):
        base=Path('/fixture')
        original=dict(original_ai=[1,2,3,4,5],starts=[dict(player=i,leader='LEADER_TEST'+str(i)) for i in range(6)])
        def digest(path):return SZEGED_SEAT_PROVENANCE[path.relative_to(base).as_posix()]
        def metadata(path):return original if path.name=='source.json' else dict(untuned=True)
        with patch('nicopolis_replay.sha',side_effect=digest),patch('nicopolis_replay.load',side_effect=metadata):
            code,provenance=seed_source_seats(b'-- production sentinel',base,CASES['szeged'])
        self.assertEqual(provenance['files'],SZEGED_SEAT_PROVENANCE)
        for change in ('','properties.CSC_AI_OriginalHuman_5=0',
                'properties.CSC_AI_OriginalHuman_5=1','leaders[5]="WRONG"','turn=201','humans[5]=true'):
            with self.subTest(change=change):
                vm=LuaRuntime()
                vm.execute('''
turn=200;properties={};writes=0;leaders={};humans={};Players={};PlayerConfigurations={}
for i=0,5 do
 leaders[i]='LEADER_TEST'..i;humans[i]=i==0
 Players[i]={IsHuman=function()return humans[i]end}
 PlayerConfigurations[i]={GetLeaderTypeName=function()return leaders[i]end}
end
Game={GetCurrentGameTurn=function()return turn end,
 GetProperty=function(_,key)if properties[key]~=nil then return properties[key]end end,
 SetProperty=function(_,key,value)writes=writes+1;properties[key]=value end}
print=function()end
'''+change)
                if change in ('','properties.CSC_AI_OriginalHuman_5=0'):
                    vm.execute(code.decode())
                    self.assertEqual(vm.globals().writes,6 if change=='' else 5)
                    self.assertEqual(vm.globals().properties.CSC_AI_OriginalHuman_0,1)
                    before=vm.globals().writes
                    vm.execute(code.decode())
                    self.assertEqual(vm.globals().writes,before)
                else:
                    with self.assertRaises(Exception):vm.execute(code.decode())
                    self.assertEqual(vm.globals().writes,0)
        with patch('nicopolis_replay.sha',return_value='changed'):
            with self.assertRaisesRegex(AssertionError,'provenance differs'):
                seed_source_seats(b'',base,CASES['szeged'])

    def test_policy_gate_records_inactivity_before_stopping_autoplay(self):
        class PolicyController:
            def __init__(self,active):self.active=active
            def cmd(self,code,state,label):
                assert state=='CSC_AI_BakersGameplay' and 'Initialize()' not in code
                status=dict(ready=1,faults=0,enabled=int(self.active),version=int(self.active))
                return '\n'.join(['CSC_POLICY_BRIDGE\ttrue','CSC_POLICY_SINGLE_PLAYER\ttrue',
                    'CSC_POLICY_NATIVE\t'+json.dumps(status),'CSC_POLICY_SEAT\t2\t'+('0' if self.active else 'nil')+'\tfalse',
                    'CSC_POLICY_BASE_TAG\tCLASS_CSC_TAILORS_BASE\t'+str(self.active).lower()])
        for active in (False,True):
            with self.subTest(active=active),tempfile.TemporaryDirectory() as path:
                if active:qualify_integrated_policy(PolicyController(active),Path(path),CASES['szeged'])
                else:
                    with self.assertRaisesRegex(AssertionError,'inactive or unqualified'):
                        qualify_integrated_policy(PolicyController(active),Path(path),CASES['szeged'])
                record=json.loads((Path(path)/'policy-qualification.json').read_text())
                self.assertEqual(record['verified'],active)
                self.assertEqual(record['seats'][0]['originalHuman'],0 if active else None)

    def test_all_city_quotes_and_source_bank_are_recorded(self):
        with tempfile.TemporaryDirectory() as path:
            qualify_purchase(Controller(),Path(path),CASES['szeged'])
            record=json.loads((Path(path)/'source-purchase-qualification.json').read_text())
            self.assertTrue(record['verified'])
            self.assertEqual((record['cities_quoted'],record['quote'],record['treasuryGold']),(3,85,719))

    def test_cheaper_other_city_tie_shortfall_and_occupied_plot_fail_preflight(self):
        for change, message in [('prices[2]=80','proposing-city'),('prices[2]=85','tied'),
                ('bank=84','Treasury'),('owner=2','occupied')]:
            with self.subTest(change=change),tempfile.TemporaryDirectory() as path:
                with self.assertRaisesRegex(Exception,message):
                    qualify_purchase(Controller(change),Path(path),CASES['szeged'])
                self.assertFalse((Path(path)/'source-purchase-qualification.json').exists())

    def test_both_watchers_compile_with_their_exact_scope(self):
        vm=LuaRuntime()
        compile_lua=vm.eval('function(code)return assert(loadstring(code))end')
        for case in CASES.values():
            with self.subTest(case=case['profile']):
                compile_lua(WATCHER.replace('__SCOPE__',lua(case)).replace('__ENDPOINT__','208'))

    def test_ablation_changes_only_the_fixture_positive_candidate_condition(self):
        path=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
        source=path.read_bytes()
        changed=ablate_frontier_offer(source,CASES['szeged'])
        before=source.splitlines();after=changed.splitlines()
        differences=[(a,b)for a,b in zip(before,after)if a!=b]
        self.assertEqual(len(before),len(after))
        self.assertEqual(len(differences),1)
        self.assertIn(b'pid == 2 and city:GetID() == 589829 and district.Index == 37 and index == 1365',differences[0][1])
        LuaRuntime().eval('function(code)return assert(loadstring(code))end')(changed.decode('utf-8-sig'))

    def test_live_quote_bridge_rejects_ambiguous_buyer_without_reading_bank(self):
        controller=Controller()
        vm=controller.vm
        vm.execute("ExposedMembers={};Players[2].GetTreasury=function()error('No live cash veto')end")
        path=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'
        vm.execute(path.read_text(encoding='utf-8-sig'))
        quote=vm.eval('function()return ExposedMembers.CSC_Adjacency.GetPlotPurchaseQuote(2,589829,1365)end')
        self.assertEqual(quote(),85)
        for change in ('prices[2]=85','prices[2]=80','prices[2]=nil','prices[1]=-1'):
            with self.subTest(change=change):
                vm.execute('prices={85,130,-1};'+change)
                self.assertIsNone(quote())

    def test_nuremberg_control_withholds_both_profiles_at_one_footprint(self):
        path=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
        source=path.read_bytes();changed=ablate_frontier_offer(source,CASES['nuremberg'])
        differences=[(a,b)for a,b in zip(source.splitlines(),changed.splitlines())if a!=b]
        self.assertEqual(len(differences),1)
        condition='(pid == 3 and city:GetID() == 458758 and (district.Index == 36 or district.Index == 37) and index == 788)'
        self.assertIn(condition.encode(),differences[0][1])
        vm=LuaRuntime()
        predicate=vm.eval('function(pid,id,d,index)local city={GetID=function()return id end};local district={Index=d};return '+condition+' end')
        for pid,city,district,index in ((3,458758,36,788),(3,458758,37,788),
                (2,458758,36,788),(3,458757,36,788),(3,458758,35,788),(3,458758,36,789)):
            self.assertEqual(predicate(pid,city,district,index),pid==3 and city==458758 and district in(36,37)and index==788)
        vm.eval('function(code)return assert(loadstring(code))end')(changed.decode('utf-8-sig'))

    def test_explicit_prototype_qualification_records_ambiguity(self):
        with tempfile.TemporaryDirectory() as path:
            qualify_purchase(Controller('prices[2]=85'),Path(path),CASES['szeged'],allow_tied=True)
            record=json.loads((Path(path)/'source-purchase-qualification.json').read_text())
            self.assertTrue(record['ambiguousBuyer'])
            self.assertEqual(record['purpose'],'buyer-prototype')
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaisesRegex(Exception,'cheapest buyer'):
                qualify_purchase(Controller('prices[2]=80'),Path(path),CASES['szeged'],allow_tied=True)

    def test_missing_optional_ui_metadata_does_not_erase_core_qualification(self):
        c=Controller()
        c.vm.execute('local city=CityManager.GetCity(2,589829);city.GetBuildQueue=function()return {}end;city.GetDistricts=function()return {}end')
        with tempfile.TemporaryDirectory() as path:
            qualify_purchase(c,Path(path),CASES['szeged'])
            raw=(Path(path)/'source-purchase-qualification.txt').read_text()
            self.assertIn('unknown',raw)
            self.assertTrue((Path(path)/'source-purchase-qualification.json').exists())

    def test_quote_bypass_is_exact_and_staged_only(self):
        path=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'
        source=path.read_bytes();staged=bypass_szeged_quote_screen(source,CASES['szeged'])
        controller=Controller('prices[2]=85');vm=controller.vm
        vm.execute('ExposedMembers={}')
        vm.execute(source.decode('utf-8-sig'))
        quote=vm.eval('function()return ExposedMembers.CSC_Adjacency.GetPlotPurchaseQuote(2,589829,1365)end')
        self.assertIsNone(quote())
        vm.execute(staged.decode('utf-8-sig'))
        self.assertEqual(quote(),85)
        self.assertEqual(path.read_bytes(),source)
        with self.assertRaises(AssertionError):
            bypass_szeged_quote_screen(source,CASES['nicopolis'])


if __name__=='__main__':unittest.main()
