-- Shared planning overlay data for manual lenses and native district placement.
-- Does not depend on More Lenses and never writes gameplay properties.
if CSC_QuarterLensSupport ~= nil then return end
if CSC_Adjacency == nil then include("CSC_AdjacencyCore") end

CSC_QuarterLensSupport = { Quarters = {}, ByDistrict = {} }
local S = CSC_QuarterLensSupport

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
                quarter = {
                    id = key, districtType = districtType,
                    lensName = "ML_CSC_" .. key,
                    locName = "LOC_HUD_CSC_" .. key .. "_LENS",
                    locTooltip = "LOC_HUD_CSC_" .. key .. "_LENS_TOOLTIP",
                    colorPrefix = "COLOR_CSC_LENS",
                    quarterColor = "COLOR_CSC_LENS_" .. key .. "_QUARTER",
                    locLegendQ = "LOC_TOOLTIP_CSC_LENS_" .. key .. "_QUARTER",
                    baseSet = {}, specSet = {}, saleSet = {}, wonderSaleSet = {},
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
    end
end

if GameInfo.CSC_QuarterWonderSales ~= nil then
    for row in GameInfo.CSC_QuarterWonderSales() do
        local quarter = S.Quarters[row.QuarterKey]
        local wonder = GameInfo.Buildings[row.BuildingType]
        if quarter and wonder and (wonder.IsWonder == true or wonder.IsWonder == 1) then
            quarter.wonderSaleSet[row.BuildingType] = true
        end
    end
end

function S.GetQuarter(districtIndex)
    local district = districtIndex ~= nil and GameInfo.Districts[districtIndex]
    return district and S.ByDistrict[district.DistrictType] or nil
end

function S.GetLensLegend(key)
    local quarter = S.Quarters[key]
    if quarter == nil then return nil end
    return {
        LensTextKey = quarter.locName,
        Legend = {
            {quarter.locLegendQ, UI.GetColorValue(quarter.quarterColor)},
            {"LOC_TOOLTIP_CSC_LENS_BASE", UI.GetColorValue(quarter.colorPrefix .. "_BASE_IMPROVED")},
            {"LOC_TOOLTIP_CSC_LENS_SPEC", UI.GetColorValue(quarter.colorPrefix .. "_SPEC_IMPROVED")},
            {"LOC_TOOLTIP_CSC_LENS_SALE_DISTRICT", UI.GetColorValue("COLOR_CSC_LENS_SALE_DISTRICT")},
        },
    }
end

-- Share classification between both views and the manual lens's resource borders.
-- This is planning data, not a prediction of ownership-gated adjacency yields.
function S.GetPlotEntries(key, includeIgnored)
    local quarter = S.Quarters[key]
    local playerID = Game.GetLocalPlayer()
    local visibility = PlayersVisibility[playerID]
    if quarter == nil or visibility == nil then return {} end
    local colors = {
        QUARTER = UI.GetColorValue(quarter.quarterColor),
        BASE_IMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_BASE_IMPROVED"),
        BASE_UNIMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_BASE_UNIMPROVED"),
        SPEC_IMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_SPEC_IMPROVED"),
        SPEC_UNIMPROVED = UI.GetColorValue(quarter.colorPrefix .. "_SPEC_UNIMPROVED"),
        SALE = UI.GetColorValue("COLOR_CSC_LENS_SALE_DISTRICT"),
    }
    -- Placement leaves irrelevant tiles to the native overlay; More Lenses greys them.
    if includeIgnored ~= false then colors.IGNORE = UI.GetColorValue("COLOR_MORELENSES_GREY") end
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
            local color = colors[category or "IGNORE"]
            if color ~= nil then
                local definition = (category == "QUARTER" or category == "SALE")
                    and (wonderSale and wonder or district) or (resourceType and GameInfo.Resources[resourceType])
                table.insert(result, {
                    index = index, category = category or "IGNORE", color = color,
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
    -- Adapt the shared per-plot records to More Lenses' color -> plot-list API.
    -- Placement uses the same buckets but omits the grey background category.
    local quarter = S.Quarters[key]
    if quarter == nil or PlayersVisibility[Game.GetLocalPlayer()] == nil then return {} end
    local result = {}
    -- Preserve empty palette buckets for the More Lenses contract.
    result[UI.GetColorValue(quarter.quarterColor)] = {}
    for _, suffix in ipairs({"BASE_IMPROVED", "BASE_UNIMPROVED", "SPEC_IMPROVED", "SPEC_UNIMPROVED"}) do
        result[UI.GetColorValue(quarter.colorPrefix .. "_" .. suffix)] = {}
    end
    result[UI.GetColorValue("COLOR_CSC_LENS_SALE_DISTRICT")] = {}
    if includeIgnored ~= false then result[UI.GetColorValue("COLOR_MORELENSES_GREY")] = {} end
    for _, entry in ipairs(S.GetPlotEntries(key, includeIgnored)) do
        table.insert(result[entry.color], entry.index)
    end
    return result
end

-- Borders belong only to the manual More Lenses view. Placement uses fills.
function S.ClearImprovedBorders(owner)
    if owner ~= "Lens" then return end
    local overlay = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Improved")
    if overlay then overlay:ClearPlotChannel(); overlay:SetVisible(false) end
end

function S.DrawImprovedBorders(owner, key)
    if owner ~= "Lens" then return end
    local overlay = UILens.GetOverlay("CSC_Quarter" .. owner .. "_Improved")
    if overlay == nil then return end -- Colour fills still work without cooked art.
    overlay:ClearPlotChannel()
    overlay:ShowHighlights(false)
    overlay:ShowBorders(true)
    local channel = 0
    for _, entry in ipairs(S.GetPlotEntries(key, false)) do
        local material = entry.category:match("^(BASE)_IMPROVED$") or entry.category:match("^(SPEC)_IMPROVED$")
        if material then
            channel = channel + 1
            -- Individual channels retain the shared edge between improved plots.
            overlay:SetBorderColors(channel, entry.color, UI.GetColorValue("COLOR_CSC_LENS_" .. material .. "_OUTLINE"))
            overlay:SetPlotChannel({entry.index}, channel)
        end
    end
    overlay:SetVisible(channel > 0)
end
