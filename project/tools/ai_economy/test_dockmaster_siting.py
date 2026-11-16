"""Qualify the Harbor/Tailors exception through live facts and bid publication.

These tests cover the low-adjacency boundary, unique Harbors, unchanged economic
values/caps, and the strict native-adjacency guard on customer preparation.
"""
from pathlib import Path
import unittest

import test_boundaries as boundaries
import test_customer_first_planning as customers
import test_spatial_planning as spatial

AI = Path(__file__).resolve().parents[3] / 'Civ Supply Chains/Lua_UI/AI'


class DockmasterSiting(unittest.TestCase):
    def test_geometry_requires_actual_owned_completed_harbor_and_resolves_unique(self):
        vm = customers.CustomerFirstPlanning().facts()
        vm.execute('''
GameInfo.Districts[30]={Index=30,DistrictType='DISTRICT_HARBOR'}
GameInfo.Districts[31]={Index=31,DistrictType='DISTRICT_UNIQUE_HARBOR'}
GameInfo.Districts[32]={Index=32,DistrictType='DISTRICT_RURALCOMMUNITYC'}
GameInfo.DistrictReplaces=function()
 local done=false;return function()if not done then done=true
 return{CivUniqueDistrictType='DISTRICT_UNIQUE_HARBOR',ReplacesDistrictType='DISTRICT_HARBOR'}end end
end
CSC_Adjacency.ByDistrict={}
plots[3].IsRiver=function()return false end
local kind,complete,foreign=31,true,false
city.GetDistricts=function()return{
 GetNumDistricts=function()return foreign and 0 or 1 end,
 GetDistrictByIndex=function()return{GetX=function()return 0 end,GetY=function()return 0 end,
 GetType=function()return kind end,IsComplete=function()return complete end,
 IsPillaged=function()return true end}end}end
local profile={key='TAILORS',district={Index=36,DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}}
local function geometry()
 return CSC_AI_EconomyFacts.New(player,placement,ui).Geometry(city,plots[3],profile)
end
assert(geometry().completedHarborPlot==2) -- unique Harbor; pillage preserves physical adjacency
complete=false;assert(geometry().completedHarborPlot==nil) -- foundation is insufficient
complete=true;foreign=true;assert(geometry().completedHarborPlot==nil)
foreign=false;kind=32;assert(geometry().completedHarborPlot==nil) -- CL provider is not a Harbor
kind=30;assert(geometry().completedHarborPlot==2)
profile.key='BAKERS';assert(geometry().completedHarborPlot==nil)
''')

    def test_plus_one_exception_survives_both_admission_and_complete_bid_publication(self):
        vm = boundaries.Boundaries().bid_vm()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local key,harbor,adjacency,base='TAILORS',99,1,1
placement.StageTwoProfiles()[1].key=key
snapshot.Geometry=function()return{upper=adjacency,quarterKey=key,completedHarborPlot=harbor}end
snapshot.Site=function(_,plot)return{value=plot:GetIndex()*1000,baseCount=base,
 quarterKey=key,completedHarborPlot=harbor}end
CSC_AI_EconomyModel.Forecast=function(site)return{valueQ8=site.value,adjacency=adjacency,streams={},omissions={}}end
local entries,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#entries==3 and stats.final==3 and stats.qualityDeferred==0)
for _,entry in ipairs(entries)do
 assert(entry.adjacency==1 and entry.dockmasterHarborPlot==99)
 assert(entry.preferenceQ8==48*256 and entry.finalQ8==entry.plot*1000+48*256)
