-- Disposable native fixture; pristine start is reloaded before observations.
assert(Game.GetCurrentGameTurn()==1)
CSC_QR_FIXTURE={cases={}}
local occupied={}
for k,q in ipairs({'BAKERS','TAILORS'}) do
 local pid=k;local player=Players[pid];assert(not player:IsHuman())
 for t in GameInfo.Technologies() do player:GetTechs():SetTech(t.Index,true) end
 local center
 for i=0,Map.GetPlotCount()-1 do
  local p=Map.GetPlotByIndex(i)
  if p:GetOwner()==-1 and not p:IsWater() and not p:IsImpassable() and p:GetY()>3 and p:GetY()<Map.GetGridSize()-4 then
   local good=true
   for _,c in ipairs(occupied) do if Map.GetPlotDistance(p:GetX(),p:GetY(),c:GetX(),c:GetY())<9 then good=false end end
   for d=0,5 do local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),d);if not n or n:IsWater() or n:IsImpassable() then good=false end end
   if good then center=p;break end
  end
 end
 assert(center,'No fixture site');occupied[#occupied+1]=center
 TerrainBuilder.SetFeatureType(center,-1);ResourceBuilder.SetResourceType(center,-1)
 local city=player:GetCities():Create(center:GetX(),center:GetY());assert(city)
 local qp=Map.GetAdjacentPlot(center:GetX(),center:GetY(),0)
 local mats={}
 for d=0,5 do local n=Map.GetAdjacentPlot(qp:GetX(),qp:GetY(),d);if n and n:GetIndex()~=center:GetIndex() and Map.GetPlotDistance(n:GetX(),n:GetY(),center:GetX(),center:GetY())==1 then mats[#mats+1]=n end end
 local p=mats[1];local wrong=mats[2];assert(p and wrong);local far;for d=0,5 do local n=Map.GetAdjacentPlot(center:GetX(),center:GetY(),d);if Map.GetPlotDistance(n:GetX(),n:GetY(),qp:GetX(),qp:GetY())==2 then far=n;break end end;assert(far)
 for _,x in ipairs({qp,p,wrong,far}) do assert(x:GetOwner()==pid,'Fixture target not natively owned');TerrainBuilder.SetFeatureType(x,-1);ResourceBuilder.SetResourceType(x,-1) end
 ResourceBuilder.SetResourceType(p,GameInfo.Resources.RESOURCE_CSC_FLAX.Index,1)
 ResourceBuilder.SetResourceType(far,GameInfo.Resources.RESOURCE_CSC_FLAX.Index,1)
 ResourceBuilder.SetResourceType(wrong,GameInfo.Resources.RESOURCE_STONE.Index,1)
 city:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts['DISTRICT_CSC_'..q..'_QUARTER'].Index,qp:GetIndex(),100)
 CSC_QR_FIXTURE.cases[#CSC_QR_FIXTURE.cases+1]={player=pid,city=city:GetID(),quarter=qp:GetIndex(),material=p:GetIndex(),wrong=wrong:GetIndex(),far=far:GetIndex()}
end
Game:SetProperty('CSC_QR_FIXTURE',CSC_QR_FIXTURE)
print('CSC_QR_FIXTURE_READY')
