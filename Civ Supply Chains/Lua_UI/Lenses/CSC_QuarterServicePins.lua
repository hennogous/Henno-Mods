-- Camera-facing Quarter and Service markers above the world. These controls
-- share focus without changing the player's saved MapPin collection.
include("InstanceManager")
local instances = InstanceManager:new("QuarterServicePin", "Anchor", Controls.ServicePins)
local owners, visible = {}, {}
local shuttingDown = false
local worldViewParent = nil
local focus = nil
local Draw
-- Match WorldViewIconsManager.GetInstanceAt so pins sit at the resource icon
-- position on each tile. Groups of Services are centered around this point.
local resourceIconOffsetY = -16
-- Quarter atlases include a matching grayscale face for unfocused pins.
local grayscaleQuarterIcons = {
    BAKERS = "ICON_DISTRICT_CSC_BAKERS_QUARTER_GRAY",
    TAILORS = "ICON_DISTRICT_CSC_TAILORS_QUARTER_GRAY",
}

local function SetFocus(owner, key, record, id)
    if shuttingDown then return end
    local previous = focus
    if previous and previous.owner == owner and previous.key == key and previous.id == id then
        record = nil -- Clicking the focused marker again restores the full lens.
    end
    focus = record and {owner = owner, key = key, id = id} or nil
    if previous and (not focus or previous.owner ~= owner or previous.key ~= key) then
        LuaEvents.CSC_QuarterServiceFocus(previous.owner, previous.key)
    end
    if record then LuaEvents.CSC_QuarterServiceFocus(owner, key, record.index, record.target, record.isQuarter) end
    Draw()
end

local function Slots(count, index)
    local spacing = 562 -- Preserve the pin group footprint at the atlas control scale.
    local half = spacing / 2
    if count == 1 then return 0, 0 end
    if count == 2 then return (index - 1.5) * spacing, 0 end
    if count == 3 then
        if index == 1 then return 0, -half end
        return (index == 2 and -half or half), half
    end
    -- Four form a square. Additional future services continue in paired rows.
    return ((index - 1) % 2 == 0 and -half or half), (math.floor((index - 1) / 2) - .5) * spacing
end

