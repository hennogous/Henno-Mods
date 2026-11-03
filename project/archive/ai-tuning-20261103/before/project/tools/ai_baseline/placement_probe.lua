-- Read-only native prospective adjacency probe after the natural-run archive.
-- Do not treat a completed modifier as proof of prospective material scoring.
local y=assert(GameInfo.Yields['YIELD_CSC_AI_PLACEMENT']).Index
local result={rows={},completed={},modifiers={},human={},ui_filter=CSC_AI_UIFilterInstalled==true}
local function tagged(resource,tag)
 for r in GameInfo.TypeTags() do if r.Type==resource and r.Tag==tag then return true end end
 return false
end
local function visible(player,r)
 if r.PrereqTech and not player:GetTechs():HasTech(GameInfo.Technologies[r.PrereqTech].Index) then return false end
 if r.PrereqCivic and not player:GetCulture():HasCivic(GameInfo.Civics[r.PrereqCivic].Index) then return false end
 return true
end
local function customer(dt,q)
 if tagged(dt,'CLASS_CSC_'..q..'_SALES') then return true end
 for r in GameInfo.DistrictReplaces() do
  if r.CivUniqueDistrictType==dt and tagged(r.ReplacesDistrictType,'CLASS_CSC_'..q..'_SALES') then return true end
 end
 return false
end
local function facts(p,pid,player,q)
 local base,spec,sales=0,0,0
 for direction=0,5 do
  local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),direction)
  if n then
   local r=GameInfo.Resources[n:GetResourceType()]
   if n:GetOwner()==pid and r and visible(player,r) then
    if tagged(r.ResourceType,'CLASS_CSC_'..q..'_BASE') then base=base+1 end
    if tagged(r.ResourceType,'CLASS_CSC_'..q..'_SPEC') then spec=spec+1 end
   end
   local nd=GameInfo.Districts[n:GetDistrictType()]
   if nd and customer(nd.DistrictType,q) then sales=sales+1 end
  end
 end
 return base,spec,sales
end
for _,player in ipairs(PlayerManager.GetAliveMajors()) do
 local pid=player:GetID()
 result.human[#result.human+1]={player=pid,human=player:IsHuman()}
 for _,city in player:GetCities():Members() do
  local districts=city:GetDistricts()
  for _,d in districts:Members() do
   local dt=GameInfo.Districts[d:GetType()]
   local q=dt.DistrictType=='DISTRICT_CSC_BAKERS_QUARTER' and 'BAKERS' or dt.DistrictType=='DISTRICT_CSC_TAILORS_QUARTER' and 'TAILORS'
   if q then
    local p=Map.GetPlot(d:GetX(),d:GetY());local base,spec,sales=facts(p,pid,player,q)
    local ok,value=pcall(function()return d:GetYield(y)end)
    local adjok,adjvalue=pcall(function()return d:GetAdjacencyYield(y)end)
    local plotok,plotvalue=pcall(function()return p:GetAdjacencyYield(pid,city:GetID(),d:GetType(),y)end)
    result.completed[#result.completed+1]={player=pid,city=city:GetID(),quarter=q,plot=p:GetIndex(),
      complete=districts:IsComplete(d:GetType(),p:GetIndex()),pillaged=districts:IsPillaged(d:GetType(),p:GetIndex()),
      base=base,spec=spec,sales=sales,native_value=ok and value or nil,error=not ok and tostring(value) or nil,
      native_adjacency=adjok and adjvalue or nil,adjacency_error=not adjok and tostring(adjvalue) or nil,
      native_plot_adjacency=plotok and plotvalue or nil,plot_adjacency_error=not plotok and tostring(plotvalue) or nil}
   end
  end
  for q,dt in pairs({BAKERS='DISTRICT_CSC_BAKERS_QUARTER',TAILORS='DISTRICT_CSC_TAILORS_QUARTER'}) do
   local di=GameInfo.Districts[dt].Index
   for _,index in ipairs(Map.GetCityPlots():GetPurchasedPlots(city)) do
    local p=Map.GetPlotByIndex(index)
    if p:GetOwner()==pid and p:GetDistrictType()==-1 and not p:IsWater() and not p:IsImpassable()
       and Map.GetPlotDistance(city:GetX(),city:GetY(),p:GetX(),p:GetY())<=3 then
     local base,spec,sales=facts(p,pid,player,q)
     local ok,value=pcall(function()return p:GetAdjacencyYield(pid,city:GetID(),di,y)end)
     result.rows[#result.rows+1]={player=pid,city=city:GetID(),quarter=q,plot=index,base=base,spec=spec,sales=sales,
      legal=p:CanHaveDistrict(di,pid,city:GetID()),native_value=ok and value or nil,error=not ok and tostring(value) or nil}
    end
   end
  end
 end
end
-- Read live material-modifier activation separately from prospective values.
local ok,err=pcall(function()
 for _,id in ipairs(GameEffects.GetModifiers()) do
  local def=GameEffects.GetModifierDefinition(id)
  if def and def.Id and def.Id:match('^MOD_CSC_AI_MATERIAL_') then
   local owner=GameEffects.GetModifierOwner(id)
   result.modifiers[#result.modifiers+1]={definition=def.Id,active=GameEffects.GetModifierActive(id),
      owner=GameEffects.GetObjectString(owner),player=GameEffects.GetObjectsPlayerId(owner),subjects=GameEffects.GetModifierSubjects(id)}
  end
 end
end)
if not ok then result.modifier_probe_error=tostring(err) end
-- CSCBASE.json is available only in the separate gameplay context; this probe
-- uses the map helper's exported pure encoder, also includeable in UI.
include('CSC_MaterialMapCore')
print('CSC_AI_PLACEMENT_PROBE='..CSC_MaterialMapCore.Json(result))
