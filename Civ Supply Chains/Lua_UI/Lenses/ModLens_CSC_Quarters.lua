-- ===========================================================================
-- CSC Quarter Lenses (Factory)
-- Soft dependency on More Lenses (astog) — only activates if g_ModLenses exists
--
-- Generates a lens for each CSC Quarter automatically by reading
-- resource tags and adjacency relationships from GameInfo.
--
-- Resources are shown in two shades: bright (improved) and dim (unimproved)
-- to help inform placement and improvement decisions.
-- ===========================================================================

local ML_LENS_LAYER = UILens.CreateLensLayerHash("Hex_Coloring_Appeal_Level")

-- ===========================================================================
-- Quarter definitions
-- Each entry generates a lens. Colors are defined in CSC_Lens_Colors.sql.
--
-- To add a new Quarter lens, just add an entry here — everything else
-- (resources, sale districts) is read from the game DB at runtime.
-- ===========================================================================

local CSC_QUARTERS = {
    {
        id          = "BAKERS",
        lensName    = "ML_CSC_BAKERS",
        locName     = "LOC_HUD_CSC_BAKERS_LENS",
        locTooltip  = "LOC_HUD_CSC_BAKERS_LENS_TOOLTIP",
        colorPrefix = "COLOR_CSC_LENS_BAKERS",
        locLegendQ  = "LOC_TOOLTIP_CSC_LENS_BAKERS_QUARTER",
        locLegendB  = "LOC_TOOLTIP_CSC_LENS_BAKERS_BASE",
        locLegendS  = "LOC_TOOLTIP_CSC_LENS_BAKERS_SPEC",
    },
    -- Uncomment as Quarters are implemented:
    -- {
    --     id          = "TAILORS",
    --     lensName    = "ML_CSC_TAILORS",
    --     locName     = "LOC_HUD_CSC_TAILORS_LENS",
    --     locTooltip  = "LOC_HUD_CSC_TAILORS_LENS_TOOLTIP",
    --     colorPrefix = "COLOR_CSC_LENS_TAILORS",
    --     locLegendQ  = "LOC_TOOLTIP_CSC_LENS_TAILORS_QUARTER",
    --     locLegendB  = "LOC_TOOLTIP_CSC_LENS_TAILORS_BASE",
    --     locLegendS  = "LOC_TOOLTIP_CSC_LENS_TAILORS_SPEC",
    -- },
}

-- ===========================================================================
-- Helpers
-- ===========================================================================

local function GetResourceTypeStr(pPlot)
    local resType = pPlot:GetResourceType()
    if resType == -1 then return nil end
    local info = GameInfo.Resources[resType]
    return info and info.ResourceType or nil
end

local function GetDistrictTypeStr(pPlot)
    local distType = pPlot:GetDistrictType()
    if distType == -1 then return nil end
    local info = GameInfo.Districts[distType]
    return info and info.DistrictType or nil
end

local function PlotIsImproved(pPlot)
    return pPlot:GetImprovementType() ~= -1
end

-- ===========================================================================
-- Factory: creates a lens for one Quarter
-- ===========================================================================