end
harbor=nil;entries,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#entries==0 and stats.qualityDeferred==3)
harbor=99;key='BAKERS';entries=E.QuarterBids(snapshot,placement,{},early);assert(#entries==0)
key='TAILORS';adjacency=0;entries=E.QuarterBids(snapshot,placement,{},early);assert(#entries==0)
adjacency=1;base=0;entries=E.QuarterBids(snapshot,placement,{},early);assert(#entries==0)
base=1;entries,stats=E.QuarterBids(snapshot,placement,{[1]=true,[2]=true,[3]=true},early)
assert(#entries==0 and stats.materialDeferred==3)
''')

    def test_exception_keeps_real_income_and_weak_quality_cap(self):
        vm = spatial.SpatialPlanning().adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local site={quarterKey='TAILORS',completedHarborPlot=5,baseCount=1,
 comparisonReferenceQ8=600*256,sitingReadiness=1}
local quote={adjacency=1,valueQ8=100*256}
local value,why,parts=E.PlacementValue(quote,site)
assert(why=='positive' and value==148*256 and parts.adjacencyQ8==48*256)
assert(quote.adjacency==1 and quote.valueQ8==100*256) -- no fabricated adjacency or Service income
assert(parts.qualityCapQ8==300*256)
quote.valueQ8=10000*256;assert(E.PlacementValue(quote,site)==300*256)
quote.valueQ8=-1;assert(E.PlacementValue(quote,site)==-1)
site.completedHarborPlot=nil;assert(E.PlacementValue(quote,site)==E.DeferredQuarterQ8)
''')

    def test_harbor_preparation_is_stronger_bounded_and_cannot_sacrifice_native_adjacency(self):
        vm = spatial.SpatialPlanning().adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local row={quarterKey='TAILORS',customerFamily='DISTRICT_HARBOR',baseCount=1,
 specialtyCount=0,adjacency=3,bestAdjacency=3,quarterCity=1,quarterDistrict=43,quarterPlot=5}
assert(E.CustomerFirstPreference(row)==16)
row.specialtyCount=1;assert(E.CustomerFirstPreference(row)==20)
row.baseCount=30;assert(E.CustomerFirstPreference(row)==24)
row.adjacency=0;assert(E.CustomerFirstPreference(row)==0) -- +3 to +0 explicitly refused
row.adjacency=2;assert(E.CustomerFirstPreference(row)==0) -- guard still protects even one point
row.adjacency=3;row.customerFamily='DISTRICT_COMMERCIAL_HUB';assert(E.CustomerFirstPreference(row)==16)
row.customerFamily='DISTRICT_HARBOR';row.quarterKey='BAKERS';assert(E.CustomerFirstPreference(row)==16)
row.quarterKey='TAILORS'
local other={};for k,v in pairs(row)do other[k]=v end
other.quarterCity=2;other.quarterPlot=6
local plan=E.CustomerFirstPlan({row,other},{},{})
assert(plan.rawPreference==48 and plan.preference==32 and #plan.links==2)
''')

    def test_real_reverse_facts_identify_tailors_and_unique_harbor_without_authored_map(self):
        vm = customers.CustomerFirstPlanning().facts()
        vm.execute('''
local quarter=GameInfo.Districts[36];quarter.DistrictType='DISTRICT_CSC_TAILORS_QUARTER'
GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER=quarter
GameInfo.Adjacency_YieldChanges.native.AdjacentDistrict=quarter.DistrictType
GameInfo.Districts[20].DistrictType='DISTRICT_UNIQUE_HARBOR'
GameInfo.DistrictReplaces=function()
 local done=false;return function()if not done then done=true
 return{CivUniqueDistrictType='DISTRICT_UNIQUE_HARBOR',ReplacesDistrictType='DISTRICT_HARBOR'}end end
end
CSC_Adjacency.HasTag=function(tag,resource)
 return tag=='CLASS_CSC_TAILORS_BASE'and resource=='RESOURCE_MOD_BASE'
 or tag=='CLASS_CSC_TAILORS_SPEC'and resource=='RESOURCE_MOD_SPEC'
end
''')
        vm.execute('CSC_AI_EconomyModel={}')
        vm.execute((AI / 'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local row=CSC_AI_EconomyFacts.New(player,placement,ui).CustomerFirstOptions({})[1]
assert(row.quarterKey=='TAILORS'and row.customerFamily=='DISTRICT_HARBOR')
assert(CSC_AI_EconomyAdapters.CustomerFirstPreference(row)==20)
''')


if __name__ == '__main__':
    unittest.main()
