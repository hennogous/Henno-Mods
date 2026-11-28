"""Regression cases for city-local signed adjacencies and their two saved slots."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime
from test_local_material_guidance import SETUP

HERE = Path(__file__).parent


class PairedSiteTest(unittest.TestCase):
    def setUp(self):
        self.vm = LuaRuntime()
        self.vm.execute("""
        GameInfo={CSC_AdjacencyRules=function()return function()return nil end end}
        profile={district={Index=1,DistrictType='QUARTER'}}
        local function props()
          local obj,data={},{}
          function obj:GetProperty(k)return data[k]end
          function obj:SetProperty(k,v)data[k]=v end
          return obj
        end
        function makeCity()
          local c=props(); function c:GetID()return 34 end
          function c:GetName()return 'CITY' end
          c.bound=0;function c:AttachModifierByID(id)self.bound=self.bound+1 end
          return c,props()
        end
        city,center=makeCity()
        function site(id,a,b,isBase)
          return {count={GRASS=a,PLAINS=b},baseCount=isBase and 1 or 0,
            materialTerrain=isBase and {GRASS=true} or {},customerRank=0,
            plot={GetIndex=function()return id end,IsHills=function()return false end,
                  GetRiverCrossingCount=function()return 0 end}}
        end
        print=function()end
        """)
        self.vm.execute((HERE/'paired_material_layout.lua').read_text())

    def test_two_terms_on_real_target_and_no_site_ties(self):
        self.vm.execute("""
        -- The good site shares each count with a different bad rival.
        sites={site(2,1,1,true),site(3,0,1,false),site(4,1,0,false)}
        cue=pairPolicy.choose(sites,city,1,profile,1)
        assert(cue.a and cue.b and cue.target==2 and cue.margin==1)
        local single=pairPolicy.choose({sites[1],sites[2]},city,1,profile,2)
        assert(single.a and not single.b)
        assert(not pairPolicy.choose({sites[1],site(9,1,1,false)},city,1,profile,3))
        """)

    def test_switch_withdraw_reload_and_another_city(self):
        self.vm.execute("""
        local A,B,C='a','b','c'
        function apply(c,p,cue)pairPolicy.update(c,p,1,profile,cue,1,'owner') end
        local second,other=makeCity()
        apply(city,center,{a=A,b=B});apply(second,other,{a=A})
        apply(city,center,{a=B,b=C})
        assert(center:GetProperty(A)==0 and center:GetProperty(B)==1 and center:GetProperty(C)==1)
        assert(other:GetProperty(A)==1 and not other:GetProperty(C))
        """)

        self.vm.execute((HERE/'paired_material_layout.lua').read_text())
        self.vm.execute("""
        apply(city,center,{a='b',b='c'});assert(city.bound==3)
        apply(city,center,nil)
        assert(center:GetProperty('b')==0 and center:GetProperty('c')==0 and not center:GetProperty('CSC_AI_PAIR_ACTIVE_QUARTER2'))
        apply(city,center,{a='a'});assert(city.bound==3 and center:GetProperty('a')==1)
        """)

    def test_relief_keeps_each_known_weak_site_below_ordinary_value(self):
        self.vm.execute("terrainKeys={'GRASS','PLAINS'};reliefWeight=6")
        # Both policy files normally share the gameplay entry's lexical scope.
        self.vm.execute((HERE/'paired_material_layout.lua').read_text()+'\n'+(HERE/'layout_floor.lua').read_text())
        self.vm.execute("""
        local good=site(675,1,5,true)
        local bad=site(750,0,6,false)
        local function pick(sites)return pairPolicy.choose(sites,city,1,profile,10)end
        local mixed=pick({good,bad})
        assert(mixed.floor and mixed.target==675 and mixed.a:match('__R_GRASS$'))
        assert(pick({bad}).floor and not pick({bad}).a)
        assert(not pick({good}).floor and not pick({good}).a)
        local same=pick({good,site(751,1,5,false)})
        assert(same.floor and not same.a)
        local newRival=site(599,2,4,false)
        assert(not pick({good,bad,newRival}).a)
        local frontier={count={GRASS=2},unknown=0,neighbors=6}
        local bordered={good,bad,frontierWeak={frontier}}
        assert(not pick(bordered).a and pick(bordered).floor)
        frontier.count={}
        assert(pick(bordered).target==675)
        frontier.unknown=1
        assert(not pick(bordered).a)
        assert(pick({good,frontierWeak={frontier}}).floor)
        assert(not pick({frontierWeak={frontier}}).target)
        pairPolicy.releaseAmbiguousFloor=true
        local fallback=pick(bordered)
        assert(not fallback.floor and not fallback.a and not fallback.target)
        assert(not pick({good,site(751,1,5,false)}).floor)
        assert(pick({bad,frontierWeak={frontier}}).floor and pick({}).floor)
        local distinct=pick({good,bad})
        assert(distinct.floor and distinct.target==675 and distinct.a)
        -- Civ reads the centre properties when scoring a site. Check a city
        -- which already had BOTH the penalty and a positive cue attached.
        GameInfo.Terrains=function()return function()return nil end end
        local gate='CSC_AI_NO_BASE_QUARTER'
        local function publish(cue)pairPolicy.update(city,center,1,profile,cue,10,'owner')end
        publish(distinct)
        assert(center:GetProperty(gate)==1 and center:GetProperty(distinct.a)==1)
        publish(fallback)
        assert(center:GetProperty(gate)==0 and center:GetProperty(distinct.a)==0)
        publish(pick({bad}))
        assert(center:GetProperty(gate)==1 and center:GetProperty(distinct.a)==0)
        reliefWeight=0
        assert(pick({good}).floor and not pick({good,bad}).a)
        """)

    def test_split_relief_with_hidden_frontier_neighbor_and_ordinary_fallback(self):
        self.vm.execute("terrainKeys={'GRASS','PLAINS'};reliefWeight=6")
        self.vm.execute('\n'.join((HERE/f).read_text() for f in
                        ('paired_material_layout.lua','layout_floor.lua','split_floor_relief.lua')))
        self.vm.execute("""
        pairPolicy.releaseAmbiguousFloor=true
        local good,left,right=site(675,1,2,true),site(750,1,0,false),site(751,0,1,false)
        good.count.WATER=3;left.count.WATER=5;right.count.WATER=5
        local frontier={count={WATER=5},unknown=1,neighbors=6}
        local sites={good,left,right,frontierWeak={frontier}}
        local function choose()return pairPolicy.choose(sites,city,1,profile,25)end
        local result=choose()
        assert(result.a and result.b and result.target==675 and result.delta==3)
        -- One Tundra-like match plus an unseen hex can erase the penalty on
        -- the frontier, the same hazard observed on Tenochtitlan's plot 599.
        frontier.count={WATER=4,PLAINS=1}
        local veto=choose()
        assert(not veto.a and not veto.b and not veto.floor)
        -- Each weak rival matches both cues equally. A positive-only rule
        -- rewards them; the signed pair gives them zero and the target +3.
        good.count={GRASS=3,PLAINS=2,WATER=1}
        left.count={GRASS=2,PLAINS=2,WATER=2}
        right.count={GRASS=1,PLAINS=1,WATER=4}
        frontier.count={GRASS=1,PLAINS=2,WATER=2}
        local signed=choose()
        assert(not signed.floor and signed.target==675 and signed.delta==3)
        assert(signed.a:match('__P_GRASS$') and signed.b:match('__N_PLAINS$'))
        frontier.count={GRASS=2,PLAINS=2,WATER=1}
        assert(not choose().target)
        terrainKeys={'GRASS','PLAINS','TUNDRA'}
        good.count={GRASS=2,PLAINS=2,TUNDRA=2}
        left.count={GRASS=3,TUNDRA=3}
        right.count={PLAINS=3,TUNDRA=3}
        sites.frontierWeak={}
        assert(not choose().target)
        pairPolicy.thirdRelief=true
        local three=choose()
        assert(three.target==675 and three.delta==6 and three.c)
        sites.frontierWeak={{count={GRASS=1,TUNDRA=1},unknown=4,neighbors=6}}
        assert(not choose().target)
        GameInfo.Terrains=function()return function()return nil end end
        pairPolicy.update(city,center,1,profile,three,25,'owner')
        assert(center:GetProperty(three.c)==1)
        pairPolicy.update(city,center,1,profile,{a=three.c},26,'owner')
        assert(center:GetProperty(three.c)==1 and center:GetProperty(three.a)==0)
        pairPolicy.update(city,center,1,profile,nil,27,'owner')
        assert(center:GetProperty(three.c)==0 and not center:GetProperty('CSC_AI_PAIR_ACTIVE_QUARTER3'))
        """)

    def test_foundation_and_capture_callbacks_clear_only_the_affected_city(self):
        self.vm.execute(SETUP + """
        profiles={[4]={district={Index=4,DistrictType='TEST'}}}
        function ownedSites()
          return {site(2,1,1,true),site(3,0,1,false),site(4,1,0,false)}
        end
        Events={DistrictAddedToMap={Add=function(f)foundation=f end},
                CityTransfered={Add=function(f)capture=f end}}
        CityManager={GetCity=function(_,cid)return cities[cid] end}
        centers[1].GetDistrictType=function()return 4 end
        """)
        self.vm.execute((HERE/'local_material_guidance.lua').read_text())
        self.vm.execute("""
        turn=2;tick()
        local key='CSC_AI_PAIR_ACTIVE_TEST'
        local a=centers[1]:GetProperty(key..1);local b=centers[1]:GetProperty(key..2)
        assert(a and b and centers[2]:GetProperty(b)==1)
        foundation(2,100,1,1,0,4)
        assert(centers[1]:GetProperty(a)==0 and centers[1]:GetProperty(b)==0)
        assert(centers[2]:GetProperty(b)==1)
        capture(2,2,1)
        assert(centers[2]:GetProperty(a)==0 and centers[2]:GetProperty(b)==0)
        """)

if __name__=='__main__':
    unittest.main()
