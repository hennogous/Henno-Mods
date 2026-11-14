-- DIAGNOSTIC ONLY: physical supplier on/off -> actual recipient building yield.
-- The shared controller loads this after the ordinary campaign is saved/closed,
-- in a separate disposable session. Nothing imports it from the shipping mod.
-- Explicit human-0 plots/buildings are fixture grants, never AI outcomes.
assert(CSC_MaterialCoverageFixture==nil,'Fixture already defined')
local F={}
CSC_MaterialCoverageFixture=F
local cases={
 farm={resource='RESOURCE_WHEAT',improvement='IMPROVEMENT_FARM',quarter='BAKERS'},
 maple={resource='RESOURCE_MAPLE',improvement='IMPROVEMENT_RES2_SAWMILL',quarter='BAKERS'},
 bamboo={resource='RESOURCE_BAMBOO',improvement='IMPROVEMENT_RES2_SAWMILL',quarter='TAILORS'},
}
local producers={{'BAKERS','BUILDING_CSC_BAKERS_WIND_MILL'},
                 {'BAKERS','BUILDING_CSC_BAKERS_CAFE'},
                 {'TAILORS','BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'}}
local function economyGuard(label)
 local c=F.config;local city=Players[0]:GetCities():FindID(c.city)
 local pop,gold,item=city:GetPopulation(),Players[0]:GetTreasury():GetGoldBalance(),city:GetBuildQueue():CurrentlyBuilding()
 assert(pop==F.before.population and gold==F.before.gold and item==F.before.item,'Fixture changed queue, population or Treasury')
 print('CSC_MATERIAL_COVERAGE_GUARD',label,c.turn,c.city,pop,gold,tostring(item))
end
local function cityAndPlot(cityID,index)
 local city=assert(Players[0]:GetCities():FindID(cityID),'Human fixture city missing')
 local plot=assert(Map.GetPlotByIndex(index))
 assert(plot:GetOwner()==-1 or plot:GetOwner()==0,'Fixture may not take foreign land')
 assert(not plot:IsWater(),'Land fixture required')
 assert(Map.GetPlotDistance(city:GetX(),city:GetY(),plot:GetX(),plot:GetY())<=3,'Fixture outside city range')
 return city,plot
end
local function own(city,plot)
 WorldBuilder.CityManager():SetPlotOwner(plot:GetX(),plot:GetY(),0,city:GetID())
 local assigned=assert(Cities.GetPlotPurchaseCity(plot))
 assert(plot:GetOwner()==0 and assigned:GetID()==city:GetID(),'Fixture ownership failed')
