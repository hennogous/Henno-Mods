-- Preserve native PlotInfo and augment its district placement event only for
-- configured CSC Quarters. Native valid/purchase tiles and adjacency art remain.
include("PlotInfo")
include("CSC_QuarterLensSupport")

local S = CSC_QuarterLensSupport
-- Placement's native layer uses fixed green art. Appeal is the colour-capable
-- layer used by More Lenses; CSC_Lenses.artdef permits it during placement.
local placementLayer = UILens.CreateLensLayerHash("Hex_Coloring_Appeal_Level")
local ownsPlacementLayer = false
local stockAdd = OnAddDistrictPlacementShadowHexes
local stockClear = OnClearDistrictPlacementShadowHexes
local stockShutdown = OnShutdown
local stockModeChanged = OnInterfaceModeChanged

local function ClearQuarterHighlights()
    if ownsPlacementLayer then
        -- ToggleLayerOff emits LensLayerOff synchronously.
        ownsPlacementLayer = false
        -- A modal Appeal/More Lenses selection may have already reused the
        -- layer before the interface-mode event arrives. Its contents are now
        -- owned by that lens, not by placement.
        if UILens.IsLensActive("Appeal") then return true end
        UILens.ClearLayerHexes(placementLayer)
        UILens.ToggleLayerOff(placementLayer)
        return true
    end
    return false
end

function OnAddDistrictPlacementShadowHexes(hexes)
    local quarter = nil
    if UI.GetInterfaceMode() == InterfaceModeTypes.DISTRICT_PLACEMENT
        and UI.GetHeadSelectedCity() ~= nil then
        quarter = S.GetQuarter(UI.GetInterfaceModeParameter(CityOperationTypes.PARAM_DISTRICT_TYPE))
    end
    if quarter == nil then
        local hadHighlights = ClearQuarterHighlights()
        local result = stockAdd(hexes)
        -- A direct switch may keep the same active native lens. Restore its
        -- mask immediately rather than waiting for another layer/plot event.
        if hadHighlights then RealizeShadowMask() end
        return result
    end

    local colorPlots = S.GetColorPlotTable(quarter.id, false)
    -- Extend the existing mask so highlighted materials/customers remain bright.
    -- Preserve every native placement tile and other PlotInfo mask categories.
    local combined, seen = {}, {}
    local function add(index)
        if not seen[index] then seen[index] = true; table.insert(combined, index) end
    end
    for _, index in ipairs(hexes) do add(index) end
    for _, plots in pairs(colorPlots) do for _, index in ipairs(plots) do add(index) end end
    stockAdd(combined)
    ownsPlacementLayer = true
    UILens.ToggleLayerOn(placementLayer)
    -- Native/More Lenses listeners may paint Appeal when it turns on. Replace
    -- their contents afterwards, then restore the native placement shadow mask.
    UILens.ClearLayerHexes(placementLayer)
    for color, plots in pairs(colorPlots) do
        if #plots > 0 then
            UILens.SetLayerHexesColoredArea(placementLayer, Game.GetLocalPlayer(), plots, color)
        end
    end
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

local function OnQuarterLayerOff(layer)
    if layer == placementLayer and ownsPlacementLayer then
        -- SetActive switches layers before switching interface mode. Release
        -- ownership here so later cleanup cannot erase a newly selected lens.
        ownsPlacementLayer = false
        UILens.ClearLayerHexes(placementLayer)
        stockClear()
    end
end

-- PlotInfo initializes while included, so rebind its already registered callbacks.
LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Remove(stockAdd)
LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Add(OnAddDistrictPlacementShadowHexes)
LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Remove(stockClear)
LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Add(OnClearDistrictPlacementShadowHexes)
Events.InterfaceModeChanged.Remove(stockModeChanged)
Events.InterfaceModeChanged.Add(OnInterfaceModeChanged)
Events.LensLayerOff.Add(OnQuarterLayerOff)
ContextPtr:SetShutdown(function()
    ClearQuarterHighlights()
    LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Remove(OnAddDistrictPlacementShadowHexes)
    LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Remove(OnClearDistrictPlacementShadowHexes)
    Events.InterfaceModeChanged.Remove(OnInterfaceModeChanged)
    Events.LensLayerOff.Remove(OnQuarterLayerOff)
    stockShutdown()
end)
