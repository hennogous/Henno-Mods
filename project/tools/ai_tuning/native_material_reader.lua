-- Read-only, scoped AI3 material/Builder observation at an inactive boundary.
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 if t~='table'then return 'null'end
 local a,n,array={},0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
local function call(o,k,...)
 if not o or type(o[k])~='function'then return {unavailable=k}end
 local ok,v=pcall(o[k],o,...);if ok then return v end;return {error=tostring(v)}
end
local function scalar(row)
 local out={};if row then for k,v in pairs(row)do if type(v)=='string'or type(v)=='number'or type(v)=='boolean'then out[k]=v end end end;return out
end
local coreLegalityOnly=__CORE_LEGALITY_ONLY__;local pid=3;local player=assert(Players[pid]);assert(player:IsAlive()and player:IsMajor()and not player:IsHuman())
-- PlayerConfigurations:IsHuman is a UI-only binding here; the complete
-- Core source gate and player:IsHuman above already establish Core identity.
if not coreLegalityOnly then assert(not PlayerConfigurations[pid]:IsHuman())end
local out={turn=Game.GetCurrentGameTurn(),player=pid,targets={},builders={},quarters={},metadata={},path_assignment='unknown; inspect native closed log segments',action_authorization=false}
local catalog={count=0,index_limit=0,rows={},selected={}}
for improvement in GameInfo.Improvements()do
 local row={index=improvement.Index,type=improvement.ImprovementType,hash=improvement.Hash}
 catalog.rows[#catalog.rows+1]=row;catalog.count=catalog.count+1;catalog.index_limit=math.max(catalog.index_limit,improvement.Index+1)
 if improvement.ImprovementType=='IMPROVEMENT_FARM'or improvement.ImprovementType=='IMPROVEMENT_CAMP'or improvement.ImprovementType=='IMPROVEMENT_MINE'then catalog.selected[improvement.ImprovementType]=row end
end
out.metadata.improvement_catalog=catalog
local function unlocked(row)
 return(not row.PrereqTech or player:GetTechs():HasTech(GameInfo.Technologies[row.PrereqTech].Index))and(not row.PrereqCivic or player:GetCulture():HasCivic(GameInfo.Civics[row.PrereqCivic].Index))
end
local function tile(p)
 local row={plot=p:GetIndex(),x=p:GetX(),y=p:GetY(),owner=p:GetOwner(),resource=p:GetResourceType(),count=p:GetResourceCount(),feature=p:GetFeatureType(),improvement=p:GetImprovementType(),improvement_pillaged=p:IsImprovementPillaged(),district=p:GetDistrictType(),terrain=p:GetTerrainType(),river=p:IsRiver(),hills=p:IsHills(),water=p:IsWater(),impassable=p:IsImpassable(),revealed=PlayersVisibility[pid]:IsRevealed(p:GetX(),p:GetY()),properties={}}
 for _,k in ipairs({'CSC_AI_CARE_LAST_BASE','CSC_AI_CARE_LAST_SPEC','CSC_AI_CARE_REDUNDANT'})do row.properties[k]=p:GetProperty(k)end
 return row
end
for _,idx in ipairs({2489,2344})do
 local p=assert(Map.GetPlotByIndex(idx));local row=tile(p);row.legal_improvements={};row.resource_definition=scalar(GameInfo.Resources[row.resource]);row.feature_definition=scalar(GameInfo.Features[row.feature]);row.feature_removals={}
 local removalTech=row.feature_definition.RemoveTech;if removalTech and GameInfo.Technologies[removalTech]then row.feature_removal_tech_owned=player:GetTechs():HasTech(GameInfo.Technologies[removalTech].Index)end;local resource=row.resource_definition.ResourceType;local feature=row.feature_definition.FeatureType
 for valid in GameInfo.Improvement_ValidResources()do if valid.ResourceType==resource then
  local imp=assert(GameInfo.Improvements[valid.ImprovementType]);local binding=ImprovementBuilder and ImprovementBuilder.CanHaveImprovement;local ok,value=false,'binding unavailable';if type(binding)=='function'then ok,value=pcall(binding,p,imp.Index,pid)end
  row.legal_improvements[#row.legal_improvements+1]={mapping=scalar(valid),definition=scalar(imp),unlocked=unlocked(imp),native_legal=ok and value or 'unknown',native_status=ok and 'observed'or'unknown',native_error=not ok and tostring(value)or nil,valid_features={}}
  local r=row.legal_improvements[#row.legal_improvements];if ok then r.native_legal=value end
  for entry in GameInfo.Improvement_ValidFeatures()do if entry.ImprovementType==imp.ImprovementType then r.valid_features[#r.valid_features+1]=scalar(entry)end end
 end end
 if feature and GameInfo.Feature_Removes then for entry in GameInfo.Feature_Removes()do if entry.FeatureType==feature then local e=scalar(entry);row.feature_removals[#row.feature_removals+1]=e end end end
 out.targets[#out.targets+1]=row
end
if coreLegalityOnly then print('CSC_MATERIAL_LEGALITY='..json({turn=out.turn,player=pid,targets=out.targets}));return end
for _,unit in player:GetUnits():Members()do if unit:GetType()==GameInfo.Units.UNIT_BUILDER.Index then
 local row={unit=unit:GetID(),x=unit:GetX(),y=unit:GetY(),moves=unit:GetMovesRemaining(),charges=unit:GetBuildCharges(),damage=unit:GetDamage(),distances={}}
 for _,target in ipairs(out.targets)do row.distances[tostring(target.plot)]=Map.GetPlotDistance(row.x,row.y,target.x,target.y)end
 out.builders[#out.builders+1]=row
end end
table.sort(out.builders,function(a,b)return a.unit<b.unit end)
for _,city in player:GetCities():Members()do
 for _,district in city:GetDistricts():Members()do local p=Map.GetPlot(district:GetX(),district:GetY());local idx=p:GetIndex()
 if idx==2488 or idx==2564 or idx==2419 then
  local row={plot=idx,city=city:GetID(),district=GameInfo.Districts[district:GetType()].DistrictType,complete=district:IsComplete(),pillaged=district:IsPillaged(),buildings={},neighbors={},adjacency={},city_yields={}}
  for b in GameInfo.Buildings()do if city:GetBuildings():HasBuilding(b.Index)then row.buildings[#row.buildings+1]={definition=scalar(b),pillaged=call(city:GetBuildings(),'IsPillaged',b.Index)}end end
  for _,neighbor in ipairs(Map.GetAdjacentPlots(p:GetX(),p:GetY()))do row.neighbors[#row.neighbors+1]=tile(neighbor)end
  for _,name in ipairs({'YIELD_PRODUCTION','YIELD_GOLD','YIELD_FOOD'})do local y=GameInfo.Yields[name].Index;row.adjacency[name]=call(district,'GetAdjacencyYield',y);row.city_yields[name]=city:GetYield(y)end
  out.quarters[#out.quarters+1]=row
 end end
end
local prefix='CSC_AI_ASSISTANCE_V1_';out.ledger={}
local function get(k)local v=Game:GetProperty(prefix..k);if v~=nil then out.ledger[k]=v end;return v end
for _,k in ipairs({'TOTALS','INITIAL_HUMANS','HOST_REVISION','DIAGNOSTIC_ERRORS_BEFORE_REVISION3'})do get(k)end
local sites={}
for _,kind in ipairs({'RECEIPT','FOUNDATION'})do for _,key in ipairs(get(kind..'_INDEX')or{})do local v=get(kind..'_'..key);if v and v.site then sites[v.site]=true end;if kind=='FOUNDATION'then sites[key]=true end end end
for site in pairs(sites)do get('SITE_COST_'..site)end
for id=0,63 do for _,k in ipairs({'PENDING_','ERROR_','TURN_','BUYS_'})do get(k..id)end end
for _,p in ipairs(PlayerManager.GetAlive())do for _,city in p:GetCities():Members()do get('CITY_BUY_'..p:GetID()..':'..city:GetID())end end
print('CSC_MATERIAL_FOLLOWTHROUGH='..json(out))
