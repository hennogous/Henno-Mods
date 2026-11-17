"""Diagnostic-only cold/warm pass of current integrated placement policy.

Load production modules lexically, keep existing callbacks/globals untouched,
and calculate packets without submitting them. Counts and Lua-clock/wall time expose
joint work and budget failures before the fresh integrated-only outcome games.
"""
import re
import time
from pathlib import Path
from driver import read,lua,write_json,require
from route_catalogue_probe import encoder,modules,records,MOD

NAMES=('CSC_AI_EconomyModel.lua','CSC_AI_EconomyFacts.lua','CSC_AI_EconomyAdapters.lua',
       'CSC_AI_AdjacencyScan.lua','CSC_AI_QuarterPlacement.lua')


def inputs():
    return [Path(__file__),*[MOD/'Lua_UI/AI'/name for name in NAMES]]


def code(observed,pid):
    sources=[read(p)for p in inputs()[1:]]
    exports=set()
    for source in sources:
        exports.update(re.findall(r'^(?:function\s+)?(CSC_[A-Za-z0-9_]+)(?=[.(\s=])',source,re.M))
    result=encoder()+modules()+'''
local output=print
local logs,logCount={},0
local function print(...)
 logCount=logCount+1
 if #logs<24 then local row={};for i=1,select('#',...)do row[#row+1]=tostring(select(i,...))end
  logs[#logs+1]=table.concat(row,' ')end
end
local observed='''+lua(observed)+'''
local actualExposed=ExposedMembers
local ExposedMembers={CSC_Adjacency=actualExposed.CSC_Adjacency,CSC_TradeRoutes={GetFacts=function()return observed end}}
local '''+','.join(sorted(exports))+'\n'
    for source in sources:result+='\ndo\n'+source+'\nend\n'
    result+='''
local pid='''+str(pid)+'''
local rows={}
for pass=1,2 do
 local started=os and os.clock and os.clock()
 local wallStarted=type(CE_AIMonotonicSeconds)=='function'and CE_AIMonotonicSeconds()
 local snapshot=assert(CSC_AI_EconomyAdapters.Snapshot(Players[pid],CSC_AI_QuarterPlacement,actualExposed.CSC_Adjacency))
 local deductions,sites,bids,candidates,chains=CSC_AI_QuarterPlacement.MaterialDeductions(
  Players[pid],false,0,0,snapshot.ui.CanProduceItem,false,snapshot)
 local protected={};for _,entry in ipairs(deductions)do protected[entry.plot]=true end
 local offers,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,CSC_AI_QuarterPlacement,protected,deductions,{})
 local quarters,customers,minimum,maximum,unique=0,0,nil,nil,{}
 for _,offer in ipairs(offers)do
  local key=offer.city..':'..offer.district..':'..offer.plot
  assert(not unique[key],'Duplicate native score key');unique[key]=true
  if offer.economy then quarters=quarters+1 end
  if offer.customerEconomic then customers=customers+1 end
  local value=offer.finalQ8 or offer.delta
  minimum=math.min(minimum or value,value);maximum=math.max(maximum or value,value)
 end
 rows[#rows+1]={pass=pass,offers=#offers,quarters=quarters,customerEconomic=customers,
  stats=stats,worlds=snapshot.WorldStats(),nativeQuotes=snapshot.QuoteCount(),
  minimumQ8=minimum,maximumQ8=maximum,
  luaClockMicros=started and math.floor((os.clock()-started)*1000000+.5)or -1,
  wallMicros=wallStarted and math.floor((CE_AIMonotonicSeconds()-wallStarted)*1000000+.5)or -1}
end
output('CSC_INTEGRATED_ECONOMY='..encode({player=pid,turn=Game.GetCurrentGameTurn(),rows=rows,
 diagnosticOnly=true,submittedBids=0,advancedTurns=0,logCount=logCount,firstLogs=logs,verified=true}))
'''
    return result


def run(controller,output,observed,players):
    output=Path(output);output.mkdir()
    results=[]
    for pid in players:
        source=code(observed,pid);(output/f'player-{pid}.lua').write_text(source,encoding='utf-8')
        started=time.perf_counter()
        raw=controller.cmd(source,'CSC_AI_BakersGameplay','integrated-economy-'+str(pid),wait=240)
        elapsed=time.perf_counter()-started
        (output/f'player-{pid}.txt').write_text(raw,encoding='utf-8')
        result,=records(raw,'CSC_INTEGRATED_ECONOMY')
        require(result['verified']and len(result['rows'])==2,'Integrated policy pass incomplete')
        result['wall_seconds']=elapsed;results.append(result)
        write_json(output/'progress.json',results)
    result={'verified':True,'players':results,'diagnostic_only':True,'submitted_bids':0,'advanced_turns':0}
    write_json(output/'result.json',result)
    return result
