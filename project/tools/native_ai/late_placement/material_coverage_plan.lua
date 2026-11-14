-- Read-only search for the separate payout fixture. No cities or plots change.
-- Use a human city without either Quarter and five distinct vacant land plots.
assert(Players[0]:IsHuman() and not AutoplayManager.IsActive())
local turn=assert(CSC_MATERIAL_COVERAGE_TURN)
assert(Game.GetCurrentGameTurn()==turn)
local quarterTypes={}
for _,family in ipairs({'BAKERS','TAILORS'})do
 quarterTypes[GameInfo.Districts['DISTRICT_CSC_'..family..'_QUARTER'].Index]=true
end
local function adjacent(a,b)return Map.GetPlotDistance(a:GetX(),a:GetY(),b:GetX(),b:GetY())==1 end
for _,city in Players[0]:GetCities():Members()do
 local hasQuarter=false;local manager=city:GetDistricts()
 for i=0,manager:GetNumDistricts()-1 do hasQuarter=hasQuarter or quarterTypes[manager:GetDistrictByIndex(i):GetType()]end
 local item=city:GetBuildQueue():CurrentlyBuilding()
 -- Completed district creation can PopFront an unrelated queued district.
 -- Pick another city; the fixture never repairs or clears a production queue.
 if not hasQuarter and(item==nil or not GameInfo.Districts[item])then
  local pool={}
  for _,plot in ipairs(CSC_Adjacency.PlotsInBand(Map.GetPlot(city:GetX(),city:GetY()),1,3))do
   local owner=plot:GetOwner();local assigned=owner==0 and Cities.GetPlotPurchaseCity(plot)
   local feature=GameInfo.Features[plot:GetFeatureType()]
   local wonder=feature and(feature.NaturalWonder==true or feature.NaturalWonder==1)
   if not plot:IsWater() and not wonder and plot:GetDistrictType()==-1 and plot:GetImprovementType()==-1
    and(owner==-1 or assigned and assigned:GetID()==city:GetID())then pool[#pool+1]=plot end
  end
  table.sort(pool,function(a,b)return a:GetIndex()<b:GetIndex()end)
  for _,bakers in ipairs(pool)do for _,tailors in ipairs(pool)do if bakers~=tailors then
   for _,bamboo in ipairs(pool)do if bamboo~=bakers and bamboo~=tailors and adjacent(bamboo,tailors)then
    local suppliers={}
    for _,plot in ipairs(pool)do
     if plot~=bakers and plot~=tailors and plot~=bamboo and adjacent(plot,bakers)then suppliers[#suppliers+1]=plot end
    end
    if #suppliers>=2 then
     print('CSC_MATERIAL_COVERAGE_PLAN='..string.format(
      '{"diagnosticOnly":true,"player":0,"turn":%d,"city":%d,"quarters":{"BAKERS":%d,"TAILORS":%d},"materials":{"farm":%d,"maple":%d,"bamboo":%d}}',
      turn,city:GetID(),bakers:GetIndex(),tailors:GetIndex(),suppliers[1]:GetIndex(),suppliers[2]:GetIndex(),bamboo:GetIndex()))
     return
    end
   end end
  end end end
 end
end
error('No human city has the five empty fixture footprints; inspect before preparing another world')
