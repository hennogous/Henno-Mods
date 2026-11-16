"""Diagnostic-only route parity and native timer reads; no packet is submitted."""
import json
import re
from pathlib import Path
from driver import lua,read,require,write_json

HERE=Path(__file__).resolve().parent
MOD=HERE.parents[3]/'Civ Supply Chains'
PATH='Lua_UI/TradeRoutes/'
SCANNER='CSC_TradeRouteInteractions.lua'
MODULES=('CSC_TradeRouteCore.lua','CSC_TradeRouteFacts.lua')


def inputs(legacy):
    return [Path(__file__),legacy,*[MOD/PATH/name for name in (*MODULES,SCANNER)]]


def encoder():
    source=read(HERE/'economy_component_probe.lua')
    return source[source.index('local function encode'):source.index('for _,target in ipairs(CSC_COMPONENT_TARGETS)do')]


def modules():
    return '\nlocal CSC_TradeRouteCore,CSC_TradeRouteFacts\n'+''.join('\ndo\n'+read(MOD/PATH/name)+'\nend\n'for name in MODULES)


def ui_code(legacy):
    original=read(legacy).split('local function CSC_OnBakersRouteRefreshEvent()',1)[0]
    old='if cityState == nil or CSC_CityStateMatchesPlotProperties(cityState) then return; end'
    require(original.count(old)==1,'Legacy route recorder boundary changed')
    original=original.replace(old,'if cityState == nil then return; end')
    current=read(MOD/PATH/SCANNER).split('local function CSC_OnBakersRouteRefreshEvent()',1)[0]
    require(current.count('if not matches(state)then')==1,'Current route recorder boundary changed')
    current=current.replace('if not matches(state)then','if true then')
    def capture(name,source,new):
        return '''
local '''+name+'''={}
do
 local CSC_GetBakersTradeRouteState,CSC_GetTailorsTradeRouteState,CSC_RefreshBakersTradeRouteProperties
 local ExposedMembers={}
 local include=function()end
 local UI={RequestPlayerOperation=function(sender,operation,state)
  assert(sender==Game.GetLocalPlayer())
  '''+name+'''[state.CityPlayerID..':'..state.CityID]=state
 end}
'''+(modules()if new else'')+source+'''
 CSC_RefreshBakersTradeRouteProperties()
'''+(''' local facts=assert(ExposedMembers.CSC_TradeRoutes.GetFacts())
 for _,city in pairs(facts.cities)do print('CSC_ROUTE_CITY='..encode(city))end
 for _,route in ipairs(facts.routes)do print('CSC_ROUTE_LINK='..encode(route))end
 print('CSC_ROUTE_OBSERVED='..encode({turn=facts.turn,version=facts.version,routes=#facts.routes}))
'''if new else'')+'''
end
'''
    return encoder()+capture('original',original,False)+capture('current',current,True)+'''
assert(encode(original)==encode(current),'Shared route scanner changes gameplay packets')
local count=0;for _ in pairs(current)do count=count+1 end
assert(count>0)
print('CSC_ROUTE_PARITY='..encode({verified=true,cities=count,turn=Game.GetCurrentGameTurn(),submittedOperations=0}))
'''


def durations_code(observed):
    return encoder()+modules()+'''
local observed='''+lua(observed)+'''
assert(Game.GetCurrentGameTurn()-observed.turn>=0 and Game.GetCurrentGameTurn()-observed.turn<=1)
local qualified=CSC_TradeRouteFacts.QualifyWindows(observed,GameInfo,Game,GameConfiguration,Players,UnitOperationTypes)
for _,route in ipairs(qualified.routes)do print('CSC_ROUTE_DURATION='..encode(route))end
print('CSC_ROUTE_DURATION_RESULT='..encode({turn=Game.GetCurrentGameTurn(),stats=qualified.durationStats,policy=qualified.durationPolicy}))
'''


def records(raw,marker):
    return [json.loads(v)for v in re.findall(re.escape(marker)+r'=([^\r\n]+)',raw)]


def run(controller,output,legacy):
    output=Path(output);output.mkdir()
    code=ui_code(legacy);(output/'ui.lua').write_text(code,encoding='utf-8')
    raw=controller.cmd(code,'PlotInfo','route-scanner-parity')
    (output/'ui.txt').write_text(raw,encoding='utf-8')
    parity,=records(raw,'CSC_ROUTE_PARITY');require(parity['verified'],'Route scanner parity failed')
    observed,=records(raw,'CSC_ROUTE_OBSERVED')
    observed['cities']={r['key']:r for r in records(raw,'CSC_ROUTE_CITY')}
    observed['routes']=records(raw,'CSC_ROUTE_LINK')
    require(len(observed['cities'])==parity['cities'],'Route endpoint capture incomplete')
    write_json(output/'observed.json',observed)
    code=durations_code(observed);(output/'durations.lua').write_text(code,encoding='utf-8')
    raw=controller.cmd(code,'GameCore_Tuner','route-native-duration')
    (output/'durations.txt').write_text(raw,encoding='utf-8')
    durations,=records(raw,'CSC_ROUTE_DURATION_RESULT');durations['routes']=records(raw,'CSC_ROUTE_DURATION')
    require(len(durations['routes'])==len(observed['routes']),'Native duration capture incomplete')
    write_json(output/'durations.json',durations)
    result=dict(verified=True,diagnostic_only=True,submitted_operations=0,ai_turns_advanced=0,
                scanner=parity,route_count=len(observed['routes']),duration=durations['stats'],policy=durations['policy'])
    write_json(output/'result.json',result)
    return result
