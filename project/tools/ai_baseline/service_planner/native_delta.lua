-- Cheap delta detection over a city's fixed geography, not a placement scan.
-- Event availability varies by context, so compare native facts as well as
-- periodically reconciling. Treasury is read afresh by the main collector.
CSC_SERVICE_DELTA={cache={},interval=25}
local D=CSC_SERVICE_DELTA
local function get(o,k,...)
 if not o or type(o[k])~='function'then return nil end
 local ok,v=pcall(o[k],o,...);if ok then return v end
end
function D.Geography(S,c,pid)
 S.geography_cache=S.geography_cache or {}
 local key=tostring(pid)..':'..tostring(c:GetID())..':'..tostring(c:GetX())..':'..tostring(c:GetY())
 local indices=S.geography_cache[key]
 if not indices then
  indices={}
  for idx=0,Map.GetPlotCount()-1 do local p=Map.GetPlotByIndex(idx)
   if Map.GetPlotDistance(c:GetX(),c:GetY(),p:GetX(),p:GetY())<=4 then indices[#indices+1]=idx end
  end
  S.geography_cache[key]=indices
 end
 return key,indices
end
function D.Fingerprint(S,c,p,pid)
 local key,indices=D.Geography(S,c,pid);local a={}
 local function add(v)a[#a+1]=tostring(v)end
 add(c:GetPopulation());add(p:GetEra())
 local q=c:GetBuildQueue();add(q:GetSize());add(get(q,'GetCurrentProductionTypeHash'))
 for _,name in ipairs({'BAKERS','TAILORS'})do local d=GameInfo.Districts['DISTRICT_CSC_'..name..'_QUARTER']
  add(q:CanProduce(d.Hash,false,true));add(q:HasBeenPlaced(d.Hash));add(c:GetDistricts():HasDistrict(d.Index))
 end
 -- A new unlock can reveal materials or enable a Quarter without border growth.
 for tech in GameInfo.Technologies()do add(p:GetTechs():HasTech(tech.Index))end
 for civic in GameInfo.Civics()do add(p:GetCulture():HasCivic(civic.Index))end
 for _,idx in ipairs(indices)do local plot=Map.GetPlotByIndex(idx);add(idx)
  local revealed=PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY());add(revealed)
  if revealed then
   add(plot:GetOwner());add(plot:GetResourceType());add(plot:GetImprovementType());add(plot:IsImprovementPillaged())
   add(plot:GetDistrictType());add(plot:GetFeatureType());add(get(plot,'GetTerrainType'));add(get(plot,'IsRiver'))
   if plot:GetOwner()==-1 and Map.GetPlotDistance(c:GetX(),c:GetY(),plot:GetX(),plot:GetY())<=3 then add(get(c:GetGold(),'GetPlotPurchaseCost',idx))end
   -- A foreign neighbor beyond the material ring can change frontier safety.
   for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do add(near:GetOwner())end
  end
 end
 return key,table.concat(a,'|'),#indices
end
function D.Decide(key,fingerprint,turn,force)
 local old=D.cache[key]
 if force then return true,'explicit-refresh'end
 if not old then return true,'new-scope'end
 if old.fingerprint~=fingerprint then return true,'native-delta'end
 if turn-old.turn>=D.interval then return true,'periodic-reconciliation'end
 return false,'unchanged'
end
function D.Remember(key,fingerprint,turn)D.cache[key]={fingerprint=fingerprint,turn=turn}end
