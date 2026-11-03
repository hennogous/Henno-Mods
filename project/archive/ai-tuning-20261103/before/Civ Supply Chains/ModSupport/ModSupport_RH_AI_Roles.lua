-- RH-only configured-role and material-fact bridge for CSC forecasts.
-- Original configured human identities survive temporary autoplay role flags.
-- Three source-plot properties mirror role and six-neighbour Base/Specialty
-- facts; SQL owns their private planning effects. No native production, treasury,
-- ownership, research or improvement order is issued by this component.
local PROPERTY='CSC_RH_CUSTOMER_CONFIGURED_AI'
local HUMANS='CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS'
local M={version=2,ready=false,writes=0,refreshes=0,supply_scans=0,supply_writes=0,errors={}}
ExposedMembers.CSC_RH_CustomerRoles=M
local function mode()
 for row in GameInfo.CSC_AI_Profile()do if row.Id=='ACTIVE'then return row.Mode end end
 return 'OFF'
end
local function humans()
 local value=Game:GetProperty(HUMANS)
 if type(value)~='table'then
  local ui=ExposedMembers.CSC_AI_AssistanceUI
  if not ui or type(ui.InitialHumanPlayers)~='function'then return nil end
  value=ui.InitialHumanPlayers()
 end
 if type(value)~='table'then return nil end
 M.ready=true
 return value
end
local function quarter(info)
 return info and (info.DistrictType=='DISTRICT_CSC_BAKERS_QUARTER'
  or info.DistrictType=='DISTRICT_CSC_TAILORS_QUARTER')
end
-- Material eligibility is a bounded six-neighbour fact scan. A native
-- empire-wide collection counter disagreed with an owned, visible, farmed Flax
-- beside a completed Quarter. Its cache/collection cause was not isolated.
-- Mirror facts on the source plot instead of creating a filtered requirement
-- instance for every empire plot. SQL still owns the private planning effect.
local BASE='CSC_RH_WORKSHOP_BASE_PRESENT'
local SPEC='CSC_RH_WORKSHOP_SPEC_PRESENT'
local mappings=nil
local function materials()
 if mappings then return mappings end
 mappings={base={},spec={}}
 local legal={};for row in GameInfo.Improvement_ValidResources()do legal[row.ResourceType]=true end
 for row in GameInfo.TypeTags()do
  local target=row.Tag=='CLASS_CSC_TAILORS_BASE'and mappings.base or(row.Tag=='CLASS_CSC_TAILORS_SPEC'and mappings.spec or nil)
  if target and legal[row.Type]and GameInfo.Resources[row.Type]then target[row.Type]=true end
 end
 return mappings
end
local function visible(player,res)
 if res.PrereqTech then local t=GameInfo.Technologies[res.PrereqTech];return t and player:GetTechs():HasTech(t.Index)or false end
 if res.PrereqCivic then local c=GameInfo.Civics[res.PrereqCivic];return c and player:GetCulture():HasCivic(c.Index)or false end
 return true
end
local function writeFact(plot,key,value)
 if plot:GetProperty(key)~=value then plot:SetProperty(key,value);M.writes=M.writes+1;M.supply_writes=M.supply_writes+1 end
end
local function supply(plot,eligible)
 local base,spec=false,false;M.supply_scans=M.supply_scans+1
 if eligible then
  local ok,b,s=pcall(function()
   local foundBase,foundSpec=false,false
   local pid=plot:GetOwner();local player=Players[pid];local map=materials()
   for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
    local res=GameInfo.Resources[near:GetResourceType()]
    if near:GetOwner()==pid and near:GetDistrictType()<0 and res and visible(player,res)then
     foundBase=foundBase or map.base[res.ResourceType]==true;foundSpec=foundSpec or map.spec[res.ResourceType]==true
    end
   end
   return foundBase,foundSpec
  end)
  if not ok then
   -- Unknown facts cannot retain a previously positive reward.
   writeFact(plot,BASE,0);writeFact(plot,SPEC,0);error(b)
  end
  base,spec=b,s
 end
 writeFact(plot,BASE,base and 1 or 0);writeFact(plot,SPEC,spec and 1 or 0)
end
local function stamp(plot,roles,info)
 local pid=plot:GetOwner();local player=Players[pid]
 local human=roles[tostring(pid)]==true or roles[pid]==true
 local value=player and player:IsMajor()and not human and 1 or 0
 if plot:GetProperty(PROPERTY)~=value then
  plot:SetProperty(PROPERTY,value);M.writes=M.writes+1
 end
 if info and info.DistrictType=='DISTRICT_CSC_TAILORS_QUARTER'then supply(plot,value==1)end
end
local function refresh(pid)
 if mode()~='RH'then return end
 local roles=humans();if not roles then return end -- Missing identity fails closed.
 local player=Players[pid];if not player then return end
 M.refreshes=M.refreshes+1
 for _,city in player:GetCities():Members()do
  local ds=city:GetDistricts()
  -- Gameplay API; the UI collection instead exposes Members().
  for i=0,ds:GetNumDistricts()-1 do
   local d=ds:GetDistrictByIndex(i)
   if d and quarter(GameInfo.Districts[d:GetType()])then
    local p=Map.GetPlot(d:GetX(),d:GetY());if p then stamp(p,roles,GameInfo.Districts[d:GetType()])end
   end
  end
 end
