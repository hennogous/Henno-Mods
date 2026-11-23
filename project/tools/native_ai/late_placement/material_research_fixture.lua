-- Diagnostic only. Give a closed Fractal turn-100 replay one working Bakers
-- buyer and one adjacent supplier that needs a genuine, missing technology.
-- Player 4 has one city at this checkpoint and it already has an incomplete
-- Bakers Quarter. Give both arms the same small fixture city, Quarter and
-- buyer. The control omits only this research offer from CE staging.
local playerID=4
local player=assert(Players[playerID])
local tech=assert(GameInfo.Technologies.TECH_IRRIGATION)
local techs=player:GetTechs()
local quarter=assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
local mill=assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL)
local bananas=assert(GameInfo.Resources.RESOURCE_BANANAS)
local plantation=assert(GameInfo.Improvements.IMPROVEMENT_PLANTATION)
assert(Game.GetCurrentGameTurn()==100 and not AutoplayManager.IsActive())
assert(not player:IsHuman() and not techs:HasTech(tech.Index) and techs:GetResearchingTech()~=tech.Index)
assert(plantation.PrereqTech==tech.TechnologyType and techs:HasTech(GameInfo.Technologies[mill.PrereqTech].Index))
assert(CSC_Adjacency.HasTag('CLASS_CSC_BAKERS_BASE',bananas.ResourceType))

local function emptyLand(plot)
    return plot:GetOwner()==-1 and not plot:IsWater() and not plot:IsImpassable()
        and plot:GetDistrictType()==-1 and plot:GetResourceType()==-1 and plot:GetImprovementType()==-1
        and plot:GetFeatureType()==-1
end

local function distance(a,b)
    return Map.GetPlotDistance(a:GetX(),a:GetY(),b:GetX(),b:GetY())
end

local function supplierFree(site)
    for _,p in ipairs(Map.GetAdjacentPlots(site:GetX(),site:GetY()))do
        local r=GameInfo.Resources[p:GetResourceType()]
        if r and CSC_Adjacency.HasTag('CLASS_CSC_BAKERS_BASE',r.ResourceType) then return false end
    end
    return true
end

local cities={}
for i=0,Map.GetPlotCount()-1 do
    local p=Map.GetPlotByIndex(i)
    if p:IsCity() then cities[#cities+1]=p end
end

local function fixtureRing(center)
    for _,existing in ipairs(cities)do if distance(center,existing)<4 then return end end
    local ring=Map.GetAdjacentPlots(center:GetX(),center:GetY())
    for _,site in ipairs(ring)do
        if emptyLand(site) and not site:IsRiver() and supplierFree(site) then
            for _,p in ipairs(ring)do
                if p~=site and emptyLand(p) and distance(site,p)==1 then return site,p end
            end
        end
    end
end

local capital=assert(player:GetCities():GetCapitalCity())
local origin=assert(Map.GetPlot(capital:GetX(),capital:GetY()))
local center,site,plot
local near=math.huge
for i=0,Map.GetPlotCount()-1 do
    local p=Map.GetPlotByIndex(i)
    local range=distance(origin,p)
    if range>=4 and range<near and emptyLand(p) then
        local q,m=fixtureRing(p)
        if q then center,site,plot,near=p,q,m,range end
    end
end
assert(center,'No unowned research fixture neighbourhood')
local city=assert(player:GetCities():Create(center:GetX(),center:GetY()))
assert(site:GetOwner()==playerID and plot:GetOwner()==playerID)
TerrainBuilder.SetTerrainType(plot,assert(GameInfo.Terrains.TERRAIN_PLAINS).Index)
TerrainBuilder.SetFeatureType(plot,assert(GameInfo.Features.FEATURE_JUNGLE).Index)
ResourceBuilder.SetResourceType(plot,bananas.Index,1)
assert(plot:GetResourceType()==bananas.Index and ImprovementBuilder.CanHaveImprovement(plot,plantation.Index,playerID),
    'Bananas must accept the native Plantation location check before Irrigation')
local queue=city:GetBuildQueue()
queue:CreateIncompleteDistrict(quarter.Index,site:GetIndex(),100)
local district=assert(city:GetDistricts():GetDistrictAtLocation(site:GetX(),site:GetY()))
assert(district:GetType()==quarter.Index and district:IsComplete() and not district:IsPillaged())
queue:CreateBuilding(mill.Index,site:GetIndex())
local buildings=city:GetBuildings()
assert(buildings:HasBuilding(mill.Index) and buildings:GetBuildingLocation(mill.Index)==site:GetIndex())

local chain
for _,row in ipairs(CSC_AI_QuarterPlacement.ReadChains(player))do
    if row.plot:GetIndex()==site:GetIndex() then chain=row;break end
end
assert(chain and chain.ready and #chain.supply.base==1 and chain.supply.base[1].plot==plot:GetIndex()
    and not chain.supply.base[1].ready and not chain.supply.base[1].working)

if CSC_MATERIAL_RESEARCH_CONTROL then
    local publish=assert(CE_AIMaterialResearchBid)
    CE_AIMaterialResearchBid=function(pid,kind,topic,delta)
        if pid==playerID and kind==0 and topic==tech.Index then
            print('CSC_MATERIAL_RESEARCH_FIXTURE_OMITTED',Game.GetCurrentGameTurn(),pid,kind,topic,delta)
            return 1
        end
        return publish(pid,kind,topic,delta)
    end
end

function CSC_MaterialFixtureRead(label)
    print(string.format('%s={"turn":%d,"player":%d,"city":%d,"quarter":%d,"plot":%d,"topic":%d,"active":%d,"owned":%s,"working":%s}',
        label,Game.GetCurrentGameTurn(),playerID,city:GetID(),site:GetIndex(),plot:GetIndex(),tech.Index,
        techs:GetResearchingTech(),tostring(techs:HasTech(tech.Index)),
        tostring(plot:GetImprovementType()==plantation.Index and not plot:IsImprovementPillaged())))
end
CSC_MaterialFixtureRead('CSC_MATERIAL_FIXTURE_START')
