"""Exercise the city opportunity rule with Lua 5.1 before running matched games."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


POLICY = Path(__file__).with_name('no_base_city.lua').read_text()
WORLD = """
function catalog(rows,key)
 local lookup={}
 for _,r in ipairs(rows) do if key then lookup[r[key]]=r;lookup[r.Index]=r end end
 return setmetatable(lookup,{__call=function() local i=0;return function()i=i+1;return rows[i]end end})
end
function object()
 local v={};return {GetProperty=function(_,k)return v[k]end,SetProperty=function(_,k,x)v[k]=x end}
end
local d='DISTRICT_CSC_TAILORS_QUARTER'
local tag='CLASS_CSC_TAILORS_BASE'
GameInfo={CSC_QuarterMaterialAdjacencyConfig=catalog({{QuarterKey='TAILORS',SourceTag=tag,
 SourceFilter='',AdjacencyType='FROM_RINGS_TYPETAG_RESOURCE'}}),
 Districts=catalog({{DistrictType=d,Index=4}},'DistrictType'),
 Resources=catalog({{ResourceType='FLAX',ResourceClassType='RESOURCECLASS_BONUS',Index=8},
 {ResourceType='COTTON',ResourceClassType='RESOURCECLASS_LUXURY',Index=9}},'ResourceType'),
 TypeTags=catalog({{Type='FLAX',Tag=tag},{Type='COTTON',Tag=tag}}),Terrains=catalog({{TerrainType='GRASS'}}),
 Technologies={},Civics={},Features={}}
turn=1;multi=false;human=false;covered=-1;resource=-1;owner=-1;unseen=-1;built=false
siteOwner=-1;siteResource=-1;calls=0;attach=0;id=1
Game=object();Game.GetCurrentGameTurn=function()return turn end
GameConfiguration={IsAnyMultiplayer=function()return multi end,IsHotseat=function()return false end}
gate='CSC_AI_NO_BASE_'..d
center=object()
function plot(n)
 return {GetX=function()return n end,GetY=function()return 0 end,GetIndex=function()return n end,
  GetOwner=function()return n==4 and owner or siteOwner end,GetDistrictType=function()return n==4 and covered or -1 end,
  GetWonderType=function()return -1 end,IsWater=function()return false end,IsImpassable=function()return false end,
  GetFeatureType=function()return -1 end,GetResourceType=function()return n==4 and resource or siteResource end}
end
site=plot(3);supplier=plot(4)
center.GetIndex=function()return 0 end
city=object();city.GetX=function()return 0 end;city.GetY=function()return 0 end
city.GetID=function()return 1 end;city.GetName=function()return 'TEST' end
city.GetDistricts=function()return {HasDistrict=function()return built end}end
city.AttachModifierByID=function()attach=attach+1 end
player=object();player.GetID=function()return id end;player.IsHuman=function()return human end
player.GetCities=function()return {Members=function()return ipairs({city})end}end
PlayerManager={GetAliveMajors=function()return {player}end}
PlayersVisibility={[1]={IsRevealed=function(_,x)return x~=unseen end}}
Map={GetPlot=function()return center end,GetPlotXYWithRangeCheck=function(x,y,dx,dy,r)
 assert(r==3);calls=calls+1;if dx==3 and dy==0 then return site end end,
 GetAdjacentPlot=function(x,y,dir)if dir==0 then return supplier end end}
GameEvents={OnGameTurnStarted={Add=function(f)tick=f end}};print=function()end
function advance()turn=turn+12;tick()end
function check(expected)assert(city:GetProperty(gate..'_REASON')==expected)
 assert((center:GetProperty(gate)==1)==(expected=='absent'))end
"""


class Opportunity(unittest.TestCase):
    def game(self, extra=''):
        vm=LuaRuntime()
        vm.execute(WORLD+extra)
        vm.execute(POLICY)
        return vm

    def test_unowned_site_and_supplier_then_last_supplier_lost(self):
        vm=self.game('resource=8')
        vm.execute("check('base');covered=6;advance();check('absent');assert(attach==1)")
        vm.execute("covered=-1;resource=9;advance();check('base');owner=2;advance();check('absent');assert(attach==1)")
        vm.execute("built=true;advance();check('built')")

    def test_fog_and_blocked_footprint(self):
        vm=self.game('unseen=4')
        vm.execute("check('unknown');unseen=-1;resource=8;siteResource=9;advance();check('absent')")
        vm.execute("siteResource=-1;siteOwner=2;advance();check('absent');siteOwner=-1;advance();check('base')")

    def test_multiplayer_human_capture_and_reload(self):
        self.game('multi=true').execute('assert(calls==0 and attach==0)')
        self.game('human=true').execute('assert(calls==0 and attach==0)')
        vm=self.game()
        vm.execute("check('absent');initial=calls")
        vm.execute(POLICY)
        vm.execute("assert(calls==initial and attach==1);id=2;human=true;advance();assert(center:GetProperty(gate)~=1)")


if __name__=='__main__':
    unittest.main()
