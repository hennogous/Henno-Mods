-- Shared planning overlay data for manual lenses and native district placement.
-- Does not depend on More Lenses and never writes gameplay properties.
if CSC_QuarterLensSupport ~= nil then return end
if CSC_Adjacency == nil then include("CSC_AdjacencyCore") end

CSC_QuarterLensSupport = { Quarters = {}, ByDistrict = {}, FlowSignatures = {}, SpriteSignatures = {} }
local S = CSC_QuarterLensSupport
local overlayKinds = {"BASE", "SPEC", "SALE", "QUARTER", "GOODS"}

include("CSC_ServicePresentation")
local Presentation = CSC_ServicePresentation

-- Exact UI palettes are shared by the manual lens and placement renderer.
local quarterPalette = {}
if GameInfo.CSC_LensQuarterColors then
    for row in GameInfo.CSC_LensQuarterColors() do quarterPalette[row.QuarterKey] = row end
end
S.FlowYieldColors = {}
if GameInfo.CSC_LensFlowYieldColors then
    for row in GameInfo.CSC_LensFlowYieldColors() do
        S.FlowYieldColors[row.YieldType] = row.ColorType
    end
end

-- Match the adjacency processor's default SQLite LIKE for ASCII identifiers.
local function MatchesFilter(value, filter)
    if filter == nil or filter == "" then return true end
    local pattern = "^"
    for char in filter:lower():gmatch(".") do
        if char == "%" then pattern = pattern .. ".*"
        elseif char == "_" then pattern = pattern .. "."
        else pattern = pattern .. char:gsub("(%W)", "%%%1") end
    end
    return value:lower():match(pattern .. "$") ~= nil
end

if GameInfo.CSC_QuarterMaterialAdjacencyConfig ~= nil then
    for config in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
        local key = config.QuarterKey
        local districtType = "DISTRICT_CSC_" .. key .. "_QUARTER"
        if GameInfo.Districts[districtType] then
            local quarter = S.Quarters[key]
            if not quarter then
                local palette = quarterPalette[key]
                local quarterColor = palette and palette.ColorType or "COLOR_CSC_LENS_QUARTER"
                quarter = {
                    id = key, districtType = districtType,
                    locName = "LOC_HUD_CSC_" .. key .. "_LENS",
                    locTooltip = "LOC_HUD_CSC_" .. key .. "_LENS_TOOLTIP",
                    colorPrefix = "COLOR_CSC_LENS",
                    quarterColor = quarterColor,
                    materialYield = palette and palette.MaterialYieldType or "YIELD_PRODUCTION",
                    quarterEmptyColor = quarterColor .. "_EMPTY",
                    quarterOutlineColor = quarterColor .. "_OUTLINE",
                    quarterStyle = quarterColor:gsub("^COLOR_CSC_LENS_", ""),
                    locLegendQ = "LOC_TOOLTIP_CSC_LENS_" .. key .. "_QUARTER",
                    baseSet = {}, specSet = {}, saleSet = {}, goodsSet = {}, wonderSaleSet = {}, customerBuildings = {},
                    flowStages = {}, flowCustomers = {}, wonderProducerStages = {},
                    customerYields = {}, wonderYields = {},
                }
                S.Quarters[key] = quarter
                S.ByDistrict[districtType] = quarter
            end
            local target = config.SourceTag:match("_BASE$") and quarter.baseSet
                or config.SourceTag:match("_SPEC$") and quarter.specSet
            if target then
                for row in GameInfo.TypeTags() do
                    if row.Tag == config.SourceTag and GameInfo.Resources[row.Type]
                        and MatchesFilter(row.Type, config.SourceFilter) then
                        target[row.Type] = true
                    end
                end
            end
        end
    end
end

-- The bundled adjacency processor already propagates sales tags to uniques.
for key, quarter in pairs(S.Quarters) do
    for row in GameInfo.TypeTags() do
        if row.Tag == "CLASS_CSC_" .. key .. "_SALES" and GameInfo.Districts[row.Type] then
            quarter.saleSet[row.Type] = true
        end
        if row.Tag == "CLASS_CSC_" .. key .. "_GOODS_PROVIDER" and GameInfo.Districts[row.Type] then
            quarter.goodsSet[row.Type] = true
        end
        local suffix = row.Tag:match("^CLASS_CSC_" .. key .. "_SALES_(.+)$")
        if suffix and GameInfo.Districts[row.Type] then
            local yieldType = "YIELD_" .. suffix
            if S.FlowYieldColors[yieldType] then
                quarter.customerYields[row.Type] = quarter.customerYields[row.Type] or {}
                quarter.customerYields[row.Type][yieldType] = true
            end
        end
    end
end

local function BuildingFamily(buildingType)
    local result = {}
    local definition = GameInfo.Buildings[buildingType]
    if definition then result[definition.Index] = true end
    if GameInfo.BuildingReplaces then
        for row in GameInfo.BuildingReplaces() do
            local replacement = GameInfo.Buildings[row.CivUniqueBuildingType]
            if row.ReplacesBuildingType == buildingType and replacement then result[replacement.Index] = true end
        end
    end
    return result
end

if GameInfo.CSC_QuarterFlowBuildings then
    for row in GameInfo.CSC_QuarterFlowBuildings() do
        local quarter = S.Quarters[row.QuarterKey]
        if quarter then
            quarter.flowStages[row.Stage] = quarter.flowStages[row.Stage] or {}
            for index in pairs(BuildingFamily(row.BuildingType)) do quarter.flowStages[row.Stage][index] = true end
        end
    end
end

if GameInfo.CSC_QuarterWonderSales ~= nil then
    for row in GameInfo.CSC_QuarterWonderSales() do
        local quarter = S.Quarters[row.QuarterKey]
        local wonder = GameInfo.Buildings[row.BuildingType]
        if quarter and wonder and (wonder.IsWonder == true or wonder.IsWonder == 1) then
            quarter.wonderSaleSet[row.BuildingType] = true
            quarter.wonderProducerStages[row.BuildingType] = row.ProducerStage
            quarter.wonderYields[row.BuildingType] = row.CustomerYieldType
        end
    end
end

