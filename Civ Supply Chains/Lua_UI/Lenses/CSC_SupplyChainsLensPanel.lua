-- CSC owns this menu extension, selector, legend and native overlays.
-- It inserts one row into the existing lens list without replacing its scripts.
include("InstanceManager")
include("InputSupport")
include("CSC_QuarterLensSupport")
local S = CSC_QuarterLensSupport
local rows = InstanceManager:new("QuarterChoiceInstance", "QuarterButton", Controls.QuarterChoices)
local legendRows = InstanceManager:new("QuarterLegendInstance", "LegendColor", Controls.LegendStack)
local quarters, buttons = {}, {}
for _, quarter in pairs(S.Quarters) do table.insert(quarters, quarter) end
table.sort(quarters, function(a, b) return a.id < b.id end)
local selected = quarters[1] and quarters[1].id
local active, shuttingDown = false, false
local lensFocus = nil
local quarterData = {}
local serviceEffects, serviceRevision = nil, 0
local mapDirty, servicesDirty, refreshQueued = false, false, false
-- Mirror the native radio value while its control and callback owner are live.
-- SetCheck fires native/Lua callbacks even for a redundant false assignment;
-- never initiate that callback path while the UI context is being destroyed.
local entryChecked = Controls.SupplyChainsLensEntry:IsChecked() == true
local FinishActivation = nil
local activationPending, settingCarrier = false, false
local entryUncheckedPending = false
local menuStack, menuPanel, nativeModal = nil, nil, nil
local nativeTitle, nativeKeyPanel, nativeHeaderBorrowed = nil, nil, false
local displayParent = nil
local originalMenuHeight, attachedMenuHeight = nil, nil
local appealLayer = UILens.CreateLensLayerHash("Hex_Coloring_Appeal_Level")
-- Fixed Quarter identities: adding/sorting menu entries must not move shortcuts.
local hotkeyQuarters = {[tonumber(Keys["1"])] = "BAKERS", [tonumber(Keys["2"])] = "TAILORS"}
local qHeld, qUsed = false, false
local keysDown, capturedKeys = {}, {}
-- Opt in when investigating the native input dispatcher.
local DEBUG_HOTKEYS = false
local function HotkeyDebug(format, ...)
    if DEBUG_HOTKEYS then print("CSC Hotkeys: " .. string.format(format, ...)) end
end

local function SetEntryChecked(checked, reason)
    checked = checked == true
    if shuttingDown then
        return
    end
    if entryChecked == checked then return end
    -- Publish first: native SetCheck may synchronously call our check handler.
    entryChecked = checked
    Controls.SupplyChainsLensEntry:SetCheck(checked)
end

-- The global callback observes input before UI roots and the action matcher.
-- Its Lua return value is ignored by the native bridge. Mask World actions for
-- handled keystrokes instead; restore the context after that dispatch finishes.
-- No native gestures or saved player bindings are edited.
local shortcutInputContext = 0x20000000
local inputMaskOwned = false
local function ReleaseInputMask()
    if inputMaskOwned and Input.GetActiveContext() == shortcutInputContext then
        Input.PopContext()
        inputMaskOwned = false
        Events.SystemUpdateUI.Remove(ReleaseInputMask)
    end
end

local function ResetHotkeys()
    qHeld, qUsed = false, false
    keysDown, capturedKeys = {}, {}
end

local function CancelHotkeys(reason)
    if qHeld then HotkeyDebug("cancelled Q prefix reason=%s", reason or "interrupted") end
    qHeld, qUsed = false, false
    keysDown = {}
    -- Still consume releases from keys captured before a mode/focus change.
end

-- Inspect visible controls only on shortcut keystrokes, never every frame.
-- This also protects text fields added/reparented by other mods, not just chat.
local function HasTextFocus(control)
    if control == nil or not control:IsVisible() then return false end
    if control.HasFocus and control:HasFocus() then return true end
    for _, child in ipairs(control:GetChildren()) do
        if HasTextFocus(child) then return true end
    end
    return false
end

