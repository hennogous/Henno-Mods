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


def build(control,candidate,prototype=None,players=(5,)):
    assert 1<=len(players)<=2 and len(set(players))==len(players) and all(type(p)is int and 1<=p<=5 for p in players)
    control,candidate=Path(control)/'Lua_UI/AI',Path(candidate)/'Lua_UI/AI'
    facts='CSC_AI_EconomyFacts.lua';model='CSC_AI_EconomyModel.lua';adapter='CSC_AI_EconomyAdapters.lua'
    assert (control/facts).read_bytes()==(candidate/facts).read_bytes()
    assert (control/model).read_bytes()==(candidate/model).read_bytes()
    arms={'A':[control/facts,control/model,control/adapter],
          'B':[candidate/facts,candidate/model,candidate/adapter]}
    names={'A':'control_adapter','B':'candidate_adapter'}
    if prototype:
        arms={'A':[candidate/facts,candidate/model,candidate/adapter],
              'B':[candidate/facts,Path(prototype),candidate/adapter]}
        names={'A':'current_model','B':'starting_world_reuse'}
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
        code+=' local CSC_AI_EconomyFacts,CSC_AI_EconomyModel,CSC_AI_EconomyAdapters\n'
        for path in paths:
            text=path.read_text(encoding='utf-8')
            assert not re.search(r'\b_G\b',text),'Explicit global access requires review'
            code+='\ndo\n'+text+'\nend\n'
            pins[str(path.resolve())]=hashlib.sha256(path.read_bytes()).hexdigest()
        code+='\n return CSC_AI_EconomyAdapters,CSC_AI_EconomyModel\nend\n'
    # The marker lets offline tests initialise every private factory without
    # reaching the native-read section below; Havok has no setfenv/_G helpers.
    code+='\n-- CSC_TIMING_NATIVE_BEGIN\n'+'''
local clock=assert(CE_AIMonotonicSeconds)
local turn=Game.GetCurrentGameTurn()
local P=assert(CSC_AI_QuarterPlacement)
local ui=assert(ExposedMembers.CSC_Adjacency)
local emit=print
local print=function()end
local prior,common,proofs={},{},{}
local order={'B','A','A','B'}
local players='''+'{'+','.join(map(str,players))+'}'+'''
local modelEquality='''+('true'if prototype else'false')+'''
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
for pass,arm in ipairs(order)do for _,pid in ipairs(players)do
 assert(Game.GetCurrentGameTurn()==turn,'Timing world advanced')
 local player=assert(Players[pid]);assert(not player:IsHuman())
 emit('CSC_CUSTOMER_TIMING_BEGIN='..encode({turn=turn,pass=pass,arm=arm,player=pid,diagnosticOnly=true}))
 if not player:IsAlive()then
  emit('CSC_CUSTOMER_TIMING='..encode({turn=turn,pass=pass,arm=arm,player=pid,skipped='eliminated',coldHistory=true}))
 else
 -- Module construction/compilation and proof formatting are outside timers.
 local E,M=factories[arm]()
 local worlds={};local originalWorld=M.JointForecast
 M.JointForecast=function(w,p)
  local result,problem=originalWorld(w,p)
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
 local semantics=encode({entries=sortedEntries(entries),status=status,worlds=worlds})
 local identity=arm..':'..pid
 if prior[identity]then assert(prior[identity]==semantics,'Same-arm cold-history result changed')else prior[identity]=semantics end
 if modelEquality then
  if proofs[pid]then assert(proofs[pid]==semantics,'Model optimization changes bids, plans or economic outcomes')else proofs[pid]=semantics end
 end
 emit('CSC_CUSTOMER_TIMING='..encode({turn=turn,pass=pass,arm=arm,player=pid,
  totalSeconds=finished-started,preparationSeconds=centralStarted-started,
  centralSeconds=finished-centralStarted,customerSeconds=customerSeconds,
  customer=customerStats,work=work,nativeQuotes=snapshot.QuoteCount(),
  chains=#snapshot.chains,entries=#entries,semanticFingerprint=digest(semantics),
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
                     arms=names,order=['B','A','A','B'],players=list(players),sources=pins)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('control','candidate','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--prototype-model',type=Path)
    p.add_argument('--players',type=int,nargs='+',default=[5])
    args=p.parse_args();code,meta=build(args.control,args.candidate,args.prototype_model,args.players)
    args.output.write_text(code,encoding='utf-8')
    args.output.with_suffix('.inputs.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(output=str(args.output),bytes=len(code.encode()),**meta),indent=2))
