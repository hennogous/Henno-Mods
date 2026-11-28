-- Shared by the controlled preview and the lightweight candidate. The map
-- supplies the candidate sites and CSC's loaded gameplay tags identify Base.
local profiles, tags = {}, {}
for row in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
    local district = GameInfo.Districts["DISTRICT_CSC_" .. row.QuarterKey .. "_QUARTER"]
    local tag = "CLASS_CSC_" .. row.QuarterKey .. "_BASE"
    if district and row.SourceTag == tag and row.SourceFilter == ''
            and row.AdjacencyType == 'FROM_RINGS_TYPETAG_RESOURCE' and not profiles[district.Index] then
        local profile = {district=district, resources={}, customers={}, coastal=false}
        profiles[district.Index] = profile
        tags[tag] = profile
    end
end
for row in GameInfo.TypeTags() do
    local profile, resource = tags[row.Tag], GameInfo.Resources[row.Type]
    if profile and resource then profile.resources[resource.Index] = resource end
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

local function ownedSites(city, player, profile)
    local plots = {}
    for dy = -3, 3 do
        for dx = -3, 3 do
            local p = Map.GetPlotXYWithRangeCheck(city:GetX(), city:GetY(), dx, dy, 3)
            if p and p:GetOwner() == player and p:GetDistrictType() < 0
                and p:CanHaveDistrict(profile.district.Index, player, city:GetID()) then
                local owner = Cities.GetPlotPurchaseCity(p)
                if owner and owner:GetID() == city:GetID() then
                    local item = {plot=p, count={}, materialTerrain={}, customerRank=0}
                    for direction = 0, 5 do
                        local near = Map.GetAdjacentPlot(p:GetX(), p:GetY(), direction)
                        local terrain = near and GameInfo.Terrains[near:GetTerrainType()]
                        if terrain then
                            local key = terrain.TerrainType
                            item.count[key] = (item.count[key] or 0) + 1
                            local district = near:GetDistrictType()
                            local resource = profile.resources[near:GetResourceType()]
                            if near:GetOwner() == player and district < 0 and resource then
                                local actor = Players[player]
                                local tech = resource.PrereqTech and GameInfo.Technologies[resource.PrereqTech]
                                local civic = resource.PrereqCivic and GameInfo.Civics[resource.PrereqCivic]
                                if (not tech or actor:GetTechs():HasTech(tech.Index))
                                        and (not civic or actor:GetCulture():HasCivic(civic.Index)) then
                                    item.materialTerrain[key] = true
                                end
                            end
                            -- Only break ties between signals that exclusively
                            -- reward Base. Prefer an existing mapped customer,
                            -- then an empty coast footprint for coastal customers.
                            if near:GetOwner() == player and profile.customers[district] then
                                item.customerRank = 2
                            elseif profile.coastal and key == 'TERRAIN_COAST' and district < 0
                                    and near:GetFeatureType() < 0 and near:GetResourceType() < 0
                                    and (near:GetOwner() == player or near:GetOwner() < 0) then
                                item.customerRank = math.max(1,item.customerRank)
                            end
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
    if not flag(terrain.Water) and not flag(terrain.Impassable) then
        terrainKeys[#terrainKeys+1] = terrain.TerrainType
    end
end
table.sort(terrainKeys)