local function CanUseLensShortcutMode(mode)
    -- Native MinimapPanel permits lens hotkeys outside ordinary Selection too.
    -- An allow-list of Selection/modal mode rejected Q while debug placement
    -- was active, leaving the following 1 free to open Religion. Accept World
    -- map interactions, but leave actual construction and cinematic UI alone.
    for _, name in ipairs({"DISTRICT_PLACEMENT", "BUILDING_PLACEMENT", "CINEMATIC", "FULLSCREEN_MAP"}) do
        local excluded = InterfaceModeTypes[name]
        if excluded ~= nil and mode == excluded then return false end
    end
    return true
end

local function CanUseHotkeys()
    local mode = UI.GetInterfaceMode()
    if shuttingDown then return false, "shutdown" end
    if Game.GetLocalPlayer() == -1 then return false, "no local player" end
    if Input.GetActiveContext() ~= InputContext.World then return false, "not World input" end
    if Input.IsRecordingGestures() then return false, "recording bindings" end
    if GameConfiguration.IsWorldBuilderEditor() then return false, "WorldBuilder" end
    if not CanUseLensShortcutMode(mode) then return false, "interface mode" end
    if HasTextFocus(ContextPtr:LookUpControl("/InGame")) then return false, "text focus" end
    return true
end

local function TogglePlainQ()
    -- Q normally toggles resources (WorldInput.lua). Delay that single-key
    -- action until release so holding Q for a Quarter never toggles icons.
    -- Honour a player who has removed Q from the resource action's bindings.
    local action = Input.GetActionId("ToggleResources")
    local q = Locale.Lookup("LOC_OPTIONS_KEY_Q")
    if Input.GetActionEnabled(action) and GameCapabilities.HasCapability("CAPABILITY_DISPLAY_MINIMAP_RESOURCES")
        and (Input.GetGestureDisplayString(action, 0) == q or Input.GetGestureDisplayString(action, 1) == q) then
        UserConfiguration.ShowMapResources(not UserConfiguration.ShowMapResources())
        UI.PlaySound("Play_UI_Click")
        LuaEvents.MinimapPanel_RefreshMinimapOptions()
        HotkeyDebug("plain Q: resource icons=%s", tostring(UserConfiguration.ShowMapResources()))
    end
end

local function ClearFills(preserveSharedFill)
    S.ClearOverlay("Lens", preserveSharedFill)
end

local function RestoreNativeHeader()
    if not nativeHeaderBorrowed then return end
    nativeHeaderBorrowed = false
    -- Restore the carrier's ordinary UI before its next owner paints. If a
    -- different native lens has already painted, preserve that lens's layout.
    if UILens.IsLensActive("Appeal") then
        nativeTitle:SetText(Locale.ToUpper(Locale.Lookup("LOC_HUD_APPEAL_LENS")))
        if nativeKeyPanel then nativeKeyPanel:SetHide(false) end
    end
end

local function SyncNativeHeader()
    if nativeModal and nativeTitle then
        -- Reuse the actual native/More Lenses header, including its draw order
        -- above TopPanel. The earlier HUD copy let TopPanel's brown edge show.
        Controls.LensHeader:SetHide(true)
        nativeTitle:SetText(Locale.ToUpper(Locale.Lookup(S.Quarters[selected].locName)))
        if nativeKeyPanel then nativeKeyPanel:SetHide(true) end
        nativeHeaderBorrowed = true
        nativeModal:SetHide(false)
    else
        Controls.LensHeader:SetHide(false)
        if nativeModal then nativeModal:SetHide(true) end
    end
end

local function Close(exitMode, nativeTakeover, reason)
    if FinishActivation then Events.SystemUpdateUI.Remove(FinishActivation) end
    activationPending = false
    refreshQueued = false
    entryUncheckedPending = false
    ContextPtr:ClearUpdate()
    active = false
    lensFocus = nil
    RestoreNativeHeader()
    ClearFills(nativeTakeover)
    SetEntryChecked(false, reason or "close")
    Controls.SupplyChainsLensPanel:SetHide(true)
    Controls.SupplyChainsLensDisplay:SetHide(true)
    if nativeTakeover and nativeModal and UI.GetInterfaceMode() == InterfaceModeTypes.VIEW_MODAL_LENS then
        nativeModal:SetHide(false)
    end
    if exitMode and UI.GetInterfaceMode() == InterfaceModeTypes.VIEW_MODAL_LENS then
        UI.SetInterfaceMode(InterfaceModeTypes.SELECTION)
    end
