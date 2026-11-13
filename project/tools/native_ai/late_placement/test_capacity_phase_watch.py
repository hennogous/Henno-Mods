"""Diagnostic transparency and separation of cache state from live facts."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime


class CapacityPhases(unittest.TestCase):
    def vm(self):
        vm=LuaRuntime()
        vm.execute('''
lines={};callbacks={};population=6;uiPopulation=6;used=2;allowed=2;turn=50;calls=0
print=function(...)local t={...};for i,v in ipairs(t)do t[i]=tostring(v)end;lines[#lines+1]=table.concat(t,'\\t')end
Game={GetCurrentGameTurn=function()return turn end}
CE_AIDistrictScoresStatus=function()return '{"version":1}'end
local function event(name)return{Add=function(f)callbacks[name]=f end}end
Events={CityPopulationChanged=event('population'),DistrictAddedToMap=event('district'),PlayerTurnActivated=event('player')}
GameEvents={OnGameTurnStarted=event('round')}
local districts={GetNumDistricts=function()return used end,GetDistrictByIndex=function(_,i)
return{GetType=function()return 1 end,IsComplete=function()return true end}end}
city={GetID=function()return 7 end,GetPopulation=function()return population end,GetName=function()return 'CITY' end,GetDistricts=function()return districts end}
CityManager={GetCity=function()return city end}
local player={GetID=function()return 1 end,GetCities=function()return{Members=function()local done=false;return function()if not done then done=true;return 1,city end end end}end}
PlayerManager={GetAliveMajors=function()return{player}end}
GameInfo={Districts={[1]={RequiresPopulation=true}}}
ExposedMembers={CSC_Adjacency={GetDistrictCapacity=function()return{population=uiPopulation,used=used,allowed=allowed}end}}
CSC_AI_DistrictBridge={Publish=function(...)calls=calls+1;args={...};return true,'receipt'end}
''')
        vm.execute(Path(__file__).with_name('capacity_phase_watch.lua').read_text(encoding='utf-8'))
        return vm

    def test_wrapper_retains_packet_and_results_and_keeps_initial_offers_unknown(self):
        vm=self.vm()
        vm.execute('''
assert(calls==0)
entry={player=1,city=7,district=37,plot=99,delta=0,finalQ8=1234}
local ok,message=CSC_AI_DistrictBridge.Publish(2,74,46,38,{1},{entry},'extra')
assert(ok and message=='receipt'and calls==1 and args[7]=='extra')
assert(args[6][1]==entry and entry.delta==0 and entry.finalQ8==1234)
local text=table.concat(lines,'\\n')
assert(text:find('offersKnown=false',1,true)and text:find('bid37=1234',1,true))
assert(text:find('offers37=1',1,true)and text:find('event=publication%-accepted'))
''')

    def test_population_event_retains_stale_ui_before_next_publication(self):
        vm=self.vm()
        vm.execute('''
population=7;turn=51;callbacks.population(1,7)
local text=lines[#lines]
assert(text:find('event=population%-event')and text:find('agrees=false',1,true))
assert(text:find('population=7',1,true)and text:find('uiPopulation=6',1,true)and text:find('version=1',1,true))
uiPopulation=7;allowed=3
CSC_AI_DistrictBridge.Publish(2,74,46,38,{1},{})
text=table.concat(lines,'\\n')
assert(text:find('event=publication%-accepted')and text:find('uiAllowed=3',1,true))
''')

    def test_observer_failure_does_not_block_publisher(self):
        vm=self.vm()
        vm.execute('''
city.GetDistricts=function()error('bad diagnostic read')end
local ok,message=CSC_AI_DistrictBridge.Publish(2,74,46,38,{1},{})
assert(ok and message=='receipt'and calls==1)
assert(table.concat(lines,'\\n'):find('CSC_CAPACITY_PHASE_FAULT',1,true))
assert(not pcall(CSC_CAPACITY_PHASE_WATCH.Finish))
''')


if __name__=='__main__':unittest.main()
