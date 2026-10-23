-- Preserve native PlotInfo and augment its district placement event only for
-- configured CSC Quarters. Native valid/purchase tiles and adjacency art remain.
include("CSC_AI_UIFilter")
include("PlotInfo")
include("CSC_QuarterLensSupport")

local S = CSC_QuarterLensSupport
-- An independent native BorderOverlay supplies tile fills without changing any
-- lens layer or More Lenses state. MapSearch uses this same highlight API.
local placementOverlayName = "CSC_QuarterPlacement"
local hasHighlights = false
local stockAdd = OnAddDistrictPlacementShadowHexes
local stockClear = OnClearDistrictPlacementShadowHexes
local stockShutdown = OnShutdown
local stockModeChanged = OnInterfaceModeChanged

local function ClearQuarterHighlights()
    if hasHighlights then
        hasHighlights = false
        local overlay = UILens.GetOverlay(placementOverlayName)
        if overlay then
            overlay:ClearPlotChannel()
            overlay:SetVisible(false)
        end
        return true
    end
    return false
end

function OnAddDistrictPlacementShadowHexes(hexes)
    local quarter = nil
    local city = UI.GetHeadSelectedCity()
    if UI.GetInterfaceMode() == InterfaceModeTypes.DISTRICT_PLACEMENT
        and city ~= nil then
        quarter = S.GetQuarter(UI.GetInterfaceModeParameter(CityOperationTypes.PARAM_DISTRICT_TYPE))
    end
    local overlay = quarter and UILens.GetOverlay(placementOverlayName)
    -- Missing cooked art leaves native placement fully usable.
    if overlay == nil then
        local hadHighlights = ClearQuarterHighlights()
        local result = stockAdd(hexes)
        -- A direct switch may keep the same active native lens. Restore its
        -- mask immediately rather than waiting for another layer/plot event.
        if hadHighlights then RealizeShadowMask() end
        return result
    end

    -- Placement highlights opportunities outside this city's territory. Compare
    -- both owner and city ID: IDs alone can coincide across different players.
    -- Leave the shared classifier/manual lens and native placement tiles intact.
    local owner, cityID = city:GetOwner(), city:GetID()
    local colorPlots = {}
    for color, plots in pairs(S.GetColorPlotTable(quarter.id, false)) do
        local externalPlots = {}
        for _, index in ipairs(plots) do
            local plotCity = Cities.GetPlotPurchaseCity(Map.GetPlotByIndex(index))
            if plotCity == nil or plotCity:GetOwner() ~= owner or plotCity:GetID() ~= cityID then
                table.insert(externalPlots, index)
            end
        end
        colorPlots[color] = externalPlots
    end
    -- Extend the existing mask so highlighted materials/customers remain bright.
    -- Preserve every native placement tile and other PlotInfo mask categories.
    local combined, seen = {}, {}
    -- This list controls brightness only. Extra planning plots never become
    -- legal placement/purchase tiles; native PlotInfo still owns those decisions.
    local function add(index)
        if not seen[index] then seen[index] = true; table.insert(combined, index) end
    end
    for _, index in ipairs(hexes) do add(index) end
    for _, plots in pairs(colorPlots) do for _, index in ipairs(plots) do add(index) end end
    stockAdd(combined)
    overlay:ClearPlotChannel()
    overlay:ShowHighlights(true)
    overlay:ShowBorders(false)
    local channel = 0
    for color, plots in pairs(colorPlots) do
        if #plots > 0 then
            overlay:SetHighlightColor(channel, color)
            overlay:SetPlotChannel(plots, channel)
            channel = channel + 1
        end
    end
    hasHighlights = channel > 0
    overlay:SetVisible(hasHighlights)
    RealizeShadowMask()
end

function OnClearDistrictPlacementShadowHexes()
    ClearQuarterHighlights()
    return stockClear()
end

function OnInterfaceModeChanged(oldMode, newMode)
    if oldMode == InterfaceModeTypes.DISTRICT_PLACEMENT
        and newMode ~= InterfaceModeTypes.DISTRICT_PLACEMENT then
        -- Confirmation need not emit the native shadow-clear event. Always
        -- release our colours and mask when the placement mode ends.
        OnClearDistrictPlacementShadowHexes()
    end
    return stockModeChanged(oldMode, newMode)
end

-- PlotInfo initializes while included, so rebind its already registered callbacks.
LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Remove(stockAdd)
LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Add(OnAddDistrictPlacementShadowHexes)
LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Remove(stockClear)
LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Add(OnClearDistrictPlacementShadowHexes)
Events.InterfaceModeChanged.Remove(stockModeChanged)
Events.InterfaceModeChanged.Add(OnInterfaceModeChanged)
ContextPtr:SetShutdown(function()
    ClearQuarterHighlights()
    LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Remove(OnAddDistrictPlacementShadowHexes)
    LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Remove(OnClearDistrictPlacementShadowHexes)
    Events.InterfaceModeChanged.Remove(OnInterfaceModeChanged)
    stockShutdown()
end)