end

local function SetLegend()
    local legend = selected and S.GetLensLegend(selected)
    if legend == nil then return end
    Controls.LensTitle:SetText(Locale.ToUpper(Locale.Lookup(legend.LensTextKey)))
    legendRows:ResetInstances()
    for _, row in ipairs(legend.Legend) do
        local entry = legendRows:GetInstance()
        -- Firaxis ships a hollow swatch; nesting resized filled textures draws
        -- overlapping hexes because their native image stretch mode is fixed.
        entry.LegendColor:SetTexture(row.outlined and "Controls_KeySwatchHexEmpty" or "Controls_KeySwatchHex")
        entry.LegendColor:SetColor(row[2])
        entry.LegendLabel:LocalizeAndSetText(row[1])
    end
    Controls.LegendStack:CalculateSize()
    -- Allow 54 px above the rows for the header and 14 px below them.
    Controls.LegendPanel:SetSizeY(Controls.LegendStack:GetSizeY() + 68)
    Controls.LegendStack:ReprocessAnchoring()
end

local function SharedServiceEffects(playerID)
    if serviceEffects == nil then serviceEffects = S.CollectServiceEffects(playerID) end
    return serviceEffects
end

local function Refresh(forceBackground)
    if not active or selected == nil then return end
    if UI.GetInterfaceMode() ~= InterfaceModeTypes.VIEW_MODAL_LENS then Close(false); return end
    local overlayData = quarterData[selected]
    local servicesOnly = false
    if overlayData == nil then
        local background = {}
        overlayData = S.PrepareOverlay(S.GetPlotEntries(selected, false, background), false, SharedServiceEffects)
        overlayData.background = background
        overlayData.serviceRevision = serviceRevision
        quarterData[selected] = overlayData
    elseif overlayData.serviceRevision ~= serviceRevision then
        overlayData.markers = S.GetServiceMarkers(selected, overlayData.entries, SharedServiceEffects)
        overlayData.serviceRevision = serviceRevision
        servicesOnly = S.ActiveLensData == overlayData
    end
    if lensFocus then
        local marker
        if lensFocus.isQuarter then
            marker = overlayData.quarterPins[lensFocus.index]
        else
            marker = S.FindServiceMarker(overlayData.markers, lensFocus)
        end
        if marker == nil then
            lensFocus = nil
            servicesOnly = false
        end
    end
    if servicesOnly and not forceBackground and not activationPending then
        S.PublishPreparedServicePins(overlayData)
    else
        S.DrawPreparedOverlay("Lens", overlayData, forceBackground == true or activationPending, lensFocus)
    end
    SyncNativeHeader()
end

local function Invalidate(full)
    if full then quarterData = {} end
    serviceEffects = nil
    serviceRevision = serviceRevision + 1
end

local function OnWorldChanged()
    Invalidate(true)
    Refresh()
end

local function MarkMapDirty() mapDirty = true end
local function MarkServicesDirty() servicesDirty = true end

local mapEvents = {
    "PlotVisibilityChanged", "CityTileOwnershipChanged", "CityAddedToMap", "CityRemovedFromMap", "CityTransfered",
    "ResourceAddedToMap", "ResourceChanged", "ResourceRemovedFromMap",
    "ImprovementAddedToMap", "ImprovementChanged", "ImprovementRemovedFromMap",
    "DistrictAddedToMap", "DistrictBuildProgressChanged", "DistrictPillaged", "DistrictRemovedFromMap",
    "BuildingAddedToMap", "BuildingChanged", "BuildingRemovedFromMap", "TechCompleted", "CivicCompleted",
}
local serviceEvents = {"CityNameChanged", "CityPopulationChanged", "GovernmentPolicyChanged"}

local function BindInvalidationEvents(method)
    for _, name in ipairs(mapEvents) do
        if Events[name] then Events[name][method](MarkMapDirty) end
    end
    for _, name in ipairs(serviceEvents) do
        if Events[name] then Events[name][method](MarkServicesDirty) end
    end
