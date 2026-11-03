-- Shared planning overlay data for manual lenses and native district placement.
-- Does not depend on More Lenses and never writes gameplay properties.
if CSC_QuarterLensSupport ~= nil then return end
if CSC_Adjacency == nil then include("CSC_AdjacencyCore") end

CSC_QuarterLensSupport = { Quarters = {}, ByDistrict = {}, FlowSignatures = {}, SpriteSignatures = {} }
local S = CSC_QuarterLensSupport

include("CSC_ServicePresentation")
local Presentation = CSC_ServicePresentation

-- Exact UI palettes are shared by the manual lens and placement renderer.
local quarterColors = {}
if GameInfo.CSC_LensQuarterColors then
    for row in GameInfo.CSC_LensQuarterColors() do quarterColors[row.QuarterKey] = row.ColorType end
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
                local quarterColor = quarterColors[key] or "COLOR_CSC_LENS_QUARTER"
                quarter = {
                    id = key, districtType = districtType,
                    locName = "LOC_HUD_CSC_" .. key .. "_LENS",
                    locTooltip = "LOC_HUD_CSC_" .. key .. "_LENS_TOOLTIP",
                    colorPrefix = "COLOR_CSC_LENS",
                    quarterColor = quarterColor,
                    quarterEmptyColor = quarterColor .. "_EMPTY",
                    quarterOutlineColor = quarterColor .. "_OUTLINE",
                    quarterStyle = quarterColor:gsub("^COLOR_CSC_LENS_", ""),
                    locLegendQ = "LOC_TOOLTIP_CSC_LENS_" .. key .. "_QUARTER",
                    baseSet = {}, specSet = {}, saleSet = {}, wonderSaleSet = {}, customerBuildings = {},
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
local function AddCustomer(quarter, districtType, buildingType, producers)
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
            table.insert(quarter.flowCustomers, {districtType = district, customers = customers, producers = producers})
        end
    end
end

if GameInfo.CSC_Stage3CustomerTransactions then
    for row in GameInfo.CSC_Stage3CustomerTransactions() do
        AddCustomer(S.ByDistrict[row.SellerDistrictType], row.CustomerDistrictType, row.CustomerBuildingType, BuildingFamily(row.SellerBuildingType))
    end
end
if GameInfo.CSC_QuarterCustomerBuildings then
    for row in GameInfo.CSC_QuarterCustomerBuildings() do
        local quarter = S.Quarters[row.QuarterKey]
        AddCustomer(quarter, row.DistrictType, row.BuildingType, quarter and quarter.flowStages[row.ProducerStage])
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

function S.GetLensLegend(key)
    local quarter = S.Quarters[key]
    if quarter == nil then return nil end
    local function entry(text, fill, outline)
        local color = UI.GetColorValue(fill)
        return {text, outline and UI.GetColorValue(outline) or color, outlined = outline ~= nil}
    end
    return {
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
function S.GetPlotEntries(key, includeIgnored)
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
    }
    -- Placement leaves irrelevant tiles to the native overlay; manual lenses grey them.
    if includeIgnored ~= false then colors.IGNORE = UI.GetColorValue("COLOR_CSC_LENS_IGNORE") end
    local result = {}
    local width, height = Map.GetGridSize()
    for index = 0, width * height - 1 do
        local plot = Map.GetPlotByIndex(index)
        if visibility:IsRevealed(plot:GetX(), plot:GetY()) then
            local district = GameInfo.Districts[plot:GetDistrictType()]
            local districtType = district and district.DistrictType
            local wonder = GameInfo.Buildings[plot:GetWonderType()]
            local wonderSale = wonder and quarter.wonderSaleSet[wonder.BuildingType]
                and plot:IsWonderComplete()
            local resourceType = nil
            if CSC_Adjacency.ResourceVisible(playerID, plot:GetResourceType()) then
                resourceType = GameInfo.Resources[plot:GetResourceType()].ResourceType
            end
            -- Specificity wins: Quarter/customer sites take precedence over a
            -- resource on the same plot, and Base wins a shared Base/Spec match.
            local category = nil
            if districtType == quarter.districtType then category = "QUARTER"
            elseif wonderSale or quarter.saleSet[districtType] then category = "SALE"
            elseif quarter.baseSet[resourceType] then category = "BASE"
            elseif quarter.specSet[resourceType] then category = "SPEC" end
            if category == "BASE" or category == "SPEC" then
                local improved = plot:GetImprovementType() ~= -1 and not plot:IsImprovementPillaged()
                category = category .. (improved and "_IMPROVED" or "_UNIMPROVED")
            end
            local readyStyle = nil
            if category == "BASE_IMPROVED" then readyStyle = "BASE"
            elseif category == "SPEC_IMPROVED" then readyStyle = "SPEC"
            elseif category == "SALE" and (wonderSale or HasCustomerBuilding(quarter, districtType, plot)) then readyStyle = "SALE" end
            local color = category == "SALE" and readyStyle == nil and colors.SALE_UNREADY or colors[category or "IGNORE"]
            local isReady = readyStyle ~= nil
            if category == "QUARTER" then
                isReady = QuarterHasBuilding(quarter, plot)
                color = isReady and colors.QUARTER or colors.QUARTER_EMPTY
            end
            if color ~= nil then
                local definition = (category == "QUARTER" or category == "SALE")
                    and (wonderSale and wonder or district) or (resourceType and GameInfo.Resources[resourceType])
                table.insert(result, {
                    index = index, quarterKey = key, category = category or "IGNORE", color = color,
                    readyStyle = readyStyle,
                    -- All relevant tiles are outlined and filled: 30% for
                    -- unready Base, 20% for other unready sites, 60% ready.
                    outlineStyle = category and (category:match("^BASE_") and "BASE"
                        or category:match("^SPEC_") and "SPEC" or category == "SALE" and "SALE"
                        or category == "QUARTER" and "QUARTER"),
                    ready = isReady,
                    icon = definition and "ICON_" .. (definition.BuildingType or definition.DistrictType or definition.ResourceType),
                    name = definition and definition.Name,
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
    local wonder = GameInfo.Buildings[plot:GetWonderType()]
    if wonder and (wonder.IsWonder == true or wonder.IsWonder == 1) then
        if not plot:IsWonderComplete() then return nil end
    elseif districts.IsComplete == nil or not districts:IsComplete(district.Index, plot:GetIndex()) then return nil end
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
    local function add(source, target, kind, yieldType)
        -- An unmapped customer yield must not invent a gold/production delivery.
        if yieldType == nil or S.FlowYieldColors[yieldType] == nil then return end
        local id = source .. ":" .. target .. ":" .. kind .. ":" .. yieldType
        if not seen[id] then
            seen[id] = true
            table.insert(links, {source = source, target = target, kind = kind, yieldType = yieldType})
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
                    -- ring; no arrows to an unbuilt placement/hover candidate.
                    if neighbor and adjacent:GetOwner() == playerID then
                        if neighbor.readyStyle == "BASE" and HasAny(quarter.flowStages[2], producerBuildings) then
                            add(neighbor.index, entry.index, "BASE", "YIELD_PRODUCTION")
                        elseif neighbor.readyStyle == "SPEC" and HasAny(quarter.flowStages[4], producerBuildings) then
                            add(neighbor.index, entry.index, "SPEC", "YIELD_PRODUCTION")
                        elseif neighbor.category == "SALE" and neighbor.readyStyle == "SALE" then
                            local customerBuildings = buildings(adjacent)
                            if customerBuildings then
                                local district = GameInfo.Districts[adjacent:GetDistrictType()]
                                for _, mapping in ipairs(quarter.flowCustomers) do
                                    if district and mapping.districtType == district.DistrictType
                                        and HasAny(mapping.producers, producerBuildings)
                                        and HasAny(mapping.customers, customerBuildings) then
                                        -- Same return-yield tags as the adjacency processor,
                                        -- including its already-propagated unique districts.
                                        for yieldType in pairs(quarter.customerYields[district.DistrictType] or {}) do
                                            add(entry.index, neighbor.index, "SALE", yieldType)
                                        end
                                    end
                                end
                                local wonder = GameInfo.Buildings[adjacent:GetWonderType()]
                                local stage = wonder and quarter.wonderProducerStages[wonder.BuildingType]
                                if stage and customerBuildings[wonder.Index] and HasAny(quarter.flowStages[stage], producerBuildings) then
                                    add(entry.index, neighbor.index, "SALE", quarter.wonderYields[wonder.BuildingType])
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
function S.GetServiceMarkers(key, entries)
    local playerID = Game.GetLocalPlayer()
    if playerID == -1 then return {} end
    local current = Presentation.Collect(playerID)
    local markers = {}
    for _, entry in ipairs(entries or S.GetPlotEntries(key, false)) do
        if entry.category == "SALE" and entry.readyStyle == "SALE" then
            local plot = Map.GetPlotByIndex(entry.index)
            local city = plot and Cities.GetPlotPurchaseCity(plot)
            if city and plot:GetOwner() == playerID then
                local effects = current[city:GetID()] or {}
                local groups = {}
                for effectID, effect in pairs(effects) do
                    local row = effect.row
                    local target = row.AbilityIconTarget
                    if row.NotificationQuarter == key and target and target:find("_SERVICE", 1, true)
                        and effect.districts[plot:GetDistrictID()] then
                        groups[target] = true
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
                        if data then icon = data.icon; table.insert(tooltip, data.tooltip) end
                    end
                    markers[#markers+1] = {index=entry.index, target=target, icon=icon,
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

local function PublishServicePins(owner, key, markers)
    -- Keep a small UI-only snapshot for a context loaded after its first draw.
    -- No map pins, gameplay properties, or saved player configuration are made.
    if ExposedMembers then
        ExposedMembers.CSC_QuarterServicePins = ExposedMembers.CSC_QuarterServicePins or {}
        ExposedMembers.CSC_QuarterServicePins[owner] = {key=key, markers=markers}
    end
    if LuaEvents and LuaEvents.CSC_QuarterServicePins_Update then
        LuaEvents.CSC_QuarterServicePins_Update(owner, key, markers)
    end
end

local function DrawFlows(owner, entries)
    local overlay = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Flow")
    if overlay == nil then S.FlowSignatures[owner] = nil; return 0, false end
    local key = entries[1] and entries[1].quarterKey
    local links = S.GetFlowLinks(key, entries)
    local signature, waves = {key or ""}, {}
    for _, link in ipairs(links) do
        local color = UI.GetColorValue(S.FlowYieldColors[link.yieldType])
        table.insert(signature, link.source .. ":" .. link.target .. ":" .. link.kind .. ":" .. link.yieldType .. ":" .. tostring(color))
        -- Native in-game review confirms positive-speed arrows travel from
        -- pos1 to pos2. Anchor the effect on the semantic source tile itself.
        table.insert(waves, {pos1 = link.source, pos2 = link.target,
            color = color,
            speed = 2, type = "CIVILIZATION_UNKNOWN"})
    end
    local nextSignature = table.concat(signature, "|")
    if S.FlowSignatures[owner] ~= nextSignature then
        overlay:ResetAllWaves()
        if #waves > 0 then overlay:CreateLinearWaves(waves) end
        S.FlowSignatures[owner] = nextSignature
        if LuaEvents and LuaEvents.CSC_QuarterFlowTrial_Update then
            LuaEvents.CSC_QuarterFlowTrial_Update(owner, waves)
        end
    end
    -- Repeated UI refreshes must not continually restart an unchanged effect.
    local trial = ExposedMembers and ExposedMembers.CSC_QuarterFlowTrial
    overlay:SetVisible(#waves > 0 and not (trial and trial.Enabled and trial.Ready))
    return #waves, true
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
    local services = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Services")
    if services then services:ClearAll(); services:SetVisible(false) end
    local flow = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Flow")
    if flow then flow:ResetAllWaves(); flow:SetVisible(false) end
    if LuaEvents and LuaEvents.CSC_QuarterFlowTrial_Update then LuaEvents.CSC_QuarterFlowTrial_Update(owner, {}) end
    S.FlowSignatures[owner] = nil
    S.SpriteSignatures[owner .. "_Fill"] = nil
    S.SpriteSignatures[owner .. "_Ready"] = nil
    S.SpriteSignatures[owner .. "_Tint"] = nil
    S.SpriteSignatures[owner .. "_Services"] = nil
    PublishServicePins(owner, nil, {})
    if owner == "Lens" then S.NativeFillSignature = nil end
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
local function DrawTintGroups(owner, overlay, groups)
    local key = owner .. "_Tint"
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

function S.DrawOverlay(owner, entries, forceBackground)
    if owner ~= "Lens" and owner ~= "Placement" then return false end
    local quarter = S.Quarters[entries[1] and entries[1].quarterKey]
    local function spriteKind(kind)
        return kind == "QUARTER" and quarter and quarter.quarterStyle or kind
    end
    local fill = UILens.GetOverlay("CSC_Quarter" .. owner)
    local textureFill = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Fill")
    local tint = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Tint")
    if owner == "Placement" and fill == nil and textureFill == nil and tint == nil then S.ClearOverlay(owner); return false end
    if fill then fill:ClearPlotChannel(); fill:SetVisible(false) end
    local colors, patterns = {}, {BASE = {}, SPEC = {}, SALE = {}, QUARTER = {}}
    local texturedPlots, tintPlots = {}, {}
    for _, entry in ipairs(entries) do
        local color = entry.color
        if tint and entry.outlineStyle then
            tintPlots[color] = tintPlots[color] or {}
            table.insert(tintPlots[color], entry.index)
        elseif textureFill and entry.outlineStyle then
            local style = "CSC_Lens_Fill_" .. spriteKind(entry.outlineStyle) .. (entry.ready and "_Ready" or "_Unready")
            texturedPlots[style] = texturedPlots[style] or {}
            table.insert(texturedPlots[style], entry.index)
        elseif color ~= nil then
            colors[color] = colors[color] or {}
            table.insert(colors[color], entry.index)
        end
        if entry.outlineStyle then table.insert(patterns[entry.outlineStyle], entry.index) end
    end
    -- Native BorderOverlay colours are stored in allocated style slots. A
    -- non-nil overlay object alone does not prove those slots exist. Reserve 0
    -- and use positive fill channels, like XP2 PowerCityPlots; allocate every
    -- slot with the native InitializeStyles(count, materialHash) API first.
    local count = 0
    for _ in pairs(colors) do count = count + 1 end
    local nativeFill = owner == "Lens" and UILens.CreateLensLayerHash("Hex_Coloring_Appeal_Level") or nil
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
    -- Only unrelated grey plots use it now. Direct native hex highlights supply
    -- category RGBA. Keep the stable texture path as a missing-new-art fallback.
    local texturedCount, textureChannel, fillRebuilt = 0, 0, false
    local fillGroups = {}
    if textureFill then
        for _, kind in ipairs({"BASE", "SPEC", "SALE", "QUARTER"}) do
            for _, state in ipairs({"Unready", "Ready"}) do
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
    local tintCount, tintRebuilt = DrawTintGroups(owner, tint, tintPlots)
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
        for index, kind in ipairs({"BASE", "SPEC", "SALE", "QUARTER"}) do
            if #patterns[kind] > 0 then
                table.insert(outlineGroups, {plots = patterns[kind], style = "CSC_Lens_Ready_" .. spriteKind(kind), channel = index - 1})
            end
        end
    end
    local outlined, outlinesRebuilt = DrawSpriteGroups(owner, "_Ready", ready, outlineGroups)
    -- Retire the flat SpriteOverlay even when an older art package still has it.
    local services = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Services")
    if services then services:SetVisible(false) end
    local key = entries[1] and entries[1].quarterKey
    local markers = key and S.GetServiceMarkers(key, entries) or {}
    PublishServicePins(owner, key, markers)
    local serviceCount, servicesRebuilt = #markers, false
    table.sort(palette)
    local flows, flowAvailable = DrawFlows(owner, entries)
    return count > 0 or texturedCount > 0 or tintCount > 0 or (ready ~= nil and outlined > 0) or flows > 0, {
        channels = count, styles = nativeFill and 0 or count + 1,
        outlines = ready and outlined or 0,
        flows = flows, flowAvailable = flowAvailable, flowSignature = S.FlowSignatures[owner],
        services = serviceCount, servicesAvailable = true, servicesRebuilt = servicesRebuilt,
        readyAvailable = ready ~= nil, readyMaterial = readyMaterial, readyStyles = ready and 4 or 0,
        textureFillAvailable = textureFill ~= nil, textureFillPlots = texturedCount,
        fillRebuilt = fillRebuilt, outlinesRebuilt = outlinesRebuilt,
        tintAvailable = tint ~= nil, tintPlots = tintCount, tintRebuilt = tintRebuilt,
        backgroundRepainted = repaintNative,
        palette = table.concat(palette, ","),
        backend = tint and "HexHighlightOverlay (Base 30%, other unready 20%, ready 60%)"
            or textureFill and "textured hexes (Base 30%, other unready 20%, ready 60%)"
            or (nativeFill and "native coloured hexes (fallback: fixed alpha)" or "BorderOverlay (fallback)"),
    }
end
