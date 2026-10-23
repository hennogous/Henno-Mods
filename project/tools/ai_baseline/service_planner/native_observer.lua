-- Read-only live collector for the separate Service-planner experiment.
-- UI owns native operation targets/costs; no inferred legality or strategy getter.
CSC_SERVICE_NATIVE=CSC_SERVICE_NATIVE or {dirty={}}
local S=CSC_SERVICE_NATIVE
local function call(o,k,...)
 if not o or type(o[k])~='function' then return nil end
 local ok,v=pcall(o[k],o,...);if ok then return v end
end
local function json(v)
 local t=type(v);if t=='nil'then return 'null' end
 if t=='boolean'or t=='number'then return tostring(v)end
 if t=='string'then return string.format('%q',v)end
 if t~='table'then return 'null'end
 local n,array=0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 local a={};if array then for i=1,#v do a[#a+1]=json(v[i])end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
S.Json=json
local types={'BAKERS','TAILORS'}
local maps={}
for _,q in ipairs(types)do
 maps[q]={base={},spec={}}
 for r in GameInfo.TypeTags()do local def=GameInfo.Resources[r.Type];if def then
  if r.Tag=='CLASS_CSC_'..q..'_BASE'then maps[q].base[def.Index]=true end
  if r.Tag=='CLASS_CSC_'..q..'_SPEC'then maps[q].spec[def.Index]=true end
 end end
end
local function unlocked(p,d)
 if d.PrereqTech and not p:GetTechs():HasTech(GameInfo.Technologies[d.PrereqTech].Index)then return false end
 if d.PrereqCivic and not p:GetCulture():HasCivic(GameInfo.Civics[d.PrereqCivic].Index)then return false end
 return true