-- Reuse the gameplay transaction registry, then supplement missing stages with
-- UI-only venue metadata. Expand direct unique replacements exactly once.
local function AddCustomer(quarter, districtType, buildingType, producers, stage)
    if quarter == nil or GameInfo.Districts[districtType] == nil or GameInfo.Buildings[buildingType] == nil then return end
    local districts, buildings = {districtType}, {GameInfo.Buildings[buildingType].Index}
    if GameInfo.DistrictReplaces then
        for row in GameInfo.DistrictReplaces() do
            if row.ReplacesDistrictType == districtType and GameInfo.Districts[row.CivUniqueDistrictType] then
                table.insert(districts, row.CivUniqueDistrictType)
            end
        end
    end
    if GameInfo.BuildingReplaces then
        for row in GameInfo.BuildingReplaces() do
            local building = GameInfo.Buildings[row.CivUniqueBuildingType]
            if row.ReplacesBuildingType == buildingType and building then table.insert(buildings, building.Index) end
        end
    end
    for _, district in ipairs(districts) do
        quarter.customerBuildings[district] = quarter.customerBuildings[district] or {}
        for _, building in ipairs(buildings) do quarter.customerBuildings[district][building] = true end
        if producers and next(producers) then
            local customers = {}
            for _, building in ipairs(buildings) do customers[building] = true end
            table.insert(quarter.flowCustomers, {districtType = district, customers = customers, producers = producers, stage = stage})
        end
    end
end

if GameInfo.CSC_Stage3CustomerTransactions then
    for row in GameInfo.CSC_Stage3CustomerTransactions() do
        AddCustomer(S.ByDistrict[row.SellerDistrictType], row.CustomerDistrictType, row.CustomerBuildingType, BuildingFamily(row.SellerBuildingType), 3)
    end
end
if GameInfo.CSC_QuarterCustomerBuildings then
    for row in GameInfo.CSC_QuarterCustomerBuildings() do
        local quarter = S.Quarters[row.QuarterKey]
        AddCustomer(quarter, row.DistrictType, row.BuildingType, quarter and quarter.flowStages[row.ProducerStage], row.ProducerStage)
    end
end

local function HasCustomerBuilding(quarter, districtType, plot)
    local candidates = quarter.customerBuildings[districtType]
    if candidates == nil then return false end
    local city = Cities.GetPlotPurchaseCity(plot)
    if city == nil then return false end
    local district = GameInfo.Districts[districtType]
    local districts = city:GetDistricts()
    if district and districts:IsPillaged(district.Index, plot:GetIndex()) then return false end
    local buildings = city:GetBuildings()
    -- Use the native UI query (CitySupport/PlotToolTip). GetBuildingLocation is
    -- a gameplay-only API and must not be used in this UI context.
    for _, index in ipairs(buildings:GetBuildingsAtLocation(plot:GetIndex())) do
        if candidates[index] and buildings:HasBuilding(index) and not buildings:IsPillaged(index) then return true end
    end
    return false
end

function S.GetQuarter(districtIndex)
    local district = districtIndex ~= nil and GameInfo.Districts[districtIndex]
    return district and S.ByDistrict[district.DistrictType] or nil
end

local HasAny, WorkingBuildings

local function CompletedMappedWonder(quarter, plot, districtType)
    local wonder = GameInfo.Buildings[plot:GetWonderType()]
    if wonder then
        if not quarter.wonderSaleSet[wonder.BuildingType] then return nil end
        if plot:IsWonderComplete() then return wonder end
    elseif districtType ~= "DISTRICT_WONDER" or next(quarter.wonderSaleSet) == nil then
        return nil
    end

    -- The stock tooltip also recognizes completion when the city owns the
    -- unique Wonder identified by the plot, even if the plot flag is false.
    local city = Cities.GetPlotPurchaseCity(plot)
    local buildings = city and city:GetBuildings()
    if buildings == nil then return nil end
    if wonder then return buildings:HasBuilding(wonder.Index) and wonder or nil end

    -- When there is no plot Wonder type, use the exact plot's building list
    -- so a Wonder elsewhere in the city cannot match this tile.
    for _, index in ipairs(buildings:GetBuildingsAtLocation(plot:GetIndex())) do
        local building = GameInfo.Buildings[index]
        if building and quarter.wonderSaleSet[building.BuildingType] and buildings:HasBuilding(index) then
            return building
        end
    end
end

local function WorkingWonder(plot, playerID, wonder)
    -- The plot entry already confirms the mapped Wonder is complete.
    if plot:GetOwner() ~= playerID then return false end
    local city = Cities.GetPlotPurchaseCity(plot)
    return city ~= nil and city:GetOwner() == playerID and not city:GetBuildings():IsPillaged(wonder.Index)
end

function S.GetLensLegend(key)
    local quarter = S.Quarters[key]
    if quarter == nil then return nil end
    local function entry(text, fill, outline)
        local color = UI.GetColorValue(fill)
        return {text, outline and UI.GetColorValue(outline) or color, outlined = outline ~= nil}
    end
    local result = {
        LensTextKey = quarter.locName,
        Legend = {
            -- UI swatches need opaque colours against the blue key backing;
            -- terrain fill alpha must never make the legend unreadably dark.
            entry("LOC_TOOLTIP_CSC_LENS_QUARTER_EMPTY", quarter.quarterOutlineColor, quarter.quarterOutlineColor),
            entry("LOC_TOOLTIP_CSC_LENS_QUARTER_READY", quarter.quarterOutlineColor),
            entry("LOC_TOOLTIP_CSC_LENS_BASE", "COLOR_CSC_LENS_LEGEND_BASE", "COLOR_CSC_LENS_BASE_OUTLINE"),
            entry("LOC_TOOLTIP_CSC_LENS_BASE_READY", "COLOR_CSC_LENS_LEGEND_BASE"),
            entry("LOC_TOOLTIP_CSC_LENS_SPEC", "COLOR_CSC_LENS_LEGEND_SPEC", "COLOR_CSC_LENS_SPEC_OUTLINE"),
            entry("LOC_TOOLTIP_CSC_LENS_SPEC_READY", "COLOR_CSC_LENS_LEGEND_SPEC"),
            entry("LOC_TOOLTIP_CSC_LENS_SALE_DISTRICT", "COLOR_CSC_LENS_LEGEND_SALE", "COLOR_CSC_LENS_SALE_OUTLINE"),
            entry("LOC_TOOLTIP_CSC_LENS_SALE_READY", "COLOR_CSC_LENS_LEGEND_SALE"),
        },
    }
    if next(quarter.goodsSet) then
        table.insert(result.Legend, entry("LOC_TOOLTIP_CSC_LENS_GOODS", "COLOR_CSC_LENS_GOODS_OUTLINE"))
    end
    return result