end
function F.Setup(config)
 assert(not F.config,'Fixture preparation is once only')
 assert(config.diagnosticOnly==true and config.player==0 and Players[0]:IsHuman())
 assert(Game.GetCurrentGameTurn()==config.turn and not AutoplayManager.IsActive())
 local adjacency=assert(CSC_Adjacency);adjacency.Initialize()
 local city=assert(Players[0]:GetCities():FindID(config.city))
 local item=city:GetBuildQueue():CurrentlyBuilding()
 assert(item==nil or not GameInfo.Districts[item],'District queued; select another fixture city')
 local tags={'CLASS_CSC_BAKERS_BASE','CLASS_CSC_BAKERS_SPEC','CLASS_CSC_TAILORS_BASE'}
 local expected={farm={true,false,false},maple={false,true,false},bamboo={false,false,true}}
 for name,case in pairs(cases)do
  assert(GameInfo.Resources[case.resource] and GameInfo.Improvements[case.improvement])
  for i,tag in ipairs(tags)do
   assert((not not adjacency.HasTag(tag,case.resource))==expected[name][i],'Loaded material classes changed; review fixture')
  end
  local valid=false
  for row in GameInfo.Improvement_ValidResources()do
   valid=valid or row.ResourceType==case.resource and row.ImprovementType==case.improvement
  end
  assert(valid,'Fixture improvement/resource mapping absent')
 end
 assert(GameInfo.Resources.RESOURCE_STONE and GameInfo.Terrains.TERRAIN_GRASS and GameInfo.Features.FEATURE_FOREST)
 for _,tag in ipairs(tags)do assert(not CSC_Adjacency.HasTag(tag,'RESOURCE_STONE'),'Negative control is a mapped material')end
 for _,entry in ipairs(producers)do assert(GameInfo.Buildings[entry[2]])end
 for _,family in ipairs({'BAKERS','TAILORS'})do assert(GameInfo.Districts['DISTRICT_CSC_'..family..'_QUARTER'])end
 local seen={}
 -- Check every declared footprint before changing any. Existing districts,
 -- improvements and natural Wonders are excluded rather than erased.
 for _,index in pairs(config.quarters)do
  assert(not seen[index]);seen[index]=true
  local _,plot=cityAndPlot(config.city,index)
  assert(plot:GetDistrictType()==-1 and plot:GetImprovementType()==-1)
  local feature=GameInfo.Features[plot:GetFeatureType()]
  assert(not feature or not(feature.NaturalWonder==true or feature.NaturalWonder==1))
 end
 for name,case in pairs(cases)do
  local index=assert(config.materials[name]);assert(not seen[index]);seen[index]=true
  local _,plot=cityAndPlot(config.city,index)
  assert(plot:GetDistrictType()==-1 and plot:GetImprovementType()==-1)
  local feature=GameInfo.Features[plot:GetFeatureType()]
  assert(not feature or not(feature.NaturalWonder==true or feature.NaturalWonder==1))
  local q=assert(Map.GetPlotByIndex(config.quarters[case.quarter]))
  assert(Map.GetPlotDistance(plot:GetX(),plot:GetY(),q:GetX(),q:GetY())==1,'Supplier must border its Quarter')
  assert(GameInfo.Resources[case.resource] and GameInfo.Improvements[case.improvement])
 end
 for _,family in ipairs({'BAKERS','TAILORS'})do
  local definition=assert(GameInfo.Districts['DISTRICT_CSC_'..family..'_QUARTER'])
  local manager=city:GetDistricts()
  for i=0,manager:GetNumDistricts()-1 do
   assert(manager:GetDistrictByIndex(i):GetType()~=definition.Index,'Choose a city without either Quarter')
  end
 end
 F.config=config
 F.before={population=city:GetPopulation(),gold=Players[0]:GetTreasury():GetGoldBalance(),item=item}
 economyGuard('before')
 for _,family in ipairs({'BAKERS','TAILORS'})do
  local index=config.quarters[family];local plot=Map.GetPlotByIndex(index)
  own(city,plot);ResourceBuilder.SetResourceType(plot,-1)
  TerrainBuilder.SetFeatureType(plot,-1)
  TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS.Index)
  local definition=GameInfo.Districts['DISTRICT_CSC_'..family..'_QUARTER']
  city:GetBuildQueue():CreateIncompleteDistrict(definition.Index,index,100)
  assert(plot:GetDistrictType()==definition.Index,'Fixture Quarter creation failed')
  local complete=false;local manager=city:GetDistricts()
  for i=0,manager:GetNumDistricts()-1 do
   local d=manager:GetDistrictByIndex(i)
   if d:GetX()==plot:GetX() and d:GetY()==plot:GetY()then complete=d:IsComplete() and not d:IsPillaged()end
  end
  assert(complete,'Fixture Quarter is not functioning')
 end
 for _,entry in ipairs(producers)do
  local id=assert(GameInfo.Buildings[entry[2]]).Index
  city:GetBuildQueue():CreateBuilding(id,config.quarters[entry[1]])
  local buildings=city:GetBuildings()
  assert(buildings:HasBuilding(id) and not buildings:IsPillaged(id)
   and buildings:GetBuildingLocation(id)==config.quarters[entry[1]],'Fixture producer placement failed')
 end
 for name,case in pairs(cases)do
  local plot=Map.GetPlotByIndex(config.materials[name]);own(city,plot)
  ResourceBuilder.SetResourceType(plot,-1);TerrainBuilder.SetFeatureType(plot,-1)
  TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS.Index)
  if name~='farm'then TerrainBuilder.SetFeatureType(plot,GameInfo.Features.FEATURE_FOREST.Index)end
  ResourceBuilder.SetResourceType(plot,GameInfo.Resources[case.resource].Index,1)
 end
 F.active='none'
 economyGuard('granted')
 print('CSC_MATERIAL_COVERAGE_SETUP',config.turn,config.city)
end
function F.Activate(name)
 assert(F.config and Game.GetCurrentGameTurn()==F.config.turn)
 assert(name=='none' or name=='unmapped' or cases[name],'Unknown fixture phase')
 for key in pairs(cases)do
  local plot=Map.GetPlotByIndex(F.config.materials[key])
  ImprovementBuilder.SetImprovementType(plot,-1,0)
  ResourceBuilder.SetResourceType(plot,GameInfo.Resources[cases[key].resource].Index,1)
 end
 if name~='none'then
  local key=name=='unmapped' and 'maple' or name
  local plot=Map.GetPlotByIndex(F.config.materials[key]);local case=cases[key]
  -- Stone on the declared Sawmill plot is a negative material-tag test. This
  -- explicit diagnostic grant tests modifier gating, not Builder legality.
  if name=='unmapped'then ResourceBuilder.SetResourceType(plot,GameInfo.Resources.RESOURCE_STONE.Index,1)end
  ImprovementBuilder.SetImprovementType(plot,GameInfo.Improvements[case.improvement].Index,0)
  assert(plot:GetImprovementType()==GameInfo.Improvements[case.improvement].Index)
 end
 F.active=name
 F.Observe()
end
function F.Observe()
 assert(F.config and Game.GetCurrentGameTurn()==F.config.turn)
 economyGuard(F.active)
 for key,case in pairs(cases)do
  local plot=Map.GetPlotByIndex(F.config.materials[key])
  local active=key==F.active or F.active=='unmapped' and key=='maple'
  local resource=F.active=='unmapped' and key=='maple' and 'RESOURCE_STONE' or case.resource
  assert(plot:GetOwner()==0 and plot:GetResourceType()==GameInfo.Resources[resource].Index)
  assert(plot:GetImprovementType()==(active and GameInfo.Improvements[case.improvement].Index or -1))
  assert(not active or not plot:IsImprovementPillaged(),'Supplier became pillaged during observation')
  print('CSC_MATERIAL_COVERAGE_WORLD',F.config.turn,F.active,key,plot:GetIndex(),plot:GetOwner(),plot:GetResourceType(),plot:GetImprovementType(),plot:IsImprovementPillaged())
 end
end
