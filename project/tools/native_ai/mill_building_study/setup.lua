-- Controlled fixture preparation, not an AI treatment or a campaign script.
-- The host issues this exactly once in a fresh CSC-only world. Human cities
-- exercise actual Mill yields; two AI cities supply ordinary forecast calls.
assert(Game.GetCurrentGameTurn()==1,'Fresh turn-1 disposable world required')
assert(Players[0]:IsHuman(),'Original human must be player zero')
assert(not CSC_MILL_STUDY_SETUP_DONE,'Never replay fixture preparation')
assert(type(CSC_MILL_STUDY_TOKEN)=='string' and #CSC_MILL_STUDY_TOKEN>8
    and #CSC_MILL_STUDY_TOKEN<=80 and CSC_MILL_STUDY_TOKEN:match('^[%w_-]+$'),'Explicit safe study token required')
CSC_MILL_STUDY_SETUP_DONE=CSC_MILL_STUDY_TOKEN
local A=assert(CSC_Adjacency,'Use the installed CSC_AdjacencyGameplay context')
assert(UnitManager and type(UnitManager.Kill)=='function','Native unit removal API required')
assert(PlayerManager and type(PlayerManager.GetAlive)=='function','Native alive-player enumeration required')
local function capital(pid)
    local p=assert(Players[pid]);local city=nil
    for _,c in p:GetCities():Members() do assert(not city,'One starting city at most');city=c end
    if not city then
        local settler=nil
        for _,u in p:GetUnits():Members() do
            if u:GetType()==GameInfo.Units.UNIT_SETTLER.Index then assert(not settler);settler=u end
        end
        assert(settler,'Starting Settler required')
        city=assert(p:GetCities():Create(settler:GetX(),settler:GetY()),'City creation failed')
        -- Consume the founding Settler, as ordinary founding would do. Leaving
        -- it alive would give this diagnostic world an extra expansion unit.
        -- This exact two-argument call is used by shipped Debug/Unit.ltp.
        UnitManager.Kill(settler,false)
    end
    return city
end
local cities={};for pid=0,2 do cities[pid]=capital(pid) end
local function clearLand(plot)
    assert(plot:GetDistrictType()==-1,'Never clear an existing district')
    ResourceBuilder.SetResourceType(plot,-1)
    if plot:GetFeatureType()>=0 then TerrainBuilder.SetFeatureType(plot,-1) end
    TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS.Index)
end
local function own(plot,pid,city)
    assert(plot:GetOwner()==-1 or plot:GetOwner()==pid,'Do not steal another player plot')
    WorldBuilder.CityManager():SetPlotOwner(plot:GetX(),plot:GetY(),pid,city:GetID())
    assert(plot:GetOwner()==pid,'Ownership write did not take effect')
end
local function humanNeighborhood(plot)
    -- The Mill fixture later normalizes this plot and its immediate ring.
    -- Reject foreign land, improvements (including goody huts) and neighboring
    -- districts before choosing it; never alter those as incidental cleanup.
    if plot:IsWater() or plot:GetDistrictType()~=-1 or plot:GetImprovementType()~=-1
        or (plot:GetOwner()~=-1 and plot:GetOwner()~=0) then return false end
    for direction=0,5 do
        local neighbor=Map.GetAdjacentPlot(plot:GetX(),plot:GetY(),direction)
        if not neighbor or (neighbor:GetOwner()~=-1 and neighbor:GetOwner()~=0)
            or neighbor:GetImprovementType()~=-1
            or (neighbor:GetDistrictType()~=-1 and not neighbor:IsCity()) then return false end
    end
    return true
end
local function firstQuarterSite(city,pid)
    for _,plot in ipairs(Map.GetAdjacentPlots(city:GetX(),city:GetY())) do
        if not plot:IsWater() and plot:GetDistrictType()==-1 and plot:GetImprovementType()==-1
            and (plot:GetOwner()==-1 or plot:GetOwner()==pid) and (pid~=0 or humanNeighborhood(plot)) then
            own(plot,pid,city);clearLand(plot);return plot
        end
    end
    error('No empty land adjacent to fixture city')
