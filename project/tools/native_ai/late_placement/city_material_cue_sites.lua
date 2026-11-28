-- Shared by the controlled preview and the lightweight candidate. The map
-- supplies the candidate sites and CSC's loaded gameplay tags identify Base.
local profiles, tags = {}, {}
for row in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
    local district = GameInfo.Districts["DISTRICT_CSC_" .. row.QuarterKey .. "_QUARTER"]
    local tag = "CLASS_CSC_" .. row.QuarterKey .. "_BASE"
    if district and row.SourceTag == tag and row.SourceFilter == ''
            and row.AdjacencyType == 'FROM_RINGS_TYPETAG_RESOURCE' and not profiles[district.Index] then
        local profile = {district=district, resources={}, specialty={}, customers={}, coastal=false}
        profiles[district.Index] = profile
        tags[tag] = profile.resources
        tags["CLASS_CSC_" .. row.QuarterKey .. "_SPEC"] = profile.specialty
    end
end
for row in GameInfo.TypeTags() do
    local class, resource = tags[row.Tag], GameInfo.Resources[row.Type]
    if class and resource then class[resource.Index] = resource end
end
local function flag(value) return value == true or tonumber(value) == 1 end
for row in GameInfo.CSC_QuarterCustomerBuildings() do
    local quarter = GameInfo.Districts["DISTRICT_CSC_" .. row.QuarterKey .. "_QUARTER"]
    local customer = GameInfo.Districts[row.DistrictType]
    local profile = quarter and profiles[quarter.Index]
    if profile and customer and row.ProducerStage == 2 then
        profile.customers[customer.Index] = true
        profile.coastal = profile.coastal or flag(customer.Coast)
    end
end
for row in GameInfo.DistrictReplaces() do
    local parent = GameInfo.Districts[row.ReplacesDistrictType]
    local replacement = GameInfo.Districts[row.CivUniqueDistrictType]
    if parent and replacement then
        for _, profile in pairs(profiles) do
            if profile.customers[parent.Index] then profile.customers[replacement.Index] = true end
        end
    end
end

-- Each review has one snapshot shared by every missing Quarter type. Query
-- legal placement per district; read a candidate's six neighbors only once.
-- Discard the snapshot after the pass so an ownership or supplier change is
-- visible on the next review without a separate map-invalidation system.
local function citySites(city, player)
    local snapshot = {candidates={}, visibleResources={}}
    local x, y, id = city:GetX(), city:GetY(), city:GetID()
    for dy = -3, 3 do
        for dx = -3, 3 do
            local p = Map.GetPlotXYWithRangeCheck(x, y, dx, dy, 3)
            if p and p:GetOwner() == player and p:GetDistrictType() < 0 then
                local owner = Cities.GetPlotPurchaseCity(p)
                if owner and owner:GetID() == id then
                    snapshot.candidates[#snapshot.candidates+1] = {plot=p, index=p:GetIndex()}
                end
            end
        end
    end
    table.sort(snapshot.candidates,function(a,b) return a.index < b.index end)
    return snapshot
end

local function visibleResource(player, id, cache)
    if id < 0 then return false end
    if cache[id] == nil then
        local resource = GameInfo.Resources[id]
        local tech = resource.PrereqTech and GameInfo.Technologies[resource.PrereqTech]
        local civic = resource.PrereqCivic and GameInfo.Civics[resource.PrereqCivic]
        cache[id] = (not tech or player:GetTechs():HasTech(tech.Index))
            and (not civic or player:GetCulture():HasCivic(civic.Index))
    end
    return cache[id]
end

local function geometry(site, player, cache)
    local g = {count={}, materials={}, districts={}, clearCoast=false, known=true}
    local x, y = site.plot:GetX(), site.plot:GetY()
    local actor, vision = Players[player], PlayersVisibility[player]
    for direction = 0, 5 do
        local near = Map.GetAdjacentPlot(x,y,direction)
        if near and not vision:IsRevealed(near:GetX(),near:GetY()) then
            g.known = false
        elseif near then
            local key = GameInfo.Terrains[near:GetTerrainType()].TerrainType
            g.count[key] = (g.count[key] or 0) + 1
            local owner, district, resource = near:GetOwner(), near:GetDistrictType(), near:GetResourceType()
            if owner == player and district >= 0 then
                g.districts[#g.districts+1] = district
            elseif owner == player and visibleResource(actor,resource,cache) then
                g.materials[#g.materials+1] = {id=resource,terrain=key}
            end
            if key == 'TERRAIN_COAST' and district < 0 and (owner == player or owner < 0)
                    and near:GetFeatureType() < 0 and not visibleResource(actor,resource,cache) then
                g.clearCoast = true
            end
        end
    end
    return g
end

local function ownedSites(city, player, profile, snapshot)
    local plots = {}
    for _, candidate in ipairs(snapshot.candidates) do
        if candidate.plot:CanHaveDistrict(profile.district.Index,player,city:GetID()) then
            local g = candidate.geometry or geometry(candidate,player,snapshot.visibleResources)
            candidate.geometry = g
            -- An unseen neighbor could make a material-free competitor reach
            -- the terrain cutoff. Defer this city's cue until the ring is known.
            if not g.known then return {} end
            local item = {plot=candidate.plot,count=g.count,materialTerrain={},
                customerRank=profile.coastal and g.clearCoast and 1 or 0}
            for _, deposit in ipairs(g.materials) do
                if profile.resources[deposit.id] then item.materialTerrain[deposit.terrain] = true end
                if profile.specialty[deposit.id] then item.hasSpecialty = true end
            end
            for _, district in ipairs(g.districts) do
                if profile.customers[district] then item.customerRank = 2; break end
            end
            plots[#plots+1] = item
        end
    end
    return plots
end

local terrainKeys = {}
for terrain in GameInfo.Terrains() do
    if not flag(terrain.Water) and not flag(terrain.Impassable) then
        terrainKeys[#terrainKeys+1] = terrain.TerrainType
    end
end
table.sort(terrainKeys)