end

local function OnGameCorePublish()
    -- Unknown publications can change visibility, supply or readiness too.
    Invalidate(mapDirty or not servicesDirty)
    mapDirty, servicesDirty = false, false
    if active and not refreshQueued then
        refreshQueued = true
        ContextPtr:RequestRefresh()
    end
end

local function OnPinFocus(owner, key, index, target, isQuarter)
    if shuttingDown or not active or owner ~= "Lens" or key ~= selected then return end
    lensFocus = index ~= nil and {index = index, target = target, isQuarter = isQuarter} or nil
    Refresh()
end

local function ShowLensControls()
    -- Reparenting our radio does not join MinimapPanel's context-local radio
    -- group. Clear its live choices without clicking them or changing modes.
    local function clearOthers(parent)
        for _, child in ipairs(parent:GetChildren()) do
            if child ~= Controls.SupplyChainsLensEntry then
                if child.IsChecked and child.SetCheck and child:IsChecked() then
                    child:SetCheck(false)
                end
                clearOthers(child)
            end
        end
    end
    if menuStack then clearOthers(menuStack) end
    Controls.SupplyChainsLensPanel:SetHide(false)
    Controls.SupplyChainsLensDisplay:SetHide(false)
    SyncNativeHeader()
    if menuPanel then menuPanel:SetHide(false) end
    local nativeButton = ContextPtr:LookUpControl("/InGame/MinimapPanel/LensButton")
    if nativeButton then nativeButton:SetSelected(true) end
end

FinishActivation = function()
    ContextPtr:ClearUpdate()
    activationPending = false
    Events.SystemUpdateUI.Remove(FinishActivation)
    if not active or UI.GetInterfaceMode() ~= InterfaceModeTypes.VIEW_MODAL_LENS or not UILens.IsLensActive("Appeal") then return end
    -- Paint after queued mode/layer cleanup has run, and restore the chooser
    -- that native minimap cleanup can hide during the intermediate mode exit.
    ShowLensControls()
    Refresh(true)
end

local function QueueActivation()
    activationPending = true
    ContextPtr:SetUpdate(FinishActivation)
    ContextPtr:RequestRefresh()
end

local function SelectQuarter(key)
    if S.Quarters[key] == nil then return end
    if selected ~= key then lensFocus = nil end
    selected = key
    for id, button in pairs(buttons) do
        button:SetCheck(id == key)
    end
    SetLegend()
    Refresh()
end

local function Attach()
    if shuttingDown or selected == nil or Game.GetLocalPlayer() == -1 then return false end
    local stack = ContextPtr:LookUpControl("/InGame/MinimapPanel/LensToggleStack")
    local panel = ContextPtr:LookUpControl("/InGame/MinimapPanel/LensPanel")
    local hud = ContextPtr:LookUpControl("/InGame/HUD")
    if stack == nil or panel == nil or hud == nil then
        return false
    end
    if menuStack ~= stack then
        menuStack, menuPanel = stack, panel
        local oldStackHeight = stack:GetSizeY()
        originalMenuHeight = panel:GetSizeY()
        Controls.SupplyChainsLensEntry:ChangeParent(stack)
        Controls.SupplyChainsLensEntry:SetHide(false)
        Controls.SupplyChainsLensPanel:ChangeParent(panel)
        stack:CalculateSize()
        stack:ReprocessAnchoring()
        -- Add only our row's height; preserve a modded menu's scroll viewport.
        attachedMenuHeight = originalMenuHeight + math.max(0, math.min(40, stack:GetSizeY() - oldStackHeight))
        panel:SetSizeY(attachedMenuHeight)
        local chooser = ContextPtr:LookUpControl("/InGame/MinimapPanel/LensChooserList")
        if chooser then chooser:CalculateSize() end
    end
    Controls.SupplyChainsLensPanel:SetOffsetX(panel:GetSizeX() + 5)
    nativeModal = ContextPtr:LookUpControl("/InGame/ModalLensPanel")
    nativeTitle = ContextPtr:LookUpControl("/InGame/ModalLensPanel/LensText")
    nativeKeyPanel = ContextPtr:LookUpControl("/InGame/ModalLensPanel/KeyPanel")
    local parent = nativeModal and nativeTitle and nativeModal or hud
    if displayParent ~= parent then
        Controls.SupplyChainsLensDisplay:ChangeParent(parent)
        displayParent = parent
    end
    return true
