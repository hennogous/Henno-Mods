"""Diagnostic-only joint customer quotes on native-admitted owned footprints.

Uses current production readers/model/pricing adapter in lexical isolation.
Never submits an order, score packet or property write. Per-player commands
bound console work and preserve every unavailable quote alongside successes.
"""
import time
from pathlib import Path
from driver import lua,read,write_json
from route_catalogue_probe import encoder,modules,records,MOD


def inputs():
    return [Path(__file__),*[MOD/'Lua_UI/AI'/name for name in
        ('CSC_AI_EconomyFacts.lua','CSC_AI_EconomyModel.lua','CSC_AI_EconomyAdapters.lua')]]


def code(observed,player):
    result=encoder()+modules()+'''
local observed='''+lua(observed)+'''
local actualExposed=ExposedMembers
local ExposedMembers={CSC_Adjacency=actualExposed.CSC_Adjacency,
 CSC_TradeRoutes={GetFacts=function()return observed end}}
local CSC_AI_EconomyFacts,CSC_AI_EconomyModel,CSC_AI_EconomyAdapters
'''
    for path in inputs()[1:]:result+='\ndo\n'+read(path)+'\nend\n'
    result+='''
local pid='''+str(player)+'''
local snapshot=assert(CSC_AI_EconomyAdapters.Snapshot(Players[pid],CSC_AI_QuarterPlacement,actualExposed.CSC_Adjacency))
local types={};for _,mapping in pairs(CSC_AI_EconomyFacts.CustomerQuarterMap())do types[#types+1]=mapping end
local function priority(row)
 if row.definition.DistrictType=='DISTRICT_COMMERCIAL_HUB'then return 0 end
 return row.definition.DistrictType:find('CORE',1,true)and 2 or 1
end
table.sort(types,function(a,b)local x,y=priority(a),priority(b)
 return x<y or x==y and a.definition.Index<b.definition.Index end)
local candidates,seen={},{}
for _,chain in ipairs(snapshot.chains)do
 for _,mapping in ipairs(types)do
  local matches=false
  for _,quarter in ipairs(mapping.quarters)do matches=matches or quarter.key==chain.profile.key end
  if matches then
   for _,plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(),chain.plot:GetY()))do
    local city=plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
    if city and plot:GetDistrictType()==-1 then
     local key=city:GetID()..':'..mapping.definition.Index..':'..plot:GetIndex()
     if not seen[key]then
      local targets=snapshot.ui.GetLegalDistrictTargets(pid,city:GetID(),mapping.definition.Hash)
      for _,index in ipairs(targets)do if index==plot:GetIndex()then
       candidates[#candidates+1]={city=city:GetID(),district=mapping.definition.Index,plot=index,
        priority=priority(mapping)};seen[key]=true;break
      end end
     end
    end
   end
  end
 end
end
table.sort(candidates,function(a,b)
 if a.priority~=b.priority then return a.priority<b.priority end
 if a.city~=b.city then return a.city<b.city end
 if a.district~=b.district then return a.district<b.district end
 return a.plot<b.plot
end)
local successes,attempts=0,math.min(2,#candidates)
for i=1,attempts do
 local target=candidates[i]
 local before,after=snapshot.CustomerWorld(target.city,target.district,target.plot)
 local quote,problem
 if before then quote,problem=CSC_AI_EconomyModel.JointCustomerForecast(before,after,snapshot.Price)
 else problem=after end
 local row={player=pid,city=target.city,district=target.district,plot=target.plot,available=quote~=nil,
  reason=problem,nativeQuotes=snapshot.QuoteCount(),chains=#snapshot.chains}
 if quote then
  successes=successes+1
  row.beforeQ8=quote.before.valueQ8;row.afterQ8=quote.after.valueQ8;row.deltaQ8=quote.valueQ8
  row.bidDeltaQ8=quote.bidValueQ8;row.ready=after.customer.ready
  row.evaluations=quote.before.evaluations+quote.after.evaluations
  row.components={};row.lostSuppliers=0
  for _,f in ipairs(quote.after.streams)do if f.component then
   row.components[f.component]=(row.components[f.component]or 0)+f.valueQ8
  end end
  for j,site in ipairs(before.sites)do row.lostSuppliers=row.lostSuppliers+#site.suppliers-#after.sites[j].suppliers end
 end
 print('CSC_CUSTOMER_WORLD_QUOTE='..encode(row))
end
print('CSC_CUSTOMER_WORLD_RESULT='..encode({player=pid,candidates=#candidates,attempts=attempts,
 successes=successes,chains=#snapshot.chains,verified=true,diagnosticOnly=true,submittedBids=0}))
'''
    return result


def run(controller,output,observed,players):
    output=Path(output);output.mkdir()
    results=[];quotes=[]
    for player in players:
        source=code(observed,player);(output/f'player-{player}.lua').write_text(source,encoding='utf-8')
        started=time.perf_counter()
        raw=controller.cmd(source,'CSC_AI_BakersGameplay','customer-world-'+str(player),wait=60)
        elapsed=time.perf_counter()-started
        (output/f'player-{player}.txt').write_text(raw,encoding='utf-8')
        result,=records(raw,'CSC_CUSTOMER_WORLD_RESULT');result['wall_seconds']=elapsed
        results.append(result);quotes.extend(records(raw,'CSC_CUSTOMER_WORLD_QUOTE'))
    result={'verified':all(r['verified']for r in results),'players':results,'quotes':quotes,
            'attempts':sum(r['attempts']for r in results),'successes':sum(r['successes']for r in results),
            'diagnostic_only':True,'submitted_bids':0,'advanced_turns':0}
    write_json(output/'result.json',result)
    return result
