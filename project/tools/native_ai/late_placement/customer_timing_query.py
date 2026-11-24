"""Build a DIAGNOSTIC ONLY, zero-turn economic timing query.

Use the existing tailors_coast_survey lifecycle with --query-timeout-seconds60,
after the serial campaign closes. Nothing here launches or connects to Civ.
Private F/M/E modules are reset before every measured player/arm; their normal
QuarterBids path warms the customer solver's caches in production order. Empty
previous offers explicitly mean cold continuity history. Builder nominations,
repairs, packet publication and Committed are outside this benchmark.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]


def build(control,candidate,prototype=None,players=(5,),service_comparison=False,*,
          facts_equivalence=False,layout_policy=False):
    assert 1<=len(players)<=2 and len(set(players))==len(players) and all(type(p)is int and 1<=p<=5 for p in players)
    control,candidate=Path(control)/'Lua_UI/AI',Path(candidate)/'Lua_UI/AI'
    facts='CSC_AI_EconomyFacts.lua';model='CSC_AI_EconomyModel.lua';adapter='CSC_AI_EconomyAdapters.lua'
    if facts_equivalence:
        assert not prototype and not service_comparison, 'Compare one facts change in the full layout policy'
        assert (control/adapter).read_bytes()==(candidate/adapter).read_bytes()
    else:
        assert (control/facts).read_bytes()==(candidate/facts).read_bytes()
    assert (control/model).read_bytes()==(candidate/model).read_bytes()
    arms={'A':[control/facts,control/model,control/adapter],
          'B':[candidate/facts,candidate/model,candidate/adapter]}
    names={'A':'control_adapter','B':'candidate_adapter'}
    if facts_equivalence:
        names={'A':'control_facts','B':'candidate_facts'}
    if service_comparison:
        assert not prototype and control.resolve()==candidate.resolve(),'Service mode requires identical current sources'
        names={'A':'services_excluded','B':'services_included'}
    if prototype:
        arms={'A':[candidate/facts,candidate/model,candidate/adapter],
              'B':[candidate/facts,Path(prototype),candidate/adapter]}
        names={'A':'current_model','B':'candidate_model'}
    encoder=(HERE/'economy_component_probe.lua').read_text(encoding='utf-8')
    code='-- DIAGNOSTIC ONLY: no bids, orders, properties or turn changes.\n'
    proof_encoder=encoder[encoder.index('local function encode'):encoder.index('for _,target in ipairs(CSC_COMPONENT_TARGETS)do')]
    # Havok exposes integer IDs separately from Lua51's numeric type. An array
    # requires exactly1..n: sparse protected plot0/maps must retain every key.
    proof_encoder=proof_encoder.replace("if t=='number'then","if t=='number'or t=='integer'then")
    old="for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end"
    new="""for k in pairs(v)do n=n+1;if(type(k)~='number'and type(k)~='integer')or k<1 or k%1~=0 then array=false end end
 if array then for i=1,n do if v[i]==nil then array=false;break end end end"""
    assert old in proof_encoder;proof_encoder=proof_encoder.replace(old,new)
    code+=proof_encoder
    code+='''
local function activeTables()return CSC_AI_EconomyFacts,CSC_AI_EconomyModel,CSC_AI_EconomyAdapters end
local active={activeTables()}
local factories={}
'''
    pins={}
    for arm,paths in arms.items():
        code+='\nfactories.'+arm+'=function()\n local print=function()end\n'
        if service_comparison and arm=='A':
            code+=''' local actualStatus=CE_AIEconomyStatus
 local CE_AIEconomyStatus=function()
  return (actualStatus():gsub('"servicePricingReady":1','"servicePricingReady":0'))
 end
'''
        code+=' local CSC_AI_EconomyFacts,CSC_AI_EconomyModel,CSC_AI_EconomyAdapters\n'
        for path in paths:
            text=path.read_text(encoding='utf-8')
            assert not re.search(r'\b_G\b',text),'Explicit global access requires review'
            code+='\ndo\n'+text+'\nend\n'
            pins[str(path.resolve())]=hashlib.sha256(path.read_bytes()).hexdigest()
        code+='\n return CSC_AI_EconomyAdapters,CSC_AI_EconomyModel\nend\n'
    code+='''
local function proofCopy(value,field,depth)
 depth=depth or 0;assert(depth<20,'Proof copy depth bound')
 if type(value)~='table'then return value end
 local result,count={},0
 for key,item in pairs(value)do result[key]=proofCopy(item,key,depth+1);count=count+1 end
 if field=='streams'or field=='contributors'then
  -- Finished priced streams are independent flows. Population attribution is
  -- also a list of records; amenity contributors can instead be ID->true sets.
  -- Normalize only dense record arrays, retaining every full record/duplicate.
  local dense=true
  for i=1,count do if type(result[i])~='table'then dense=false;break end end
  if dense and count==#result then
   local keyed={};for _,item in ipairs(result)do keyed[#keyed+1]={value=item,key=encode(item)}end
   table.sort(keyed,function(a,b)return a.key<b.key end)
   for i,row in ipairs(keyed)do result[i]=row.value end
  end
 end
 return result
end
'''
    # The marker lets offline tests initialise every private factory without
    # reaching the native-read section below; Havok has no setfenv/_G helpers.
    code+='\n-- CSC_TIMING_NATIVE_BEGIN\n'+'''
local clock=assert(CE_AIMonotonicSeconds)
local turn=Game.GetCurrentGameTurn()
local P=assert(CSC_AI_QuarterPlacement)
local ui=assert(ExposedMembers.CSC_Adjacency)
local emit=print
local print=function()end
local prior,priorObjects,common,proofs={},{},{},{}
local order={'B','A','A','B'}
local players='''+'{'+','.join(map(str,players))+'}'+'''
local modelEquality='''+('true'if prototype or facts_equivalence else'false')+'''
local layoutPolicy='''+('true'if facts_equivalence or layout_policy else'false')+'''
local serviceComparison='''+('true'if service_comparison else'false')+'''
if serviceComparison then
 assert(CE_AIEconomyStatus():find('"servicePricingReady":1',1,true),'Native Service quotes unavailable')
 local player=Players[5];local city;local surplus=-math.huge
 for _,c in player:GetCities():Members()do
  local value=c:GetGrowth():GetFoodSurplus()
  if value>surplus then city,surplus=c,value end
 end
 assert(city,'No quote recipient')
 local context=CE_AIEvaluationContext();local discount=assert(tonumber(context:match('"discountQ8":(%d+)')))
 for _,name in ipairs({'PSEUDOYIELD_GPP_ENGINEER','PSEUDOYIELD_TOURISM'})do
  local kind=assert(GameInfo.PseudoYields[name]).Index
  local one=assert(CE_AIPseudoYieldIntervalValue(5,city:GetID(),kind,256,0,1,discount))
  local tail=assert(CE_AIPseudoYieldIntervalValue(5,city:GetID(),kind,256,1,2,discount))
  local both=assert(CE_AIPseudoYieldIntervalValue(5,city:GetID(),kind,256,0,2,discount))
  assert(one+tail==both,'Pseudo-yield interval subdivision failed')
  emit('CSC_SERVICE_QUOTE='..encode({kind=name,one=one,tail=tail,both=both}))
 end
 local growth=assert(CE_AIGrowthIntervalValue(5,city:GetID(),2560,0,2,discount))
 assert(CE_AIPseudoYieldIntervalValue(5,city:GetID(),1024,256,0,2,discount)==nil,'Invalid pseudo type accepted')
 emit('CSC_SERVICE_QUOTE='..encode({kind='GROWTH_PERCENT10',value=growth,city=city:GetID(),foodSurplus=surplus}))
end
local function digest(text)
 local value=0;for i=1,#text do value=(value*65599+text:byte(i))%4294967291 end
 return string.format('%.0f/%d',value,#text)
end
local function key(e)return table.concat({e.player or -1,e.city or -1,e.district or -1,e.plot or -1},':')end
local function sortedEntries(entries)
 local rows={};for _,e in ipairs(entries)do rows[#rows+1]=e end
 table.sort(rows,function(a,b)local x,y=key(a),key(b)
  return x<y or x==y and encode(a)<encode(b)end)
 return rows
end
local function firstDifference(a,b,path,depth)
 depth=depth or 0;assert(depth<20,'Difference depth bound')
 if type(a)~='table'or type(b)~='table'then
  if a~=b then return {path=path,left=tostring(a):sub(1,120),right=tostring(b):sub(1,120)}end
  return nil
 end
 local keys,seen={},{}
 for k in pairs(a)do keys[#keys+1]=k;seen[k]=true end
 for k in pairs(b)do if not seen[k]then keys[#keys+1]=k end end
 table.sort(keys,function(x,y)return tostring(x)<tostring(y)end)
 for _,k in ipairs(keys)do
  local result=firstDifference(a[k],b[k],path..'/'..tostring(k),depth+1)
  if result then return result end
 end
end
for pass,arm in ipairs(order)do for _,pid in ipairs(players)do
 assert(Game.GetCurrentGameTurn()==turn,'Timing world advanced')
 local player=assert(Players[pid]);assert(not player:IsHuman())
 emit('CSC_CUSTOMER_TIMING_BEGIN='..encode({turn=turn,pass=pass,arm=arm,player=pid,diagnosticOnly=true}))
 if not player:IsAlive()then
  emit('CSC_CUSTOMER_TIMING='..encode({turn=turn,pass=pass,arm=arm,player=pid,skipped='eliminated',coldHistory=true}))
 else
 -- Module construction/compilation and proof formatting are outside timers.
 local E,M=factories[arm]()
 if layoutPolicy then E.AnchoredConnectionsEnabled=true;E.ProspectiveConnectionsEnabled=true end
 local worlds,worldSeconds={},0;local originalWorld=M.JointForecast
 M.JointForecast=function(w,p)
  local started=clock()
  local result,problem=originalWorld(w,p)
  worldSeconds=worldSeconds+clock()-started
  worlds[#worlds+1]={result=result or false,problem=problem or false}
  return result,problem
 end
 local customerSeconds,customerStats=0,nil
 local originalCustomer=E.CustomerEconomicOffers
 E.CustomerEconomicOffers=function(...)
  local started=clock();local offers,stats=originalCustomer(...)
  customerSeconds=customerSeconds+clock()-started;customerStats=stats
  return offers,stats
 end
 local started=clock()
 local snapshot,reason=E.Snapshot(player,P,ui);assert(snapshot,reason)
 -- Real material deductions and legacy Quarter proposals are common inputs.
 -- SupplyValue's global adapter is unchanged in the active saved package;
 -- its identical plain early/protection vectors are checked across all arms.
 local early,_,_,_,chains=P.MaterialDeductions(player,false,0,0,snapshot.ui.CanProduceItem,false,snapshot)
 local protected={};for _,e in ipairs(early)do protected[e.plot]=true end
 for _,profile in ipairs(P.StageTwoProfiles())do
  local extra=CSC_AI_QuarterSiteForecasts(player,profile,chains,
   function(_,plot,p)return snapshot.Supply(plot,p)end,protected,snapshot.ui,snapshot)
  for _,e in ipairs(extra)do early[#early+1]=e end
 end
 local centralStarted=clock()
 local entries,status=E.QuarterBids(snapshot,P,protected,early,{})
 local finished=clock()
 local work=snapshot.WorldStats()
 local earlyText=encode({entries=sortedEntries(early),protected=protected})
 if common[pid]then assert(common[pid]==earlyText,'Common early/protection inputs differ')else common[pid]=earlyText end
 -- Native Havok hash traversal can change the append order of finished
 -- population/amenity streams. Compare their full multiset after pricing,
 -- outside timing. Queue investments, world order, plans and errors keep order.
 local semanticObject={entries=sortedEntries(entries),status=status,worlds=proofCopy(worlds)}
 local semantics=encode(semanticObject)
 local identity=arm..':'..pid
 if prior[identity]and prior[identity]~=semantics then
  -- Diagnose the first actual field before stopping. In particular, an
  -- unordered stream/contributor list must not be mistaken for a new bid.
  emit('CSC_CUSTOMER_TIMING_DIFFERENCE='..encode({arm=arm,pass=pass,player=pid,
   difference=firstDifference(priorObjects[identity],semanticObject,'result'),
   currentTotalSeconds=finished-started,currentCentralSeconds=finished-centralStarted,
   currentCustomerSeconds=customerSeconds,currentCustomer=customerStats,currentWork=work}))
  error('Same-arm cold-history result changed')
 end
 prior[identity]=semantics;priorObjects[identity]=semanticObject
 if serviceComparison and not proofs[identity]then
  local values={}
  for _,e in ipairs(entries)do if e.finalQ8 and e.finalQ8>0 then
   values[#values+1]={city=e.city,district=e.district,plot=e.plot,finalQ8=e.finalQ8}
  end end
  local serviceValues={}
  for _,w in ipairs(worlds)do if w.result and not w.result.servicesExcluded then
   local effects={}
   for _,s in ipairs(w.result.streams)do if s.service then
    effects[#effects+1]={id=s.id,yield=s.yield,city=s.city,amount=s.amount,ready=s.ready,valueQ8=s.valueQ8}
   end end
   serviceValues[#serviceValues+1]={totalQ8=w.result.valueQ8,serviceQ8=w.result.serviceValueQ8,effects=effects}
  end end
  emit('CSC_SERVICE_BIDS='..encode({arm=arm,player=pid,entries=values,worlds=serviceValues}))
  proofs[identity]=true
 end
 if modelEquality then
  if proofs[pid]then assert(proofs[pid]==semantics,'Model optimization changes bids, plans or economic outcomes')else proofs[pid]=semantics end
 end
 emit('CSC_CUSTOMER_TIMING='..encode({turn=turn,pass=pass,arm=arm,player=pid,
  totalSeconds=finished-started,preparationSeconds=centralStarted-started,
  centralSeconds=finished-centralStarted,customerSeconds=customerSeconds,worldSeconds=worldSeconds,
  customer=customerStats,work=work,nativeQuotes=snapshot.QuoteCount(),
  chains=#snapshot.chains,entries=#entries,semanticFingerprint=digest(semantics),
  serviceWorlds=(function()local n=0;for _,w in ipairs(worlds)do if w.result and not w.result.servicesExcluded then n=n+1 end end;return n end)(),
  serviceStreams=(function()local n=0;for _,w in ipairs(worlds)do if w.result then n=n+(w.result.serviceStreams or 0)end end;return n end)(),
  semanticBytes=#semantics,earlyFingerprint=digest(earlyText),coldHistory=true}))
 end
end end
local current={activeTables()}
assert(current[1]==active[1]and current[2]==active[2]and current[3]==active[3],'Active module replaced')
assert(Game.GetCurrentGameTurn()==turn,'Timing world advanced')
emit('CSC_CUSTOMER_TIMING_COMPLETE='..encode({turn=turn,verified=true,passes=4,players=#players,
 noPublishedPackets=true,coldHistory=true,modelEquality=modelEquality}))
emit('CSC_COAST_END\\t'..turn)
'''
    return code,dict(scope='Cold-history integrated economic pass; no Builder nominations/repairs/publication',
                     arms=names,order=['B','A','A','B'],players=list(players),sources=pins,
                     service_comparison=service_comparison,facts_equivalence=facts_equivalence,
                     layout_policy=bool(facts_equivalence or layout_policy))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('control','candidate','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--prototype-model',type=Path)
    p.add_argument('--players',type=int,nargs='+',default=[5])
    p.add_argument('--service-comparison',action='store_true')
    p.add_argument('--facts-equivalence',action='store_true')
    p.add_argument('--layout-policy',action='store_true',help='Measure with the candidate layout policy enabled in both arms')
    args=p.parse_args();code,meta=build(args.control,args.candidate,args.prototype_model,args.players,
                                       args.service_comparison,facts_equivalence=args.facts_equivalence,
                                       layout_policy=args.layout_policy)
    args.output.write_text(code,encoding='utf-8')
    args.output.with_suffix('.inputs.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(args.output),bytes=len(code.encode()),**meta),indent=2))
