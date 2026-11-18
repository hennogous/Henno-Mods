-- The native placement event supplies the legal tiles. Draw Wind Mill
-- potential at the center of each Hills tile without changing its badge.
include("InstanceManager")

local markers = InstanceManager:new("BakersPlacementHill", "Anchor", Controls.Markers)
local attached = false
local addPlacement = LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes
local clearPlacement = LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes

local function Clear()
    markers:ResetInstances()
end

local function Draw(plotIndices)
    Clear()
    if UI.GetInterfaceMode() ~= InterfaceModeTypes.DISTRICT_PLACEMENT then return end
    local district = GameInfo.Districts[UI.GetInterfaceModeParameter(CityOperationTypes.PARAM_DISTRICT_TYPE)]
    if not district or district.DistrictType ~= "DISTRICT_CSC_BAKERS_QUARTER" then return end

    -- InGame loads custom contexts hidden. Join the native map marker parent.
    if not attached then
        local parent = ContextPtr:LookUpControl("/InGame/WorldViewControls")
        if not parent then return end
        ContextPtr:ChangeParent(parent)
        ContextPtr:SetHide(false)
        attached = true
    end

    for _, index in ipairs(plotIndices) do
        local plot = Map.GetPlotByIndex(index)
        if plot and plot:IsHills() then
            local terrain = GameInfo.Terrains[plot:GetTerrainType()]
            local icon = terrain and "ICON_" .. terrain.TerrainType or "ICON_TERRAIN_GRASS_HILLS"
            local marker = markers:GetInstance()
            local x, y = UI.GridToWorld(index)
            marker.Anchor:SetWorldPositionVal(x, y, 0)
            marker.Icon:SetIcon(icon, 50)
        end
    end
end

local function OnModeChanged(oldMode, newMode)
    if newMode ~= InterfaceModeTypes.DISTRICT_PLACEMENT then Clear() end
end

addPlacement.Add(Draw)
clearPlacement.Add(Clear)
Events.InterfaceModeChanged.Add(OnModeChanged)
Events.LocalPlayerChanged.Add(Clear)
ContextPtr:SetShutdown(function()
    addPlacement.Remove(Draw)
    clearPlacement.Remove(Clear)
    Events.InterfaceModeChanged.Remove(OnModeChanged)
    Events.LocalPlayerChanged.Remove(Clear)
end)
