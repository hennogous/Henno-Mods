-- Read-only UI half of the local-cue experiment. Pick two reachable, owned
-- sites of one city. One touches a mapped raw material and terrain of that
-- material. The other must have a different count of the same terrain.
local private = assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT).Index
local profiles, tags = {}, {}
for row in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
    local district = GameInfo.Districts["DISTRICT_CSC_" .. row.QuarterKey .. "_QUARTER"]
    local tag = "CLASS_CSC_" .. row.QuarterKey .. "_BASE"
    if district and row.SourceTag == tag and not profiles[district.Index] then
        local profile = {district=district, resources={}}
        profiles[district.Index] = profile
        tags[tag] = profile
    end
end
for row in GameInfo.TypeTags() do
    local profile, resource = tags[row.Tag], GameInfo.Resources[row.Type]
    if profile and resource then profile.resources[resource.Index] = true end
end

local function ownedSites(city, player, profile)
    local plots = {}
    for dy = -3, 3 do
        for dx = -3, 3 do
            local p = Map.GetPlotXYWithRangeCheck(city:GetX(), city:GetY(), dx, dy, 3)
            if p and p:GetOwner() == player and p:GetDistrictType() < 0
                and p:CanHaveDistrict(profile.district.Index, player, city:GetID()) then
                local owner = Cities.GetPlotPurchaseCity(p)
                if owner and owner:GetID() == city:GetID() then
                    local item = {plot=p, count={}, materialTerrain={}}
                    for _, near in ipairs(Map.GetAdjacentPlots(p:GetX(), p:GetY())) do
                        local terrain = GameInfo.Terrains[near:GetTerrainType()]
                        if terrain then
                            local key = terrain.TerrainType
                            item.count[key] = (item.count[key] or 0) + 1
                            if near:GetOwner() == player and profile.resources[near:GetResourceType()]
                                and near:GetDistrictType() < 0 then item.materialTerrain[key] = true end
                        end
                    end
                    plots[#plots+1] = item
                end
            end
        end
    end
    table.sort(plots,function(a,b) return a.plot:GetIndex() < b.plot:GetIndex() end)
    return plots
end

for _, pid in ipairs(CSC_CUE_SEATS) do
    for _, city in Players[pid]:GetCities():Members() do
        for district in GameInfo.Districts() do
            local profile = profiles[district.Index]
            if profile then
                local sites = ownedSites(city, pid, profile)
                for _, a in ipairs(sites) do
                    for terrain in GameInfo.Terrains() do
                        local key = terrain.TerrainType
                        local modifier = 'MOD_CSC_AI_LOCAL_CUE_' .. district.DistrictType .. '__' .. key
                        if a.materialTerrain[key] and GameInfo.Modifiers[modifier] then
                            for _, b in ipairs(sites) do
                                local count = b.count[key] or 0
                                if count < a.count[key] then
                                    print('CSC_NATIVE_CUE_PAIR',pid,city:GetID(),district.Index,
                                        a.plot:GetIndex(),b.plot:GetIndex(),a.count[key],count,modifier,
                                        a.plot:GetAdjacencyYield(pid,city:GetID(),district.Index,private),
                                        b.plot:GetAdjacencyYield(pid,city:GetID(),district.Index,private))
                                    return
                                end
                            end
                        end
                    end
                end
            end
        end
    end
end
print('CSC_NATIVE_CUE_NO_PAIR',Game.GetCurrentGameTurn())
