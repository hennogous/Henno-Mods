-- Diagnostic-only temporary ship: compare an ordinary ocean step with the Rim.
assert(Game:GetProperty('DISC_NAVAL_FIXTURE')==nil,'Fixture already exists');
local f=GameInfo.Features.FEATURE_DISC_VOID.Index;
for i=0,Map.GetPlotCount()-1 do
 local p=Map.GetPlotByIndex(i);
 if p:IsWater() and not p:IsImpassable() and p:GetUnitCount()==0 then
  local inside,outside;
  for d=0,5 do local q=Map.GetAdjacentPlot(p:GetX(),p:GetY(),d);
   if q and q:IsWater() then
    if q:GetFeatureType()==f then outside=q:GetIndex();
    elseif not q:IsImpassable() and q:GetUnitCount()==0 then inside=q:GetIndex();end
   end
  end
  if inside and outside then
   local u=UnitManager.InitUnit(0,'UNIT_DESTROYER',p:GetX(),p:GetY());assert(u);
   -- Even modern ships need the owner's ocean-access technology in this test.
   -- Callers must restore the prior Cartography flag when removing the fixture.
   local techs=Players[0]:GetTechs();
   Game:SetProperty('DISC_TEST_HAD_CARTOGRAPHY',techs:HasTech(GameInfo.Technologies.TECH_CARTOGRAPHY.Index));
   techs:SetTech(GameInfo.Technologies.TECH_CARTOGRAPHY.Index,true);
   UnitManager.PlaceUnit(u,p:GetX(),p:GetY());
   assert(u:GetX()==p:GetX() and u:GetY()==p:GetY());
   Game:SetProperty('DISC_NAVAL_FIXTURE',{u:GetID(),i,inside,outside});
   print('DISC_NAVAL_CREATED',u:GetID(),i,inside,outside);return;
  end
 end
end
error('No boundary test site');
