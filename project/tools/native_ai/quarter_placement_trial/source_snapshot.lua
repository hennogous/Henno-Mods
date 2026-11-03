-- Read-only before/after facts for one declared existing-save city. The caller
-- substitutes these three literals once each; this reader issues no orders.
local PLAYER=__PLAYER__
local CITY=__CITY__
local DISTRICT=__DISTRICT__
local function object(t)return setmetatable(t or {},{__json_object=true})end
local function json(v)
 local t=type(v)
 if t=='nil'then return 'null'end
 if t=='boolean'or t=='number'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 assert(t=='table','Non-scalar observation: '..t)
 local n,array=0,not(getmetatable(v)and getmetatable(v).__json_object)
 for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 local a={}
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 local keys={};for k in pairs(v)do keys[#keys+1]=k end
 table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 for _,k in ipairs(keys)do a[#a+1]=json(tostring(k))..':'..json(v[k])end
 return '{'..table.concat(a,',')..'}'
end
local function call(o,k,...)
 if not o or type(o[k])~='function'then return {unavailable=k}end
 local ok,v=pcall(o[k],o,...);if ok then return v end
 return {error=tostring(v)}
end
local function scalar(v)
 if type(v)~='table'then return v end
 local r=object();for k,x in pairs(v)do if type(x)=='string'or type(x)=='number'or type(x)=='boolean'then r[tostring(k)]=x end end;return r
end
local function rows(name)
 local source=GameInfo[name]
 if not source then return function()return nil end end
 return source()
end
local d=assert(GameInfo.Districts[DISTRICT],'Selected Quarter definition absent')
local out={version=1,turn=Game.GetCurrentGameTurn(),target={player=PLAYER,city=CITY,exists=false},
 districtCatalog={},players={},currentHumans={},candidates={},mapping={},definition=object(),
 assistance={properties=object(),pending=object(),turnCycles=object()},aiReset=object()}
out.width,out.height=Map.GetGridSize()
local districtCount,maxIndex=0,-1
for row in GameInfo.Districts()do
 districtCount=districtCount+1;maxIndex=math.max(maxIndex,row.Index)
 out.districtCatalog[#out.districtCatalog+1]={index=row.Index,type=row.DistrictType}
end
out.mapping={districtIndex=d.Index,districtType=d.DistrictType,districtCount=districtCount,districtIndexLimit=maxIndex+1}
for _,key in ipairs({'DistrictType','Index','Hash','PrereqTech','PrereqCivic','Cost','CostProgressionModel','CostProgressionParam1',
 'RequiresPlacement','RequiresPopulation','InternalOnly','OnePerCity','Coast','NoAdjacentCity','Aqueduct','Maintenance','CityStrengthModifier'})do
 out.definition[key]=d[key]
end
out.aiReset.privateYieldPresent=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT~=nil
out.aiReset.profileTablePresent=GameInfo.CSC_AI_Profile~=nil
out.aiReset.profileRows={}
for row in rows('CSC_AI_Profile')do out.aiReset.profileRows[#out.aiReset.profileRows+1]={id=row.Id,mode=row.Mode}end
out.aiReset.cscAILists={};out.aiReset.cscAIAdjacencies={};out.aiReset.cscAIModifiers={}
for row in rows('AiLists')do if type(row.ListType)=='string'and(row.ListType:match('^CSC_AI_')or row.ListType:match('^CSC_RH_'))then out.aiReset.cscAILists[#out.aiReset.cscAILists+1]={list=row.ListType,system=row.System}end end
for row in rows('Adjacency_YieldChanges')do if row.YieldType=='YIELD_CSC_AI_PLACEMENT'then out.aiReset.cscAIAdjacencies[#out.aiReset.cscAIAdjacencies+1]=row.ID end end
for row in rows('Modifiers')do if type(row.ModifierId)=='string'and(row.ModifierId:match('^MOD_CSC_AI_')or row.ModifierId:match('^MOD_CSC_RH_'))then out.aiReset.cscAIModifiers[#out.aiReset.cscAIModifiers+1]=row.ModifierId end end
for _,key in ipairs({'TOTALS','ERROR_INDEX','PURCHASE_INDEX','FOUNDATION_INDEX','INITIAL_HUMANS'})do
 out.assistance.properties[key]=Game:GetProperty('CSC_AI_ASSISTANCE_V1_'..key)
end
for _,key in ipairs({'CSC_AI_SELECTIVE_SCREEN_V1','CSC_AI_SELECTIVE_SCREEN_STATE_V1','CSC_AI_INVESTMENT_PILOT_V1','CSC_AI_INVESTMENT_PILOT_STATE_V1'})do
 out.assistance.properties[key]=Game:GetProperty(key)
end
for pid=0,61 do
 local p=Players[pid]
 if p then
  local r={player=pid,human=p:IsHuman(),alive=p:IsAlive(),major=p:IsMajor()};out.players[#out.players+1]=r
  if r.human then out.currentHumans[#out.currentHumans+1]=pid end
 end
 local cycle=Game:GetProperty('CSC_AI_ASSISTANCE_V1_TURN_'..pid)
 local pending=Game:GetProperty('CSC_AI_ASSISTANCE_V1_PENDING_'..pid)
 if cycle~=nil then out.assistance.turnCycles[tostring(pid)]=cycle end
 if pending~=nil then out.assistance.pending[tostring(pid)]=pending end
end
-- ExposedMembers has context boundaries. Presence here is evidence only about
-- this GameCore_Tuner context; Modding action logs remain the loading authority.
out.assistance.contextExposure=object()
for _,key in ipairs({'CSC_AI_Assistance','CSC_AI_AssistanceUI','CSC_AI_OpportunityPolicy','CSC_AI_Research'})do
 out.assistance.contextExposure[key]=type(ExposedMembers)=='table'and ExposedMembers[key]~=nil or false
end
local p=assert(Players[PLAYER],'Target player absent');local target=out.target
target.human=p:IsHuman();target.alive=p:IsAlive();target.major=p:IsMajor()
assert(target.human==false,'Target is currently human; original identity must be gated before autoplay')
target.gold=call(p:GetTreasury(),'GetGoldBalance')
local techs,culture=p:GetTechs(),p:GetCulture()
target.research={technology=call(techs,'GetResearchingTech'),civic=call(culture,'GetProgressingCivic')}
if d.PrereqTech then target.research.prereqTech=call(techs,'HasTech',assert(GameInfo.Technologies[d.PrereqTech]).Index)end
if d.PrereqCivic then target.research.prereqCivic=call(culture,'HasCivic',assert(GameInfo.Civics[d.PrereqCivic]).Index)end
for _,c in p:GetCities():Members()do if c:GetID()==CITY then
 target.exists=true;target.name=c:GetName();target.x=c:GetX();target.y=c:GetY();target.population=c:GetPopulation()
 target.yields=object();for row in GameInfo.Yields()do target.yields[row.YieldType]=call(c,'GetYield',row.Index)end
 target.districts={};target.hasSelectedQuarter=false
 local q,ds=c:GetBuildQueue(),c:GetDistricts()
 assert(type(ds.GetNumDistricts)=='function'and type(ds.GetDistrictByIndex)=='function','Native indexed district API unavailable')
 for i=0,ds:GetNumDistricts()-1 do
  local district=ds:GetDistrictByIndex(i)
  if district then
   local di=district:GetType();local definition=assert(GameInfo.Districts[di])
   local r={index=di,type=definition.DistrictType,x=district:GetX(),y=district:GetY(),complete=district:IsComplete(),pillaged=district:IsPillaged(),
    progress=call(q,'GetDistrictProgress',di),cost=call(q,'GetDistrictCost',di)}
   r.plot=r.x+r.y*out.width;target.districts[#target.districts+1]=r
   if di==d.Index then target.hasSelectedQuarter=true end
  end
 end
 target.queue={production=call(q,'CurrentlyBuilding'),hash=call(q,'GetCurrentProductionTypeHash'),size=call(q,'GetSize'),
  selectedDistrictProgress=call(q,'GetDistrictProgress',d.Index),selectedDistrictCost=call(q,'GetDistrictCost',d.Index),entries={}}
 if type(target.queue.size)=='number'and target.queue.size>=0 and target.queue.size<=64 then
  for i=0,target.queue.size-1 do target.queue.entries[#target.queue.entries+1]=scalar(call(q,'GetAt',i))end
 end
 assert(type(Map.GetPlotDistance)=='function','Map distance API unavailable')
 local visibility=PlayersVisibility and PlayersVisibility[PLAYER]
 for index=0,out.width*out.height-1 do
  local plot=Map.GetPlotByIndex(index)
  if plot then
   local x,y=plot:GetX(),plot:GetY();local distance=Map.GetPlotDistance(target.x,target.y,x,y)
   if distance<=3 then
    local r={index=index,x=x,y=y,distance=distance,owner=plot:GetOwner(),district=plot:GetDistrictType(),feature=plot:GetFeatureType(),
     resource=plot:GetResourceType(),improvement=plot:GetImprovementType(),pillaged=plot:IsImprovementPillaged(),
     water=plot:IsWater(),impassable=plot:IsImpassable(),revealed=call(visibility,'IsRevealed',x,y),
     legal=call(plot,'CanHaveDistrict',d.Index,PLAYER,CITY)}
    if Cities and type(Cities.GetPlotPurchaseCity)=='function'then
     local ok,ownerCity=pcall(Cities.GetPlotPurchaseCity,plot)
     if not ok then r.purchaseCity={error=tostring(ownerCity)}
     elseif ownerCity then r.purchaseCity={player=ownerCity:GetOwner(),city=ownerCity:GetID()}end
    else r.purchaseCity={unavailable='GetPlotPurchaseCity'}end
    out.candidates[#out.candidates+1]=r
   end
  end
 end
end end
print('CSC_QUARTER_PLACEMENT_WORLD='..json(out))
