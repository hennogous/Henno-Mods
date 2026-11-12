-- Passive full-game census, promoted from the existing endpoint comparison.
-- Reads physical suppliers, Quarter/customer buildings, native source properties
-- and empire output. It never publishes bids, changes game facts or issues orders.
-- The caller supplies original AI seats and an exact sample turn. Keep these
-- rows compatible with the archived baseline so like-for-like totals can be read.
assert(CSC_ENDPOINT_EXPECTED_TURN and Game.GetCurrentGameTurn() == CSC_ENDPOINT_EXPECTED_TURN)
local keys = {
    BAKERS = {"GROWTH", "HOUSING", "TOURISM"},
    TAILORS = {"PRODUCTION", "FAITH", "TOURISM"},
}
local count = 0
local function emit(kind, ...)
    local fields = {...}
    for index, value in ipairs(fields) do fields[index] = tostring(value) end
    print("CSC_ENDPOINT_" .. kind .. "\t" .. table.concat(fields, "\t"))
    count = count + 1
end
local profiles = {}
for key, effects in pairs(keys) do
    local district = assert(GameInfo.Districts["DISTRICT_CSC_" .. key .. "_QUARTER"])
    profiles[district.DistrictType] = {key=key, effects=effects, sales={}, producers={}, customers={}}
end
local function profile(key)
    return profiles["DISTRICT_CSC_" .. key .. "_QUARTER"]
end
local districtReplacements, buildingReplacements = {}, {}
local function addReplacement(list, original, unique)
    list[original] = list[original] or {}
    table.insert(list[original], unique)
end
for row in GameInfo.DistrictReplaces() do
    addReplacement(districtReplacements, row.ReplacesDistrictType, row.CivUniqueDistrictType)
end
for row in GameInfo.BuildingReplaces() do
    addReplacement(buildingReplacements, row.ReplacesBuildingType, row.CivUniqueBuildingType)
end
for row in GameInfo.CSC_QuarterFlowBuildings() do
    local p = profile(row.QuarterKey)
    if p then p.producers[row.BuildingType] = row.Stage end
end
local function addCustomer(p, stage, host, building)
    if not p or not stage or not GameInfo.Districts[host] or not GameInfo.Buildings[building] then return end
    local function register(district, typeName)
        p.customers[district] = p.customers[district] or {}
        local stages = p.customers[district]
        stages[stage] = stages[stage] or {}
        stages[stage][typeName] = true
    end
    local function registerFamily(district, typeName)
        if not district then return end
        register(district, typeName)
        for _, unique in ipairs(districtReplacements[district] or {}) do register(unique, typeName) end
    end
    registerFamily(host, building)
    for _, unique in ipairs(buildingReplacements[building] or {}) do
        registerFamily(assert(GameInfo.Buildings[unique]).PrereqDistrict, unique)
    end
end
for row in GameInfo.CSC_QuarterCustomerBuildings() do
    addCustomer(profile(row.QuarterKey), row.ProducerStage, row.DistrictType, row.BuildingType)
end
for row in GameInfo.CSC_Stage3CustomerTransactions() do
    addCustomer(profiles[row.SellerDistrictType], 3, row.CustomerDistrictType, row.CustomerBuildingType)
end
for row in GameInfo.CSC_QuarterWonderSales() do
    if profile(row.QuarterKey) then
        addCustomer(profile(row.QuarterKey), row.ProducerStage, "DISTRICT_WONDER", row.BuildingType)
    end
end
for _, p in pairs(profiles) do
    for row in GameInfo.Districts() do
        local host = row.DistrictType
        if CSC_Adjacency.HasTag("CLASS_CSC_" .. p.key .. "_SALES", host) then
            p.sales[host] = true
            for _, replacement in ipairs(districtReplacements[host] or {}) do p.sales[replacement] = true end
        end
    end
end
local compatible = {}
for row in GameInfo.Improvement_ValidResources() do
    compatible[row.ResourceType] = compatible[row.ResourceType] or {}
    compatible[row.ResourceType][assert(GameInfo.Improvements[row.ImprovementType]).Index] = true
end
local function buildingAt(city, typeName, plot)
    local index = assert(GameInfo.Buildings[typeName]).Index
    local buildings = city:GetBuildings()
    if not buildings:HasBuilding(index) or buildings:GetBuildingLocation(index) ~= plot then return 0 end
    return buildings:IsPillaged(index) and 1 or 2