end
local function guard(fn,...)
 local ok,err=pcall(fn,...)
 if not ok then if #M.errors<20 then M.errors[#M.errors+1]=tostring(err)end;print('CSC RH customer role error',tostring(err))end
end
local function added(pid,did,cid,x,y,districtType)
 if mode()~='RH'or not quarter(GameInfo.Districts[districtType])then return end
 local roles=humans();if not roles then return end
 local plot=Map.GetPlot(x,y);if plot then stamp(plot,roles,GameInfo.Districts[districtType])end
end
Events.PlayerTurnActivated.Add(function(pid)guard(refresh,pid)end)
Events.DistrictAddedToMap.Add(function(...)guard(added,...)end)
-- Capture changes the source owner's configured role. Refresh that empire on
-- the established CityTransfered(newOwner, cityID, oldOwner) notification too;
-- activation remains the bounded reconciliation if collections are not ready.
if Events.CityTransfered then Events.CityTransfered.Add(function(pid)guard(refresh,pid)end)end
-- Fresh and loaded games may already contain Quarters. This is bounded by city
-- districts, not a map scan. If UI has not loaded yet, activation/placement will
-- reconcile them later. Never infer configured roles from current IsHuman.
for _,player in ipairs(PlayerManager.GetAliveMajors())do guard(refresh,player:GetID())end

-- Reconcile the same facts after ownership, resource, reveal and district
-- changes. No event signature is guessed: rare map changes rescan only majors'
-- existing city districts and six neighbours per Tailors source. Turn activation
-- provides a bounded backstop, and unchanged properties are never rewritten.
local function refreshAll()
 for _,player in ipairs(PlayerManager.GetAliveMajors())do refresh(player:GetID())end
end
for _,name in ipairs({'PlotOwnershipChanged','ResourceAddedToMap','ResourceRemovedFromMap','TechCompleted','CivicCompleted','DistrictAddedToMap','DistrictBuildProgressChanged','DistrictRemovedFromMap'})do
 if Events[name]then Events[name].Add(function()guard(refreshAll)end)end
end
if Events.PlayerTurnDeactivated then Events.PlayerTurnDeactivated.Add(function(pid)guard(refresh,pid)end)end


-- Native strategy callbacks: prefer a Quarter type only while a confirmed
-- assisted foundation survives in its original city and remains incomplete.
-- This reads a small journal, not city scopes/the map. Do not cache within a
-- turn: DistrictAdded fires before the host changes requested to confirmed.
-- Never use CanProduce here: same-type exclusion after placement is not proof
-- that continuing the already placed district is illegal.
local F={version=1,registered=0,calls=0,positive_calls=0,states={},transitions={},errors={}}
M.foundation_priority=F
local function backlog(pid,q)
 if mode()~='RH'then return false,0 end
 local roles=humans();if not roles then return false,0 end
 if roles[tostring(pid)]==true or roles[pid]==true then return false,0 end
 local player=Players[pid]
 if not player or not player:IsAlive()or not player:IsMajor()then return false,0 end
 local def=GameInfo.Districts['DISTRICT_CSC_'..q..'_QUARTER']
 if not def then return false,0 end
 local count=0
 for _,key in ipairs(Game:GetProperty('CSC_AI_ASSISTANCE_V1_FOUNDATION_INDEX')or{})do
  local owner,cid,kind,source=key:match('^(%d+):(%d+):([A-Z_]+):(%d+)$')
  if tonumber(owner)==pid and kind==q then
   local receipt=Game:GetProperty('CSC_AI_ASSISTANCE_V1_FOUNDATION_'..key)
   local index=tonumber(source)
   if type(receipt)=='table'and receipt.status=='confirmed'and receipt.source==index and receipt.quarter==q then
    local city=player:GetCities():FindID(tonumber(cid));local plot=Map.GetPlotByIndex(index)
    if city and city:GetOwner()==pid and plot and plot:GetOwner()==pid then
     local district=city:GetDistricts():GetDistrictAtLocation(plot:GetX(),plot:GetY())
     if district and district:GetType()==def.Index and not district:IsComplete()then count=count+1 end
    end
   end
  end
 end
 return count>0,count
end
local function evaluate(pid,q)
 F.calls=F.calls+1
 local ok,active,count=pcall(backlog,pid,q)
 if not ok then
  if #F.errors<20 then F.errors[#F.errors+1]=tostring(active)end
  print('CSC RH foundation priority error',tostring(active));active=false;count=0
 end
 if active then F.positive_calls=F.positive_calls+1 end
 local key=tostring(pid)..':'..q;local previous=F.states[key]
 if not previous or previous.active~=active or previous.count~=count then
  local record={turn=Game.GetCurrentGameTurn(),player=pid,quarter=q,active=active,count=count}
  F.states[key]=record
  if #F.transitions<1024 then F.transitions[#F.transitions+1]=record end
  print('CSC_RH_FOUNDATION_PRIORITY',record.turn,pid,q,tostring(active),count)
 end
 return active
end
-- Retain the role bridge's version-2 contract for existing readers. A separate
-- registration contract is mandatory in the v8 native preflight. Missing native
-- GameEvents therefore cannot silently pass a test run.
for _,q in ipairs({'BAKERS','TAILORS'})do
 local kind=q
 if GameEvents and GameEvents['CSC_RH_Finish_'..kind]then
  GameEvents['CSC_RH_Finish_'..kind].Add(function(pid,threshold)return evaluate(pid,kind)end)
  F.registered=F.registered+1
 end
end
