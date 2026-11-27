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
                    for direction = 0, 5 do
                        local near = Map.GetAdjacentPlot(p:GetX(), p:GetY(), direction)
                        local terrain = near and GameInfo.Terrains[near:GetTerrainType()]
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

local terrainKeys = {}
for terrain in GameInfo.Terrains() do
    if terrain.Water ~= true and tonumber(terrain.Water) ~= 1
            and terrain.Impassable ~= true and tonumber(terrain.Impassable) ~= 1 then
        terrainKeys[#terrainKeys+1] = terrain.TerrainType
    end
end
table.sort(terrainKeys)

local function report(pid, city, profile, pair, exact)
    local a, b, terrain = pair.a, pair.b, pair.terrain
    local district = profile.district
    local modifier = 'MOD_CSC_AI_LOCAL_CUE_' .. district.DistrictType .. '__' .. terrain
    assert(GameInfo.Modifiers[modifier], modifier)
    print('CSC_NATIVE_CUE_PAIR',pid,city:GetID(),district.Index,
        a.plot:GetIndex(),b.plot:GetIndex(),a.count[terrain],b.count[terrain] or 0,modifier,
        a.plot:GetAdjacencyYield(pid,city:GetID(),district.Index,private),
        b.plot:GetAdjacencyYield(pid,city:GetID(),district.Index,private),
        pair.cutoff,pair.hits,pair.total,exact and 1 or 0)
end

-- An ordinary pair with different terrain counts still tests whether the
-- stock effect works when no city has a discriminating material cue by the
-- final checkpoints. Record this case separately from an exact cue.
local function controlPair(sites)
    for _, a in ipairs(sites) do
        for _, key in ipairs(terrainKeys) do
            if a.materialTerrain[key] then
                for _, b in ipairs(sites) do
                    if (b.count[key] or 0) < a.count[key] then
                        return {a=a,b=b,terrain=key,cutoff=2,hits=-1,total=#sites}
                    end
                end
            end
        end
    end
end

local fallback
for _, pid in ipairs(CSC_CUE_SEATS) do
    for _, city in Players[pid]:GetCities():Members() do
        for district in GameInfo.Districts() do
            local profile = profiles[district.Index]
            if profile then
                local sites = ownedSites(city, pid, profile)
                local exact = selectMaterialCue(sites, terrainKeys)
                if exact then report(pid, city, profile, exact, true); return end
                if CSC_CUE_ALLOW_FALLBACK and not fallback then
                    local sample = controlPair(sites)
                    if sample then fallback = {pid, city, profile, sample} end
                end
            end
        end
    end
end
if fallback then report(fallback[1], fallback[2], fallback[3], fallback[4], false); return end
print('CSC_NATIVE_CUE_NO_PAIR',Game.GetCurrentGameTurn())
