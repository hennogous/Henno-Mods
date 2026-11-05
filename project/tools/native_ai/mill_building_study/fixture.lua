-- Controlled Mill fixture for a disposable, fresh turn-1 research world.
--
-- Root's shared controller supplies two human-player cities and empty adjacent
-- sites, and owns all console commands. This file neither advances time nor
-- changes AI scores. Mutations are explicit, once-only phases. Native yield
-- samples are collected in later commands so modifier updates can settle.
assert(CSC_MillFixture == nil, 'Mill fixture already loaded; do not reset its phase history')
local F = {schema=1, phase='unbound', nextCase=1, history={}}
CSC_MillFixture = F

local QUARTER = 'DISTRICT_CSC_BAKERS_QUARTER'
local WIND = 'BUILDING_CSC_BAKERS_WIND_MILL'
local WATER = 'BUILDING_CSC_BAKERS_WATER_MILL'
local RULES = {
    {id='CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS', building=WIND, maximum=1},
    {id='CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER', building=WATER, maximum=3}
}
local BITS = {1,2,4,8,16,32,64,128,256,512}
local CASES = {
    {id='wind-flat', hill=false, edges=0, action='local-wind', delta={0,0}},
    {id='wind-hill', hill=true, edges=0, action='local-wind', delta={1,0}},
    {id='water-0', hill=false, edges=0, action='local-water', delta={0,0}},
    {id='water-1', hill=false, edges=1, action='local-water', delta={0,0}},
    {id='water-2', hill=false, edges=2, action='local-water', delta={1,0}},
    {id='water-3', hill=false, edges=3, action='local-water', delta={1,0}},
    {id='water-4', hill=false, edges=4, action='local-water', delta={2,0}},
    {id='water-5', hill=false, edges=5, action='local-water', delta={2,0}},
    {id='water-6', hill=false, edges=6, action='local-water', delta={3,0}},
    {id='remote-wind', hill=true, edges=0, remoteHill=true, action='remote-wind', delta={0,1}},
    {id='remote-water', hill=false, edges=4, remoteEdges=4, action='remote-water', delta={0,2}},
    {id='both-wind', hill=true, edges=0, remoteHill=true, action='both-wind', delta={1,1}},
    {id='both-water', hill=false, edges=4, remoteEdges=4, action='both-water', delta={2,2}},
    {id='remove-wind', hill=true, edges=0, baseline='wind', action='remove-wind', delta={-1,0}},
    {id='remove-water', hill=false, edges=4, baseline='water', action='remove-water', delta={-2,0}},
    {id='pillage-wind', hill=true, edges=0, baseline='wind', action='pillage-wind', delta={-1,0}},
    {id='repair-wind', hill=true, edges=0, baseline='wind-pillaged', action='repair-wind', delta={1,0}},
    {id='pillage-water', hill=false, edges=4, baseline='water', action='pillage-water', delta={-2,0}},
    {id='repair-water', hill=false, edges=4, baseline='water-pillaged', action='repair-water', delta={2,0}},
    {id='pillage-quarter', hill=true, edges=0, baseline='wind', action='pillage-quarter', delta={-1,0}},
    {id='repair-quarter', hill=true, edges=0, continuation='pillage-quarter', action='repair-quarter', delta={1,0}}
}

local function integer(value)
    local kind = type(value)
    return (kind=='number' or kind=='integer') and value==math.floor(value)
end
local function requireTurnOne()
    assert(Game.GetCurrentGameTurn()==1, 'Mill fixture mutations require a fresh disposable turn-1 world')
end
local function definition(name)
    return assert(GameInfo.Buildings[name], 'Missing fixture building '..name)
end
local function districtAt(city, plot)
    local manager = city:GetDistricts()
    for i=0,manager:GetNumDistricts()-1 do
        local district = manager:GetDistrictByIndex(i)
        if district:GetX()==plot:GetX() and district:GetY()==plot:GetY() then return district end
    end
    error('Native district missing at declared fixture site')