end

local function OnLayerOn(layer)
    -- A native or other mod's lens takes over. Preserve all of its layer data.
    -- Unrelated map-label layers can turn on while our Appeal carrier is active.
    if not active then return end
    if entryUncheckedPending or not entryChecked then Close(false, true, "another lens selected")
    elseif not UILens.IsLensActive("Appeal") then Close(false, true, "native layer " .. tostring(layer))
    elseif layer == appealLayer then
        -- Native minimap and modal callbacks just painted Appeal. Reclaim the
        -- shared layer and heading here, even if our context update has already
        -- run or is skipped while its controls are reparented.
        ShowLensControls()
        Refresh(true)
        QueueActivation()
    end
end

local function Open(key)
    if not Attach() or (key ~= nil and S.Quarters[key] == nil) then return end
    if active and UI.GetInterfaceMode() == InterfaceModeTypes.VIEW_MODAL_LENS and UILens.IsLensActive("Appeal") then
        SelectQuarter(key or selected)
        ShowLensControls()
        QueueActivation()
        return
    end
    -- Follow More Lenses: replace the active lens directly and enter modal mode
    -- only if necessary. A Selection round trip queues WorldInput's Default
    -- reset, which can erase the new overlay after this function has painted.
    Close(false)
    -- Optional compatibility handshake only; with no More Lenses listener this
    -- event is inert. It prevents its old modded lens from repainting our fill.
    settingCarrier = true
    LuaEvents.ML_CloseLensPanels()
    LuaEvents.MinimapPanel_SetActiveModLens("VANILLA_APPEAL")
    settingCarrier = false
    -- Join after the stock or More Lenses callbacks, which can register after
    -- our context loads. Later layer-on events must finish with CSC's paint.
    Events.LensLayerOn.Remove(OnLayerOn)
    Events.LensLayerOn.Add(OnLayerOn)
    UILens.SetActive("Appeal")
    if UI.GetInterfaceMode() ~= InterfaceModeTypes.VIEW_MODAL_LENS then
        UI.SetInterfaceMode(InterfaceModeTypes.VIEW_MODAL_LENS)
    end
    -- Native mode/layer cleanup may run synchronously during the mode change.
    -- Publish ownership only after that cleanup has completed.
    active = true
    SetEntryChecked(true, "open")
    SelectQuarter(key or selected)
    ShowLensControls()
    Refresh()
    QueueActivation()
end

local function OnEntryClick()
    if active and not entryChecked then Close(true) else Open() end
end

local function OnModeChanged(_, newMode)
    -- Interface-mode notifications can be queued. Open leaves a previous modal
    -- lens through Selection and re-enters modal mode before that intermediate
    -- Selection event arrives. Never close the new lens for the old event.
    local currentMode = UI.GetInterfaceMode()
    if newMode ~= currentMode then
        return
    end
    if not CanUseLensShortcutMode(newMode) then CancelHotkeys("interface mode " .. tostring(newMode)) end
    if newMode ~= InterfaceModeTypes.VIEW_MODAL_LENS then Close(false, false, "mode " .. tostring(newMode))
    elseif active then Refresh() end
end

local function OnLayerOff(layer)
    if active and layer == appealLayer and not UILens.IsLayerOn(appealLayer) then Close(false, true, "carrier off") end
end

local function OnMoreLensSelected(name)
    if active and not settingCarrier then Close(false, true, "More Lenses selected " .. tostring(name)) end
end

local nativeLensActions = {}
local nativeAppealAction = Input.GetActionId("LensAppeal")
for _, name in ipairs({"LensReligion", "LensContinent", "LensAppeal", "LensSettler", "LensGovernment", "LensPolitical", "LensTourism", "LensEmpire", "LensPower", "LensLoyalty"}) do
    local id = Input.GetActionId(name)
    if id ~= nil and id ~= -1 then nativeLensActions[id] = true end
