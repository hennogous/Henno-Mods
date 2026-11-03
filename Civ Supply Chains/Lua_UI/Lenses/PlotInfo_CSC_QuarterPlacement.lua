-- Preserve native PlotInfo and augment its district placement event only for
-- configured CSC Quarters. Native valid/purchase tiles and adjacency art remain.
include("CSC_AI_UIFilter")
include("PlotInfo")
include("CSC_QuarterLensSupport")

local S = CSC_QuarterLensSupport
-- Private direct RGBA hexes use the same readiness palette as manual lenses,
-- without changing any lens layer or More Lenses state. Older cooked art falls
-- back to texture sprites, then the legacy independent BorderOverlay.
local placementOverlayName = "CSC_QuarterPlacement_Tint"
local hasHighlights = false
local stockAdd = OnAddDistrictPlacementShadowHexes
local stockClear = OnClearDistrictPlacementShadowHexes
local stockShutdown = OnShutdown
local stockModeChanged = OnInterfaceModeChanged

local function ClearQuarterHighlights()
    if hasHighlights then
        hasHighlights = false
        S.ClearOverlay("Placement")
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
    local overlay = quarter and (UILens.GetOverlay(placementOverlayName) or UILens.GetOverlay("CSC_QuarterPlacement_Fill") or UILens.GetOverlay("CSC_QuarterPlacement"))
    -- Missing cooked art leaves native placement fully usable.
    if overlay == nil then
        local hadHighlights = ClearQuarterHighlights()
        local result = stockAdd(hexes)
        -- A direct switch may keep the same active native lens. Restore its
        -- mask immediately rather than waiting for another layer/plot event.
        if hadHighlights then RealizeShadowMask() end
        return result
    end

    -- Show relevant sites in the selected city as well as other territories.
    -- Shared discovery/readiness rules still apply; only the native placement
    -- system decides which plots can actually receive the district.
    local entries = S.GetPlotEntries(quarter.id, false)
    -- Keep all coloured planning sites outside the native background fade,
    -- including the faint 20% fills on unimproved/empty sites.
    -- Preserve every native placement tile and other PlotInfo mask categories.
    local combined, seen = {}, {}
    -- This list controls brightness only. Extra planning plots never become
    -- legal placement/purchase tiles; native PlotInfo still owns those decisions.
    local function add(index)
        if not seen[index] then seen[index] = true; table.insert(combined, index) end
    end
    for _, index in ipairs(hexes) do add(index) end
    for _, entry in ipairs(entries) do add(entry.index) end
    stockAdd(combined)
    hasHighlights = S.DrawOverlay("Placement", entries)
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
