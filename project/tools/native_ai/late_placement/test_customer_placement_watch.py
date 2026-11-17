"""Customer diagnostics preserve policy calls while recording opportunities.

The observer must see singleton/ordinary alternatives, remove stale sets and
retain native journal order without publishing another bid or quote.
"""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

SOURCE=Path(__file__).with_name('customer_placement_watch.lua').read_text()


class CustomerPlacementWatch(unittest.TestCase):
    def vm(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute('''
turn=150;lines={};calls=0;reads=0;publishes=0
print=function(s)lines[#lines+1]=s end
Game={GetCurrentGameTurn=function()return turn end}
groups={{city=7,district=6,reference={plot=10,adjacency=3,links=0},candidates={
 {plot=20,adjacency=2,links=1}}},
 {city=8,district=4,reference={plot=30,adjacency=1,links=1},candidates={}}}
local function reader()reads=reads+1;return groups,'reader-extra'end
snapshot={id=1,CustomerCandidateSets=reader};originalReader=reader
CSC_AI_EconomyAdapters={CustomerEconomicOffers=function(s,p)
 calls=calls+1;local result,extra=s.CustomerCandidateSets(p)
 assert(result==groups and extra=='reader-extra')
 if crash then error('policy failure')end
 return result,99
end}
CSC_AI_DistrictBridge={Publish=function(...)publishes=publishes+1;return true,'same'end}
CE_AIDistrictScoresStatus=function()return '{"generation":9,"trace_count":2}'end
CE_AIDistrictScoresTraceRead=function()return '{"records":[{"k":"net","player":1,"city":7,"district":6,"plot":20,"base":50,"result":70},{"k":"best","player":2,"city":7,"district":6,"plot":50}]}'end
''')
        vm.execute(SOURCE)
        return vm

    def test_transparency_changed_sets_and_invalidation(self):
        self.vm().execute(r'''
local E=CSC_AI_EconomyAdapters
local result,extra=E.CustomerEconomicOffers(snapshot,{})
assert(result==groups and extra==99 and calls==1 and reads==1)
assert(snapshot.CustomerCandidateSets==originalReader)
local joined=table.concat(lines,'\n')
assert(joined:find('linked=20:2.000000:1 ordinary=10:3.000000:0',1,true))
assert(joined:find('city=8 district=4 reference=30 linked=30:1.000000:1 ordinary=',1,true))
local before=#lines;turn=151;E.CustomerEconomicOffers(snapshot,{})
assert(#lines==before+1) -- unchanged candidates only need a freshness clock
groups={};turn=152;E.CustomerEconomicOffers(snapshot,{})
assert(table.concat(lines,'\n'):find('REMOVED turn=152 scope=1:7:6',1,true))
crash=true;local ok=pcall(E.CustomerEconomicOffers,snapshot,{})
assert(not ok and snapshot.CustomerCandidateSets==originalReader)
''')

    def test_native_generation_ordinal_and_existing_reader_dispatch(self):
        self.vm().execute(r'''
CSC_AI_EconomyAdapters.CustomerEconomicOffers(snapshot,{})
assert(CSC_AI_DistrictBridge.Publish(123)==true and publishes==1)
local count=0;for _,line in ipairs(lines)do if line:find('_NATIVE ',1,true)then count=count+1 end end
assert(count==1) -- unrelated scope is excluded
CSC_CUSTOMER_PLACEMENT_WATCH.Finish()
local count2=0;for _,line in ipairs(lines)do if line:find('_NATIVE ',1,true)then count2=count2+1 end end
assert(count2==1) -- same generation/ordinal is not reported twice
local drains=0;CSC_QUARTER_PLACEMENT_WATCH={Drain=function()drains=drains+1 end}
CE_AIDistrictScoresStatus=function()error('duplicate journal reader')end
assert(CSC_AI_DistrictBridge.Publish()==true and publishes==2)
CSC_CUSTOMER_PLACEMENT_WATCH.Finish();assert(drains==1)
''')


if __name__=='__main__':unittest.main()