end
local serviceBuildings = {}
for row in GameInfo.Buildings() do
    if row.BuildingType:match("^BUILDING_CSC_BAKERS_STAGE_[234]_SERVICE")
        or row.BuildingType:match("^BUILDING_CSC_TAILORS_STAGE_[234]_SERVICE") then
        table.insert(serviceBuildings, row)
    end
end
local function observeNumber(object, method)
    local getter = object[method]
    if type(getter) == "function" then
        local ok, value = pcall(getter, object)
        if ok and type(value) == "number" then return value end
    end
    return "unavailable"
end
local production = assert(GameInfo.Yields.YIELD_PRODUCTION).Index
for _, pid in ipairs(CSC_ENDPOINT_PLAYERS) do
    local player = assert(Players[pid])
    emit("PLAYER", pid, player:IsAlive())
    if player:IsAlive() then
        local treasury = player:GetTreasury()
        emit("TREASURY", pid, treasury:GetGoldBalance(),
            observeNumber(treasury, "GetGoldYield"), observeNumber(treasury, "GetTotalMaintenance"))
        for _, city in player:GetCities():Members() do
            emit("CITY", pid, city:GetID(), city:GetPopulation(), city:GetYield(production),
                observeNumber(city:GetGrowth(), "GetFoodSurplus"))
            for _, row in ipairs(serviceBuildings) do
                if city:GetBuildings():HasBuilding(row.Index) then
                    emit("SERVICE_BUILDING", pid, city:GetID(), row.BuildingType,
                        city:GetBuildings():IsPillaged(row.Index))
                end
            end
            local districts = city:GetDistricts()
            for index = 0, districts:GetNumDistricts()-1 do
                local district = districts:GetDistrictByIndex(index)
                local p = profiles[GameInfo.Districts[district:GetType()].DistrictType]
                if p then
                    local plot = Map.GetPlot(district:GetX(), district:GetY())
                    local id = plot:GetIndex()
                    local properties = {}
                    for i, effect in ipairs(p.effects) do
                        properties[i] = city:GetProperty("CSC_" .. p.key .. "_STAGE_" .. (i+1) .. "_EFFECT_" .. effect) or 0
                    end
                    emit("QUARTER", p.key, pid, city:GetID(), id, district:IsComplete(),
                        district:IsPillaged(), plot:IsRiver(), properties[1], properties[2], properties[3])
                    for typeName, stage in pairs(p.producers) do
                        local status = buildingAt(city, typeName, id)
                        if status > 0 then emit("PRODUCER", id, stage, typeName, status) end
                    end
                    for _, near in ipairs(Map.GetAdjacentPlots(plot:GetX(), plot:GetY())) do
                        if near:GetOwner() == pid then
                            local nearID = near:GetIndex()
                            local resource = GameInfo.Resources[near:GetResourceType()]
                            if resource and near:GetDistrictType() == -1
                                and CSC_Adjacency.ResourceVisible(pid, resource.Index)
                                and PlayersVisibility[pid]:IsRevealed(near:GetX(), near:GetY()) then
                                for _, class in ipairs({"BASE", "SPEC"}) do
                                    if CSC_Adjacency.HasTag("CLASS_CSC_" .. p.key .. "_" .. class, resource.ResourceType) then
                                        local valid = compatible[resource.ResourceType] or {}
                                        emit("MATERIAL", id, nearID, class, resource.ResourceType,
                                            valid[near:GetImprovementType()] == true and not near:IsImprovementPillaged())
                                    end
                                end
                            end
                            local host = GameInfo.Districts[near:GetDistrictType()]
                            if host then
                                local hostType = host.DistrictType
                                if p.sales[hostType] then emit("SALES", id, nearID, hostType) end
                                local buyer = Cities.GetPlotPurchaseCity(near)
                                for stage, types in pairs(p.customers[hostType] or {}) do
                                    local status, complete = 0, false
                                    if buyer and buyer:GetOwner() == pid then
                                        local hostDistricts = buyer:GetDistricts()
                                        for i = 0, hostDistricts:GetNumDistricts()-1 do
                                            local d = hostDistricts:GetDistrictByIndex(i)
                                            if d:GetX() == near:GetX() and d:GetY() == near:GetY() then
                                                complete = d:IsComplete() and not d:IsPillaged()
                                                break
                                            end
                                        end
                                        for typeName in pairs(types) do
                                            status = math.max(status, buildingAt(buyer, typeName, nearID))
                                        end
                                    end
                                    emit("CUSTOMER", id, nearID, stage, hostType, complete, status)
                                end
                            end
                        end
                    end
                end
            end
        end
    end
end
print("CSC_ENDPOINT_END\t" .. Game.GetCurrentGameTurn() .. "\t" .. count)
