-- Terrain-preserving fixture around a normally founded capital.
assert(Players[0]:GetCities():GetCount()==1,'one normally founded capital required');
assert(not Game:GetProperty('CSC_TAILORS_QA'),'use a new, unmodified disposable fixture');
local city=nil;for _,c in Players[0]:GetCities():Members() do city=c;break;end;
assert(city);
TQA.Tech('TECH_CONSTRUCTION',true);TQA.Civic('CIVIC_CRAFTSMANSHIP',true);TQA.Civic('CIVIC_HUMANISM',true);
local request={Player=0,District='DISTRICT_CSC_TAILORS_QUARTER',Slots={
 {Name='MP1',Resource='RESOURCE_COTTON',Improvements={'IMPROVEMENT_PLANTATION'}},
 {Name='MP2',Resource='RESOURCE_DYES',Improvements={'IMPROVEMENT_PLANTATION'}}}};
local plan=QAPlacement.Find(request);
assert(#plan.Candidates>0,'QA_PLACEMENT_BLOCKED: no legal Cotton/Dyes layout on this map');
local candidate=plan.Candidates[1];assert(QAPlacement.Recheck(request,candidate));
TQA.Store({PlacementVersion=QAPlacement.Version,Cities={A=city:GetID()},Sites={},SiteCities={},MaterialPlan=candidate});
local q=Map.GetPlotByIndex(candidate.Quarter.Plot);
TQA.District('QA','A',request.District,q:GetX(),q:GetY());
for _,material in ipairs(candidate.Materials) do
 local p=Map.GetPlotByIndex(material.Plot);TQA.ResourceSite(material.Name,'A',p);
 TQA.Resource(material.Name,material.Resource,material.Improvement);
end;
Players[0]:GetTreasury():ChangeGoldBalance(100000);CSC_RefreshAdjacencies();
print('MATERIAL_CAPITAL_FIXTURE',city:GetX(),city:GetY(),q:GetX(),q:GetY());
