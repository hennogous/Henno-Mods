-- DIAGNOSTIC ONLY. Observe the main CSC adapter's existing legal candidate
-- sets and CE's existing journal. No extra world quote, site enumeration,
-- score/property write or gameplay order is issued. Changed sets provide an
-- opportunity denominator; the native selector and physical observers supply
-- the later choice and construction. Legal-at-publication is labelled as such.
assert(not CSC_CUSTOMER_PLACEMENT_WATCH,'Duplicate customer observer')
local E=assert(CSC_AI_EconomyAdapters)
local B=assert(CSC_AI_DistrictBridge)
local W={};CSC_CUSTOMER_PLACEMENT_WATCH=W
local unpack=unpack or table.unpack
local function pack(...)return{n=select('#',...),...}end
local states,previous,wanted={},{},{}
local faults,records,dropped=0,0,0
local limit=100000
local function emit(kind,payload)
 if records>=limit then dropped=dropped+1;return end
 records=records+1;print('CSC_CUSTOMER_WATCH_'..kind..' '..payload)
end
local function safe(fn,...)
 local ok,problem=pcall(fn,...)
 if not ok then faults=faults+1;emit('FAULT',tostring(problem):gsub('[\r\n]',' '))end
end
local function scope(p,c,d)return p..':'..c..':'..d end
local function capture(snapshot,groups)
 local nextState={};local count=0
 for _,g in ipairs(groups)do
  count=count+1;assert(count<=512,'Customer group observation bound')
  local plots,seen={},{}
  for _,rows in ipairs({{g.reference},g.candidates})do for _,r in ipairs(rows)do
   if not seen[r.plot]then
    plots[#plots+1]=r;seen[r.plot]=true
   end
  end end
  table.sort(plots,function(a,b)return a.plot<b.plot end)
  local linked,ordinary={},{}
  for _,r in ipairs(plots)do
   local list=(r.links or 0)>0 and linked or ordinary
   list[#list+1]=string.format('%d:%.6f:%d',r.plot,r.adjacency or 0,r.links or 0)
  end
  local key=scope(snapshot.id,g.city,g.district)
  local signature='reference='..g.reference.plot..' linked='..table.concat(linked,',')..' ordinary='..table.concat(ordinary,',')
  nextState[key]=signature
  if not states[snapshot.id]or states[snapshot.id][key]~=signature then
   emit('GROUP','turn='..Game.GetCurrentGameTurn()..' player='..snapshot.id..' city='..g.city..' district='..g.district..' '..signature..' eligibility=publicationLegalOwnedUnprotected')
  end
 end
 previous[snapshot.id]=states[snapshot.id]or{}
 for key in pairs(previous[snapshot.id])do if not nextState[key]then
  -- Removed means absent from this policy result, which can also follow a
  -- failed legality/adjacency query. Only positive sets establish opportunities;
  -- an absent player CLOCK leaves coverage unknown.
  emit('REMOVED','turn='..Game.GetCurrentGameTurn()..' scope='..key)
 end end
 states[snapshot.id]=nextState
 -- Keep the previous publication's scopes for the journal drained before
 -- the next commit. A just-constructed district may already leave today's set.
 wanted={}
 for _,players in ipairs({states,previous})do for _,groupsForPlayer in pairs(players)do
  for key in pairs(groupsForPlayer)do wanted[key]=true end
 end end
 emit('CLOCK','turn='..Game.GetCurrentGameTurn()..' player='..snapshot.id..' groups='..count)
end
local offers=E.CustomerEconomicOffers
E.CustomerEconomicOffers=function(snapshot,protected,...)
 local reader=snapshot.CustomerCandidateSets
 if not reader then return offers(snapshot,protected,...)end
 snapshot.CustomerCandidateSets=function(...)
  local result=pack(reader(...));safe(capture,snapshot,result[1]);return unpack(result,1,result.n)
 end
 local result=pack(pcall(offers,snapshot,protected,...))
 snapshot.CustomerCandidateSets=reader
 if not result[1]then error(result[2])end
 return unpack(result,2,result.n)
end
local generationSeen,ordinalSeen
local function number(record,name)return tonumber(record:match('"'..name..'":(-?%d+)'))end
function W.Record(record,ordinal,generation)
 local p,c,d=number(record,'player'),number(record,'city'),number(record,'district')
 if not(p and c and d)then return end
 local target=wanted[scope(p,c,d)]
 for _,row in ipairs(CSC_CUSTOMER_WATCH_TARGETS or{})do
  if row[1]==p and row[2]==c then target=true end
 end
 if not target then return end
 if generationSeen~=generation then generationSeen=generation;ordinalSeen={}end
 if ordinalSeen[ordinal]then return end
 ordinalSeen[ordinal]=true
 emit('NATIVE','observedTurn='..Game.GetCurrentGameTurn()..' generation='..generation..' ordinal='..ordinal..' record='..record)
end
local function drain()
 local status=assert(CE_AIDistrictScoresStatus())
 local generation=assert(number(status,'generation'));local total=assert(number(status,'trace_count'))
 assert(total<=65536,'Customer journal observation bound')
 for offset=0,total-1,64 do
  local page=assert(CE_AIDistrictScoresTraceRead(offset,64,generation))
  assert(not page:find('"stale":true',1,true),'Customer journal changed during read')
  assert(number(page,'offset')==offset and number(page,'total')==total,'Customer journal page bounds differ')
  local ordinal=0
  for record in page:gmatch('{[^{}]+}')do if record:match('"k":"([^"]+)"')then
   ordinal=ordinal+1;W.Record(record,offset+ordinal,generation)
  end end
  assert(ordinal==math.min(64,total-offset),'Customer journal page record count differs')
 end
end
local publish=B.Publish
B.Publish=function(...)
 -- A full-game quarter observer already reads these same pages and dispatches
 -- Record. Short customer replays own that passive read when it is absent.
 if not CSC_QUARTER_PLACEMENT_WATCH then safe(drain)end
 return publish(...)
end
function W.Finish()
 if CSC_QUARTER_PLACEMENT_WATCH then CSC_QUARTER_PLACEMENT_WATCH.Drain()else safe(drain)end
 emit('FINISH','records='..records..' faults='..faults..' dropped='..dropped)
end
emit('INSTALLED','turn='..Game.GetCurrentGameTurn()..' policy=mainCSC extraWorldQuotes=0')
