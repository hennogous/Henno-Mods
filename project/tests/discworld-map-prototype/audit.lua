-- Read-only census. The exterior count is checked against Euclidean geometry,
-- not inferred from the custom feature alone, so missing/stray flags are caught.
local w,h=Map.GetGridSize();assert(w==48 and h==56);
assert(not Map.IsWrapX() and not Map.IsWrapY());
local f=GameInfo.Features.FEATURE_DISC_VOID.Index;
local outside,inside,land,bad,resources,units=0,0,0,0,0,0;
for i=0,Map.GetPlotCount()-1 do
 local p=Map.GetPlotByIndex(i);local x,y=p:GetX(),p:GetY();
 local a=x+(y%2)*0.5-(w-0.5)/2;local b=(y-(h-1)/2)*math.sqrt(3)/2;
 -- Match the generator's sqrt comparison at the two floating-point rim ties.
 local out=math.sqrt(a*a+b*b)>=21.5;
 if out then
  outside=outside+1;
  if p:GetFeatureType()~=f or not p:IsImpassable() then bad=bad+1;end
  if p:GetResourceType()~=-1 then resources=resources+1;end
  units=units+p:GetUnitCount();
 else
  inside=inside+1;if not p:IsWater() then land=land+1;end
  if p:GetFeatureType()==f then bad=bad+1;end
 end
end
print('DISC_AUDIT',Game.GetCurrentGameTurn(),w,h,outside,inside,land,bad,resources,units);
assert(bad==0 and resources==0 and units==0);
for _,p in ipairs(PlayerManager.GetAliveMajors()) do
 local id=p:GetID();
 print('DISC_MAJOR',id,p:GetCities():GetCount(),p:GetUnits():GetCount());
 for _,u in p:GetUnits():Members() do assert(Map.GetPlot(u:GetX(),u:GetY()):GetFeatureType()~=f);end
end