end
local localPlot=firstQuarterSite(cities[0],0)
local remotePlan=nil
local center=Map.GetPlot(cities[0]:GetX(),cities[0]:GetY())
for _,plot in ipairs(A.PlotsInBand(center,8,10)) do
    local separated=true
    -- AI fixture cities later claim radius three. A distance-six center leaves
    -- the human Quarter and its radius-one ring outside that claimed radius,
    -- even when both are placed toward the AI. Include every existing city,
    -- including city-states, not only the three majors created above. GetAlive
    -- is used by the shipped Automation_DailySmokeTest and StandardTests.
    for _,player in ipairs(PlayerManager.GetAlive()) do
        for _,city in player:GetCities():Members() do
            if Map.GetPlotDistance(plot:GetX(),plot:GetY(),city:GetX(),city:GetY())<6 then separated=false end
        end
    end
    if separated and not plot:IsWater() and plot:GetOwner()==-1 and plot:GetDistrictType()==-1 and plot:GetImprovementType()==-1 then
        for _,quarter in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY())) do
            if humanNeighborhood(quarter) and Map.GetPlotDistance(quarter:GetX(),quarter:GetY(),localPlot:GetX(),localPlot:GetY())>=6 then
                remotePlan={center=plot,quarter=quarter};break
            end
        end
        if remotePlan then break end
    end
end
assert(remotePlan,'No separate human city with a clean Quarter neighborhood')
-- Selection is complete before the first remote-city mutation. If native city
-- creation rejects this declared site, preserve that failure; do not retry a
-- second site after partially changing the world.
clearLand(remotePlan.center)
local remote=assert(Players[0]:GetCities():Create(remotePlan.center:GetX(),remotePlan.center:GetY()),'Remote city creation failed')
local remotePlot=remotePlan.quarter
assert(humanNeighborhood(remotePlot),'Remote Quarter neighborhood changed during founding')
own(remotePlot,0,remote);clearLand(remotePlot)
local config={schema=1,player=0,localCity=cities[0]:GetID(),localPlot=localPlot:GetIndex(),
    remoteCity=remote:GetID(),remotePlot=remotePlot:GetIndex(),token=CSC_MILL_STUDY_TOKEN}

-- These research unlocks deliberately make the seven ordinary CSC building
-- definitions visible to the native forecast. They are controlled fixture
-- inputs, not a claim about Ancient-era availability or ordinary AI research.
local techs={'TECH_IRRIGATION','TECH_ENGINEERING','TECH_MACHINERY','TECH_CONSTRUCTION'}
local civics={'CIVIC_GUILDS','CIVIC_HUMANISM','CIVIC_FEUDALISM','CIVIC_MEDIEVAL_FAIRES',
    'CIVIC_URBANIZATION','CIVIC_NAVAL_TRADITION','CIVIC_DIVINE_RIGHT','CIVIC_OPERA_BALLET'}