end

local function QuarterHasBuilding(quarter, plot)
    local present = WorkingBuildings(plot, plot:GetOwner())
    if present == nil then return false end
    -- Stage membership excludes automatically granted river/access flags and
    -- hidden Service buildings. A real, unpillaged Quarter building counts.
    for _, stage in ipairs({2, 3, 4}) do
        if HasAny(quarter.flowStages[stage], present) then return true end
    end
    return false
end

-- Share material/customer classification and ready markers between both views.
-- This is planning data, not a prediction of ownership-gated adjacency yields.
function S.GetPlotEntries(key, includeIgnored, background)
    local quarter = S.Quarters[key]
    local playerID = Game.GetLocalPlayer()
    local visibility = PlayersVisibility[playerID]
    if quarter == nil or visibility == nil then return {} end
    local colors = {
        QUARTER = UI.GetColorValue(quarter.quarterColor),
        QUARTER_EMPTY = UI.GetColorValue(quarter.quarterEmptyColor),
        BASE_IMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_BASE_IMPROVED"),
        BASE_UNIMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_BASE_UNIMPROVED"),
        SPEC_IMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_SPEC_IMPROVED"),
        SPEC_UNIMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_SPEC_UNIMPROVED"),
        SALE = UI.GetColorValue("COLOR_CSC_LENS_SALE_DISTRICT"),
        SALE_UNREADY = UI.GetColorValue("COLOR_CSC_LENS_SALE_UNREADY"),
        GOODS = UI.GetColorValue("COLOR_CSC_LENS_GOODS"),
        GOODS_UNREADY = UI.GetColorValue("COLOR_CSC_LENS_GOODS_UNREADY"),
    }
    -- The lens collects background plot indices separately from its entries.
    if includeIgnored ~= false then colors.IGNORE = UI.GetColorValue("COLOR_CSC_LENS_IGNORE") end
    local result = {}
    local width, height = Map.GetGridSize()
    for index = 0, width * height - 1 do
        local plot = Map.GetPlotByIndex(index)
        if visibility:IsRevealed(plot:GetX(), plot:GetY()) then
            local district = GameInfo.Districts[plot:GetDistrictType()]
            local districtType = district and district.DistrictType
            local wonder = CompletedMappedWonder(quarter, plot, districtType)
            local resourceType = nil
            if CSC_Adjacency.ResourceVisible(playerID, plot:GetResourceType()) then
                resourceType = GameInfo.Resources[plot:GetResourceType()].ResourceType
            end
            -- Specificity wins: Quarter/customer sites take precedence over a
            -- resource on the same plot, and Base wins a shared Base/Spec match.
            local category = nil
            if districtType == quarter.districtType then category = "QUARTER"
            elseif quarter.goodsSet[districtType] then category = "GOODS"
            elseif wonder or quarter.saleSet[districtType] then category = "SALE"
            elseif quarter.baseSet[resourceType] then category = "BASE"
            elseif quarter.specSet[resourceType] then category = "SPEC" end
            if category == nil and background then
                background[#background + 1] = index
            end
            if category == "BASE" or category == "SPEC" then
                local improved = plot:GetImprovementType() ~= -1 and not plot:IsImprovementPillaged()
                category = category .. (improved and "_IMPROVED" or "_UNIMPROVED")
            end
            local readyStyle = nil
            if category == "BASE_IMPROVED" then readyStyle = "BASE"
            elseif category == "SPEC_IMPROVED" then readyStyle = "SPEC"
            elseif category == "SALE" and (wonder or HasCustomerBuilding(quarter, districtType, plot)) then readyStyle = "SALE"
            elseif category == "GOODS" and WorkingBuildings(plot, plot:GetOwner()) then readyStyle = "GOODS" end
            local color = category == "SALE" and readyStyle == nil and colors.SALE_UNREADY or colors[category or "IGNORE"]
            if category == "GOODS" and readyStyle == nil then color = colors.GOODS_UNREADY end
            local isReady = readyStyle ~= nil
            if category == "QUARTER" then
                isReady = QuarterHasBuilding(quarter, plot)
                color = isReady and colors.QUARTER or colors.QUARTER_EMPTY
            end
            if color ~= nil then
                local definition = (category == "QUARTER" or category == "SALE" or category == "GOODS")
                    and (wonder or district) or (resourceType and GameInfo.Resources[resourceType])
                table.insert(result, {
                    index = index, quarterKey = key, category = category or "IGNORE", color = color,
                    readyStyle = readyStyle,
                    -- All relevant tiles are outlined and filled: 30% for
                    -- unready Base, 20% for other unready sites, 60% ready.
                    outlineStyle = category and (category:match("^BASE_") and "BASE"
                        or category:match("^SPEC_") and "SPEC" or category == "SALE" and "SALE"
                        or category == "QUARTER" and "QUARTER" or category == "GOODS" and "GOODS"),
                    ready = isReady,
                    icon = definition and "ICON_" .. (definition.BuildingType or definition.DistrictType or definition.ResourceType),
                    name = definition and definition.Name,
                    wonder = wonder,
                    pillaged = plot:IsImprovementPillaged(),
                })
            end
        end
    end
    return result
end

function S.GetColorPlotTable(key, includeIgnored)
    -- Adapt the shared per-plot records to color -> plot-list buckets.
    -- Placement uses the same buckets but omits the grey background category.
    local quarter = S.Quarters[key]
    if quarter == nil or PlayersVisibility[Game.GetLocalPlayer()] == nil then return {} end
    local result = {}
    -- Preserve empty palette buckets for callers switching Quarter palettes.
    result[UI.GetColorValue(quarter.quarterColor)] = {}
    result[UI.GetColorValue(quarter.quarterEmptyColor)] = {}
    for _, suffix in ipairs({"BASE_IMPROVED", "BASE_UNIMPROVED", "SPEC_IMPROVED", "SPEC_UNIMPROVED"}) do
        result[UI.GetColorValue(quarter.colorPrefix .. "_" .. suffix)] = {}
    end
    result[UI.GetColorValue("COLOR_CSC_LENS_SALE_DISTRICT")] = {}
    result[UI.GetColorValue("COLOR_CSC_LENS_SALE_UNREADY")] = {}
    if next(quarter.goodsSet) then
        result[UI.GetColorValue("COLOR_CSC_LENS_GOODS")] = {}
        result[UI.GetColorValue("COLOR_CSC_LENS_GOODS_UNREADY")] = {}
    end
    if includeIgnored ~= false then result[UI.GetColorValue("COLOR_CSC_LENS_IGNORE")] = {} end
    for _, entry in ipairs(S.GetPlotEntries(key, includeIgnored)) do
        table.insert(result[entry.color], entry.index)
    end
    return result
end

-- Both UI owners use the same renderer, while retaining separate native objects.
HasAny = function(candidates, present)
    for index in pairs(candidates or {}) do if present[index] then return true end end
    return false
end

-- Native UI APIs: completion and pillage are checked on the exact district
-- plot, and buildings come from GetBuildingsAtLocation, never a city-wide test.
WorkingBuildings = function(plot, playerID)
    if plot:GetOwner() ~= playerID then return nil end
    local city = Cities.GetPlotPurchaseCity(plot)
    if city == nil or city:GetOwner() ~= playerID then return nil end
    local district = GameInfo.Districts[plot:GetDistrictType()]
    if district == nil then return nil end
    local districts = city:GetDistricts()
    if districts.IsComplete == nil or not districts:IsComplete(district.Index, plot:GetIndex()) then return nil end
    if districts:IsPillaged(district.Index, plot:GetIndex()) then return nil end
    local buildings, present = city:GetBuildings(), {}
    for _, index in ipairs(buildings:GetBuildingsAtLocation(plot:GetIndex())) do
        if buildings:HasBuilding(index) and not buildings:IsPillaged(index) then present[index] = true end
    end
    return present
end

function S.GetFlowLinks(key, entries)
    local quarter = S.Quarters[key]
    local playerID = Game.GetLocalPlayer()
    if quarter == nil or playerID == -1 then return {} end
    entries = entries or S.GetPlotEntries(key, false)
    local byPlot, links, seen, buildingCache = {}, {}, {}, {}
    for _, entry in ipairs(entries) do byPlot[entry.index] = entry end
    local function buildings(plot)
        local index = plot:GetIndex()
        if buildingCache[index] == nil then buildingCache[index] = WorkingBuildings(plot, playerID) or false end
        return buildingCache[index] or nil
    end
    local function add(source, target, kind, yieldType, stage)
        -- An unmapped customer yield must not invent a gold/production delivery.
        if yieldType == nil or S.FlowYieldColors[yieldType] == nil then return end
        local id = source .. ":" .. target .. ":" .. kind .. ":" .. yieldType
        if not seen[id] then
            seen[id] = {source = source, target = target, kind = kind, yieldType = yieldType}
            table.insert(links, seen[id])
        end
        if stage then
            local link = seen[id]
            link.stages = link.stages or {}
            link.stages[stage] = true
        end
    end
    for _, entry in ipairs(entries) do
        if entry.category == "QUARTER" then
            local plot = Map.GetPlotByIndex(entry.index)
            local producerBuildings = buildings(plot)
            if producerBuildings then
                for _, adjacent in ipairs(Map.GetAdjacentPlots(plot:GetX(), plot:GetY())) do
                    local neighbor = byPlot[adjacent:GetIndex()]
                    -- Entries already enforce revelation/discovery. Both ends
                    -- must be owned by this player, within the actual adjacency
                    -- ring. Goods Providers grant adjacency only, so they
                    -- appear in the overlay without a transaction link.
                    if neighbor and adjacent:GetOwner() == playerID then
                        if neighbor.readyStyle == "BASE" and HasAny(quarter.flowStages[2], producerBuildings) then
                            add(neighbor.index, entry.index, "BASE", quarter.materialYield)
                        elseif neighbor.readyStyle == "SPEC" and HasAny(quarter.flowStages[4], producerBuildings) then
                            add(neighbor.index, entry.index, "SPEC", quarter.materialYield)
                        elseif neighbor.category == "SALE" and neighbor.readyStyle == "SALE" then
                            local wonder = neighbor.wonder
                            if wonder then
                                -- A Wonder's plot is authoritative. Native Wonder
                                -- tiles need not expose a normal district/building list.
                                local stage = quarter.wonderProducerStages[wonder.BuildingType]
                                if stage and WorkingWonder(adjacent, playerID, wonder)
                                    and HasAny(quarter.flowStages[stage], producerBuildings) then
                                    add(entry.index, neighbor.index, "SALE", quarter.wonderYields[wonder.BuildingType], stage)
                                end
                            else
                                local customerBuildings = buildings(adjacent)
                                local district = GameInfo.Districts[adjacent:GetDistrictType()]
                                for _, mapping in ipairs(quarter.flowCustomers) do
                                    if customerBuildings and district and mapping.districtType == district.DistrictType
                                        and HasAny(mapping.producers, producerBuildings)
                                        and HasAny(mapping.customers, customerBuildings) then
                                        -- Same return-yield tags as the adjacency processor,
                                        -- including its already-propagated unique districts.
                                        for yieldType in pairs(quarter.customerYields[district.DistrictType] or {}) do
                                            add(entry.index, neighbor.index, "SALE", yieldType, mapping.stage)
                                        end
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    table.sort(links, function(a, b)
        if a.source ~= b.source then return a.source < b.source end
        if a.target ~= b.target then return a.target < b.target end
        if a.kind ~= b.kind then return a.kind < b.kind end
        return a.yieldType < b.yieldType
    end)
    return links
end

-- Exact customer identity restricts placement, while the tooltip deliberately
-- reports the same cumulative city effect as the corresponding MCUIS icon.
function S.GetServiceMarkers(key, entries, collect)
    local playerID = Game.GetLocalPlayer()
    if playerID == -1 then return {} end
    local current
    local markers = {}
    for _, entry in ipairs(entries or S.GetPlotEntries(key, false)) do
        if entry.category == "SALE" and entry.readyStyle == "SALE" then
            local plot = Map.GetPlotByIndex(entry.index)
            local city = plot and Cities.GetPlotPurchaseCity(plot)
            if city and plot:GetOwner() == playerID and (not entry.wonder or WorkingWonder(plot, playerID, entry.wonder)) then
                current = current or (collect or Presentation.Collect)(playerID)
                local effects = current[city:GetID()] or {}
                local groups = {}
                local buildings, buildingsAtPlot
                for effectID, effect in pairs(effects) do
                    local row = effect.row
                    local target = row.AbilityIconTarget
                    if row.NotificationQuarter == key and target and target:find("_SERVICE", 1, true) then
                        if entry.wonder then
                            -- Use the same location check as the other Wonder
                            -- UIs. Live effects still gate lens pins, unlike tooltips.
                            buildings = buildings or city:GetBuildings()
                            buildingsAtPlot = buildingsAtPlot or buildings:GetBuildingsAtLocation(entry.index)
                            local service = Presentation.FindServiceOnPlot(buildingsAtPlot, target)
                            if service and not buildings:IsPillaged(service.Index) then groups[target] = true end
                        elseif effect.districts[plot:GetDistrictID()] then
                            groups[target] = true
                        end
                    end
                end
                for target in pairs(groups) do
                    local ids, tooltip, icon = {}, {}, nil
                    for effectID, effect in pairs(effects) do
                        if effect.row.NotificationQuarter == key and effect.row.AbilityIconTarget == target then
                            table.insert(ids, effectID)
                        end
                    end
                    table.sort(ids)
                    for _, effectID in ipairs(ids) do
                        local data = Presentation.Format(effectID, effects[effectID].count, playerID)
                        if data then
                            icon = data.icon
                            table.insert(tooltip, data.tooltip)
                        end
                    end
                    local stage = tonumber(target:match("^BUILDING_CSC_" .. key .. "_STAGE_([234])_SERVICE"))
                    markers[#markers+1] = {index=entry.index, target=target, icon=icon, stage=stage, isWonder=entry.wonder ~= nil,
                        tooltip=table.concat(tooltip, "[NEWLINE][NEWLINE]")}
                end
            end
        end
    end
    table.sort(markers, function(a,b)
        return a.index < b.index or (a.index == b.index and a.target < b.target)
    end)
    return markers
end

function S.GetServicePlots(key, entries)
    local plots, seen = {}, {}
    for _, marker in ipairs(S.GetServiceMarkers(key, entries)) do
        if not seen[marker.index] then seen[marker.index] = true; plots[#plots+1] = marker.index end
    end
    return plots
end

local function PublishServicePins(owner, key, markers, links)
    -- Keep a small UI-only snapshot for a context loaded after its first draw.
    -- No map pins, gameplay properties, or saved player configuration are made.
    if ExposedMembers then
        ExposedMembers.CSC_QuarterServicePins = ExposedMembers.CSC_QuarterServicePins or {}
        ExposedMembers.CSC_QuarterServicePins[owner] = {key=key, markers=markers, links=links}
    end
    if LuaEvents and LuaEvents.CSC_QuarterServicePins_Update then
        LuaEvents.CSC_QuarterServicePins_Update(owner, key, markers, links)
    end
end

-- Start at the exact customer plot and follow only sales from its Service stage.
-- Then look one ring around each producer for improved, unpillaged materials.
function S.FindServiceMarker(markers, selection)
    if selection == nil then return nil end
    for _, candidate in ipairs(markers) do
        if candidate.index == selection.index and candidate.target == selection.target and candidate.icon and candidate.stage then
            return candidate
        end
    end
end

local function ServiceFocus(selection, markers, entries, links, quarter, cached)
    local marker = quarter and S.FindServiceMarker(markers, selection)
    if marker == nil then return nil end
    local serviceKey = marker.index .. ":" .. marker.target
    if cached[serviceKey] then return cached[serviceKey] end

    local plots, producers, byPlot = {[marker.index] = true}, {}, {}
    local baseLinks, additionalLinks = {}, {}
    for _, entry in ipairs(entries) do byPlot[entry.index] = entry end
    for _, link in ipairs(links) do
        if link.kind == "BASE" then baseLinks[link.source .. ":" .. link.target] = true end
    end
    local playerID = Game.GetLocalPlayer()
    for _, link in ipairs(links) do
        if link.target == marker.index and link.stages and link.stages[marker.stage] and not producers[link.source] then
            local producer = Map.GetPlotByIndex(link.source)
            producers[link.source], plots[link.source] = true, true
            for _, adjacent in ipairs(Map.GetAdjacentPlots(producer:GetX(), producer:GetY())) do
                local feeder = byPlot[adjacent:GetIndex()]
                if feeder and adjacent:GetOwner() == playerID
                    and (feeder.readyStyle == "BASE" or (marker.stage == 4 and feeder.readyStyle == "SPEC")) then
                    plots[feeder.index] = true
                    -- Later Services also require Base. The ordinary map only
                    -- animates Base into a working stage 2 building, which can
                    -- be pillaged even while a later Service still uses Base.
                    if feeder.readyStyle == "BASE" and not baseLinks[feeder.index .. ":" .. link.source] then
                        additionalLinks[#additionalLinks + 1] = {
                            source = feeder.index, target = link.source, kind = "BASE", yieldType = quarter.materialYield,
                        }
                    end
                end
            end
        end
    end
    local focus = {plots = plots, producers = producers, index = marker.index, stage = marker.stage, additionalLinks = additionalLinks}
    cached[serviceKey] = focus
    return focus
end

local function QuarterLinkPlot(link, index)
    if link.kind == "SALE" then
        if link.source == index then return link.target end
    elseif link.target == index then
        return link.source
    end
end

local function QuarterFocus(selection, data)
    local index = selection.index
    if not data.quarterPins[index] then return nil end
    if data.focusByQuarter[index] then return data.focusByQuarter[index] end
    -- Adjacent materials and sites stay visible even before they can trade.
    -- DrawFlows independently checks which working links touch this Quarter.
    local plots = {[index] = true}
    local plot = Map.GetPlotByIndex(index)
    for _, adjacent in ipairs(Map.GetAdjacentPlots(plot:GetX(), plot:GetY())) do
        local adjacentIndex = adjacent:GetIndex()
        if data.quarterNeighbors[adjacentIndex] then plots[adjacentIndex] = true end
    end
    local focus = {index = index, plots = plots, isQuarter = true}
    data.focusByQuarter[index] = focus
    return focus
end

local function WithAlpha(color, alpha)
    local rgba = color % 0x1000000 + alpha * 0x1000000
    return rgba >= 0x80000000 and rgba - 0x100000000 or rgba
end

local function DrawFlows(owner, key, links, focus)
    local overlay = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Flow")
    local signature, waves = {key or ""}, {}
    for _, link in ipairs(links) do
        local color = UI.GetColorValue(S.FlowYieldColors[link.yieldType])
        local peakAlpha
        if focus then
            local focused
            if focus.isQuarter then
                focused = QuarterLinkPlot(link, focus.index) ~= nil
            elseif link.kind == "SALE" then
                focused = link.target == focus.index and link.stages and link.stages[focus.stage]
            else
                focused = focus.producers[link.target] and focus.plots[link.source]
                    and (link.kind == "BASE" or focus.stage == 4)
            end
            peakAlpha = focused and 204 or 26
            color = WithAlpha(color, peakAlpha)
        end
        table.insert(signature, link.source .. ":" .. link.target .. ":" .. link.kind .. ":" .. link.yieldType
            .. ":" .. tostring(color) .. ":" .. tostring(peakAlpha or ""))
        -- Native in-game review confirms positive-speed arrows travel from
        -- pos1 to pos2. Anchor the effect on the semantic source tile itself.
        table.insert(waves, {pos1 = link.source, pos2 = link.target,
            color = color,
            speed = 2, type = "CIVILIZATION_UNKNOWN", peakAlpha = peakAlpha})
    end
    local nextSignature = table.concat(signature, "|")
    local available = overlay ~= nil
    if S.FlowSignatures[owner] ~= nextSignature or S.FlowOverlayAvailable ~= available then
        if overlay then
            overlay:ResetAllWaves()
            if #waves > 0 then overlay:CreateLinearWaves(waves) end
        end
        S.FlowSignatures[owner] = nextSignature
        S.FlowOverlayAvailable = available
        if LuaEvents and LuaEvents.CSC_QuarterFlowTrial_Update then
            LuaEvents.CSC_QuarterFlowTrial_Update(owner, waves)
        end
    end
    -- Repeated UI refreshes must not continually restart an unchanged effect.
    local trial = ExposedMembers and ExposedMembers.CSC_QuarterFlowTrial
    if overlay then overlay:SetVisible(#waves > 0 and not (trial and trial.Enabled and trial.Ready)) end
    return #waves, available
end

function S.ClearOverlay(owner, preserveSharedFill)
    if owner ~= "Lens" and owner ~= "Placement" then return end
    if owner == "Lens" and S.NativeLensFillOwned then
        if not preserveSharedFill then UILens.ClearLayerHexes(UILens.CreateLensLayerHash("Hex_Coloring_Appeal_Level")) end
        S.NativeLensFillOwned = false
    end
    local fill = UILens.GetOverlay("CSC_Quarter" .. owner)
    if fill then fill:ClearPlotChannel(); fill:SetVisible(false) end
    local ready = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Ready")
    if ready then ready:ClearAll(); ready:SetVisible(false) end
    local textureFill = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Fill")
    if textureFill then textureFill:ClearAll(); textureFill:SetVisible(false) end
    local tint = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Tint")
    if tint then tint:ClearAll(); tint:SetVisible(false) end
    S.SpriteSignatures[owner .. "_Fill"] = nil
    S.SpriteSignatures[owner .. "_Ready"] = nil
    S.SpriteSignatures[owner .. "_Tint"] = nil
    if owner == "Lens" then
        local shade = UILens.GetOverlay("CSC_QuarterLens_Shade")
        if shade then shade:ClearAll(); shade:SetVisible(false) end
        S.BackgroundShadeSignature, S.FocusShadeSignature = nil, nil
        local flow = UILens.GetOverlay("CSC_QuarterLens_Flow")
        if flow then flow:ResetAllWaves(); flow:SetVisible(false) end
        if LuaEvents and LuaEvents.CSC_QuarterFlowTrial_Update then LuaEvents.CSC_QuarterFlowTrial_Update(owner, {}) end
        PublishServicePins(owner, nil, {})
        S.FlowSignatures[owner], S.FlowOverlayAvailable = nil, nil
        S.ActiveLensData, S.ActiveLensMarkers, S.NativeFillSignature = nil, nil, nil
    end
end

-- GameCore publishes and deferred activation can refresh an unchanged lens.
-- Keep native sprite instances alive across those calls: clearing/hiding and
-- recreating them on every refresh can expose gaps in asynchronous rendering.
-- Signature includes exact plots, styles and channels, not just their counts.
local function DrawSpriteGroups(owner, suffix, overlay, groups)
    local key = owner .. suffix
    if overlay == nil then S.SpriteSignatures[key] = nil; return 0, false end
    local signature, count = {}, 0
    for _, group in ipairs(groups) do
        table.sort(group.plots)
        count = count + #group.plots
        table.insert(signature, group.style .. ":" .. tostring(group.channel) .. "=" .. table.concat(group.plots, ","))
    end
    local nextSignature = table.concat(signature, "|")
    if S.SpriteSignatures[key] == nextSignature then return count, false end
    overlay:ClearAll()
    for _, group in ipairs(groups) do
        if #group.plots > 0 then
            overlay:CreateSprites(group.plots, UILens.CreateLensLayerHash(group.style), group.channel)
        end
    end
    overlay:SetVisible(count > 0)
    S.SpriteSignatures[key] = nextSignature
    return count, true
end

-- Firaxis Black Death/WorldBuilder use this direct RGBA path. It avoids the
-- Appeal dispatcher's forced alpha and keeps terrain-following native hexes.
-- As with sprites, retain unchanged assignments to avoid render churn.
local function DrawTintGroups(key, overlay, groups)
    if overlay == nil then S.SpriteSignatures[key] = nil; return 0, false end
    local parts, count, order = {}, 0, {}
    for color in pairs(groups) do table.insert(order, color) end
    table.sort(order)
    for _, color in ipairs(order) do
        table.sort(groups[color])
        count = count + #groups[color]
        table.insert(parts, tostring(color) .. "=" .. table.concat(groups[color], ","))
    end
    local signature = table.concat(parts, "|")
    if S.SpriteSignatures[key] == signature then return count, false end
    overlay:ClearAll()
    for _, color in ipairs(order) do overlay:HighlightColoredHexes(groups[color], color, 0) end
    overlay:SetChannelOn(0)
    overlay:SetVisible(count > 0)
    S.SpriteSignatures[key] = signature
    return count, true
end

local emptyShade = {}
local function DrawBackgroundShade(data, dimPatterns)
    local shade = UILens.GetOverlay("CSC_QuarterLens_Shade")
    if shade == nil then
        S.BackgroundShadeSignature, S.FocusShadeSignature = nil, nil
        return 0
    end
    local background = data.background or emptyShade
    local outside = {}
    if dimPatterns then
        for _, kind in ipairs(overlayKinds) do
            for _, index in ipairs(dimPatterns[kind]) do outside[#outside + 1] = index end
        end
    end
    -- Use the same native layer for both sets. Cache the background key so
    -- switching focus only has to compare the much shorter set of changed tiles.
    data.backgroundShadeSignature = data.backgroundShadeSignature or table.concat(background, ",")
    local focusSignature = table.concat(outside, ",")
    local count = #background + #outside
    if S.BackgroundShadeSignature ~= data.backgroundShadeSignature or S.FocusShadeSignature ~= focusSignature then
        local plots = background
        if #outside > 0 then
            plots = {}
            for _, index in ipairs(background) do plots[#plots + 1] = index end
            for _, index in ipairs(outside) do plots[#plots + 1] = index end
        end
        shade:ClearAll()
        if count > 0 then
            shade:HighlightColoredHexes(plots, UI.GetColorValue("COLOR_CSC_LENS_BACKGROUND_SHADE"), 0)
            shade:SetChannelOn(0)
        end
        shade:SetVisible(count > 0)
        S.BackgroundShadeSignature, S.FocusShadeSignature = data.backgroundShadeSignature, focusSignature
    end
    return count
end

function S.CollectServiceEffects(playerID)
    return Presentation.Collect(playerID)
end

function S.PublishPreparedServicePins(data)
    local markers = data.markers or {}
    if S.ActiveLensData == data and S.ActiveLensMarkers == markers then return end
    S.ActiveLensData, S.ActiveLensMarkers = data, markers
    local pins = {}
    for _, marker in ipairs(markers) do pins[#pins + 1] = marker end
    for _, marker in pairs(data.quarterPins or {}) do pins[#pins + 1] = marker end
    PublishServicePins("Lens", data.key, pins, data.links)
end

function S.PrepareOverlay(entries, staticOnly, collect)
    local key = entries[1] and entries[1].quarterKey
    if staticOnly then return {entries = entries, key = key} end
    local quarterPins, quarterNeighbors = {}, {}
    local quarter = S.Quarters[key]
    if quarter then
        for _, entry in ipairs(entries) do
            if entry.category == "QUARTER" then
                quarterPins[entry.index] = {
                    index = entry.index, icon = "ICON_" .. quarter.districtType, isQuarter = true,
                }
            elseif entry.outlineStyle then
                quarterNeighbors[entry.index] = true
            end
        end
    end
    return {entries = entries, key = key, links = S.GetFlowLinks(key, entries),
        quarterPins = quarterPins, quarterNeighbors = quarterNeighbors, focusByQuarter = {}, focusByService = {},
        markers = key and S.GetServiceMarkers(key, entries, collect) or {}}
end

function S.DrawPreparedOverlay(owner, data, forceBackground, selection)
    if owner ~= "Lens" and owner ~= "Placement" then return false end
    local key, entries = data.key, data.entries
    local quarter = S.Quarters[key]
    local function spriteKind(kind)
        return kind == "QUARTER" and quarter and quarter.quarterStyle or kind
    end
    local fill = UILens.GetOverlay("CSC_Quarter" .. owner)
    local textureFill = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Fill")
    local tint = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Tint")
    if owner == "Placement" and fill == nil and textureFill == nil and tint == nil then S.ClearOverlay(owner); return false end
    local isLens = owner == "Lens"
    local links, markers = data.links or {}, data.markers or {}
    local focus
    if isLens and selection then
        if selection.isQuarter then
            focus = QuarterFocus(selection, data)
        else
            data.focusByService = data.focusByService or {}
            focus = ServiceFocus(selection, markers, entries, links, quarter, data.focusByService)
        end
    end
    if focus and focus.additionalLinks and #focus.additionalLinks > 0 then
        -- Keep the normal snapshot intact for later selection changes.
        links = {}
        for _, link in ipairs(data.links) do links[#links + 1] = link end
        for _, link in ipairs(focus.additionalLinks) do links[#links + 1] = link end
    end
    if fill then fill:ClearPlotChannel(); fill:SetVisible(false) end
    local colors, patterns, dimPatterns = {}, {}, {}
    for _, kind in ipairs(overlayKinds) do patterns[kind], dimPatterns[kind] = {}, {} end
    local texturedPlots, tintPlots = {}, {}
    for _, entry in ipairs(entries) do
        local kind, color = entry.outlineStyle, entry.color
        local dim = focus and kind and not focus.plots[entry.index]
        local state = entry.ready and "Ready" or "Unready"
        if kind then
            local group = dim and dimPatterns or patterns
            table.insert(group[kind], entry.index)
            if dim then
                state = entry.ready and "FocusReady" or "FocusUnready"
                color = WithAlpha(color, entry.ready and 77 or 26)
            elseif not isLens then
                state = entry.ready and "Dim" or "Faint"
                color = WithAlpha(color, entry.ready and 102 or 51)
            end
        end
        if tint and kind then
            tintPlots[color] = tintPlots[color] or {}
            table.insert(tintPlots[color], entry.index)
        elseif textureFill and kind then
            local style = "CSC_Lens_Fill_" .. spriteKind(kind) .. "_" .. state
            texturedPlots[style] = texturedPlots[style] or {}
            table.insert(texturedPlots[style], entry.index)
        elseif kind and color ~= nil then
            colors[color] = colors[color] or {}
            table.insert(colors[color], entry.index)
        end
    end
    -- Native BorderOverlay colours are stored in allocated style slots. A
    -- non-nil overlay object alone does not prove those slots exist. Reserve 0
    -- and use positive fill channels, like XP2 PowerCityPlots; allocate every
    -- slot with the native InitializeStyles(count, materialHash) API first.
    local count = 0
    for _ in pairs(colors) do count = count + 1 end
    local nativeFill = isLens and UILens.CreateLensLayerHash("Hex_Coloring_Appeal_Level") or nil
    local nativeSignature, repaintNative = nil, false
    if nativeFill then
        -- Keep unchanged background assignments too. Activation explicitly
        -- forces one settled repaint after deferred native/More painters.
        local parts = {}
        for color, plots in pairs(colors) do
            table.sort(plots)
            table.insert(parts, tostring(color) .. "=" .. table.concat(plots, ","))
        end
        table.sort(parts)
        nativeSignature = table.concat(parts, "|")
        repaintNative = forceBackground == true or not S.NativeLensFillOwned or S.NativeFillSignature ~= nativeSignature
        if repaintNative then UILens.ClearLayerHexes(nativeFill) end
        S.NativeLensFillOwned = true
    elseif fill then
        fill:InitializeStyles(count + 1, UILens.CreateLensLayerHash("MapSearchBorder"))
        fill:ShowHighlights(true)
        fill:ShowBorders(false)
    end
    local channel = 1
    local palette = {}
    for color, plots in pairs(colors) do
        if nativeFill then
            if repaintNative then UILens.SetLayerHexesColoredArea(nativeFill, Game.GetLocalPlayer(), plots, color) end
        elseif fill then
            fill:SetHighlightColor(channel, color)
            fill:SetPlotChannel(plots, channel)
        end
        table.insert(palette, tostring(color) .. "=" .. tostring(#plots))
        channel = channel + 1
    end
    if nativeFill then S.NativeFillSignature = nativeSignature end
    if not nativeFill and fill then fill:SetVisible(count > 0) end
    -- The native Appeal dispatcher strips supplied alpha and forces 0x80.
    -- Direct native hex highlights supply category RGBA. Keep the texture
    -- path as a missing-new-art fallback.
    local shadedCount = isLens and DrawBackgroundShade(data, focus and dimPatterns) or 0
    local texturedCount, textureChannel, fillRebuilt = 0, 0, false
    local fillGroups = {}
    if textureFill then
        for _, kind in ipairs(overlayKinds) do
            for _, state in ipairs({"Unready", "Ready", "Faint", "Dim", "FocusReady", "FocusUnready"}) do
                local style = "CSC_Lens_Fill_" .. spriteKind(kind) .. "_" .. state
                local plots = texturedPlots[style]
                if plots then
                    table.insert(fillGroups, {plots = plots, style = style, channel = textureChannel})
                    table.insert(palette, style .. "=" .. tostring(#plots))
                    texturedCount = texturedCount + #plots
                    textureChannel = textureChannel + 1
                end
            end
        end
    end
    texturedCount, fillRebuilt = DrawSpriteGroups(owner, "_Fill", textureFill, fillGroups)
    local tintCount, tintRebuilt = DrawTintGroups(owner .. "_Tint", tint, tintPlots)
    for color, plots in pairs(tintPlots) do
        table.insert(palette, "directRGBA:" .. tostring(color) .. "=" .. tostring(#plots))
    end
    local ready = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Ready")
    local outlineGroups = {}
    local readyMaterial = "CSC_Lens_HexOutline"
    if ready then
        -- Draw a transparent-centred hex-edge texture with Firaxis's native
        -- placement Texture/HEX_GEO path. The spline layer accepted assignments
        -- but stayed invisible in repeated native review. Each sprite is one
        -- plot, so adjacent relevant plots keep their shared edge as well.
        for index, kind in ipairs(overlayKinds) do
            if #patterns[kind] > 0 then
                local prefix = isLens and "CSC_Lens_Ready_" or "CSC_Lens_Dim_"
                table.insert(outlineGroups, {plots = patterns[kind], style = prefix .. spriteKind(kind), channel = index - 1})
            end
            if #dimPatterns[kind] > 0 then
                table.insert(outlineGroups, {plots = dimPatterns[kind], style = "CSC_Lens_Faint_" .. spriteKind(kind), channel = index - 1 + #overlayKinds})
            end
        end
    end
    local outlined, outlinesRebuilt = DrawSpriteGroups(owner, "_Ready", ready, outlineGroups)
    local flows, flowAvailable, serviceCount = 0, false, 0
    table.sort(palette)
    if isLens then
        flows, flowAvailable = DrawFlows(owner, key, links, focus)
        serviceCount = #markers
        -- A cached Quarter becomes the current publisher again when reopened.
        -- Publish last because removing a focused pin can repaint synchronously.
        S.PublishPreparedServicePins(data)
    end
    return count > 0 or texturedCount > 0 or tintCount > 0 or shadedCount > 0 or (ready ~= nil and outlined > 0) or flows > 0, {
        channels = count, styles = nativeFill and 0 or count + 1,
        outlines = ready and outlined or 0,
        flows = flows, flowAvailable = flowAvailable, flowSignature = S.FlowSignatures[owner],
        services = serviceCount, servicesAvailable = isLens, servicesRebuilt = false,
        readyAvailable = ready ~= nil, readyMaterial = readyMaterial, readyStyles = ready and #outlineGroups or 0,
        textureFillAvailable = textureFill ~= nil, textureFillPlots = texturedCount,
        fillRebuilt = fillRebuilt, outlinesRebuilt = outlinesRebuilt,
        tintAvailable = tint ~= nil, tintPlots = tintCount, tintRebuilt = tintRebuilt,
        backgroundRepainted = repaintNative,
        palette = table.concat(palette, ","),
        backend = tint and "HexHighlightOverlay" or textureFill and "textured hexes"
            or (nativeFill and "native coloured hexes (fallback: fixed alpha)" or "BorderOverlay (fallback)"),
    }
end

function S.DrawOverlay(owner, entries, forceBackground, selection)
    return S.DrawPreparedOverlay(owner, S.PrepareOverlay(entries, owner == "Placement"), forceBackground, selection)
end
