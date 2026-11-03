"""Execute the real reader in Lua5.1 with explicit mocked engine bindings."""
import argparse, copy, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = r'''
local function info(rows,key)
 local t={};for _,r in ipairs(rows)do t[r[key]]=r;t[r.Index]=r end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
GameInfo={Districts=info({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},{Index=1,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'}},'DistrictType')}
Game={GetCurrentGameTurn=function()return 250 end,GetProperty=function()end,SetProperty=function()error('Forbidden write')end}
Map={GetGridSize=function()return 74,46 end}
local d={GetType=function()return 0 end,GetX=function()return 42 end,GetY=function()return 42 end,IsComplete=function()return true end,IsPillaged=function()return false end}
DS={GetNumDistricts=function()return 1 end,GetDistrictByIndex=function(_,i)assert(i==0);return d end,Members=function()error('Gameplay Members forbidden')end}
local c={GetID=function()return 655369 end,GetName=function()return 'Avignon'end,GetX=function()return 42 end,GetY=function()return 42 end,GetPopulation=function()return 1 end,GetDistricts=function()return DS end,GetBuildQueue=function()return{CurrentlyBuilding=function()return 'UNIT_BUILDER'end}end}
local cs={Members=function()local done=false;return function()if not done then done=true;return 1,c end end end}
Players={[0]={IsHuman=function()return true end,IsAlive=function()return true end},[4]={IsHuman=function()return false end,IsAlive=function()return true end,IsMajor=function()return true end,GetCities=function()return cs end,GetTechs=function()return{}end,GetCulture=function()return{}end}}
PLOT={GetIndex=function()return 3076 end,GetX=function()return 42 end,GetY=function()return 41 end,GetOwner=function()return 4 end,GetDistrictType=function()return -1 end,GetFeatureType=function()return -1 end,GetResourceType=function()return -1 end,GetImprovementType=function()return -1 end,IsImprovementPillaged=function()return false end,IsWater=function()return false end,IsImpassable=function()return false end}
Map.GetPlotByIndex=function(i)assert(i==3076);return PLOT end
PlayersVisibility={[4]={IsRevealed=function()return true end}}
'''


def main():
    p=argparse.ArgumentParser();p.add_argument('--lua-dependencies',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(a.lua_dependencies));from lupa.lua51 import LuaRuntime
    from live_probe import parse,validate_source
    results=[]
    for name,modify,accepted in [
        ('read-only source with optional getters unavailable','',True),
        ('hidden target rejected','PlayersVisibility[4].IsRevealed=function()return false end',False),
        ('original human rejected','Players[4].IsHuman=function()return true end',False),
        ('pending assistance rejected',"Game.GetProperty=function(_,k)if k=='CSC_AI_ASSISTANCE_V1_PENDING_5'then return{status='pending'}end end",False),
        ('occupied target rejected','PLOT.GetDistrictType=function()return 0 end',False),
        ('wrong city ownership rejected','PLOT.GetOwner=function()return 3 end',False),
    ]:
        lua=LuaRuntime(unpack_returned_tuples=True);lines=[];lua.globals().print=lambda v:lines.append(v)
        lua.execute(HARNESS);lua.execute(modify);lua.execute((HERE/'source_snapshot.lua').read_text())
        assert lua.eval('_VERSION')=='Lua 5.1';value=parse(lines[0]);passed=True
        try:validate_source(value)
        except ValueError:passed=False
        assert passed==accepted,name
        results.append(dict(case=name,source_gate_accepted=passed,pass_=True))
    payload=dict(scope='Real Lua5.1 reader and source gate, mocked engine only; no native/game operations',cases=results,
                 reader_sha256=hashlib.sha256((HERE/'source_snapshot.lua').read_bytes()).hexdigest())
    a.output.write_text(json.dumps(payload,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(results))))


if __name__=='__main__':main()