Draw = function()
    if shuttingDown or worldViewParent == nil then return end
    local owner = "Lens"
    local source = owners[owner]
    local records = source and source.markers or {}
    local counts, ranks, keep = {}, {}, {}
    for _, record in ipairs(records) do
        if record.icon then counts[record.index] = (counts[record.index] or 0) + 1 end
    end
    for _, record in ipairs(records) do
        if record.icon then
            local isQuarter = record.isQuarter == true
            local id = record.index .. ":" .. (isQuarter and "QUARTER" or record.target)
            keep[id] = true
            local pin = visible[id]
            if pin == nil then pin = instances:GetInstance(); visible[id] = pin end
            ranks[record.index] = (ranks[record.index] or 0) + 1
            local offsetX, offsetY = Slots(counts[record.index], ranks[record.index])
            if pin.index ~= record.index then
                local x, y = UI.GridToWorld(record.index)
                pin.Anchor:SetWorldPositionVal(x, y + resourceIconOffsetY, 0)
                pin.index = record.index
            end
            if pin.offsetX ~= offsetX or pin.offsetY ~= offsetY then
                pin.PinRoot:SetOffsetVal(offsetX, offsetY)
                pin.offsetX, pin.offsetY = offsetX, offsetY
            end
            local key = source.key
            local grayIcon = isQuarter and grayscaleQuarterIcons[key] or nil
            local kindChanged = pin.isQuarter ~= isQuarter
            local iconChanged = kindChanged or pin.iconName ~= record.icon or pin.key ~= key
            if iconChanged then
                pin.QuarterIcon:SetHide(not grayIcon)
                pin.ServiceIcon:SetHide(grayIcon ~= nil)
                pin.isQuarter = isQuarter
            end
            local tooltip = record.tooltip
            if pin.tooltip ~= tooltip then
                pin.ServiceButton:SetToolTipString(tooltip)
                pin.tooltip = tooltip
            end
            local target = record.target
            local focused = focus ~= nil and focus.owner == owner and focus.key == key and focus.id == id
            local dim = focus ~= nil and not focused
            if isQuarter then
                if iconChanged or pin.dim ~= dim then
                    pin.Backing:SetHide(not grayIcon)
                    if grayIcon then
                        pin.Backing:SetTexture(dim and "CSC_QuarterLensBackingGray.dds" or "CSC_QuarterLensBacking.dds")
                        pin.QuarterIcon:SetIcon(dim and grayIcon or record.icon, 256)
                    else
                        -- Future Quarters can use their registered district icon
                        -- while their matching frame and grayscale face are pending.
                        pin.ServiceIcon:SetIcon(record.icon, 256)
                        pin.ServiceIcon:SetAlpha(dim and .5 or 1)
                    end
                end
            elseif iconChanged then
                pin.ServiceIcon:SetIcon(record.icon, 256)
            end
            pin.iconName = record.icon
            if kindChanged or pin.dim ~= dim then
                if not isQuarter then
                    pin.Backing:SetHide(false)
                    pin.Backing:SetTexture(dim and "CSC_ServiceMedallionGray.dds" or "CSC_ServiceMedallion.dds")
                    pin.ServiceIcon:SetAlpha(dim and .5 or 1)
                end
                pin.dim = dim
            end
            if pin.id ~= id or pin.owner ~= owner or pin.key ~= key then
                pin.id, pin.owner, pin.key = id, owner, key
                pin.ServiceButton:RegisterCallback(Mouse.eLClick, function()
                    if isQuarter or record.stage then SetFocus(owner, key, record, id) end
                end)
                if isQuarter then
                    pin.ServiceButton:RegisterCallback(Mouse.eMouseEnter, function()
                        if shuttingDown then return end
                        local snapshot = owners[owner]
                        if snapshot and snapshot.key == key then
                            if not CSC_QuarterTooltip then include("CSC_QuarterTooltip") end
                            local text = snapshot.tooltips[record.index]
                            if text == nil then
                                text = CSC_QuarterTooltip.Format(snapshot, key, record.index)
                                snapshot.tooltips[record.index] = text
                            end
                            pin.ServiceButton:SetToolTipString(text)
                        end
                    end)
                else
                    pin.ServiceButton:RegisterCallback(Mouse.eRClick, function()
                        if not shuttingDown then LuaEvents.OpenCivilopedia(target) end
                    end)
                end
            end
        end
    end
    for id, pin in pairs(visible) do
        if not keep[id] then
            pin.ServiceButton:ClearCallback(Mouse.eRClick)
            pin.ServiceButton:ClearCallback(Mouse.eLClick)
            pin.ServiceButton:ClearCallback(Mouse.eMouseEnter)
            pin.ServiceButton:SetToolTipString("")
            pin.id, pin.tooltip = nil, nil
            instances:ReleaseInstance(pin)
            visible[id] = nil
        end
    end
    if focus and (focus.owner ~= owner or focus.key ~= (source and source.key) or not keep[focus.id]) then SetFocus() end
end

local function OnUpdate(owner, key, markers, links)
    if shuttingDown or owner ~= "Lens" then return end
    owners[owner] = {key=key, markers=markers, links=links or {}, tooltips={}}
    Draw()
end

local function OnPlayerChanged()
    owners = {}
    if ExposedMembers then ExposedMembers.CSC_QuarterServicePins = {} end
    Draw()
end

local function Initialize()
    if shuttingDown then return end
    local parent = ContextPtr:LookUpControl("/InGame/WorldViewControls")
    if parent == nil then
        return
    end
    -- InGame.Initialize loads every AddUserInterfaces context with isHidden=true.
    -- Creating visible instances does not unhide that ancestor. Native map pins
    -- live under WorldViewControls; join that same visibility/draw-order group
    -- and explicitly show our context after its initialization, not just XML.
    if worldViewParent ~= parent then
        ContextPtr:ChangeParent(parent)
        worldViewParent = parent
    end
    ContextPtr:SetHide(false)
    Events.LoadScreenClose.Remove(Initialize)
    Draw()
end

LuaEvents.CSC_QuarterServicePins_Update.Add(OnUpdate)
Events.LocalPlayerChanged.Add(OnPlayerChanged)
Events.LoadScreenClose.Add(Initialize)
ContextPtr:SetInitHandler(Initialize)
ContextPtr:SetShutdown(function()
    shuttingDown = true
    LuaEvents.CSC_QuarterServicePins_Update.Remove(OnUpdate)
    Events.LocalPlayerChanged.Remove(OnPlayerChanged)
    Events.LoadScreenClose.Remove(Initialize)
    -- The engine owns control destruction. No UI/native calls during teardown.
end)
local pending = ExposedMembers and ExposedMembers.CSC_QuarterServicePins or {}
for owner, source in pairs(pending) do OnUpdate(owner, source.key, source.markers, source.links) end