end
function S.Read()
 local out={turn=Game.GetCurrentGameTurn(),cities={},players={},dirty=S.dirty,unchanged={},delta_checks={},
  purchase_parameter=true,interface_purchase_parameter=UI.GetInterfaceModeParameter(CityCommandTypes.PARAM_PLOT_PURCHASE),
  purchase_parameter_source='native boolean plot-purchase flag; independent of UI mode'}
 S.dirty={}
 for pid=1,5 do local p=Players[pid]
 if p and p:IsAlive()and p:IsMajor()and not p:IsHuman()then
  local tr=p:GetTreasury()
  local gross=call(tr,'GetGoldYield');local upkeep=call(tr,'GetTotalMaintenance')
  local observed=type(gross)=='number'and type(upkeep)=='number'
  out.players[#out.players+1]={player=pid,gold=tr:GetGoldBalance(),gross_income=gross,maintenance=upkeep,net_income=observed and(gross-upkeep)or nil,cashflow_observed=observed}
  local venues={}
  assert(S.venues_turn~=nil,'Gameplay venue readback required')
  for _,v in ipairs(S.external_venues)do if v.owner==pid then venues[#venues+1]=v end end
  for _,c in p:GetCities():Members()do
   local delta_key,delta_fingerprint,refresh,reason
   if S.delta_mode then
    local checked;delta_key,delta_fingerprint,checked=CSC_SERVICE_DELTA.Fingerprint(S,c,p,pid)
    refresh,reason=CSC_SERVICE_DELTA.Decide(delta_key,delta_fingerprint,out.turn,S.delta_force_refresh)
    out.delta_checks[#out.delta_checks+1]={player=pid,city=c:GetID(),reason=reason,checked_plots=checked,scope=delta_key}
   else refresh=true end
   if not refresh then
    out.unchanged[#out.unchanged+1]={player=pid,city=c:GetID(),scope=delta_key}
   else
   -- No watch entry means a broad scan is due, including newly founded cities.
   -- Otherwise read only marked sources and their resource-neighbor footprints.
   local watch=S.material_first and S.city_watch and S.city_watch[tostring(pid)..':'..tostring(c:GetID())]or nil
   if S.delta_mode then watch=nil end -- Rebuild changed scope; unchanged scopes returned above.
   local q=c:GetBuildQueue();local cs={player=pid,city=c:GetID(),turn=out.turn,eligible_ai=true,human=false,
    era=p:GetEra(),same_quarter_types={},tiles={},venues=venues,readiness={},district_defs={},district_state={},broad_scan=watch==nil}
   local established={}
   if S.external_quarters then
    assert(S.quarters_turn==out.turn or S.quarters_turn==out.turn+1,'Stale established Quarter bridge')
    for _,site in ipairs(S.external_quarters[tostring(pid)..':'..tostring(c:GetID())]or {})do established[site.plot]=site.quarter end
   end
   cs.population=c:GetPopulation();local growth=c:GetGrowth()
   cs.housing=call(growth,'GetHousing');cs.food_surplus=call(growth,'GetFoodSurplus')
   cs.production=c:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index)
   local unit=GameInfo.Units[call(q,'GetCurrentProductionTypeHash')or -1]
   cs.naval_unit_in_production=not S.material_first and unit and unit.Domain=='DOMAIN_SEA'or false
   local hash=call(q,'GetCurrentProductionTypeHash')or -1
   local producing=GameInfo.Buildings[hash]or GameInfo.Districts[hash]or GameInfo.Units[hash]or GameInfo.Projects[hash]
   local name=producing and(producing.BuildingType or producing.DistrictType or producing.UnitType or producing.ProjectType)
   local delay=name and call(q,'GetTurnsLeft',name)or(q:GetSize()==0 and 0 or 999)
   cs.queue_delay=q:GetSize()>1 and 999 or math.max(0,delay or 999)
   local cultureN,religionN=0,0
   for _,v in ipairs(venues)do
    if v.type=='BUILDING_AMPHITHEATER'or v.type=='BUILDING_MUSEUM_ART'or v.type=='BUILDING_MUSEUM_ARTIFACT'then cultureN=cultureN+1 end
    if v.type=='BUILDING_TEMPLE'then religionN=religionN+1 end
   end
   cs.culture_emphasis=math.min(1,cultureN/math.max(1,p:GetCities():GetCount()))
   cs.religion_emphasis=math.min(1,religionN/math.max(1,p:GetCities():GetCount()))
   local current={};local producible={}
   for _,key in ipairs(types)do local d=assert(GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER'])
    cs.district_defs[key]={Index=d.Index,Hash=d.Hash}
    if c:GetDistricts():HasDistrict(d.Index)or q:HasBeenPlaced(d.Hash)then cs.same_quarter_types[#cs.same_quarter_types+1]=key end
    current[key]={};local allowed,reasons=q:CanProduce(d.Hash,false,true);producible[key]=allowed
    cs.district_state[key]={can_produce=allowed,secondary_result=reasons,placed=q:HasBeenPlaced(d.Hash),exists=c:GetDistricts():HasDistrict(d.Index)}
    if producible[key]then local pars={};pars[CityOperationTypes.PARAM_DISTRICT_TYPE]=d.Hash
     local targets=CityManager.GetOperationTargets(c,CityOperationTypes.BUILD,pars)
     for _,idx in ipairs(targets and targets[CityOperationResults.PLOTS]or {})do local plot=Map.GetPlotByIndex(idx)
      pars[CityOperationTypes.PARAM_X]=plot:GetX();pars[CityOperationTypes.PARAM_Y]=plot:GetY()
      if CityManager.CanStartOperation(c,CityOperationTypes.BUILD,pars,true)then current[key][idx]=true end
     end
    end
   end
   local purchase={};local pars={};pars[CityCommandTypes.PARAM_PLOT_PURCHASE]=out.purchase_parameter
   -- Normal observer-context queries reject AI cities even on their turns.
   -- Native visibility results expose physical reach, not execution authority.
   local normalTargets=CityManager.GetCommandTargets(c,CityCommandTypes.PURCHASE,pars)
   local visible,targets=CityManager.CanStartCommand(c,CityCommandTypes.PURCHASE,true,pars,true)
   local commandApproved={}
   for _,idx in ipairs(visible and targets and targets[CityCommandResults.PLOTS]or {})do local plot=Map.GetPlotByIndex(idx)
    pars[CityCommandTypes.PARAM_X]=plot:GetX();pars[CityCommandTypes.PARAM_Y]=plot:GetY()
    purchase[idx]=true
    if CityManager.CanStartCommand(c,CityCommandTypes.PURCHASE,pars)then commandApproved[#commandApproved+1]=idx end
   end
   cs.native_purchase_command_target_list=normalTargets and normalTargets[CityCommandResults.PLOTS]or {}
   cs.native_purchase_command_approved=commandApproved
   cs.native_purchase_query_kind='native visibility reach; execution authority requires real ownership+gold receipt' 
   local legacy={};legacy[CityCommandTypes.PARAM_PLOT_PURCHASE]=out.interface_purchase_parameter
   local legacyTargets=CityManager.GetCommandTargets(c,CityCommandTypes.PURCHASE,legacy)
   cs.native_purchase_legacy_target_list=legacyTargets and legacyTargets[CityCommandResults.PLOTS]or {}
   cs.native_purchase_target_list=targets and targets[CityCommandResults.PLOTS]or {};cs.native_purchase_approved={};for idx in pairs(purchase)do cs.native_purchase_approved[#cs.native_purchase_approved+1]=idx end
   cs.current_production_hash=hash;cs.queue_size=q:GetSize()
   local culture=c:GetCulture();local nextplot=call(culture,'GetNextPlot');local border=call(culture,'GetTurnsUntilExpansion')
   -- Geography is fixed around a city's coordinates. Cache its ring-four
   -- indices once; every broad scan still refreshes current ownership/reveal.
   -- Focused turns iterate only watched source/material/connector footprints.
   S.geography_cache=S.geography_cache or {}
   local indices={};local geography_key=tostring(pid)..':'..tostring(c:GetID())..':'..tostring(c:GetX())..':'..tostring(c:GetY())
   if watch then for idx in pairs(watch)do indices[#indices+1]=idx end
   elseif S.geography_cache[geography_key]then indices=S.geography_cache[geography_key];cs.geography_cache_hit=true
   else
    for idx=0,Map.GetPlotCount()-1 do
     local plot=Map.GetPlotByIndex(idx)
     if Map.GetPlotDistance(c:GetX(),c:GetY(),plot:GetX(),plot:GetY())<=4 then indices[#indices+1]=idx end
    end
    S.geography_cache[geography_key]=indices
   end
   table.sort(indices);cs.checked_plot_indices=#indices
   for _,idx in ipairs(indices)do local plot=Map.GetPlotByIndex(idx)
    if (not watch or watch[idx])and Map.GetPlotDistance(c:GetX(),c:GetY(),plot:GetX(),plot:GetY())<=4 and PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY())then
     local res=GameInfo.Resources[plot:GetResourceType()]
     local row={established_quarter=established[idx],index=idx,owner=plot:GetOwner(),revealed=true,within_city_reach=Map.GetPlotDistance(c:GetX(),c:GetY(),plot:GetX(),plot:GetY())<=3,
      resource=plot:GetResourceType(),improvement=plot:GetImprovementType(),district=plot:GetDistrictType(),feature=plot:GetFeatureType(),
      terrain=call(plot,'GetTerrainType'),water=call(plot,'IsWater'),mountain=call(plot,'IsMountain'),impassable=call(plot,'IsImpassable'),
      neighbors={},base_for={},spec_for={},potential_legal={},current_legal={},chain={},
      native_purchasable=purchase[idx]or false,native_projection_verified=false,price=0,frontier_danger=false,
      improvement_pillaged=plot:IsImprovementPillaged(),
      natural_border_in_turns=idx==nextplot and border or nil,material_visible=res and unlocked(p,res)or false}
     -- Keep native estimates for later acquisition steps as well as the next
     -- currently legal buy. A missing/zero estimate makes the plan watch-only.
     if plot:GetOwner()==-1 then row.price=call(c:GetGold(),'GetPlotPurchaseCost',idx)or 0 end
     for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
      row.neighbors[#row.neighbors+1]=near:GetIndex()
      if near:GetOwner()>=0 and near:GetOwner()~=pid then row.frontier_danger=true end
     end
     for _,key in ipairs(types)do local d=GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER']
      row.potential_legal[key]=plot:CanHaveDistrict(d.Index,pid,c:GetID())and unlocked(p,d)or false
      row.current_legal[key]=current[key][idx]or false
      if maps[key].base[plot:GetResourceType()]then row.base_for[#row.base_for+1]=key end
      if maps[key].spec[plot:GetResourceType()]then row.spec_for[#row.spec_for+1]=key end
      row.native_projection_verified=row.native_projection_verified or row.potential_legal[key]
      -- Conservative production estimate: no reassignment/forced production.
      if not S.material_first then
      local producer=key=='BAKERS'and(plot:IsRiver()and'BUILDING_CSC_BAKERS_WATER_MILL'or'BUILDING_CSC_BAKERS_WIND_MILL')or'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'
      local chain={};local def=GameInfo.Buildings[producer]
      local cost=q:GetDistrictCost(d.Index);local ok=def and unlocked(p,def)
      if def then cost=cost+q:GetBuildingCost(def.Index)end
      chain[2]={turns=ok and cs.production>0 and cs.queue_delay+math.ceil(cost/cs.production)or 999,ready=ok or false}
      for stage=3,4 do local name=key=='BAKERS'and(stage==3 and'BAKERY'or'CAFE')or(stage==3 and'TAILOR'or'FASHION_HOUSE')
       local bd=GameInfo.Buildings['BUILDING_CSC_'..key..'_'..name]
       ok=ok and bd and unlocked(p,bd);if bd then cost=cost+q:GetBuildingCost(bd.Index)end
       chain[stage]={turns=ok and cs.production>0 and cs.queue_delay+math.ceil(cost/cs.production)or 999,ready=ok or false}
      end
      row.chain[key]=chain
      end
     end
     cs.tiles[#cs.tiles+1]=row
    end
   end
   for civic in GameInfo.Civics()do if p:GetCulture():HasCivic(civic.Index)then cs.readiness[civic.CivicType]=true end end
   out.cities[#out.cities+1]=cs
   if S.delta_mode then CSC_SERVICE_DELTA.Remember(delta_key,delta_fingerprint,out.turn)end
   end
  end
 end end
 print('CSC_SERVICE_NATIVE='..json(out))
end
-- Reinstalling a maintained reader at a safe source handoff must not add
-- another copy of its diagnostic callbacks. Legacy anonymous listeners from
-- earlier versions can only add dirty duplicates, which the coordinator coalesces.
if Events.CityTileOwnershipChanged then
 if S.ownership_handler and Events.CityTileOwnershipChanged.Remove then Events.CityTileOwnershipChanged.Remove(S.ownership_handler)end
 S.ownership_handler=function(pid,cid)S.dirty[#S.dirty+1]={player=pid,city=cid,event='ownership'}end
 Events.CityTileOwnershipChanged.Add(S.ownership_handler)
end
if Events.CityMadePurchase then
 if S.purchase_handler and Events.CityMadePurchase.Remove then Events.CityMadePurchase.Remove(S.purchase_handler)end
 S.purchase_handler=function(pid,cid)S.dirty[#S.dirty+1]={player=pid,city=cid,event='purchase'}end
 Events.CityMadePurchase.Add(S.purchase_handler)
end
