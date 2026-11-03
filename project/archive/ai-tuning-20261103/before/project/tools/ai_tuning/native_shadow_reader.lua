-- Bounded read-only shadow capture. Explicit AI identity; no callbacks or writes.
-- Native candidate adjacency and CSC computed contributions remain separate.
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
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
 local copy={};for k,v in pairs(row)do if type(v)=='number'or type(v)=='string'or type(v)=='boolean'then copy[k]=v end end;return copy
end
local pid,cid=3,131073
local player=assert(Players[pid]);local city=assert(CityManager.GetCity(pid,cid))
assert(Game.GetCurrentGameTurn()==110 and city:GetOwner()==pid and city:GetX()==43 and city:GetY()==30 and city:GetPopulation()==7)
assert(player:IsAlive()and player:IsMajor()and not player:IsHuman())
assert(not PlayerConfigurations[pid]:IsHuman())
local A=assert(CSC_Adjacency,'PlotInfo must expose the installed shared CSC adjacency reader')
assert(A.ByDistrict and A.Count and A.Eligible and A.Amount)
local quarters={'BAKERS','TAILORS'}
local out={schema=1,turn=110,player=pid,city=cid,scope='all native BUILD targets for Bakers/Tailors in AI3 city131073; radius4 facts; all AI3 existing Quarter dependencies',
 action_authorization=false,execution_readiness='unknown',enrichment_complete=false,district_state={},candidates={},tiles={},chains={},controls={},
 mapping={TypeTags={},Improvement_ValidResources={},requirements={},requirement_arguments={},requirement_sets={},requirement_members={}},
 economics={gold=player:GetTreasury():GetGoldBalance(),production=city:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index)},
 city_state={x=43,y=30,population=7,districts={},buildings={},queue={}},
 capacity={observed_specialty_count=call(city:GetDistricts(),'GetNumSpecialtyDistricts'),observed_district_count=call(city:GetDistricts(),'GetNumDistricts'),reserved='unknown',builder_capacity='unknown'}}
