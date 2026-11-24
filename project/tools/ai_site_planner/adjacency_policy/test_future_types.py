"""Permanent future-type restrictions, separate from unlock/population timing."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT=Path(__file__).resolve().parents[4]
SCANNER=ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
FIXTURE='''
function info(rows,key)
 local t={};for _,r in ipairs(rows)do t[r[key]]=r;if r.Index then t[r.Index]=r end end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
CSC_Adjacency={ByDistrict={}}
GameInfo={Districts=info({
 {Index=1,DistrictType='HOLY',OnePerCity=true},
 {Index=6,DistrictType='MARKET',OnePerCity=true},
 {Index=7,DistrictType='FUN',OnePerCity=true,MutuallyExclusiveDistrict='WATER'},
 {Index=17,DistrictType='LAVRA',OnePerCity=true,TraitType='TRAIT_LAVRA'},
 {Index=19,DistrictType='CARNIVAL',OnePerCity=true,TraitType='TRAIT_CARNIVAL'},
 {Index=20,DistrictType='URBAN',OnePerCity=true},
 {Index=21,DistrictType='RURAL_A',OnePerCity=false},
 {Index=22,DistrictType='RURAL_B',OnePerCity=false},
 {Index=24,DistrictType='WATER',OnePerCity=true},
 {Index=29,DistrictType='SUGUBA',OnePerCity=true,TraitType='TRAIT_SUGUBA'}},'DistrictType'),
 CivilizationTraits=info({{CivilizationType='RUSSIA',TraitType='TRAIT_LAVRA'}},'TraitType'),
 Leaders=info({{LeaderType='CHILD',InheritFrom='PARENT'},{LeaderType='PARENT'}},'LeaderType'),
 LeaderTraits=info({{LeaderType='PARENT',TraitType='TRAIT_SUGUBA'},
 {LeaderType='DISABLE',TraitType='TRAIT_DISABLE_LAVRA'}},'TraitType'),
 ExcludedDistricts=info({{TraitType='TRAIT_DISABLE_LAVRA',DistrictType='LAVRA'}},'DistrictType'),
 MutuallyExclusiveDistricts=info({
 {District='URBAN',MutuallyExclusiveDistrict='RURAL_A'},
 {District='URBAN',MutuallyExclusiveDistrict='RURAL_B'},
 {District='RURAL_A',MutuallyExclusiveDistrict='URBAN'},
 {District='RURAL_B',MutuallyExclusiveDistrict='URBAN'},
 {District='MARKET',MutuallyExclusiveDistrict='FUN'}},'District'),
 DistrictReplaces=info({{CivUniqueDistrictType='LAVRA',ReplacesDistrictType='HOLY'},
 {CivUniqueDistrictType='SUGUBA',ReplacesDistrictType='MARKET'},
 {CivUniqueDistrictType='CARNIVAL',ReplacesDistrictType='FUN'}},'CivUniqueDistrictType')}
config={civ='HUNGARY',leader='DEFAULT'}
PlayerConfigurations={[2]={GetCivilizationTypeName=function()return config.civ end,GetLeaderTypeName=function()return config.leader end}}
placed={}
unfinished={}
pillaged={}
local districts={GetNumDistricts=function()return #placed end,
 GetDistrictByIndex=function(_,i)return {
   GetType=function()return placed[i+1]end,
   IsComplete=function()return not unfinished[i+1]end,
   IsPillaged=function()return pillaged[i+1]==true end} end}
city={GetDistricts=function()return districts end,
 GetPopulation=function()error('Future geometry must not require current population')end}
'''


class FutureTypes(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime()
        self.lua.execute(FIXTURE)
        self.lua.execute(SCANNER.read_text(encoding='utf-8-sig'))

    def allowed(self,change='',ordinary_tree=False):
        self.lua.execute(change)
        return self.lua.globals().CSC_AI_FutureDistrictTypes(2,self.lua.globals().city,ordinary_tree)

    def test_foreign_uniques_are_excluded(self):
        result=self.allowed()
        self.assertTrue(result[1] and result[6])
        self.assertFalse(result[17] or result[29] or result[19])

    def test_unique_replaces_base_and_configuration_cache_changes(self):
        result=self.allowed("config.civ='RUSSIA'")
        self.assertTrue(result[17]);self.assertFalse(result[1])
        result=self.allowed("config.civ='HUNGARY'")
        self.assertTrue(result[1]);self.assertFalse(result[17])

    def test_inherited_leader_trait(self):
        result=self.allowed("config.leader='CHILD'")
        self.assertTrue(result[29]);self.assertFalse(result[6])

    def test_excluded_unique_does_not_restore_replaced_base(self):
        result=self.allowed("config.civ='RUSSIA';config.leader='DISABLE'")
        self.assertFalse(result[1] or result[17])

    def test_existing_family_and_mutual_exclusion_are_live(self):
        result=self.allowed('placed={17,7}')
        self.assertFalse(result[1] or result[24])
        result=self.allowed('placed={24}')
        self.assertFalse(result[7])
        result=self.allowed('placed={}')
        self.assertTrue(result[1] and result[7] and result[24])

    def test_unknown_actor_earns_no_future_credit(self):
        self.assertIsNone(self.allowed('PlayerConfigurations[2]=nil'))

    def test_missing_metadata_and_empty_identity_stay_unknown(self):
        for name in ('Leaders','CivilizationTraits','LeaderTraits','DistrictReplaces','ExcludedDistricts',
                     'MutuallyExclusiveDistricts'):
            with self.subTest(name=name):
                self.setUp()
                self.assertIsNone(self.allowed('GameInfo.'+name+'=nil'))
        self.setUp()
        self.assertIsNone(self.allowed("config.civ=''"))

    def test_repeatable_district_and_captured_unique_mutual_exclusion(self):
        result=self.allowed("GameInfo.Districts.MARKET.OnePerCity=false;placed={6,19}")
        self.assertFalse(result[7] or result[24])
        result=self.allowed('placed={6}')
        self.assertTrue(result[6])

    def test_citywide_conflict_retires_all_rural_options_at_foundation(self):
        result=self.allowed()
        self.assertTrue(result[20] and result[21] and result[22])
        result=self.allowed('placed={20}')
        self.assertFalse(result[20] or result[21] or result[22])
        self.assertTrue(result[24])
        result=self.allowed('placed={22}')
        self.assertFalse(result[20])
        self.assertTrue(result[21] and result[22])

    def test_ordinary_tree_skips_repeat_of_completed_intact_exact_type(self):
        raw=self.allowed('placed={21}')
        tree=self.allowed(ordinary_tree=True)
        self.assertTrue(raw[21] and raw[22])
        self.assertFalse(tree[21])
        self.assertTrue(tree[22])

    def test_repeatable_type_needs_a_completed_copy_and_an_intact_copy(self):
        tree=self.allowed('placed={21};unfinished={true}',ordinary_tree=True)
        self.assertTrue(tree[21])
        tree=self.allowed('unfinished={};pillaged={true}',ordinary_tree=True)
        self.assertTrue(tree[21])
        tree=self.allowed('placed={21,21};unfinished={false,true}',ordinary_tree=True)
        self.assertFalse(tree[21])

    def test_exclusion_inherits_base_rule_and_counts_a_placed_replacement(self):
        result=self.allowed("config.leader='CHILD';placed={19}")
        self.assertFalse(result[29])
        self.assertIsNone(result[24])
        result=self.allowed('placed={29}')
        self.assertTrue(result[7])


if __name__=='__main__':unittest.main()
