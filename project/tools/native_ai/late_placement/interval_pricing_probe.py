"""Read-only qualification of CE recurring intervals in an owned saved-world replay.

Check real native prices and subdivision, keeping raw Stream and fixed quotes
visible. This diagnostic submits no score packet and advances no game turn.
"""
from pathlib import Path
from driver import lua,write_json,require
from route_catalogue_probe import encoder,records


def run(controller,output,players):
    code=encoder()+'''\nlocal rows={}
local rawContext=assert(CE_AIEvaluationContext())
local discount=assert(tonumber(rawContext:match('"discountQ8":(%d+)')))
for _,pid in ipairs('''+lua(players)+''')do
 local city
 for _,c in Players[pid]:GetCities():Members()do if not city or c:GetID()<city:GetID()then city=c end end
 assert(city,'Pricing probe player has no city')
 local id=city:GetID();local yield=GameInfo.Yields.YIELD_PRODUCTION.Index
 for _,amount in ipairs({256,-256})do
  local one=assert(CE_AIYieldIntervalValue(pid,id,yield,amount,0,1,discount))
  local tail=assert(CE_AIYieldIntervalValue(pid,id,yield,amount,1,50,discount))
  local all=assert(CE_AIYieldIntervalValue(pid,id,yield,amount,0,50,discount))
  local raw=assert(CE_AIYieldStreamValue(pid,id,yield,amount,0,50,discount))
  local rawTail=assert(CE_AIYieldStreamValue(pid,id,yield,amount,1,50,discount))
  local fixed=assert(CE_AIYieldFixedValue(pid,id,yield,amount,0,discount))
  assert(one*amount>0 and all==one+tail and tail==rawTail and all-raw==fixed,'Yield interval contract differs')
  rows[#rows+1]={player=pid,city=id,amountQ8=amount,oneQ8=one,tailQ8=tail,
   allQ8=all,rawQ8=raw,fixedQ8=fixed}
 end
 local one=assert(CE_AIAmenityIntervalValue(pid,id,2,0,1,discount))
 local tail=assert(CE_AIAmenityIntervalValue(pid,id,2,1,50,discount))
 local all=assert(CE_AIAmenityIntervalValue(pid,id,2,0,50,discount))
 local rawOne=assert(CE_AIAmenityStreamValue(pid,id,2,0,1,discount))
 local rawAll=assert(CE_AIAmenityStreamValue(pid,id,2,0,50,discount))
 assert(all==one+tail and one-rawOne==all-rawAll,'Pooled amenity interval contract differs')
 rows[#rows+1]={player=pid,city=id,amenities=2,oneQ8=one,tailQ8=tail,allQ8=all,
  rawQ8=rawAll,originQ8=one-rawOne}
end
print('CSC_INTERVAL_PRICING='..encode({verified=true,rows=rows,submittedBids=0,advancedTurns=0}))
'''
    output=Path(output)
    (output/'interval-pricing.lua').write_text(code,encoding='utf-8')
    raw=controller.cmd(code,'CSC_AI_BakersGameplay','interval-pricing')
    (output/'interval-pricing.txt').write_text(raw,encoding='utf-8')
    result,=records(raw,'CSC_INTERVAL_PRICING')
    require(result['verified']and len(result['rows'])==3*len(players),'Interval qualification incomplete')
    write_json(output/'interval-pricing.json',result)
    return result