local q=city:GetBuildQueue();out.city_state.queue={size=q:GetSize(),hash=q:GetCurrentProductionTypeHash(),items={}}
local producing=GameInfo.Buildings[out.city_state.queue.hash]
assert(producing and producing.BuildingType=='BUILDING_GOV_FAITH','Declared source queue mismatch')
for i=0,q:GetSize()-1 do out.city_state.queue.items[#out.city_state.queue.items+1]=scalar(q:GetAt(i))end
for d in GameInfo.Districts()do if city:GetDistricts():HasDistrict(d.Index)then out.city_state.districts[#out.city_state.districts+1]=d.Index end end
for b in GameInfo.Buildings()do if city:GetBuildings():HasBuilding(b.Index)then out.city_state.buildings[#out.city_state.buildings+1]=b.BuildingType end end
table.sort(out.city_state.districts);assert(#out.city_state.districts==2 and out.city_state.districts[1]==0 and out.city_state.districts[2]==23)
local tags,valid,scope={},{},{}
for row in GameInfo.TypeTags()do if row.Tag:find('CLASS_CSC_',1,true)==1 then
 out.mapping.TypeTags[#out.mapping.TypeTags+1]=scalar(row);tags[row.Type]=tags[row.Type]or{};tags[row.Type][row.Tag]=true
end end
for row in GameInfo.Improvement_ValidResources()do
 out.mapping.Improvement_ValidResources[#out.mapping.Improvement_ValidResources+1]=scalar(row)
 valid[row.ResourceType..'|'..row.ImprovementType]=true
end
for _,entry in ipairs({{'Requirements','requirements','RequirementId'},{'RequirementArguments','requirement_arguments','RequirementId'},{'RequirementSets','requirement_sets','RequirementSetId'},{'RequirementSetRequirements','requirement_members','RequirementSetId'}})do
 for row in GameInfo[entry[1]]()do local key=row[entry[3]]or''
  if key:find('CSC',1,true)and(key:find('BAKERS',1,true)or key:find('TAILORS',1,true)or key=='REQ_CSC_PLOT_ADJ_TO_OWNER')then out.mapping[entry[2]][#out.mapping[entry[2]]+1]=scalar(row)end
 end
end
local function visibleResource(r)
 if not r then return false end
 if r.PrereqTech then return player:GetTechs():HasTech(GameInfo.Technologies[r.PrereqTech].Index)end
 if r.PrereqCivic then return player:GetCulture():HasCivic(GameInfo.Civics[r.PrereqCivic].Index)end
 return true
end
local function tile(plot)
 local r=GameInfo.Resources[plot:GetResourceType()];local imp=GameInfo.Improvements[plot:GetImprovementType()]
 local pc=Cities.GetPlotPurchaseCity(plot);local row={plot=plot:GetIndex(),x=plot:GetX(),y=plot:GetY(),owner=plot:GetOwner(),purchase_city=pc and pc:GetID()or -1,
 resource=r and r.ResourceType or '',resource_visible=visibleResource(r),improvement=imp and imp.ImprovementType or '',
 improvement_pillaged=plot:IsImprovementPillaged(),worked=call(plot,'GetWorkerCount'),district=plot:GetDistrictType(),
 river=plot:IsRiver(),revealed=PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY()),neighbors={},roles={},city_building_inventory={}}
 row.valid_resource_improvement=r and imp and valid[r.ResourceType..'|'..imp.ImprovementType]or false
 for _,key in ipairs(quarters)do row.roles[key]={base=r and tags[r.ResourceType]and tags[r.ResourceType]['CLASS_CSC_'..key..'_BASE']or false,specialty=r and tags[r.ResourceType]and tags[r.ResourceType]['CLASS_CSC_'..key..'_SPEC']or false}end
 for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do row.neighbors[#row.neighbors+1]=near:GetIndex()end;table.sort(row.neighbors)
 -- City census only: these entries do not locate buildings on this district.
 if pc and plot:GetDistrictType()>=0 then for b in GameInfo.Buildings()do if pc:GetBuildings():HasBuilding(b.Index)then row.city_building_inventory[#row.city_building_inventory+1]={type=b.BuildingType,pillaged=call(pc:GetBuildings(),'IsPillaged',b.Index)}end end end
 return row
end
local function preview(plot,c,d)
 local data={native={},computed_real={},computed_private={},computed_other={},rules={}}
 for _,y in ipairs({'YIELD_PRODUCTION','YIELD_GOLD'})do data.native[y]=call(plot,'GetAdjacencyYield',pid,c:GetID(),d.Index,GameInfo.Yields[y].Index)end
 -- Same Count/Eligible/Amount read predicates used by the maintained CSC UI.
 -- No A.Write or property-setting method is called. No native/computed sum.
 for _,rule in ipairs(A.ByDistrict[d.DistrictType]or{})do
  local eligible=A.Eligible(rule,c,pid);local count=eligible and A.Count(rule,plot,c,pid)or 0;local amount=A.Amount(rule,count)
  local row=scalar(rule);row.eligible=eligible;row.count=count;row.computed_amount=amount;data.rules[#data.rules+1]=row
  if rule.ProvideType=='SelfBonus'then
   local dest=data.computed_other
   if rule.YieldType=='YIELD_PRODUCTION'or rule.YieldType=='YIELD_GOLD'then dest=data.computed_real
   elseif rule.YieldType=='YIELD_CSC_AI_PLACEMENT'then dest=data.computed_private end
   dest[rule.YieldType]=(dest[rule.YieldType]or 0)+amount
  end
 end
 return data
end
for idx=0,Map.GetPlotCount()-1 do local plot=Map.GetPlotByIndex(idx)
 if Map.GetPlotDistance(43,30,plot:GetX(),plot:GetY())<=4 then scope[idx]=true end
end
for _,key in ipairs(quarters)do
 local d=assert(GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER']);assert(d.Index==(key=='BAKERS' and 36 or 37))
 local can,reasons=q:CanProduce(d.Hash,false,true);local pars={};pars[CityOperationTypes.PARAM_DISTRICT_TYPE]=d.Hash
 local targets=CityManager.GetOperationTargets(city,CityOperationTypes.BUILD,pars)
 local raw=targets and targets[CityOperationResults.PLOTS]or{};local state={can_produce=can,reasons=reasons,targets={},exists=city:GetDistricts():HasDistrict(d.Index),placed=q:HasBeenPlaced(d.Hash),cost=q:GetDistrictCost(d.Index),progress=q:GetDistrictProgress(d.Index)}
 assert(not state.exists and not state.placed,'Declared city already has Quarter')
 out.district_state[key]=state
 for _,idx in ipairs(raw)do
  local plot=assert(Map.GetPlotByIndex(idx));pars[CityOperationTypes.PARAM_X]=plot:GetX();pars[CityOperationTypes.PARAM_Y]=plot:GetY()
  local legal,why=CityManager.CanStartOperation(city,CityOperationTypes.BUILD,pars,true)
  state.targets[#state.targets+1]={plot=idx,legal=legal,reasons=why};assert(scope[idx],'Native target escaped declared radius scope')
  if legal then
   local candidate={quarter=key,plot=idx,legal=true,can_produce=can,potential=plot:CanHaveDistrict(d.Index,pid,cid),preview=preview(plot,city,d),future_customer_geometry={},mapped_customer_types={}}
   local customerTypes={}
   for _,rule in ipairs(A.ByDistrict[d.DistrictType]or{})do
    local object=rule.CustomAdjacentObject
    if rule.AdjacencyType=='FROM_RINGS_TYPETAG_DISTRICT'or rule.AdjacencyType=='FROM_RINGS_CAO_DISTRICT'then
     for other in GameInfo.Districts()do if other.DistrictType==object or(tags[other.DistrictType]and tags[other.DistrictType][object])then customerTypes[other.DistrictType]=other end end
    end
   end
   for name,other in pairs(customerTypes)do candidate.mapped_customer_types[#candidate.mapped_customer_types+1]={type=name,index=other.Index}end
   table.sort(candidate.mapped_customer_types,function(a,b)return a.index<b.index end)
   for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do if near:GetDistrictType()<0 then
    local facts={plot=near:GetIndex(),native_potential={}}
    for name,other in pairs(customerTypes)do facts.native_potential[name]=near:CanHaveDistrict(other.Index,pid,cid)end
    candidate.future_customer_geometry[#candidate.future_customer_geometry+1]=facts
   end end
   out.candidates[#out.candidates+1]=candidate
  end
 end
end
local function captureTiles()
 out.tiles={};local indices={};for idx in pairs(scope)do indices[#indices+1]=idx end;table.sort(indices)
 for _,idx in ipairs(indices)do out.tiles[#out.tiles+1]=tile(Map.GetPlotByIndex(idx))end
end
table.sort(out.candidates,function(a,b)return a.quarter==b.quarter and a.plot<b.plot or a.quarter<b.quarter end)
captureTiles()
-- Preserve bounded candidate facts before optional dependency/control enrichment.
-- This partial stage cannot pass the complete scientific evidence gate.
out.stage='candidate_capture';print('CSC_SHADOW_CANDIDATES='..json(out))
local ok,error=pcall(function()
-- Existing chains are dependency inventory / getter controls, never extra starts.
for _,c in player:GetCities():Members()do local ds=c:GetDistricts();local cq=c:GetBuildQueue()
 -- UI city district collection contract: shipped CitySupport.lua uses Members.
 for _,district in ds:Members()do local d=GameInfo.Districts[district:GetType()]
  if d and(d.DistrictType=='DISTRICT_CSC_BAKERS_QUARTER'or d.DistrictType=='DISTRICT_CSC_TAILORS_QUARTER')then
   local plot=assert(Map.GetPlot(district:GetX(),district:GetY()));local key=d.DistrictType=='DISTRICT_CSC_BAKERS_QUARTER'and'BAKERS'or'TAILORS'
   local chain={city=c:GetID(),quarter=key,plot=plot:GetIndex(),complete=call(district,'IsComplete'),pillaged=call(district,'IsPillaged'),progress=cq:GetDistrictProgress(d.Index),cost=cq:GetDistrictCost(d.Index),current_production_hash=cq:GetCurrentProductionTypeHash(),dependencies={},reserved_request='unknown'}
   scope[plot:GetIndex()]=true
   for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do scope[near:GetIndex()]=true;local t=tile(near)
    if t.roles[key].base or t.roles[key].specialty then chain.dependencies[#chain.dependencies+1]=t.plot end
   end
   out.chains[#out.chains+1]=chain
   local ctrl={city=c:GetID(),quarter=key,plot=plot:GetIndex(),preview=preview(plot,c,d),existing_adjacency={},existing_total={}}
    for _,y in ipairs({'YIELD_PRODUCTION','YIELD_GOLD'})do local yi=GameInfo.Yields[y].Index;ctrl.existing_adjacency[y]=call(district,'GetAdjacencyYield',yi);ctrl.existing_total[y]=call(district,'GetYield',yi)end
    out.controls[#out.controls+1]=ctrl
  end
 end
end
end)
out.enrichment_complete=ok
if not ok then out.enrichment_error=tostring(error)end
out.stage=ok and'complete_geometry_capture'or'partial_geometry_capture'
captureTiles()
table.sort(out.controls,function(a,b)return a.city==b.city and a.plot<b.plot or a.city<b.city end)
print('CSC_SHADOW_GEOMETRY='..json(out))
