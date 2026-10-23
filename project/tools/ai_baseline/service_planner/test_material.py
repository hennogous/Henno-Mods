"""Material-first broad marks, live refresh and real-command boundary fixtures."""
import json,sys,unittest
from pathlib import Path
from dataclasses import replace
from .policy import Policy,Planner,Budget
from .observations import build_candidates
from .execution import PurchaseExecutor
from .test_policy import candidate,LuaRunner,LUA_FIXTURE


def observation():
    return {'player':1,'city':10,'turn':60,'eligible_ai':True,'human':False,
      'tiles':[{'index':42,'owner':-1,'revealed':True,'within_city_reach':True,
                'neighbors':[81,82],'potential_legal':{'TAILORS':True},
                'current_legal':{'TAILORS':True},'native_projection_verified':True,
                'native_purchasable':True,'price':40,'frontier_danger':False},
               {'index':81,'owner':-1,'resource':'WOOL','revealed':True,
                'material_visible':True,'base_for':['TAILORS'],'frontier_danger':False,
                'native_purchasable':True,'price':30},
               {'index':82,'owner':-1,'resource':'SILK','revealed':True,
                'material_visible':True,'spec_for':['TAILORS'],'frontier_danger':False,
                'native_purchasable':True,'price':30}]}


class MaterialTests(unittest.TestCase):
    def setUp(self):self.p=Planner(Policy.material_first());self.o=observation()
    def rows(self):return build_candidates(self.o,material_first=True)
    def evaluate(self,c,b=Budget(1000),turn=60):return self.p.evaluate(c,{},b,turn)
    def test_no_sales_venue_research_or_need_required(self):
        c=self.rows()[0];self.assertIsNone(c.service)
        self.assertEqual(self.evaluate(c).action,'purchase')
    def test_three_tile_plan_source_first(self):
        c=self.rows()[0]
        self.assertEqual((c.missing_tiles,c.purchase_plot,c.remaining_price),((42,81,82),42,100))
        self.assertEqual((c.purchase_base,c.purchase_specialty),(0,0))
    def test_plan_identity_survives_source_and_supply_ownership(self):
        a=self.rows()[0];self.o['tiles'][0]['owner']=1;b=self.rows()[0]
        self.o['tiles'][1]['owner']=1;c=self.rows()[0]
        self.assertEqual((a.key,b.key),(b.key,c.key));self.assertEqual(c.purchase_plot,82)
    def test_marked_tile_becomes_owned_between_broad_scans(self):
        for p in self.o['tiles'][1:]:p['owner']=1
        c=self.rows()[0];self.p.update(1,10,60,[c])
        self.o['tiles'][0]['owner']=1;self.o['turn']=61;fresh=self.rows()[0]
        self.assertFalse(self.p.wide_due(1,10,61))
        chosen=self.p.select({}, {1:Budget(0)},61,lambda old:fresh)
        self.assertEqual(chosen[0].action,'place')
    def test_wide_scan_new_city_and_five_turn_schedule(self):
        self.assertTrue(self.p.wide_due(1,10,60));self.p.update(1,10,60,self.rows())
        self.assertFalse(self.p.wide_due(1,10,64));self.assertTrue(self.p.wide_due(1,10,65))
        self.assertTrue(self.p.wide_due(1,11,61))
    def test_both_beats_many_base_only_then_base_before_total(self):
        a=replace(self.rows()[0],base=1,specialty=1)
        b=replace(a,plot=43,base=6,specialty=0)
        c=replace(a,plot=44,base=2,specialty=1)
        d=replace(a,plot=45,base=1,specialty=5)
        self.p.update(1,10,60,[b,d,a,c]);self.assertEqual(self.p.cache[1,10][0].plot,44)
    def test_owned_base_fallback_does_not_consume_marked_both_slot(self):
        both=self.rows()[0]
        base=replace(both,plot=43,base=5,specialty=0,missing_tiles=(),current_legal=True)
        self.p.update(1,10,60,[base,both]);self.assertEqual(len(self.p.cache[1,10]),1)
        self.assertEqual(self.p.cache[1,10][0].plot,42)
    def test_base_only_can_place_but_cannot_spend(self):
        c=replace(self.rows()[0],specialty=0)
        self.assertEqual(self.evaluate(c).action,'watch')
        self.assertEqual(self.evaluate(replace(c,missing_tiles=(),current_legal=True)).action,'place')
    def test_no_redundant_material_buy_when_owned_supply_already_both(self):
        for p in self.o['tiles']:p['owner']=1
        self.o['tiles'].append(dict(self.o['tiles'][1],index=83,owner=-1))
        self.o['tiles'][0]['neighbors'].append(83)
        rows=self.rows();self.assertTrue(rows);self.assertTrue(all(not c.missing_tiles for c in rows))
    def test_full_chain_must_fit_budget(self):
        c=replace(self.rows()[0],price=40,remaining_price=200)
        self.assertEqual(self.evaluate(c,Budget(500)).action,'watch')
        self.assertEqual(self.evaluate(c,Budget(1000)).action,'purchase')
    def test_half_surplus_cap300_reserve150(self):
        self.assertEqual(self.evaluate(self.rows()[0]).max_price,300)
        self.assertEqual(self.evaluate(self.rows()[0],Budget(400)).max_price,125)
        self.assertEqual(self.evaluate(self.rows()[0],Budget(1000,-95)).action,'watch')
    def test_pending_no_second_purchase(self):
        self.p.pending_players.add(1);self.assertEqual(self.evaluate(self.rows()[0]).action,'reject')
    def test_next_turn_city_step_allowed_same_turn_not(self):
        self.p.purchases=[(1,10,60,40)]
        self.assertEqual(self.evaluate(self.rows()[0]).reason,'city purchase cooldown')
        self.assertEqual(self.evaluate(self.rows()[0],turn=61).action,'purchase')
    def test_one_more_than_three_steps_capped(self):
        c=replace(self.rows()[0],missing_tiles=(42,81,82,83))
        self.assertEqual(self.evaluate(c).action,'watch')
    def test_unreachable_or_unknown_remaining_price_waits(self):
        for c in [replace(self.rows()[0],purchase_plot=None),replace(self.rows()[0],remaining_price=0)]:
            self.assertEqual(self.evaluate(c).action,'watch')
    def test_hidden_foreign_or_resource_occupied_sites_never_marked(self):
        for field,value in [('owner',2),('revealed',False),('resource','WHEAT')]:
            self.o=observation();self.o['tiles'][0][field]=value;self.assertEqual(self.rows(),[])
    def test_different_unfinished_quarter_is_legal_same_type_is_not(self):
        self.o['same_quarter_types']=['BAKERS'];self.assertTrue(self.rows())
        self.o['same_quarter_types']=['TAILORS'];self.assertFalse(self.rows())
    def test_service_input_cannot_trigger_material_premium(self):
        self.assertEqual(self.evaluate(replace(self.rows()[0],service='dockmaster')).action,'reject')
    def test_actual_lua_first_step_before_materials_owned(self):
        from .execution import lua
        from lupa.lua51 import LuaRuntime
        engine=LuaRuntime(unpack_returned_tuples=True);engine.execute(LUA_FIXTURE)
        engine.execute("""
GameInfo.TypeTags[2]={Type='WOOL',Tag='CLASS_CSC_TAILORS_SPEC'}
Map.GetPlotByIndex(81).GetOwner=function()return -1 end
Map.GetPlotByIndex(82).GetOwner=function()return -1 end
""")
        c=self.rows()[0]
        # Test the actual Lua code with the fixture's 80-gold purchase, no venue
        # or civic. Projected counts are zero after buying source before supply.
        req={'player':1,'city':10,'purchase_plot':42,'source_plot':42,'quarter':'TAILORS',
             'turn':60,'base':0,'specialty':0,'material_first':True,'service':None,
             'plan_materials':{'81':True,'82':True},'remaining_tiles':{'42':True,'81':True,'82':True},
             'gold':600,'price':80,'max_price':200,'reserve':150,'plot_purchase_parameter':True}
        engine.globals().CSC_SERVICE_PURCHASE_REQUEST=engine.eval(lua(req))
        engine.execute(Path(__file__).with_name('native_purchase.lua').read_text(encoding='utf-8'))
        self.assertEqual((engine.globals().requests,engine.globals().gold,engine.globals().owner),(1,520,1))
    def test_actual_lua_rejects_lost_specialty_before_request(self):
        from .execution import lua
        from lupa.lua51 import LuaRuntime
        engine=LuaRuntime(unpack_returned_tuples=True);engine.execute(LUA_FIXTURE)
        req={'player':1,'city':10,'purchase_plot':42,'source_plot':42,'quarter':'TAILORS',
             'turn':60,'base':2,'specialty':0,'material_first':True,'service':None,
             'plan_materials':{'81':True,'82':True},'remaining_tiles':{'42':True},
             'gold':600,'price':80,'max_price':200,'reserve':150,'plot_purchase_parameter':True}
        engine.globals().CSC_SERVICE_PURCHASE_REQUEST=engine.eval(lua(req))
        with self.assertRaisesRegex(Exception,'no longer has Base'):
            engine.execute(Path(__file__).with_name('native_purchase.lua').read_text(encoding='utf-8'))
        self.assertEqual(engine.globals().requests,0)
    def test_actual_lua_rejects_numeric_UI_mode_sentinel_before_purchase(self):
        from .execution import lua
        from lupa.lua51 import LuaRuntime
        engine=LuaRuntime(unpack_returned_tuples=True);engine.execute(LUA_FIXTURE)
        req={'player':1,'city':10,'purchase_plot':42,'source_plot':42,'quarter':'TAILORS',
             'turn':60,'base':2,'specialty':0,'material_first':False,'service':None,
             'gold':600,'price':80,'max_price':200,'reserve':150,'plot_purchase_parameter':-780910418}
        engine.globals().CSC_SERVICE_PURCHASE_REQUEST=engine.eval(lua(req))
        with self.assertRaisesRegex(Exception,'boolean true'):
            engine.execute(Path(__file__).with_name('native_purchase.lua').read_text(encoding='utf-8'))
        self.assertEqual(engine.globals().requests,0)
    def test_actual_collector_broad_then_marked_footprint_then_new_city(self):
        from lupa.lua51 import LuaRuntime
        engine=LuaRuntime(unpack_returned_tuples=True)
        engine.execute(r'''
function rows(values)return setmetatable(values,{__call=function(t)local i=0;return function()i=i+1;return t[i]end end})end
captured='';print=function(v)captured=v end
Game={GetCurrentGameTurn=function()return 60 end}
GameInfo={TypeTags=rows({{Type='WOOL',Tag='CLASS_CSC_TAILORS_BASE'},{Type='SILK',Tag='CLASS_CSC_TAILORS_SPEC'}}),
 Resources={WOOL={Index=0},SILK={Index=1},[0]={Index=0},[1]={Index=1}},
 Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=36,Hash=360},DISTRICT_CSC_TAILORS_QUARTER={Index=37,Hash=370}},
 Yields={YIELD_PRODUCTION={Index=0}},Units={},Buildings={},Projects={},Civics=rows({})}
local queue={GetSize=function()return 0 end,CanProduce=function()return false,{} end,HasBeenPlaced=function()return false end}
local city={GetID=function()return 10 end,GetX=function()return 0 end,GetY=function()return 0 end,
 GetBuildQueue=function()return queue end,GetPopulation=function()return 1 end,GetGrowth=function()return {}end,
 GetYield=function()return 2 end,GetCulture=function()return {}end,GetDistricts=function()return {HasDistrict=function()return false end}end,
 GetGold=function()return {GetPlotPurchaseCost=function()return 30 end}end}
local player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,
 GetEra=function()return 0 end,GetTreasury=function()return {GetGoldBalance=function()return 600 end}end,
 GetCulture=function()return {HasCivic=function()return false end}end,
 GetCities=function()return {GetCount=function()return 1 end,Members=function()local done=false;return function()if not done then done=true;return 10,city end end end}end}
Players={[1]=player};PlayersVisibility={[1]={IsRevealed=function()return true end}}
local plots={};for i=0,3 do local idx=i;plots[idx]={GetIndex=function()return idx end,GetX=function()return idx end,GetY=function()return 0 end,
 GetOwner=function()return 1 end,GetResourceType=function()return idx==1 and 0 or(idx==2 and 1 or -1)end,
 GetImprovementType=function()return -1 end,GetDistrictType=function()return -1 end,GetFeatureType=function()return -1 end,
 IsImprovementPillaged=function()return false end,CanHaveDistrict=function()return idx==0 end}end
Map={GetPlotCount=function()return 4 end,GetPlotByIndex=function(i)return plots[i]end,
 GetPlotDistance=function(x,y,a,b)return math.abs(x-a)end,GetAdjacentPlots=function()return {plots[1],plots[2]}end}
CityOperationTypes={PARAM_DISTRICT_TYPE=1,PARAM_X=2,PARAM_Y=3,BUILD=4};CityOperationResults={PLOTS=1}
CityCommandTypes={PARAM_PLOT_PURCHASE=1,PARAM_X=2,PARAM_Y=3,PURCHASE=4};CityCommandResults={PLOTS=1}
CityManager={GetCommandTargets=function()return {}end,CanStartCommand=function(c,k,visible,p)if visible==true and p[CityCommandTypes.PARAM_PLOT_PURCHASE]==true then return true,{[CityCommandResults.PLOTS]={3}}end;return false end};UI={GetInterfaceModeParameter=function()return -780910418 end};Events={}
CSC_SERVICE_NATIVE={dirty={},material_first=true,external_venues={},venues_turn=60}
''')
        engine.execute(Path(__file__).with_name('native_observer.lua').read_text(encoding='utf-8'))
        def read():
            engine.execute('CSC_SERVICE_NATIVE.Read()')
            return json.loads(engine.globals().captured.split('=',1)[1])['cities'][0]
        first=read();self.assertEqual(first['native_purchase_target_list'],[3]);self.assertEqual(first['native_purchase_approved'],[3]);self.assertEqual(first['native_purchase_legacy_target_list'],[]);self.assertEqual(first['native_purchase_command_approved'],[]);self.assertIn('execution authority',first['native_purchase_query_kind'])
        self.assertEqual(len(first['tiles']),4)
        engine.execute("CSC_SERVICE_NATIVE.city_watch={['1:10']={[0]=true,[1]=true,[2]=true}}")
        focused=read();self.assertFalse(focused['broad_scan']);self.assertEqual(len(focused['tiles']),3)
        engine.execute("CSC_SERVICE_NATIVE.city_watch={['1:10']={}}")
        self.assertEqual(len(read()['tiles']),0)
        engine.execute("CSC_SERVICE_NATIVE.city_watch={['1:11']={}}")
        self.assertTrue(read()['broad_scan']);self.assertEqual(len(read()['tiles']),4)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--lua51-path',required=True)
    parser.add_argument('--output',type=Path);args=parser.parse_args();sys.path.insert(0,args.lua51_path)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MaterialTests))
    if args.output:args.output.write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'native_connections':0},indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
