"""Exercise the candidate's stock property lifecycle without a game or CE."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


HERE = Path(__file__).parent
POLICY = (HERE/'city_material_cue_choice.lua').read_text() + '\n' + (HERE/'local_material_guidance.lua').read_text()
SETUP = """
turn=1; connected=false; human=false; built=false; good=true; scans=0; attaches=0
function object()
    local values={}
    return {GetProperty=function(_,k)return values[k]end,SetProperty=function(_,k,v)values[k]=v end}
end
function makeCity(id)
    local c=object()
    c.GetID=function()return id end
    c.GetX=function()return id end
    c.GetY=function()return 0 end
    c.GetDistricts=function()return {HasDistrict=function()return built end}end
    c.AttachModifierByID=function(_,rule) attaches=attaches+1; lastRule=rule end
    return c
end
Game=object();Game.GetCurrentGameTurn=function()return turn end
GameConfiguration={IsAnyMultiplayer=function()return connected end,IsHotseat=function()return false end}
centers={};cities={}
for i=1,2 do
    local index=i
    centers[i]=object();centers[i].GetIndex=function()return index end
    cities[i]=makeCity(i)
end
Map={GetPlot=function(x,y)return centers[x]end}
player=object();player.GetID=function()return 2 end;player.IsHuman=function()return human end
player.GetCities=function()return {Members=function()return ipairs(cities)end}end
PlayerManager={GetAliveMajors=function()return {player}end}
GameEvents={OnGameTurnStarted={Add=function(f)tick=f end}}
terrainKeys={'PLAINS'};profiles={{district={Index=4,DistrictType='TEST'}}}
function ownedSites()
    scans=scans+1
    return {{count={PLAINS=3},materialTerrain=good and {PLAINS=true} or {},customerRank=1},
            {count={PLAINS=2},materialTerrain={},customerRank=0}}
end
print=function(kind,...)if kind=='CSC_LOCAL_CUE_FAULT' then fault=true end end
"""


class LocalMaterialGuidance(unittest.TestCase):
    def test_budget_reloads_withdrawal_and_reattachment(self):
        vm = LuaRuntime()
        vm.execute(SETUP)
        vm.execute(POLICY)
        vm.execute("assert(scans==1 and attaches==1 and centers[1]:GetProperty(lastRule)==1)")
        vm.execute(POLICY)
        vm.execute("tick(); assert(scans==1 and attaches==1)")
        vm.execute("turn=2; tick(); assert(scans==2 and attaches==2)")
        vm.execute("turn=13; good=false; tick(); assert(centers[1]:GetProperty(lastRule)==0)")
        vm.execute("turn=14; built=true; tick(); assert(scans==3 and centers[2]:GetProperty(lastRule)==0)")
        vm.execute("turn=25; good=true; built=false; tick(); assert(attaches==2 and centers[1]:GetProperty(lastRule)==1)")
        vm.execute("turn=26; human=true; tick(); assert(centers[1]:GetProperty(lastRule)==0 and not fault)")

    def test_multiplayer_and_unidentified_old_seat(self):
        vm = LuaRuntime()
        vm.execute(SETUP + '\nconnected=true')
        vm.execute(POLICY)
        vm.execute("assert(not lastRule and scans==0 and not Game:GetProperty('CSC_AI_OriginalHuman_2'))")
        vm.execute("connected=false;turn=55;tick();assert(scans==0 and not fault)")


if __name__ == '__main__':
    unittest.main()
