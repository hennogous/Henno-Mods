-- More Lenses options panel: one main-menu entry, data-driven Quarter choices.
include("InstanceManager")
include("CSC_QuarterLensSupport")

local S = CSC_QuarterLensSupport
local parent = "ML_CSC_SUPPLY_CHAINS"
local layer = UILens.CreateLensLayerHash("Hex_Coloring_Appeal_Level")
local rows = InstanceManager:new("QuarterChoiceInstance", "QuarterButton", Controls.QuarterChoices)
local quarters, buttons = {}, {}
for _, quarter in pairs(S.Quarters) do table.insert(quarters, quarter) end
table.sort(quarters, function(a, b) return a.id < b.id end)
local selected = quarters[1] and quarters[1].id

local function IsActive()
    local lens = {}
    LuaEvents.MinimapPanel_GetActiveModLens(lens)
    return lens[1] == parent
end

local function SetLegend()
    if selected then
        LuaEvents.ModalLensPanel_AddLensEntry(parent, S.GetLensLegend(selected), true)
    end
end

local function Refresh()
    -- Placement can temporarily use the same native colour layer. Its own
    -- wrapper owns painting there; refresh only the actual manual lens.
    if not IsActive() or UI.GetInterfaceMode() ~= InterfaceModeTypes.VIEW_MODAL_LENS
        or not UILens.IsLayerOn(layer) or selected == nil then
        S.ClearImprovedBorders("Lens")
        return
    end
    SetLegend()
    UILens.ClearLayerHexes(layer)
    for color, plots in pairs(S.GetColorPlotTable(selected)) do
        if #plots > 0 then
            UILens.SetLayerHexesColoredArea(layer, Game.GetLocalPlayer(), plots, color)
        end
    end
    S.DrawImprovedBorders("Lens", selected)
end

local function SelectQuarter(key)
    if S.Quarters[key] == nil then return end
    selected = key
    for id, button in pairs(buttons) do button:SetCheck(id == key) end
    SetLegend()
    Refresh()
end

local function Reoffset()
    local offsets = {}
    LuaEvents.MinimapPanel_GetLensPanelOffsets(offsets)
    if offsets.X and offsets.Y then
        Controls.SupplyChainsLensPanel:SetOffsetX(offsets.X - 5)
        Controls.SupplyChainsLensPanel:SetOffsetY(offsets.Y + 32)
    end
end

local function Close()
    Controls.SupplyChainsLensPanel:SetHide(true)
    -- More Lenses may close an options panel while keeping its lens active.
    if not IsActive() or UI.GetInterfaceMode() ~= InterfaceModeTypes.VIEW_MODAL_LENS then
        S.ClearImprovedBorders("Lens")
    end
end

local function Open()
    if selected == nil then return end
    Reoffset()
    SelectQuarter(selected)
    Controls.SupplyChainsLensPanel:SetHide(false)
end

local function OnActiveLensChanged(name)
    if name ~= parent then
        S.ClearImprovedBorders("Lens")
        Close()
    end
end

local function OnModeChanged(_, newMode)
    if newMode == InterfaceModeTypes.VIEW_MODAL_LENS then Refresh() else Close() end
end

local function OnLayerOn(layerNum)
    if layerNum == layer then Refresh() end
end

local function OnLayerOff(layerNum)
    if layerNum == layer then S.ClearImprovedBorders("Lens") end
end

local function ChangeContainer()
    local hud = ContextPtr:LookUpControl("/InGame/HUD")
    if hud then Controls.SupplyChainsLensPanel:ChangeParent(hud) end
end

local function OnLoaded()
    ChangeContainer()
    SetLegend()
    Reoffset()
end

local function OnShutdown()
    S.ClearImprovedBorders("Lens")
    LuaEvents.CSC_SupplyChainsLens_OpenPanel.Remove(Open)
    LuaEvents.CSC_SupplyChainsLens_Refresh.Remove(Refresh)
    LuaEvents.ML_CloseLensPanels.Remove(Close)
    LuaEvents.ML_ReoffsetPanels.Remove(Reoffset)
    LuaEvents.MinimapPanel_ModdedLensOn.Remove(OnActiveLensChanged)
    Events.InterfaceModeChanged.Remove(OnModeChanged)
    Events.LensLayerOn.Remove(OnLayerOn)
    Events.LensLayerOff.Remove(OnLayerOff)
    Events.LoadScreenClose.Remove(OnLoaded)
    rows:ResetInstances()
    local hud = ContextPtr:LookUpControl("/InGame/HUD")
    if hud then hud:DestroyChild(Controls.SupplyChainsLensPanel) end
end

for _, quarter in ipairs(quarters) do
    local key = quarter.id
    local button = rows:GetInstance().QuarterButton
    buttons[key] = button
    button:GetTextButton():LocalizeAndSetText(quarter.locName)
    button:SetToolTipString(Locale.Lookup(quarter.locTooltip))
    button:SetCheck(key == selected)
    button:RegisterCallback(Mouse.eLClick, function() SelectQuarter(key) end)
end
Controls.SupplyChainsLensPanel:SetSizeY(math.max(140, math.min(360, 68 + #quarters * 35)))
Controls.QuarterChoices:CalculateSize()
Controls.QuarterChoices:ReprocessAnchoring()
Controls.QuarterScroll:CalculateSize()
Close()
ContextPtr:SetInitHandler(function(isReload) if isReload then OnLoaded() end end)
ContextPtr:SetShutdown(OnShutdown)
LuaEvents.CSC_SupplyChainsLens_OpenPanel.Add(Open)
LuaEvents.CSC_SupplyChainsLens_Refresh.Add(Refresh)
LuaEvents.ML_CloseLensPanels.Add(Close)
LuaEvents.ML_ReoffsetPanels.Add(Reoffset)
LuaEvents.MinimapPanel_ModdedLensOn.Add(OnActiveLensChanged)
Events.InterfaceModeChanged.Add(OnModeChanged)
Events.LensLayerOn.Add(OnLayerOn)
Events.LensLayerOff.Add(OnLayerOff)
Events.LoadScreenClose.Add(OnLoaded)
