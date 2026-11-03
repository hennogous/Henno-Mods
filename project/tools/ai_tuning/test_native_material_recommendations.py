"""Executed Lua51 recommendations capture contracts; no native connections."""
import json
import unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime,LuaError
from native_material_probe import validate_endpoint,validate_recommendation_coverage

FIXTURE=r'''
function collection(items)return{Members=function()local n=0;return function()n=n+1;if items[n]then return n,items[n]end end end}end
Game={GetCurrentGameTurn=function()return 110 end};GameInfo={Units={UNIT_BUILDER={Index=1}}}
local cid1={owner=3,id=100,kind=7};local cid2={owner=3,id=101,kind=7};componentObjects={cid1,cid2}
local function unit(id,cid)return{GetID=function()return id end,GetOwner=function()return 3 end,GetType=function()return 1 end,
 GetComponentID=function()return cid end,GetX=function()return 47 end,GetY=function()return 32 end,GetMovesRemaining=function()return 5 end,GetBuildCharges=function()return 3 end}end
local units={unit(100,cid1),unit(101,cid2)}
local function ai(city)
 return{GetImprovementRecommendations=function()if city==12 then return{}end;return{{ImprovementLocation=2489,ImprovementHash=168372657,ImprovementScore=900,Extra={nested={value='retained'}}}}end,
 GetImprovementRecommendationsForBuilder=function(self,cid)
 assert(cid==cid1 or cid==cid2,'A reconstructed componentID was passed')
 if city==12 and cid==cid2 then error('fixture native error')end
 return{{ImprovementLocation=2346,ImprovementHash=168372657,ImprovementScore=11257},{ImprovementLocation=2344,ImprovementHash=-123,ImprovementScore=321,unfamiliar={x={y={z=44}}}}}
 end}
end
cityAI={ai(11),ai(12)}
local function city(id,index)return{GetOwner=function()return 3 end,GetID=function()return id end,GetX=function()return 49 end,GetY=function()return 34 end,GetCityAI=function()return cityAI[index]end}end
local cities={city(11,1),city(12,2)}
local player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,
 GetUnits=function()return collection(units)end,GetCities=function()return collection(cities)end}
Players={[3]=player};PlayerConfigurations={[3]={IsHuman=function()return false end}}
Map={GetPlotByIndex=function(idx)return{GetIndex=function()return idx end,GetX=function()return idx%74 end,GetY=function()return math.floor(idx/74)end,GetOwner=function()return 3 end,GetResourceType=function()return idx==2489 and 54 or-1 end,GetFeatureType=function()return-1 end,GetImprovementType=function()return-1 end}end}
Cities={GetPlotPurchaseCity=function(p)return cities[p:GetIndex()==2489 and 1 or 2]end}
'''


class RecommendationsTests(unittest.TestCase):
    def capture(self,extra=''):
        lua=LuaRuntime();texts=[];lua.globals().print=texts.append;lua.execute(FIXTURE+extra)
        lua.execute(Path(__file__).with_name('native_material_recommendations.lua').read_text(encoding='utf-8-sig'))
        return json.loads(texts[-1].split('=',1)[1])

    def test_complete_raw_fields_scores_and_nested_records(self):
        v=self.capture();self.assertEqual(v['cities'][0]['generic']['raw_result'][0]['Extra']['nested']['value'],'retained')
        records=v['cities'][0]['builder_recommendations'][0]['result']['raw_result']
        self.assertEqual([r['ImprovementLocation']for r in records],[2346,2344])
        self.assertEqual(records[1]['unfamiliar']['x']['y']['z'],44)
        self.assertEqual(records[0]['ImprovementScore'],11257)

    def test_component_objects_passed_direct_and_all_city_builder_joins(self):
        v=self.capture();self.assertEqual(v['budget']['API_calls'],6)
        self.assertEqual([(c['owner'],c['city'],[b['unit']for b in c['builder_recommendations']])for c in v['cities']],[(3,11,[100,101]),(3,12,[100,101])])
        self.assertEqual(v['builders'][0]['component_id'],{'owner':3,'id':100,'kind':7})

    def test_empty_error_and_unavailable_are_distinct(self):
        v=self.capture('cityAI[1].GetImprovementRecommendations=nil')
        missing=v['cities'][0]['generic'];empty=v['cities'][1]['generic'];error=v['cities'][1]['builder_recommendations'][1]['result']
        self.assertEqual(missing['status'],'unavailable');self.assertFalse(missing['called']);self.assertNotIn('raw_result',missing)
        self.assertEqual(empty['status'],'ok_empty');self.assertTrue(empty['called']);self.assertEqual(empty['returned_entries'],0)
        self.assertEqual(error['status'],'error');self.assertTrue(error['called']);self.assertFalse(error['ok']);self.assertNotIn('raw_result',error)

    def test_successful_nil_is_not_an_empty_list(self):
        v=self.capture('cityAI[1].GetImprovementRecommendations=function()return nil end')
        row=v['cities'][0]['generic'];self.assertEqual(row['status'],'ok_non_table');self.assertEqual(row['native_return_type'],'nil');self.assertNotIn('returned_entries',row)

    def test_complete_API_coverage_gate_accepts_empty_and_rejects_errors(self):
        good=self.capture('cityAI[2].GetImprovementRecommendationsForBuilder=function()return{}end')
        self.assertTrue(validate_recommendation_coverage(good))
        bad_owner=self.capture('cityAI[2].GetImprovementRecommendationsForBuilder=function()return{}end');bad_owner['builders'][0]['owner']=4
        with self.assertRaises(ValueError):validate_recommendation_coverage(bad_owner)
        bad_join=self.capture('cityAI[2].GetImprovementRecommendationsForBuilder=function()return{}end');bad_join['cities'][0]['builder_recommendations'][0]['city']=999
        with self.assertRaises(ValueError):validate_recommendation_coverage(bad_join)
        for bad in (self.capture(),self.capture('cityAI[1].GetImprovementRecommendations=nil')):
            with self.assertRaises(ValueError):validate_recommendation_coverage(bad)

    def test_original_human_rejected(self):
        with self.assertRaisesRegex(LuaError,'assertion failed'):self.capture('PlayerConfigurations[3].IsHuman=function()return true end')

    def test_endpoint_bounds(self):
        for endpoint in(110,111,113):validate_endpoint(endpoint,True)
        validate_endpoint(115,False)
        for endpoint,recommendations in((109,False),(116,False),(114,True),(115,True)):
            with self.assertRaises(ValueError):validate_endpoint(endpoint,recommendations)


if __name__=='__main__':unittest.main()