local targets={};local rich={districts={},resources={}}
for pid=1,2 do
    local city=cities[pid];local player=Players[pid]
    city:ChangePopulation(15-city:GetPopulation())
    for _,name in ipairs(techs) do player:GetTechs():SetTech(assert(GameInfo.Technologies[name]).Index,true) end
    for _,name in ipairs(civics) do player:GetCulture():SetCivic(assert(GameInfo.Civics[name]).Index,true) end
    for _,plot in ipairs(A.PlotsInBand(Map.GetPlot(city:GetX(),city:GetY()),1,3)) do
        if not plot:IsWater() and plot:GetDistrictType()==-1 and (plot:GetOwner()==-1 or plot:GetOwner()==pid) then
            own(plot,pid,city);clearLand(plot)
            -- Both AI cities need ordinary workable Production to expose the
            -- later building forecasts within the native planning horizon.
            -- Otherwise a high-population grass-only fixture can leave Café
            -- and Fashion House invalid merely because construction takes too
            -- long. Candidate and material plots are cleared separately below.
            TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS_HILLS.Index)
        end
    end
    local candidate=firstQuarterSite(city,pid)
    targets[#targets+1]={player=pid,city=city:GetID(),plot=candidate:GetIndex()}
end
local city=cities[1];local candidate=Map.GetPlotByIndex(targets[1].plot)
local used={[candidate:GetIndex()]=true}
local function vacant(water)
    -- Prefer the candidate's immediate ring. Continue to other city tiles when
    -- the real map cannot fit every material and customer around one site.
    local pool={};local seen={}
    for _,plot in ipairs(Map.GetAdjacentPlots(candidate:GetX(),candidate:GetY())) do pool[#pool+1]=plot;seen[plot:GetIndex()]=true end
    for _,plot in ipairs(A.PlotsInBand(Map.GetPlot(city:GetX(),city:GetY()),1,3)) do
        if not seen[plot:GetIndex()] then pool[#pool+1]=plot end
    end
    for _,plot in ipairs(pool) do
        if not used[plot:GetIndex()] and plot:GetDistrictType()==-1 and plot:GetImprovementType()==-1 and plot:IsWater()==water
            and (plot:GetOwner()==-1 or plot:GetOwner()==1) then
            own(plot,1,city);used[plot:GetIndex()]=true;return plot
        end
    end
end
for _,item in ipairs({{'RESOURCE_WHEAT','IMPROVEMENT_FARM'}, {'RESOURCE_COCOA','IMPROVEMENT_PLANTATION'},
    {'RESOURCE_COTTON','IMPROVEMENT_PLANTATION'}, {'RESOURCE_DYES','IMPROVEMENT_PLANTATION'}}) do
    local plot=assert(vacant(false),'Missing material fixture plot');clearLand(plot)
    ResourceBuilder.SetResourceType(plot,assert(GameInfo.Resources[item[1]]).Index,1)
    ImprovementBuilder.SetImprovementType(plot,assert(GameInfo.Improvements[item[2]]).Index,1)
    assert(plot:GetResourceType()==GameInfo.Resources[item[1]].Index and plot:GetImprovementType()==GameInfo.Improvements[item[2]].Index)
    rich.resources[#rich.resources+1]={plot=plot:GetIndex(),resource=item[1],improvement=item[2]}
end
for _,item in ipairs({{'DISTRICT_COMMERCIAL_HUB','BUILDING_MARKET'},
    {'DISTRICT_ENTERTAINMENT_COMPLEX','BUILDING_ZOO'}, {'DISTRICT_HOLY_SITE','BUILDING_TEMPLE'},
    {'DISTRICT_THEATER','BUILDING_AMPHITHEATER'}, {'DISTRICT_HARBOR','BUILDING_LIGHTHOUSE'}}) do
    local water=item[1]=='DISTRICT_HARBOR';local plot=vacant(water)
    if plot then
        if not water then clearLand(plot) else ResourceBuilder.SetResourceType(plot,-1) end
        local district=assert(GameInfo.Districts[item[1]])
        city:GetBuildQueue():CreateIncompleteDistrict(district.Index,plot:GetIndex(),100)
        assert(plot:GetDistrictType()==district.Index,'Customer district creation failed')
        city:GetBuildQueue():CreateBuilding(assert(GameInfo.Buildings[item[2]]).Index,plot:GetIndex())
        assert(city:GetBuildings():HasBuilding(GameInfo.Buildings[item[2]].Index),'Customer building creation failed')
        rich.districts[#rich.districts+1]={plot=plot:GetIndex(),district=item[1],building=item[2],present=true}
    else
        assert(water,'No land for required customer')
        rich.districts[#rich.districts+1]={district=item[1],building=item[2],present=false,reason='No available water plot in this city'}
    end
end
city:GetBuildQueue():CreateBuilding(GameInfo.Buildings.BUILDING_GRANARY.Index,Map.GetPlot(city:GetX(),city:GetY()):GetIndex())
-- Recheck after the AI's radius-three claims and customer construction. This
-- catches any overlap before the stricter Mill fixture can normalize geometry.
assert(humanNeighborhood(localPlot) and humanNeighborhood(remotePlot),'AI setup contaminated a human Mill neighborhood')
assert(Map.GetPlotDistance(localPlot:GetX(),localPlot:GetY(),remotePlot:GetX(),remotePlot:GetY())>=6,'Human Mill neighborhoods overlap')
CSC_RefreshAdjacencies()
CSC_MILL_STUDY_SETUP={schema=1,fixture=config,targets=targets,rich=rich,techs=techs,civics=civics,
    controlled=true,notNaturalAvailability=true}
local function num(v) return tostring(assert(tonumber(v))) end
local function target(t) return '{"player":'..num(t.player)..',"city":'..num(t.city)..',"plot":'..num(t.plot)..'}' end
-- Only compact numeric binding data cross this first transport marker. The
-- complete rich/technology facts are independently read back by world.lua.
print('CSC_MILL_STUDY_SETUP={"schema":1,"fixture":{"schema":1,"player":0,"localCity":'..num(config.localCity)..
    ',"localPlot":'..num(config.localPlot)..',"remoteCity":'..num(config.remoteCity)..',"remotePlot":'..num(config.remotePlot)..
    ',"token":"'..CSC_MILL_STUDY_TOKEN..'"},"targets":['..target(targets[1])..','..target(targets[2])..'] }')
