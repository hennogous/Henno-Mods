"""Execute the real UI filter; preserve real/other-mod rows and indexed access."""
import argparse
from pathlib import Path
import sys
import re

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--lua-dependencies',type=Path,required=True)
a=p.parse_args()
sys.path.insert(0,str(a.lua_dependencies))
from lupa import LuaRuntime

lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
UI={}; GameInfo={};
local function rows(values,field)
 local t={};for i,r in ipairs(values) do t[r[field]]=r;t[r.Index or i-1]=r end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return values[i]end end})
end
GameInfo.Yields=rows({{YieldType='YIELD_FOOD',Index=0},{YieldType='YIELD_CSC_AI_PLACEMENT',Index=6},{YieldType='YIELD_OTHER_MOD',Index=7}},'YieldType')
GameInfo.Technologies=rows({{TechnologyType='TECH_POTTERY'},{TechnologyType='TECH_CSC_AI_PLACEMENT'}},'TechnologyType')
GameInfo.Adjacency_YieldChanges=rows({{ID='real',YieldType='YIELD_FOOD'},{ID='private',YieldType='YIELD_CSC_AI_PLACEMENT'},{ID='other',YieldType='YIELD_OTHER_MOD'}},'ID')
GameInfo.District_Adjacencies=rows({{YieldChangeId='real'},{YieldChangeId='private'},{YieldChangeId='other'}},'YieldChangeId')
local native=GameInfo;GameInfo=setmetatable({}, {__index=native,__newindex=function()error('native read-only table')end})
''')
source=(Path(__file__).resolve().parents[3]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_UIFilter.lua').read_text()
lua.execute(source)
lua.execute('''
local function names(t,key)local a={};for r in t() do a[#a+1]=r[key] end;return table.concat(a,',') end
assert(names(GameInfo.Yields,'YieldType')=='YIELD_FOOD,YIELD_OTHER_MOD')
assert(names(GameInfo.Technologies,'TechnologyType')=='TECH_POTTERY,TECH_CSC_AI_PLACEMENT')
assert(names(GameInfo.District_Adjacencies,'YieldChangeId')=='real,other')
assert(names(GameInfo.Adjacency_YieldChanges,'ID')=='real,other')
assert(GameInfo.Yields['YIELD_CSC_AI_PLACEMENT'].Index==6)
assert(GameInfo.Yields[6].YieldType=='YIELD_CSC_AI_PLACEMENT')
assert(GameInfo.Yields['YIELD_OTHER_MOD'].Index==7)
assert(GameInfo.Adjacency_YieldChanges['private'].YieldType=='YIELD_CSC_AI_PLACEMENT')
''')
lua.execute(source)
print('UI filter passed: own rows hidden, other mods/real rows/indexed access preserved, reentry safe')

# Execute the shipped report function against six real yields plus our private
# yield. This catches the actual nil-arithmetic failure seen with extra yields.
game=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI")
report=(game/'Base/Assets/UI/Screens/ReportScreen.lua').read_text(encoding='utf-8-sig')
body=re.search(r'\nfunction GetWorkedTileYieldData\b.*?(?=\nfunction )',report,re.S).group(0)
body=re.sub(r':\s*(?:table|number|string|boolean)\b','',body)
test=LuaRuntime(unpack_returned_tuples=True)
test.execute('''
UI={};local names={'YIELD_FOOD','YIELD_PRODUCTION','YIELD_GOLD','YIELD_SCIENCE','YIELD_CULTURE','YIELD_FAITH','YIELD_CSC_AI_PLACEMENT'}
local rows={};for i,name in ipairs(names) do rows[i]={Index=i-1,YieldType=name} end
local yields=setmetatable({}, {__call=function() local i=0;return function()i=i+1;return rows[i]end end})
local empty=setmetatable({}, {__call=function()return function()return nil end end})
local native={Yields=yields,District_Adjacencies=empty,Adjacency_YieldChanges=empty}
GameInfo=setmetatable({}, {__index=native,__newindex=function()error('native read-only cache')end})
Map={GetCityPlots=function()return {GetPurchasedPlots=function()return {1,2}end}end,
 GetPlotByIndex=function(i)return {GetX=function()return i end,GetY=function()return 0 end,GetYield=function(_,y)return y==6 and 99 or y+1 end}end}
TEST_CITY={GetCitizens=function()return {IsPlotWorked=function()return true end}end}
TEST_CULTURE={GetTourismAt=function()return 1 end}
''')
test.execute(body)
test.execute("local ok=pcall(GetWorkedTileYieldData,TEST_CITY,TEST_CULTURE);assert(not ok,'fixture must reproduce unfiltered native report failure')")
test.execute(source)
test.execute('''local r=GetWorkedTileYieldData(TEST_CITY,TEST_CULTURE)
assert(r.YIELD_FOOD==2 and r.YIELD_PRODUCTION==4 and r.YIELD_GOLD==6)
assert(r.YIELD_SCIENCE==8 and r.YIELD_CULTURE==10 and r.YIELD_FAITH==12 and r.TOURISM==2)
assert(r.YIELD_CSC_AI_PLACEMENT==nil)
''')
print('Shipped ReportScreen worked-tile sum passed: private yield excluded, six real totals unchanged')