local function CreateQuarterLens(quarter)
    local districtType = "DISTRICT_CSC_" .. quarter.id .. "_QUARTER"
    local baseTag      = "CLASS_CSC_" .. quarter.id .. "_BASE"
    local specTag      = "CLASS_CSC_" .. quarter.id .. "_SPEC"
    local adjPattern   = "CSC_" .. quarter.id

    local function BuildLookupSets()
        local baseSet = {}
        local specSet = {}
        local saleSet = {}

        -- Resources from TypeTags
        for row in GameInfo.TypeTags() do
            if row.Tag == baseTag then
                baseSet[row.Type] = true
            elseif row.Tag == specTag then
                specSet[row.Type] = true
            end
        end

        -- Sale districts from District_Adjacencies
        for row in GameInfo.District_Adjacencies() do
            if row.YieldChangeId ~= nil
                and string.find(row.YieldChangeId, adjPattern)
                and row.DistrictType ~= districtType then
                saleSet[row.DistrictType] = true
            end
        end

        return baseSet, specSet, saleSet
    end

    local function OnGetColorPlotTable()
        local baseSet, specSet, saleSet = BuildLookupSets()

        local mapWidth, mapHeight = Map.GetGridSize()
        local localPlayer   :number = Game.GetLocalPlayer()
        local localPlayerVis:table = PlayersVisibility[localPlayer]

        -- Colors: bright = improved/active, dim = unimproved/opportunity
        local QuarterColor          = UI.GetColorValue(quarter.colorPrefix .. "_QUARTER")
        local BaseImprovedColor     = UI.GetColorValue(quarter.colorPrefix .. "_BASE_IMPROVED")
        local BaseUnimprovedColor   = UI.GetColorValue(quarter.colorPrefix .. "_BASE_UNIMPROVED")
        local SpecImprovedColor     = UI.GetColorValue(quarter.colorPrefix .. "_SPEC_IMPROVED")
        local SpecUnimprovedColor   = UI.GetColorValue(quarter.colorPrefix .. "_SPEC_UNIMPROVED")
        local SaleColor             = UI.GetColorValue("COLOR_CSC_LENS_SALE_DISTRICT")
        local IgnoreColor           = UI.GetColorValue("COLOR_MORELENSES_GREY")

        local colorPlot = {}
        colorPlot[QuarterColor]        = {}
        colorPlot[BaseImprovedColor]   = {}
        colorPlot[BaseUnimprovedColor] = {}
        colorPlot[SpecImprovedColor]   = {}
        colorPlot[SpecUnimprovedColor] = {}
        colorPlot[SaleColor]           = {}
        colorPlot[IgnoreColor]         = {}

        for i = 0, (mapWidth * mapHeight) - 1, 1 do
            local pPlot = Map.GetPlotByIndex(i)
            if localPlayerVis:IsRevealed(pPlot:GetX(), pPlot:GetY()) then
                local distStr  = GetDistrictTypeStr(pPlot)
                local resStr   = GetResourceTypeStr(pPlot)
                local improved = PlotIsImproved(pPlot)

                if distStr == districtType then
                    table.insert(colorPlot[QuarterColor], i)
                elseif saleSet[distStr] then
                    table.insert(colorPlot[SaleColor], i)
                elseif baseSet[resStr] then
                    if improved then
                        table.insert(colorPlot[BaseImprovedColor], i)
                    else
                        table.insert(colorPlot[BaseUnimprovedColor], i)
                    end
                elseif specSet[resStr] then
                    if improved then
                        table.insert(colorPlot[SpecImprovedColor], i)
                    else
                        table.insert(colorPlot[SpecUnimprovedColor], i)
                    end
                else
                    table.insert(colorPlot[IgnoreColor], i)
                end
            end
        end

        return colorPlot
    end

    return {
        LensButtonText    = quarter.locName,
        LensButtonTooltip = quarter.locTooltip,
        Initialize        = nil,
        GetColorPlotTable = OnGetColorPlotTable,
    }, {
        LensTextKey = quarter.locName,
        Legend = {
            {quarter.locLegendQ,                       UI.GetColorValue(quarter.colorPrefix .. "_QUARTER")},
            {quarter.locLegendB .. "_IMPROVED",        UI.GetColorValue(quarter.colorPrefix .. "_BASE_IMPROVED")},
            {quarter.locLegendB .. "_UNIMPROVED",      UI.GetColorValue(quarter.colorPrefix .. "_BASE_UNIMPROVED")},
            {quarter.locLegendS .. "_IMPROVED",        UI.GetColorValue(quarter.colorPrefix .. "_SPEC_IMPROVED")},
            {quarter.locLegendS .. "_UNIMPROVED",      UI.GetColorValue(quarter.colorPrefix .. "_SPEC_UNIMPROVED")},
            {"LOC_TOOLTIP_CSC_LENS_SALE_DISTRICT",     UI.GetColorValue("COLOR_CSC_LENS_SALE_DISTRICT")},
        },
    }
end

-- ===========================================================================
-- Register all Quarter lenses with More Lenses
-- ===========================================================================

if g_ModLenses ~= nil or g_ModLensModalPanel ~= nil then
    for _, quarter in ipairs(CSC_QUARTERS) do
        local lensEntry, panelEntry = CreateQuarterLens(quarter)

        if g_ModLenses ~= nil then
            g_ModLenses[quarter.lensName] = lensEntry
        end

        if g_ModLensModalPanel ~= nil then
            g_ModLensModalPanel[quarter.lensName] = panelEntry
        end
    end
end
