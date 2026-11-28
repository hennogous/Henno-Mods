"""Run the actual Lua selector and flag lifecycle on small, auditable city layouts."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime


class CityVocabulary(unittest.TestCase):
    def setUp(self):
        self.vm=LuaRuntime()
        self.vm.execute("""
        pairPolicy={update=function()end};landscape={};rank=function(s)return s.rank end
        print=function()end;GameInfo={Terrains=function()
            local i=0;return function()i=i+1;if i==1 then return {TerrainType='TERRAIN_GRASS'} end end end}
        function properties()
            local values={}
            return {SetProperty=function(_,k,v)values[k]=v end,GetProperty=function(_,k)return values[k]end}
        end
        city=properties();center=properties();city.GetID=function()return 4 end;city.GetName=function()return 'City' end
        center.GetIndex=function()return 2 end
        attachments=0;city.AttachModifierByID=function()attachments=attachments+1 end
        profile={district={Index=1,DistrictType='TEST'}};key='CSC_AI_VOC_TEST'
        function site(i,base,clues)
            return {rank=base,baseCount=base,geometry={index=i,clues=clues,unknown=0,neighbors=6}}
        end
        function choose(s)return pairPolicy.choose(s,city,1,profile,10)end
        function apply(cue)pairPolicy.update(city,center,1,profile,cue,10,'owner')end
        """)
        self.vm.execute(Path(__file__).with_name('city_vocabulary.lua').read_text())

    def test_feature_signal_and_retirement(self):
        self.vm.execute("""
        local s={site(1,1,{TERRAIN_GRASS=6,FEATURE_FOREST=2}),site(2,0,{TERRAIN_GRASS=6})}
        local cue=choose(s); assert(cue.target==1 and cue.gain==12 and #cue.rules==1)
        assert(cue.rules[1]=='P_FEATURE_FOREST')
        apply(cue);apply(cue);assert(attachments==1 and center:GetProperty(key..'__P_FEATURE_FOREST')==1)
        apply(nil);assert(center:GetProperty(key..'__P_FEATURE_FOREST')==0)
        assert(not center:GetProperty(key..'_TARGET') and not center:GetProperty(key..'_REVIEW'))
        apply({floor=true,rules={'P_TERRAIN_GRASS'}})
        assert(center:GetProperty(key..'__U_TERRAIN_GRASS')==1 and not center:GetProperty(key..'__F_TERRAIN_GRASS'))
        apply({floor=true});assert(center:GetProperty(key..'__U_TERRAIN_GRASS')==0 and center:GetProperty(key..'__F_TERRAIN_GRASS')==1)
        """)

    def test_ambiguous_owned_and_fog_frontier(self):
        self.vm.execute("""
        local s={site(10,1,{FEATURE_FOREST=1,IMPROVEMENT_FARM=1}),
                 site(11,0,{FEATURE_FOREST=1,IMPROVEMENT_FARM=1})}
        assert(not choose(s).target and not choose(s).floor)
        s[2]=nil
        -- An unknown hex can simultaneously contain both attributes.
        s.frontierAll={{supplied=false,geometry={index=22,clues={},unknown=1,neighbors=6}}}
        assert(not choose(s).target)
        s[1].geometry.clues={RIVER=1}
        assert(choose(s).target==10)
        assert(choose({site(11,0,{RIVER=1})}).floor)
        """)

    def test_first_review_after_reload_retires_old_flags(self):
        self.vm.execute("""
        local mod=key..'__P_FEATURE_FOREST'
        center:SetProperty(key..'_ACTIVE',1);center:SetProperty(mod,1)
        GameInfo.Modifiers=function()
            local i=0;return function()i=i+1;if i==1 then return {ModifierId=mod} end end
        end
        apply(nil)
        assert(center:GetProperty(mod)==0 and not center:GetProperty(key..'_ACTIVE'))
        assert(attachments==0)
        """)

    def test_three_distinct_families_jointly_identify_the_footprint(self):
        self.vm.execute("""
        local rows={site(1,1,{TERRAIN_GRASS=6,RIVER=1,FEATURE_FOREST=1,IMPROVEMENT_FARM=1}),
                    site(2,0,{TERRAIN_GRASS=6,RIVER=1}),
                    site(3,0,{TERRAIN_GRASS=6,FEATURE_FOREST=1}),
                    site(4,0,{TERRAIN_GRASS=6,IMPROVEMENT_FARM=1})}
        local cue=choose(rows)
        assert(cue.floor and #cue.rules==3 and cue.target==1 and cue.gain==12 and cue.margin==12)
        """)