end
local function sites(config, existing)
    assert(type(config)=='table' and config.schema==1 and config.player==0, 'Explicit human-0 fixture config required')
    assert(type(config.token)=='string' and config.token:match('^[%w_-]+$') and #config.token<=80, 'Invalid fixture token')
    assert(integer(config.localCity) and integer(config.remoteCity) and config.localCity~=config.remoteCity, 'Distinct city IDs required')
    assert(integer(config.localPlot) and integer(config.remotePlot) and config.localPlot~=config.remotePlot, 'Distinct plot indices required')
    local player = assert(Players[0], 'Human fixture player missing')
    assert(player:IsHuman(), 'Fixture must not target an AI')
    local result = {}
    for i,key in ipairs({'local','remote'}) do
        local city = assert(player:GetCities():FindID(config[key..'City']), 'Fixture city missing: '..key)
        local plot = assert(Map.GetPlotByIndex(config[key..'Plot']), 'Fixture plot missing: '..key)
        assert(city:GetOwner()==0 and plot:GetOwner()==0, 'Fixture city/site owner changed')
        assert(Map.GetPlotDistance(city:GetX(),city:GetY(),plot:GetX(),plot:GetY())==1, 'Fixture Quarter must be adjacent to its city')
        assert(not plot:IsCity(), 'City-center plot is not a Quarter site')
        if existing then
            assert(plot:GetDistrictType()==GameInfo.Districts[QUARTER].Index, 'Fixture Quarter type changed')
        else
            assert(plot:GetDistrictType()==-1, 'Fixture site is occupied')
        end
        result[i] = {city=city, plot=plot}
    end
    assert(Map.GetPlotDistance(result[1].plot:GetX(),result[1].plot:GetY(),result[2].plot:GetX(),result[2].plot:GetY())>=6,
        'Fixture districts need disjoint neighborhoods')
    return result
end
local function requireMethod(owner, name)
    assert(type(owner[name])=='function', 'Required native method unavailable: '..name)
end
local function validateAPIs(items)
    for _,name in ipairs({'SetTerrainType','SetFeatureType','SetWOfRiver','SetNWOfRiver','SetNEOfRiver'}) do requireMethod(TerrainBuilder,name) end
    requireMethod(ResourceBuilder,'SetResourceType')
    requireMethod(WorldBuilder.CityManager(),'SetPlotOwner')
    assert(type(CSC_RefreshAdjacencies)=='function', 'CSC gameplay refresh context required')
    for _,item in ipairs(items) do
        local buildings = item.city:GetBuildings()
        for _,name in ipairs({'HasBuilding','IsPillaged','GetBuildingLocation','RemoveBuilding','SetPillaged'}) do requireMethod(buildings,name) end
        requireMethod(item.city:GetBuildQueue(),'CreateBuilding')
        requireMethod(item.city:GetBuildQueue(),'CreateIncompleteDistrict')
        requireMethod(item.plot,'GetRiverCrossingCount')
    end
end

-- The game stores each shared river edge on exactly one of its two hexes.
-- These six ownership rules are also documented by CSC_AdjacencyPresentation.
-- Setter/flow combinations come from shipped Maps/Utility/RiversLakes.lua.
-- Every mutation is independently checked by native GetRiverCrossingCount.
local function edgeSlots(plot)
    local function neighbor(direction)
        return assert(Map.GetAdjacentPlot(plot:GetX(),plot:GetY(),direction), 'Fixture site touches map boundary')
    end
    return {
        {plot=plot, setter='SetWOfRiver', getter='IsWOfRiver', flow=FlowDirectionTypes.FLOWDIRECTION_SOUTH},
        {plot=plot, setter='SetNWOfRiver', getter='IsNWOfRiver', flow=FlowDirectionTypes.FLOWDIRECTION_NORTHEAST},
        {plot=plot, setter='SetNEOfRiver', getter='IsNEOfRiver', flow=FlowDirectionTypes.FLOWDIRECTION_NORTHWEST},
        {plot=neighbor(DirectionTypes.DIRECTION_NORTHEAST), setter='SetNEOfRiver', getter='IsNEOfRiver', flow=FlowDirectionTypes.FLOWDIRECTION_NORTHWEST},
        {plot=neighbor(DirectionTypes.DIRECTION_WEST), setter='SetWOfRiver', getter='IsWOfRiver', flow=FlowDirectionTypes.FLOWDIRECTION_SOUTH},
        {plot=neighbor(DirectionTypes.DIRECTION_NORTHWEST), setter='SetNWOfRiver', getter='IsNWOfRiver', flow=FlowDirectionTypes.FLOWDIRECTION_NORTHEAST}
    }
end
local function geometry(item, hill, count)
    assert(integer(count) and count>=0 and count<=6, 'Fixture river count must be 0..6')
    TerrainBuilder.SetTerrainType(item.plot,GameInfo.Terrains[hill and 'TERRAIN_GRASS_HILLS' or 'TERRAIN_GRASS'].Index)
    for i,slot in ipairs(edgeSlots(item.plot)) do TerrainBuilder[slot.setter](slot.plot,i<=count,slot.flow) end
    assert(item.plot:IsHills()==hill, 'Native hill readback disagrees')
    assert(item.plot:GetRiverCrossingCount()==count, 'Native river-edge readback disagrees')
end
local function removeMills(item)
    local buildings = item.city:GetBuildings()
    for _,name in ipairs({WIND,WATER}) do
        local index = definition(name).Index
        if buildings:HasBuilding(index) then buildings:RemoveBuilding(index) end
        assert(not buildings:HasBuilding(index), 'Mill removal did not complete')
    end
end
local function addMill(item, name)
    local index = definition(name).Index
    item.city:GetBuildQueue():CreateBuilding(index,item.plot:GetIndex())
    local buildings = item.city:GetBuildings()
    assert(buildings:HasBuilding(index) and buildings:GetBuildingLocation(index)==item.plot:GetIndex(), 'Native Mill placement did not match its Quarter')
end
local function millState(item, name)
    local b = item.city:GetBuildings()
    local index = definition(name).Index
    local present = b:HasBuilding(index)
    return {type=name, index=index, present=present, pillaged=present and b:IsPillaged(index) or false,
        plot=present and b:GetBuildingLocation(index) or -1}
end
local function propertyValue(plot, name)
    local value = plot:GetProperty(name)
    if value==nil then return 'ABSENT' end
    assert(integer(value), 'Fixture property is not an integer: '..name)
    return value
end
local function facts(config)
    local items = sites(config,true)
    local result = {}
    for i,item in ipairs(items) do
        local district = districtAt(item.city,item.plot)
        local wind,water = millState(item,WIND),millState(item,WATER)
        local functioning = district:IsComplete() and not district:IsPillaged()
        local windExpected = functioning and wind.present and not wind.pillaged and wind.plot==item.plot:GetIndex() and item.plot:IsHills() and 1 or 0
        local waterExpected = functioning and water.present and not water.pillaged and water.plot==item.plot:GetIndex() and math.floor(item.plot:GetRiverCrossingCount()/2) or 0
        local properties = {}
        for _,rule in ipairs(RULES) do
            local prefix = 'CSC_ADJ_'..rule.id..'_'
            local row = {id=rule.id, total=propertyValue(item.plot,prefix..'TOTAL'),
                actual=propertyValue(item.plot,prefix..'ACTUAL_AMOUNT'), encoded=propertyValue(item.plot,prefix..'ENCODED_AMOUNT'), steps={}, legacy={}}
            for n=1,rule.maximum do row.steps[n]=propertyValue(item.plot,prefix..'STEP_'..n) end
            for _,bit in ipairs(BITS) do row.legacy[tostring(bit)]=propertyValue(item.plot,prefix..bit) end
            properties[#properties+1] = row
        end
        local neighbors = {}
        for direction=0,5 do
            local neighbor = assert(Map.GetAdjacentPlot(item.plot:GetX(),item.plot:GetY(),direction))
            neighbors[#neighbors+1] = {plot=neighbor:GetIndex(), resource=neighbor:GetResourceType(), improvement=neighbor:GetImprovementType(), district=neighbor:GetDistrictType()}
        end
        result[i] = {player=0, city=item.city:GetID(), plot=item.plot:GetIndex(),
            districtType=district:GetType(), complete=district:IsComplete(), quarterPillaged=district:IsPillaged(),
            hill=item.plot:IsHills(), riverEdges=item.plot:GetRiverCrossingCount(),
            production=district:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index),
            wind=wind,water=water, properties=properties, neighbors=neighbors,
            expectedAbsoluteProductionBonus=windExpected+waterExpected,
            expectedWind=windExpected,expectedWater=waterExpected}
    end
    return result
end
local function current(id)
    assert(F.case and F.case.id==id, 'Unexpected fixture case identity')
    return F.case
end
local function close(a,b,label)
    assert(type(a)=='number' or type(a)=='integer', 'Native yield is not numeric: '..label)
    assert(math.abs(a-b)<0.001, label..': actual '..tostring(a)..', expected '..tostring(b))
end

function F.Describe()
    return {schema=1, cases=CASES, mutationsRequireTurn=1, baselineMustSettle=true,
        forcedBuildings=true, oracle='Wind hill Boolean; Water floor(native river edges / 2); local functioning building only'}
end

function F.Prepare(config)
    requireTurnOne()
    assert(F.phase=='unbound', 'Fixture already prepared or preparation failed; do not replay')
    local items = sites(config,false)
    validateAPIs(items)
    for _,item in ipairs(items) do
        -- A Granary or developed CSC producer could add a separate real return.
        -- Fresh fixture cities must contain only their Palace, if any.
        for building in GameInfo.Buildings() do
            assert(not item.city:GetBuildings():HasBuilding(building.Index) or building.BuildingType=='BUILDING_PALACE',
                'Developed building would contaminate Mill fixture: '..building.BuildingType)
        end
        for direction=0,5 do
            local plot = assert(Map.GetAdjacentPlot(item.plot:GetX(),item.plot:GetY(),direction))
            assert(plot:GetDistrictType()==-1 or plot:IsCity(), 'Other district would contaminate Mill fixture')
            assert(plot:GetImprovementType()==-1, 'Improvement would contaminate Mill fixture')
        end
    end
    F.config = config
    F.phase = 'preparing' -- Reserve before the first mutation; no automatic replay.
    for _,item in ipairs(items) do
        ResourceBuilder.SetResourceType(item.plot,-1)
        TerrainBuilder.SetFeatureType(item.plot,-1)
        TerrainBuilder.SetTerrainType(item.plot,GameInfo.Terrains.TERRAIN_GRASS.Index)
        for direction=0,5 do
            local plot = Map.GetAdjacentPlot(item.plot:GetX(),item.plot:GetY(),direction)
            ResourceBuilder.SetResourceType(plot,-1)
            if not plot:IsCity() then
                TerrainBuilder.SetFeatureType(plot,-1)
                TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS.Index)
            end
        end
        WorldBuilder.CityManager():SetPlotOwner(item.plot:GetX(),item.plot:GetY(),0,item.city:GetID())
        item.city:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts[QUARTER].Index,item.plot:GetIndex(),100)
        local district = districtAt(item.city,item.plot)
        assert(district:GetType()==GameInfo.Districts[QUARTER].Index and district:IsComplete(), 'Fixture Quarter did not complete')
        requireMethod(district,'SetPillaged')
        geometry(item,false,0)
    end
    CSC_RefreshAdjacencies()
    F.phase = 'ready'
    return {schema=1,phase=F.phase,config=F.config,caseCount=#CASES}
end

function F.PrepareCase(id)
    requireTurnOne()
    assert(F.phase=='ready' or F.phase=='finished', 'Prior fixture case is unfinished')
    local case = assert(CASES[F.nextCase], 'No remaining fixture cases')
    assert(case.id==id, 'Fixture cases must execute in declared order')
    if case.continuation then
        -- A district repair must continue the actual pillage of an already
        -- functioning Mill. Removing/recreating that Mill and pillaging its
        -- Quarter before the same command returns can suppress its initial
        -- native modifier enrollment. It is a different construction scenario.
        assert(F.phase=='finished' and F.case and F.case.id==case.continuation
            and F.history[#F.history].case==case.continuation, 'Paired Quarter repair requires the completed pillage case')
        local retained = facts(F.config)
        local localRow,remoteRow = retained[1],retained[2]
        assert(localRow.complete and localRow.quarterPillaged and localRow.hill and localRow.riverEdges==0
            and localRow.wind.present and not localRow.wind.pillaged and localRow.wind.plot==localRow.plot
            and not localRow.water.present and not remoteRow.wind.present and not remoteRow.water.present,
            'Paired Quarter repair requires the retained pillaged Quarter and healthy local Wind Mill')
        F.case,F.baseline,F.phase = case,nil,'prepared'
        -- Bookkeeping only: retain both native objects, geometry and attachment
        -- lifetimes. Root takes a separate stable baseline before repairing.
        return {schema=1,phase=F.phase,case=id,continuation=case.continuation,
            retainedNativeObjects=true,worldMutations=false,expectedDelta=case.delta}
    end
    F.case,F.baseline,F.phase = case,nil,'preparing-case'
    local items = sites(F.config,true)
    for _,item in ipairs(items) do
        removeMills(item)
        districtAt(item.city,item.plot):SetPillaged(false)
    end
    geometry(items[1],case.hill,case.edges)
    geometry(items[2],case.remoteHill or false,case.remoteEdges or 0)
    if case.baseline then
        local name = case.baseline:match('^wind') and WIND or WATER
        addMill(items[1],name)
        if case.baseline=='wind-pillaged' or case.baseline=='water-pillaged' then items[1].city:GetBuildings():SetPillaged(definition(name).Index,true) end
    end
    CSC_RefreshAdjacencies()
    F.phase = 'prepared'
    return {schema=1,phase=F.phase,case=id,geometry={hill=case.hill,edges=case.edges},expectedDelta=case.delta}
end

function F.CaptureBaseline(id)
    current(id)
    assert(F.phase=='prepared', 'Baseline capture requires the prepared phase')
    -- This updates fixture bookkeeping only, never the game. Root samples twice
    -- in separate commands and accepts a stable baseline before ApplyCase.
    F.baseline = facts(F.config)
    return {schema=1,case=id,phase='baseline',facts=F.baseline}
end

function F.ApplyCase(id)
    requireTurnOne()
    local case = current(id)
    assert(F.phase=='prepared' and F.baseline, 'A settled baseline is required before applying a case')
    F.phase = 'applying' -- Reserve before mutation; an ambiguous command cannot be replayed.
    local items = sites(F.config,true)
    local action = case.action
    if action=='local-wind' or action=='both-wind' then addMill(items[1],WIND) end
    if action=='local-water' or action=='both-water' then addMill(items[1],WATER) end
    if action=='remote-wind' or action=='both-wind' then addMill(items[2],WIND) end
    if action=='remote-water' or action=='both-water' then addMill(items[2],WATER) end
    if action=='remove-wind' then items[1].city:GetBuildings():RemoveBuilding(definition(WIND).Index) end
    if action=='remove-water' then items[1].city:GetBuildings():RemoveBuilding(definition(WATER).Index) end
    if action=='pillage-wind' or action=='repair-wind' then items[1].city:GetBuildings():SetPillaged(definition(WIND).Index,action=='pillage-wind') end
    if action=='pillage-water' or action=='repair-water' then items[1].city:GetBuildings():SetPillaged(definition(WATER).Index,action=='pillage-water') end
    if action=='pillage-quarter' or action=='repair-quarter' then districtAt(items[1].city,items[1].plot):SetPillaged(action=='pillage-quarter') end
    CSC_RefreshAdjacencies()
    F.phase = 'applied'
    return {schema=1,case=id,phase=F.phase,expectedDelta=case.delta,forcedBuildingCreation=true}
end

function F.Capture(id)
    local case = current(id)
    assert(F.phase=='applied' or F.phase=='finished', 'Case observation requires an applied case')
    return {schema=1,case=id,phase='observation',facts=facts(F.config),baseline=F.baseline,expectedDelta=case.delta}
end

function F.FinishCase(id, mode)
    local case = current(id)
    assert(F.phase=='applied', 'Fixture case already finished or not applied')
    assert(mode=='assert-local-contract' or mode=='record-only', 'Explicit validation mode required')
    local capture = F.Capture(id)
    if mode=='assert-local-contract' then
        for i,row in ipairs(capture.facts) do
            close(row.production-F.baseline[i].production,case.delta[i],id..' native Production delta city '..row.city)
            for j,property in ipairs(row.properties) do
                local expected = j==1 and row.expectedWind or row.expectedWater
                close(property.actual,expected,id..' actual property')
                close(property.encoded,expected,id..' encoded property')
                for step,value in ipairs(property.steps) do close(value,expected>=step and 1 or 0,id..' unit step') end
                for _,value in pairs(property.legacy) do close(value,0,id..' retired numeric bit') end
            end
        end
    end
    capture.validation = mode
    F.history[#F.history+1] = capture
    F.phase,F.nextCase = 'finished',F.nextCase+1
    return capture
end

function F.Export()
    assert(F.config and F.phase=='finished', 'Export requires a completed case')
    return {schema=1,config=F.config,case=F.case.id,facts=facts(F.config),completedCases=#F.history}
end

local function same(a,b,path)
    if type(a)=='table' then
        assert(type(b)=='table', 'Reload type mismatch '..path)
        for key,value in pairs(a) do assert(b[key]~=nil,'Reload field missing '..path..'.'..tostring(key));same(value,b[key],path..'.'..tostring(key)) end
        for key in pairs(b) do assert(a[key]~=nil,'Reload field added '..path..'.'..tostring(key)) end
    elseif integer(a) or type(a)=='number' then
        close(b,a,'Reload '..path)
    else
        assert(a==b, 'Reload field changed '..path)
    end
end

function F.VerifyReload(descriptor)
    -- Re-execute this file in the new gameplay context, then pass the exported
    -- descriptor. Verification is read-only and does not recreate fixture data.
    assert(type(descriptor)=='table' and descriptor.schema==1, 'Invalid reload descriptor')
    local captured = facts(descriptor.config)
    same(descriptor.facts,captured,'facts')
    return {schema=1,verified=true,case=descriptor.case,completedCases=descriptor.completedCases,facts=captured,readOnly=true}
end

local function json(value)
    local kind = type(value)
    if kind=='nil' then return 'null' end
    if kind=='boolean' then return tostring(value) end
    if kind=='number' or kind=='integer' then
        assert(value==value and value~=math.huge and value~=-math.huge, 'Nonfinite fixture receipt number')
        return tostring(value)
    end
    if kind=='string' then return '"'..value:gsub('[%z\1-\31\\"]',function(c) return string.format('\\u%04x',string.byte(c)) end)..'"' end
    assert(kind=='table','Unsupported fixture receipt value')
    local count,array = 0,true
    for key in pairs(value) do count=count+1;if not integer(key) or key<1 then array=false end end
    if count~=#value then array=false end
    local out = {}
    if array then for _,child in ipairs(value) do out[#out+1]=json(child) end;return '['..table.concat(out,',')..']' end
    local keys = {};for key in pairs(value) do keys[#keys+1]=key end;table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
    for _,key in ipairs(keys) do out[#out+1]=json(tostring(key))..':'..json(value[key]) end
    return '{'..table.concat(out,',')..'}'
end

function F.Print(value)
    print('CSC_MILL_FIXTURE='..json(value))
end
