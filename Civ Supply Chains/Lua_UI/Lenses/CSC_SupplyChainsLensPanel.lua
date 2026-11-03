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
-- Mirror the native radio value while its control and callback owner are live.
-- SetCheck fires native/Lua callbacks even for a redundant false assignment;
-- never initiate that callback path while the UI context is being destroyed.
local entryChecked = Controls.SupplyChainsLensEntry:IsChecked() == true
local lastDrawSummary = nil
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
local DEBUG = true
local function Debug(format, ...)
    if DEBUG then print("CSC Lenses: " .. string.format(format, ...)) end
end

local function SetEntryChecked(checked, reason)
    checked = checked == true
    if shuttingDown then
        Debug("entry check skipped during shutdown desired=%s reason=%s", tostring(checked), reason or "reset")
        return
    end
    if entryChecked == checked then return end
    -- Publish first: native SetCheck may synchronously call our check handler.
    entryChecked = checked
    Debug("entry check begin value=%s reason=%s", tostring(checked), reason or "reset")
    Controls.SupplyChainsLensEntry:SetCheck(checked)
    Debug("entry check end value=%s", tostring(checked))
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
        Debug("restored input context=%s", tostring(Input.GetActiveContext()))
    end
end

local function ResetHotkeys()
    qHeld, qUsed = false, false
    keysDown, capturedKeys = {}, {}
end

local function CancelHotkeys(reason)
    if qHeld then Debug("cancelled Q prefix reason=%s", reason or "interrupted") end
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
        Debug("plain Q: resource icons=%s", tostring(UserConfiguration.ShowMapResources()))
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
    entryUncheckedPending = false
    ContextPtr:ClearUpdate()
    if active then Debug("close quarter=%s reason=%s mode=%s", tostring(selected), reason or "reset", tostring(UI.GetInterfaceMode())) end
    active = false
    RestoreNativeHeader()
    lastDrawSummary = nil
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
    Controls.LegendScroll:CalculateSize()
end