end
local function OnNativeLensAction(id)
    if not nativeLensActions[id] then return end
    if DEBUG_HOTKEYS and (active or qHeld) then
        HotkeyDebug("native lens action=%s quarter=%s active=%s Q=%s captured1=%s captured2=%s", tostring(id),
            tostring(selected), tostring(active), tostring(qHeld), tostring(capturedKeys[Keys["1"]] == true),
            tostring(capturedKeys[Keys["2"]] == true))
    end
    if not active then return end
    Close(false, true, "native lens hotkey")
    if id == nativeAppealAction and UILens.IsLensActive("Appeal") then
        -- Our carrier is already Appeal, so vanilla SetActive("Appeal") is a
        -- no-op and emits no layer-on repaint. More Lenses does this same lens
        -- reset in ToggleAppealLens. Keep modal mode; a Selection round trip
        -- would queue WorldInput cleanup over the replacement's fresh colours.
        UILens.SetActive("Default")
        UILens.SetActive("Appeal")
    end
end
local function OnEntryChecked(checked)
    entryChecked = checked == true
    if shuttingDown then return end
    entryUncheckedPending = active and not entryChecked
    if entryUncheckedPending then RestoreNativeHeader(); ContextPtr:RequestRefresh() end
end

local function OnPlayerChanged()
    Invalidate(true)
    mapDirty, servicesDirty = false, false
    CancelHotkeys("local player changed")
    Close(true)
end
local function OnInput(input)
    local message, key = input:GetMessageType(), input:GetKey()
    if message ~= KeyEvents.KeyDown and message ~= KeyEvents.KeyUp then return false end
    local wasDown, captured = keysDown[key], capturedKeys[key]
    if message == KeyEvents.KeyDown and not wasDown then
        capturedKeys[key], captured = nil, nil
    end
    keysDown[key] = message == KeyEvents.KeyDown or nil
    -- The global observer may receive the same physical release repeatedly
    -- (seen in Lua.log, separated by World-context restoration). Keep capture
    -- latched through every copy. Only a fresh down above starts a new press;
    -- clearing here lets the second number-up launch the native Religion lens.
    if key == Keys.Q or hotkeyQuarters[key] or qHeld then
        local usable, reason = CanUseHotkeys()
        if input:IsControlDown() or input:IsAltDown() or input:IsShiftDown() then usable, reason = false, "modifier" end
        if DEBUG_HOTKEYS and ((message == KeyEvents.KeyDown and not wasDown) or (message == KeyEvents.KeyUp and wasDown)) then
            HotkeyDebug("key=%s message=%s Q=%s captured=%s context=%s mode=%s eligible=%s reason=%s", tostring(key), tostring(message), tostring(qHeld), tostring(captured == true), tostring(Input.GetActiveContext()), tostring(UI.GetInterfaceMode()), tostring(usable), reason or "world")
        end
        if not usable then
            -- Retain captured releases until delivered, but abandon the prefix.
            -- An interrupted chord must not become a plain Q tap on returning.
            qHeld, qUsed = false, false
            return captured == true
        end
        if key == Keys.Q then
            if message == KeyEvents.KeyDown then
                if not wasDown then qHeld, qUsed = true, false end
                capturedKeys[key] = true
            else
                if qHeld and not qUsed then TogglePlainQ() end
                qHeld, qUsed = false, false
            end
            return true
        elseif qHeld and message == KeyEvents.KeyDown then
            qUsed = true
            local quarter = hotkeyQuarters[key]
            if quarter and S.Quarters[quarter] and not wasDown then
                capturedKeys[key] = true
                HotkeyDebug("shortcut Q+%s -> %s", quarter == "BAKERS" and "1" or "2", quarter)
                Open(quarter)
                if DEBUG_HOTKEYS then
                    HotkeyDebug("shortcut result quarter=%s active=%s mode=%s", quarter, tostring(active), tostring(UI.GetInterfaceMode()))
                end
                return true
            elseif captured then return true end
        end
    end
    -- Swallow both ends (and repeat) of a recognized number even if Q was
    -- released first, so the native 1/2 lens action cannot follow our shortcut.
    if captured then return true end
    if active and input:GetKey() == Keys.VK_ESCAPE then
        if input:GetMessageType() == KeyEvents.KeyUp then Close(true, false, "Escape") end
        return true
    end
    return false
