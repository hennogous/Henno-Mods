-- A native UI marker above the world, rather than a decal on district models.
-- Native gold medallions; no changes to the player's saved MapPin collection.
include("InstanceManager")
include("CSC_QuarterLensSupport")
local S = CSC_QuarterLensSupport
local instances = InstanceManager:new("QuarterServicePin", "Anchor", Controls.ServicePins)
local owners, visible = {}, {}
local shuttingDown = false
local lastSignature = nil
local worldViewParent = nil

local function Slots(count, index)
    if count == 1 then return 0, 0 end
    if count == 2 then return (index - 1.5) * 88, 0 end
    if count == 3 then
        if index == 1 then return 0, -44 end
        return (index == 2 and -44 or 44), 44
    end
    -- Four form a square. Additional future services continue in paired rows.
    return ((index - 1) % 2 == 0 and -44 or 44), (math.floor((index - 1) / 2) - .5) * 88
end

local function Draw()
    if shuttingDown or worldViewParent == nil then return end
    -- Placement has visual ownership when both contexts are temporarily active.
    local source = owners.Placement and owners.Placement.key and owners.Placement or owners.Lens
    local records = source and source.markers or {}
    local counts, ranks, keep, signature = {}, {}, {}, {}
    for _, record in ipairs(records) do
        if record.icon then counts[record.index] = (counts[record.index] or 0) + 1 end
    end
    for _, record in ipairs(records) do
        if record.icon then
            local id = record.index .. ":" .. record.target
            keep[id] = true
            local pin = visible[id]
            if pin == nil then pin = instances:GetInstance(); visible[id] = pin end
            ranks[record.index] = (ranks[record.index] or 0) + 1
            local offsetX, offsetY = Slots(counts[record.index], ranks[record.index])
            local x, y = UI.GridToWorld(record.index)
            -- WorldAnchor is composited as UI above 3D buildings; the native
            -- medallion's bottom touches the tile centre; its face floats above.
            pin.Anchor:SetWorldPositionVal(x, y, 0)
            pin.PinRoot:SetOffsetVal(offsetX, offsetY)
            if pin.iconName ~= record.icon then
                -- Use the registered 38px atlas, nearest to 75% of the old 50px.
                pin.ServiceIcon:SetIcon(record.icon, 38)
                pin.iconName = record.icon
            end
            if pin.tooltip ~= record.tooltip then
                pin.ServiceButton:SetToolTipString(record.tooltip)
                pin.tooltip = record.tooltip
            end
            local target = record.target
            pin.ServiceButton:RegisterCallback(Mouse.eRClick, function()
                if not shuttingDown then LuaEvents.OpenCivilopedia(target) end
            end)
            signature[#signature+1] = id .. "=" .. record.icon .. ":" .. record.tooltip
        end
    end
    for id, pin in pairs(visible) do
        if not keep[id] then
            pin.ServiceButton:ClearCallback(Mouse.eRClick)
            pin.ServiceButton:SetToolTipString("")
            pin.tooltip = nil
            instances:ReleaseInstance(pin)
            visible[id] = nil
        end
    end
    local nextSignature = table.concat(signature, "|")
    if lastSignature ~= nextSignature then
        print("CSC Service Pins: pins=" .. #signature .. " quarter=" .. tostring(source and source.key))
        lastSignature = nextSignature
    end
end

local function OnUpdate(owner, key, markers)
    if shuttingDown or (owner ~= "Lens" and owner ~= "Placement") then return end
    owners[owner] = {key=key, markers=markers}
    Draw()
end

local function Refresh()
    if shuttingDown then return end
    -- No per-frame polling: refresh cumulative benefits and active recipient
    -- gates after GameCore publishes, including while placement remains open.
    for _, source in pairs(owners) do
        if source.key then source.markers = S.GetServiceMarkers(source.key) end
    end
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
        print("CSC Service Pins: waiting for WorldViewControls")
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
    print("CSC Service Pins: attached WorldViewControls contextVisible=true")
    Draw()
end

LuaEvents.CSC_QuarterServicePins_Update.Add(OnUpdate)
Events.GameCoreEventPublishComplete.Add(Refresh)
Events.LocalPlayerChanged.Add(OnPlayerChanged)
Events.LoadScreenClose.Add(Initialize)
ContextPtr:SetInitHandler(Initialize)
ContextPtr:SetShutdown(function()
    shuttingDown = true
    LuaEvents.CSC_QuarterServicePins_Update.Remove(OnUpdate)
    Events.GameCoreEventPublishComplete.Remove(Refresh)
    Events.LocalPlayerChanged.Remove(OnPlayerChanged)
    Events.LoadScreenClose.Remove(Initialize)
    -- The engine owns control destruction. No UI/native calls during teardown.
end)
local pending = ExposedMembers and ExposedMembers.CSC_QuarterServicePins or {}
for owner, source in pairs(pending) do OnUpdate(owner, source.key, source.markers) end
print("CSC Service Pins: loaded v3 (gold medallions; service art, MCUIS tooltip and Civilopedia)")
