-- DIAGNOSTIC ONLY: central live facts -> priced component records. This calls
-- the existing read-only economic helpers and publishes no bid or game order.
-- The shared controller invokes it at inactive boundaries for explicit targets.
local E,P,M=assert(CSC_AI_EconomyAdapters),assert(CSC_AI_QuarterPlacement),assert(CSC_AI_EconomyModel)
local snapshots={}
local function encode(v,depth)
 depth=depth or 0;assert(depth<16,'Component record nesting bound')
 local t=type(v)
 if t=='nil'then return 'null'end
 if t=='boolean'then return tostring(v)end
 if t=='number'then
  if v==math.huge then return '"Infinity"'elseif v==-math.huge then return '"-Infinity"'end
  assert(v==v,'NaN component');return tostring(v)
 end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 assert(t=='table','Non-scalar component: '..t)
 local n,array=0,true
 for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 assert(n<4096,'Component field bound')
 local out={}
 if array and n==#v then
  for _,x in ipairs(v)do out[#out+1]=encode(x,depth+1)end
  return '['..table.concat(out,',')..']'
 end
 local keys={};for k in pairs(v)do keys[#keys+1]=k end
 table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 for _,k in ipairs(keys)do out[#out+1]=encode(tostring(k),depth+1)..':'..encode(v[k],depth+1)end
 return '{'..table.concat(out,',')..'}'
end
for _,target in ipairs(CSC_COMPONENT_TARGETS)do
 local row={turn=Game.GetCurrentGameTurn(),player=target.player,city=target.city,plot=target.plot,key=target.key,
  diagnosticOnly=true,legacyDeductionsApplied=false}
 local player=assert(Players[target.player]);assert(not player:IsHuman(),'Original AI target required')
 local city=player:GetCities():FindID(target.city)
 if not city then row.unavailable='city_absent'
 else
  if not snapshots[target.player]then
   snapshots[target.player]=assert(E.Snapshot(player,P,assert(ExposedMembers.CSC_Adjacency)))
  end
  local snapshot=snapshots[target.player]
  local profile
  for _,p in ipairs(P.StageTwoProfiles())do if p.key==target.key then profile=p end end
  profile=assert(profile,'Unknown economic family')
  local plot=assert(Map.GetPlotByIndex(target.plot))
  row.population=city:GetPopulation();row.production=snapshot.cities[target.city].production
  row.improvement=plot:GetImprovementType();row.terrain=plot:GetTerrainType()
  row.feature=plot:GetFeatureType();row.resource=plot:GetResourceType();row.owner=plot:GetOwner()
  row.plotFacts=snapshot.PlotFacts(plot);row.geometry=snapshot.Geometry(city,plot,profile)
  row.site,row.reason=snapshot.Site(city,plot,profile)
  if row.site then
   local function objective(q)return E.PlacementValue(q,row.site)end
   row.quote,row.quoteReason=M.Forecast(row.site,snapshot.Price,objective)
   -- A bounded counterfactual isolates the documented plain-footprint debit.
   -- With no improvement, all displaced ordinary yield is outside the native
   -- improvement-loss term. Never remove an improved footprint's supplier loss.
   -- Same native weights, horizon and discount; no policy packet is changed.
   if row.improvement==-1 then
    local alternative={};for k,v in pairs(row.site)do alternative[k]=v end
    alternative.direct={}
    for _,stream in ipairs(row.site.direct)do
     if not stream.id:find('displaced:',1,true)then alternative.direct[#alternative.direct+1]=stream end
    end
    row.withoutUnimprovedFootprint=M.Forecast(alternative,snapshot.Price,function(q)return E.PlacementValue(q,alternative)end)
   end
  end
 end
 print('CSC_ECONOMY_COMPONENT='..encode(row))
end
print('CSC_ECONOMY_COMPONENT_COMPLETE',Game.GetCurrentGameTurn(),#CSC_COMPONENT_TARGETS)