end

local function OnGlobalInput(input)
    local key = input:GetKey()
    local message, edge
    if DEBUG_HOTKEYS then
        message = input:GetMessageType()
        edge = (message == KeyEvents.KeyDown and not keysDown[key]) or (message == KeyEvents.KeyUp and keysDown[key])
    end
    -- A fresh event can arrive before the queued refresh. Release our previous
    -- event's mask first; never pop a popup's newer context from above ours.
    ReleaseInputMask()
    -- Let focused text/popups consume Escape before the local UI handler.
    if key == Keys.VK_ESCAPE then return end
    if OnInput(input) and Input.GetActiveContext() == InputContext.World then
        Input.PushActiveContext(shortcutInputContext)
        inputMaskOwned = true
        Events.SystemUpdateUI.Add(ReleaseInputMask)
        ContextPtr:RequestRefresh()
        if edge then HotkeyDebug("masked World actions for key=%s message=%s", tostring(key), tostring(message)) end
    elseif inputMaskOwned then
        ContextPtr:RequestRefresh()
    end
end

-- UIManager has one global Lua input slot. Firaxis's TunerUtilities registers
-- its own handler after contexts load, so an init-only registration can vanish
-- before the first Q press. Reattach at game/focus handoff, then once after the
-- other handoff callbacks. Do not compete for this slot on every frame/event.
local observerRepairQueued = false
local function InstallShortcutObserver(reason)
    if shuttingDown then return end
    UIManager:SetGlobalInputHandler(OnGlobalInput)
    HotkeyDebug("shortcut observer v4 installed reason=%s Q=%s one=%s two=%s", reason,
        tostring(Keys.Q), tostring(Keys["1"]), tostring(Keys["2"]))
end
local function FinishObserverRepair()
    Events.SystemUpdateUI.Remove(FinishObserverRepair)
    observerRepairQueued = false
    InstallShortcutObserver("handoff settled")
end
local function RepairShortcutObserver(reason)
    InstallShortcutObserver(reason)
    if not shuttingDown and not observerRepairQueued then
        observerRepairQueued = true
        Events.SystemUpdateUI.Add(FinishObserverRepair)
    end
end
local function OnLoadScreenClose()
    Invalidate(true)
    mapDirty, servicesDirty = false, false
    Attach()
    RepairShortcutObserver("load screen closed")
end
local function OnAppRegainedFocus()
    CancelHotkeys("app regained focus")
    ReleaseInputMask()
    RepairShortcutObserver("app regained focus")
end

local function OnInputRefresh()
    ContextPtr:ClearRequestRefresh()
    ReleaseInputMask()
    if entryUncheckedPending and active and not entryChecked then
        Close(false, true, "another lens selected")
    end
    if activationPending and active then ShowLensControls() end
    if refreshQueued or (activationPending and active) then
        refreshQueued = false
        Refresh()
    end
end

local function OnContextInput(input)
    -- Global observation handles the chord once, even when our visual controls
    -- have been reparented into other contexts. Keep Escape local as well.
    if active and input:GetKey() == Keys.VK_ESCAPE then
        if input:GetMessageType() == KeyEvents.KeyUp then Close(true, false, "Escape") end
        return true
    end
    return false
end

