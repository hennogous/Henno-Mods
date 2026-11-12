"""Exercise live potential gates and versioned publication, not native choice."""
import importlib.util
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from test_ownership_publication import runtime as publisher_runtime

ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('decline_scanner_fixture',
    ROOT/'project/tools/ai_site_planner/adjacency_policy/test_scanner.py')
scanner=importlib.util.module_from_spec(spec);spec.loader.exec_module(scanner)


def potential_vm(extra,tailors_extra=''):
    vm=LuaRuntime();vm.globals().print=lambda *args:None
    vm.execute('DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1}')
    vm.execute((ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua').read_text(encoding='utf-8-sig'))
    vm.execute(scanner.HARNESS)
    vm.execute(scanner.SCANNER.read_text(encoding='utf-8-sig'))
    vm.execute('ExposedMembers={}')
    vm.execute((ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyUI.lua').read_text(encoding='utf-8-sig'))
    marker='-- The same gate accepts a future Harbor'
    setup="""targets={14}; existing=false; placed=false; unlocked=true; cattleVisible=true
plots[14].neighbors={}; pendingBase.GetOwner=function()return -1 end
pendingBase.GetResourceType=function()return 88 end
"""
    vm.execute(scanner.BAKERS_SITES.replace(marker,setup+extra+'\n'+marker)+'\n'+tailors_extra)
    return vm


class Potential(unittest.TestCase):
    def test_tailors_uses_the_same_absence_and_unowned_potential_rule(self):
        potential_vm('',"""
existing=false;plots[23].base=0
local oldTag=CSC_Adjacency.HasTag
CSC_Adjacency.HasTag=function(tag,kind)
 return tag=='CLASS_CSC_TAILORS_BASE' and kind=='RESOURCE_CATTLE' or oldTag(tag,kind)
end
assert(bids(tailors,{},legal)[23].declineNoBase)
plots[24].GetResourceType=function()return 88 end
plots[24].GetOwner=function()return -1 end
assert(not bids(tailors,{},legal)[23].declineNoBase)
""")

    def test_known_empty_site_declines_and_new_unowned_base_withdraws(self):
        potential_vm("""
assert(bids(bakers,{},readLegalTargets)[14].declineNoBase)
plots[14].neighbors={pendingBase}
assert(not bids(bakers,{},readLegalTargets)[14].declineNoBase)
pendingBase.GetOwner=function()return 1 end
assert(not bids(bakers,{},readLegalTargets)[14].declineNoBase)
""")

    def test_unknown_neighbors_hidden_types_or_missing_definitions_prevent_decline(self):
        for extra in ("plots[14].neighbors={pendingBase};PlayersVisibility[1].IsRevealed=function(_,x)return x~=99 end",
                      'cattleVisible=false',
                      "GameInfo.Resources=info({},'ResourceType')"):
            # Restore the old fixture facts before its subsequent Tailors tests.
            code="local resourceSnapshot=GameInfo.Resources;local visibilitySnapshot=PlayersVisibility[1].IsRevealed\n"
            code+=extra+"\nassert(not bids(bakers,{},readLegalTargets)[14].declineNoBase)\n"
            code+="GameInfo.Resources=resourceSnapshot;PlayersVisibility[1].IsRevealed=visibilitySnapshot;cattleVisible=true"
            with self.subTest(extra=extra):potential_vm(code)


def publication(capability=True,capacity=4096):
    vm,messages=publisher_runtime(False)
    vm.execute("""
CSC_AI_QuarterPlacement.StageTwoProfiles=function()return {
 {key='BAKERS',district={Index=2}},{key='TAILORS',district={Index=3}}}end
CSC_AI_QuarterSiteForecasts=function(player,profile)
 return {{player=3,city=42,district=profile.district.Index,plot=101,
  delta=-65536,weak=true,declineNoBase=not opportunity}},{legal=1,noBase=1,coversMaterial=0,
  noHost=0,bothPending=0,deferCities=0,offered=0,strong=0}
end
declineScopes={};declineCalls=0;receiptCalls=0
local begin=CE_AIDistrictScoresBegin
CE_AIDistrictScoresBegin=function(v)declineScopes={};return begin(v)end
""")
    if capability:
        vm.execute("""
CE_AIDistrictDeclineStatus=function()return '{"abi":1,"ready":1,"faults":0,"capacity":CAPACITY}'end
CE_AIDistrictDeclineStage=function(p,c,d,i)
 assert(p==3 and c==42 and i==101);declineCalls=declineCalls+1
 declineScopes[#declineScopes+1]={p,c,d,i};return 1
end
CE_AIDistrictDeclineReceipt=function(v,p,c,d,i)
 assert(v==version and #declineScopes>0);receiptCalls=receiptCalls+1
 return '{"staged":1,"considered":1,"masked":1,"restored":1}'
end
""".replace('CAPACITY',str(capacity)))
    return vm,messages


class Publication(unittest.TestCase):
    def test_live_scopes_withdraw_and_receipts_precede_replacement(self):
        vm,messages=publication();vm.execute('boundary()')
        self.assertEqual(vm.eval('#declineScopes'),2)
        vm.execute('opportunity=true;turn=2;boundary()')
        self.assertEqual(vm.eval('#declineScopes'),0)
        self.assertEqual(vm.eval('receiptCalls'),2)
        self.assertEqual(vm.eval('#packet'),2) # Original numeric guidance retained.
        self.assertTrue(any('CSC_AI_DECLINE_RECEIPT' in m for m in messages))

    def test_missing_optional_capability_retains_numeric_guidance(self):
        vm,messages=publication(False);vm.execute('boundary()')
        self.assertEqual(vm.eval('declineCalls'),0)
        self.assertEqual(vm.eval('#packet'),2)
        self.assertFalse(any('DISTRICTS_FAILED' in m for m in messages))

    def test_future_abi_does_not_match_abi_one(self):
        vm,messages=publication()
        vm.execute('''CE_AIDistrictDeclineStatus=function()
 return '{"abi":10,"ready":1,"faults":0,"capacity":4096}' end;boundary()''')
        self.assertEqual(vm.eval('declineCalls'),0)
        self.assertEqual(vm.eval('#packet'),2)

    def test_native_decline_rejection_does_not_commit_a_partial_packet(self):
        vm,messages=publication()
        vm.execute('CE_AIDistrictDeclineStage=function()declineCalls=declineCalls+1;return 0 end;boundary()')
        self.assertEqual(vm.eval('declineCalls'),1)
        self.assertTrue(vm.eval('packet==nil'))
        self.assertTrue(any('Native district decline rejected' in m for m in messages))

    def test_capacity_trims_only_declines(self):
        vm,messages=publication(capacity=1);vm.execute('boundary()')
        self.assertEqual(vm.eval('#declineScopes'),1)
        self.assertEqual(vm.eval('#packet'),2)
        self.assertTrue(any('scopes=1 omitted=1' in m for m in messages))


if __name__=='__main__':unittest.main()