local function Refresh(forceBackground)
    if not active or selected == nil then return end
    if UI.GetInterfaceMode() ~= InterfaceModeTypes.VIEW_MODAL_LENS then Close(false); return end
    local entries = S.GetPlotEntries(selected)
    local painted, stats = S.DrawOverlay("Lens", entries, forceBackground == true or activationPending)
    local categories = {}
    for _, entry in ipairs(entries) do categories[entry.category] = (categories[entry.category] or 0) + 1 end
    local summary = selected .. ":" .. tostring(#entries) .. ":" .. tostring(painted)
        .. ":" .. tostring(stats and stats.outlines) .. ":" .. tostring(stats and stats.flows) .. ":" .. tostring(stats and stats.palette)
        .. ":" .. tostring(stats and stats.flowSignature)
        .. ":" .. tostring(stats and stats.fillRebuilt) .. ":" .. tostring(stats and stats.outlinesRebuilt)
        .. ":" .. tostring(stats and stats.backgroundRepainted)
        .. ":" .. tostring(stats and stats.tintRebuilt)
        .. ":" .. tostring(stats and stats.services)
    if summary ~= lastDrawSummary then
        Debug("draw quarter=%s plots=%s fillAvailable=%s", selected, tostring(#entries), tostring(painted))
        if stats then
            Debug("functional service pins=%s presentationAvailable=%s rebuilt=%s", tostring(stats.services), tostring(stats.servicesAvailable), tostring(stats.servicesRebuilt))
            Debug("fill styles=%s channels=%s outlined=%s base=%s specialty=%s sales=%s ignored=%s", tostring(stats.styles), tostring(stats.channels), tostring(stats.outlines), tostring((categories.BASE_IMPROVED or 0) + (categories.BASE_UNIMPROVED or 0)), tostring((categories.SPEC_IMPROVED or 0) + (categories.SPEC_UNIMPROVED or 0)), tostring(categories.SALE or 0), tostring(categories.IGNORE or 0))
            Debug("fill packed-colour=plot-count: %s", stats.palette)
            Debug("fill backend=%s carrierOn=%s", stats.backend, tostring(UILens.IsLayerOn(appealLayer)))
            Debug("direct RGBA fill layerAvailable=%s plots=%s alpha=Base30%%/otherUnready20%%/ready60%% rebuilt=%s", tostring(stats.tintAvailable), tostring(stats.tintPlots), tostring(stats.tintRebuilt))
            Debug("texture fill layerAvailable=%s plots=%s alpha=Base30%%/otherUnready20%%/ready60%% rebuilt=%s outlinesRebuilt=%s backgroundRepainted=%s", tostring(stats.textureFillAvailable), tostring(stats.textureFillPlots), tostring(stats.fillRebuilt), tostring(stats.outlinesRebuilt), tostring(stats.backgroundRepainted))
            Debug("outline layerAvailable=%s material=%s styles=%s", tostring(stats.readyAvailable), stats.readyMaterial, tostring(stats.readyStyles))
            Debug("working supply-chain connections=%s layerAvailable=%s links(source:target:type)=%s", tostring(stats.flows), tostring(stats.flowAvailable), string.sub(stats.flowSignature or "", 1, 512))
        end
        lastDrawSummary = summary
    end
    SyncNativeHeader()
end

local function ShowLensControls()
    -- Reparenting our radio does not join MinimapPanel's context-local radio
    -- group. Clear its live choices without clicking them or changing modes.
    local cleared = 0
    local function clearOthers(parent)
        for _, child in ipairs(parent:GetChildren()) do
            if child ~= Controls.SupplyChainsLensEntry then
                if child.IsChecked and child.SetCheck and child:IsChecked() then
                    child:SetCheck(false)
                    cleared = cleared + 1
                end
                clearOthers(child)
            end
        end
    end
    if menuStack then clearOthers(menuStack) end
    if cleared > 0 then Debug("cleared previous lens menu selections=%s", tostring(cleared)) end
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
    Debug("activation settled quarter=%s; menu restored and overlay repainted", tostring(selected))
end

local function QueueActivation()
    activationPending = true
    ContextPtr:SetUpdate(FinishActivation)
    ContextPtr:RequestRefresh()
end

local function SelectQuarter(key)
    if S.Quarters[key] == nil then return end
    selected = key
    for id, button in pairs(buttons) do
        Debug("choice check begin quarter=%s value=%s", tostring(id), tostring(id == key))
        button:SetCheck(id == key)
        Debug("choice check end quarter=%s", tostring(id))
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
        Debug("attach blocked stack=%s panel=%s HUD=%s", tostring(stack ~= nil), tostring(panel ~= nil), tostring(hud ~= nil))
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

local function Open(key)
    Debug("open request quarter=%s mode=%s", tostring(key or selected), tostring(UI.GetInterfaceMode()))
    if not Attach() or (key ~= nil and S.Quarters[key] == nil) then return end
    if active and UI.GetInterfaceMode() == InterfaceModeTypes.VIEW_MODAL_LENS and UILens.IsLensActive("Appeal") then
        SelectQuarter(key or selected)
        ShowLensControls()
        QueueActivation()
        Debug("switched active Quarter=%s without restarting modal mode", tostring(selected))
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
    Debug("opened quarter=%s active=%s mode=%s", tostring(selected), tostring(active), tostring(UI.GetInterfaceMode()))
end

local function OnEntryClick()
    Debug("Supply Chains clicked checked=%s active=%s", tostring(entryChecked), tostring(active))
    if active and not entryChecked then Close(true) else Open() end
end

local function OnModeChanged(_, newMode)
    -- Interface-mode notifications can be queued. Open leaves a previous modal
    -- lens through Selection and re-enters modal mode before that intermediate
    -- Selection event arrives. Never close the new lens for the old event.
    local currentMode = UI.GetInterfaceMode()
    if newMode ~= currentMode then
        Debug("ignored stale mode notification=%s current=%s active=%s", tostring(newMode), tostring(currentMode), tostring(active))
        return
    end
    if not CanUseLensShortcutMode(newMode) then CancelHotkeys("interface mode " .. tostring(newMode)) end
    if newMode ~= InterfaceModeTypes.VIEW_MODAL_LENS then Close(false, false, "mode " .. tostring(newMode))
    elseif active then Refresh() end
end

local function OnLayerOn(layer)
    -- A native or other mod's lens takes over. Preserve all of its layer data.
    -- Unrelated map-label layers can turn on while our Appeal carrier is active.
    if not active then return end
    if entryUncheckedPending or not entryChecked then Close(false, true, "another lens selected")
    elseif not UILens.IsLensActive("Appeal") then Close(false, true, "native layer " .. tostring(layer))
    elseif layer == appealLayer then QueueActivation() end
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
    if not active or not nativeLensActions[id] then return end
    Close(false, true, "native lens hotkey")
    if id == nativeAppealAction and UILens.IsLensActive("Appeal") then
        -- Our carrier is already Appeal, so vanilla SetActive("Appeal") is a
        -- no-op and emits no layer-on repaint. More Lenses does this same lens
        -- reset in ToggleAppealLens. Keep modal mode; a Selection round trip
        -- would queue WorldInput cleanup over the replacement's fresh colours.
        UILens.SetActive("Default")
        UILens.SetActive("Appeal")
        Debug("native Appeal handoff: carrier restarted for native tile paint")
    end
end
local function OnEntryChecked(checked)
    entryChecked = checked == true
    if shuttingDown then return end
    entryUncheckedPending = active and not entryChecked
    if entryUncheckedPending then RestoreNativeHeader(); ContextPtr:RequestRefresh() end
end

local function OnPlayerChanged() CancelHotkeys("local player changed"); Close(true) end
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
        if (message == KeyEvents.KeyDown and not wasDown) or (message == KeyEvents.KeyUp and wasDown) then
            Debug("key=%s message=%s Q=%s captured=%s context=%s mode=%s eligible=%s reason=%s", tostring(key), tostring(message), tostring(qHeld), tostring(captured == true), tostring(Input.GetActiveContext()), tostring(UI.GetInterfaceMode()), tostring(usable), reason or "world")
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
                Debug("shortcut Q+%s -> %s", quarter == "BAKERS" and "1" or "2", quarter)
                Open(quarter)
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
    -- A fresh event can arrive before the queued refresh. Release our previous
    -- event's mask first; never pop a popup's newer context from above ours.
    ReleaseInputMask()
    -- Let focused text/popups consume Escape before the local UI handler.
    if input:GetKey() == Keys.VK_ESCAPE then return end
    if OnInput(input) and Input.GetActiveContext() == InputContext.World then
        Input.PushActiveContext(shortcutInputContext)
        inputMaskOwned = true
        Events.SystemUpdateUI.Add(ReleaseInputMask)
        ContextPtr:RequestRefresh()
        Debug("masked World actions for key=%s message=%s", tostring(input:GetKey()), tostring(input:GetMessageType()))
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
    Debug("shortcut observer v4 installed reason=%s Q=%s one=%s two=%s", reason,
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
    if activationPending and active then ShowLensControls(); Refresh() end
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
    Debug("shutdown begin active=%s entry=%s", tostring(active), tostring(entryChecked))
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
    LuaEvents.CSC_SupplyChainsLens_Refresh.Remove(Refresh)
    Events.InterfaceModeChanged.Remove(OnModeChanged)
    Events.LensLayerOn.Remove(OnLayerOn)
    Events.LensLayerOff.Remove(OnLayerOff)
    Events.InputActionTriggered.Remove(OnNativeLensAction)
    LuaEvents.MinimapPanel_ModdedLensOn.Remove(OnMoreLensSelected)
    Events.LocalPlayerChanged.Remove(OnPlayerChanged)
    Events.GameCoreEventPublishComplete.Remove(Refresh)
    Events.LoadScreenClose.Remove(OnLoadScreenClose)
    rows:ResetInstances()
    legendRows:ResetInstances()
    if menuStack then menuStack:DestroyChild(Controls.SupplyChainsLensEntry) end
    if menuPanel then
        menuPanel:DestroyChild(Controls.SupplyChainsLensPanel)
        if menuPanel:GetSizeY() == attachedMenuHeight then menuPanel:SetSizeY(originalMenuHeight) end
    end
    if displayParent then displayParent:DestroyChild(Controls.SupplyChainsLensDisplay) end
    Debug("shutdown complete")
end

for _, quarter in ipairs(quarters) do
    local key = quarter.id
    local button = rows:GetInstance().QuarterButton
    buttons[key] = button
    button:GetTextButton():LocalizeAndSetText(quarter.locName)
    button:SetToolTipString(Locale.Lookup(quarter.locTooltip))
    Debug("choice init begin quarter=%s", tostring(key))
    button:SetCheck(key == selected)
    Debug("choice init end quarter=%s", tostring(key))
    button:RegisterCallback(Mouse.eLClick, function()
        Debug("Quarter choice clicked=%s active=%s", key, tostring(active))
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
Debug("loaded; quarters=%s; global shortcut observer installed; Q+1=BAKERS Q+2=TAILORS", tostring(#quarters))
ContextPtr:SetAppLostFocusHandler(function() CancelHotkeys("app lost focus") end)
ContextPtr:SetAppRegainedFocusHandler(OnAppRegainedFocus)
LuaEvents.CSC_SupplyChainsLens_OpenPanel.Add(Open)
LuaEvents.CSC_SupplyChainsLens_Refresh.Add(Refresh)
Events.InterfaceModeChanged.Add(OnModeChanged)
Events.LensLayerOn.Add(OnLayerOn)
Events.LensLayerOff.Add(OnLayerOff)
Events.InputActionTriggered.Add(OnNativeLensAction)
LuaEvents.MinimapPanel_ModdedLensOn.Add(OnMoreLensSelected)
Events.LocalPlayerChanged.Add(OnPlayerChanged)
Events.GameCoreEventPublishComplete.Add(Refresh)
Events.LoadScreenClose.Add(OnLoadScreenClose)