local function OnShutdown()
    shuttingDown = true
    ResetHotkeys()
    ReleaseInputMask()
    Events.SystemUpdateUI.Remove(ReleaseInputMask)
    Events.SystemUpdateUI.Remove(FinishActivation)
    Events.SystemUpdateUI.Remove(FinishObserverRepair)
    observerRepairQueued = false
    UIManager:ClearGlobalInputHandler()
    Close(false, false, "shutdown")
    if nativeModal and UI.GetInterfaceMode() == InterfaceModeTypes.VIEW_MODAL_LENS then nativeModal:SetHide(false) end
    LuaEvents.CSC_SupplyChainsLens_OpenPanel.Remove(Open)
    LuaEvents.CSC_SupplyChainsLens_Refresh.Remove(OnWorldChanged)
    LuaEvents.CSC_QuarterServiceFocus.Remove(OnPinFocus)
    Events.InterfaceModeChanged.Remove(OnModeChanged)
    Events.LensLayerOn.Remove(OnLayerOn)
    Events.LensLayerOff.Remove(OnLayerOff)
    Events.InputActionTriggered.Remove(OnNativeLensAction)
    LuaEvents.MinimapPanel_ModdedLensOn.Remove(OnMoreLensSelected)
    Events.LocalPlayerChanged.Remove(OnPlayerChanged)
    Events.GameCoreEventPublishComplete.Remove(OnGameCorePublish)
    BindInvalidationEvents("Remove")
    Events.LoadScreenClose.Remove(OnLoadScreenClose)
    rows:ResetInstances()
    legendRows:ResetInstances()
    if menuStack then menuStack:DestroyChild(Controls.SupplyChainsLensEntry) end
    if menuPanel then
        menuPanel:DestroyChild(Controls.SupplyChainsLensPanel)
        if menuPanel:GetSizeY() == attachedMenuHeight then menuPanel:SetSizeY(originalMenuHeight) end
    end
    if displayParent then displayParent:DestroyChild(Controls.SupplyChainsLensDisplay) end
end

for _, quarter in ipairs(quarters) do
    local key = quarter.id
    local button = rows:GetInstance().QuarterButton
    buttons[key] = button
    button:GetTextButton():LocalizeAndSetText(quarter.locName)
    button:SetToolTipString(Locale.Lookup(quarter.locTooltip))
    button:SetCheck(key == selected)
    button:RegisterCallback(Mouse.eLClick, function()
        Open(key)
    end)
end
Controls.SupplyChainsLensPanel:SetSizeY(math.max(140, math.min(360, 68 + #quarters * 35)))
Controls.QuarterChoices:CalculateSize()
Controls.QuarterChoices:ReprocessAnchoring()
Controls.QuarterScroll:CalculateSize()
Controls.SupplyChainsLensEntry:RegisterCallback(Mouse.eLClick, OnEntryClick)
Controls.SupplyChainsLensEntry:RegisterCheckHandler(OnEntryChecked)
Controls.CloseButton:RegisterCallback(Mouse.eLClick, function() Close(true) end)
Controls.SupplyChainsLensEntry:SetToolTipString(Locale.Lookup("LOC_HUD_CSC_SUPPLY_CHAINS_LENS_TOOLTIP"))
ContextPtr:SetInitHandler(function(isReload)
    if isReload then Attach(); RepairShortcutObserver("UI context reload") end
end)
ContextPtr:SetShutdown(OnShutdown)
ContextPtr:SetInputHandler(OnContextInput, true)
ContextPtr:SetRefreshHandler(OnInputRefresh)
InstallShortcutObserver("startup")
HotkeyDebug("loaded; quarters=%s; global shortcut observer installed; Q+1=BAKERS Q+2=TAILORS", tostring(#quarters))
ContextPtr:SetAppLostFocusHandler(function() CancelHotkeys("app lost focus") end)
ContextPtr:SetAppRegainedFocusHandler(OnAppRegainedFocus)
LuaEvents.CSC_SupplyChainsLens_OpenPanel.Add(Open)
LuaEvents.CSC_SupplyChainsLens_Refresh.Add(OnWorldChanged)
LuaEvents.CSC_QuarterServiceFocus.Add(OnPinFocus)
Events.InterfaceModeChanged.Add(OnModeChanged)
Events.LensLayerOn.Add(OnLayerOn)
Events.LensLayerOff.Add(OnLayerOff)
Events.InputActionTriggered.Add(OnNativeLensAction)
LuaEvents.MinimapPanel_ModdedLensOn.Add(OnMoreLensSelected)
Events.LocalPlayerChanged.Add(OnPlayerChanged)
Events.GameCoreEventPublishComplete.Add(OnGameCorePublish)
BindInvalidationEvents("Add")
Events.LoadScreenClose.Add(OnLoadScreenClose)
