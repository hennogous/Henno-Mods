-- Native fading conveyor waves for the existing working supply-chain links.
-- PressureOverlay supplies the shipped chevrons' quartic opacity envelope.
-- The retained chevron/trade comparisons use PathOverlay. Both are native
-- map overlays, without zero-height UI Lines or per-frame Lua animation.
-- Width/repeat/scroll/alpha are authored by build_chevron_art.py; the native
-- renderer animates them. No per-frame Lua timer or gameplay writes are needed.
local STYLES = {conveyor="ConveyorWaves", chevrons="Chevrons", trade="Trade"}
local OWNERS = {"Lens"}
local owners, signatures = {}, {}
-- The default now uses CSC's thick chevron texture. Keep the earlier native-art
-- styles available for comparison, with PressureOverlay as the old-art fallback.
local state = {Enabled=true, Ready=false, Style="conveyor"}
ExposedMembers.CSC_QuarterFlowTrial = state
local shuttingDown = false
local function Name(owner, style)
    return "CSC_Quarter" .. owner .. "_Flow" .. STYLES[style]
end

local function IsWave(style) return style ~= "chevrons" and style ~= "trade" end

local function Reset(overlay, style)
    if IsWave(style) then overlay:ResetAllWaves() else overlay:ClearAllPaths() end
end

local function ConveyorWave(wave, alpha)
    -- The native wave color supplies the chevrons' white tint and peak opacity.
    -- Speed 3 controls wave spacing. The material scroll controls travel speed.
    return {pos1=wave.pos1, pos2=wave.pos2,
        type=wave.type, speed=3, color=alpha * 0x1000000 + 0xffffff}
end

local function Clear(owner, style)
    local name = Name(owner,style)
    local overlay = UILens.GetOverlay(name)
    if overlay and signatures[name] then Reset(overlay, style) end
    if overlay then overlay:SetVisible(false) end
    signatures[name] = nil
end

local function Rebuild()
    local ready = state.Enabled
    for _, owner in ipairs(OWNERS) do
        local waves = owners[owner] or {}
        for style in pairs(STYLES) do
            local name = Name(owner,style)
            if not state.Enabled or style ~= state.Style or #waves == 0 then
                Clear(owner,style)
            else
                local overlay = UILens.GetOverlay(name)
                if overlay == nil then
                    ready = false
                else
                    local parts = {}
                    for _, wave in ipairs(waves) do
                        table.insert(parts,wave.pos1..":"..wave.pos2..":"..tostring(wave.color)..":"..tostring(wave.peakAlpha or ""))
                    end
                    local signature = table.concat(parts,"|")
                    if signatures[name] ~= signature then
                        Reset(overlay, style)
                        if style == "conveyor" then
                            local fading = {}
                            for _, wave in ipairs(waves) do
                                fading[#fading+1] = ConveyorWave(wave, wave.peakAlpha or 128)
                            end
                            overlay:CreateLinearWaves(fading)
                        else
                            for _, wave in ipairs(waves) do
                                overlay:CreatePathAlongSpline({wave.pos1,wave.pos2},wave.color)
                            end
                        end
                        signatures[name] = signature
                    end
                    overlay:SetVisible(true)
                end
            end
        end
    end
    state.Ready = ready
    if not ready then
        -- An older art build must leave the known native waves available.
        for _, owner in ipairs(OWNERS) do for style in pairs(STYLES) do Clear(owner,style) end end
    end
    for _, owner in ipairs(OWNERS) do
        local native = UILens.GetOverlay("CSC_Quarter"..owner.."_Flow")
        if native then native:SetVisible(not (state.Enabled and ready) and #(owners[owner] or {})>0) end
    end

end

local function OnUpdate(owner,waves)
    if shuttingDown or owner ~= "Lens" then return end
    owners[owner] = waves
    Rebuild()
end

local function OnEnable(enabled)
    if shuttingDown then return end
    state.Enabled = enabled == true
    Rebuild()
end

local function OnStyle(style)
    if shuttingDown then return end
    style = type(style) == "string" and style:lower() or nil
    if style ~= "conveyor" and style ~= "chevrons" and style ~= "trade" then
        print("CSC Flow Trial: choose style conveyor, chevrons or trade")
        return
    end
    state.Style = style
    state.Enabled = true
    Rebuild()
end

local function OnPlayerChanged()
    owners = {}
    Rebuild()
end

LuaEvents.CSC_QuarterFlowTrial_Update.Add(OnUpdate)
LuaEvents.CSC_QuarterFlowTrial_Enable.Add(OnEnable)
LuaEvents.CSC_QuarterFlowTrial_SetStyle.Add(OnStyle)
Events.LocalPlayerChanged.Add(OnPlayerChanged)
ContextPtr:SetShutdown(function()
    shuttingDown = true
    LuaEvents.CSC_QuarterFlowTrial_Update.Remove(OnUpdate)
    LuaEvents.CSC_QuarterFlowTrial_Enable.Remove(OnEnable)
    LuaEvents.CSC_QuarterFlowTrial_SetStyle.Remove(OnStyle)
    Events.LocalPlayerChanged.Remove(OnPlayerChanged)
    ExposedMembers.CSC_QuarterFlowTrial = nil
    -- Existing owner shutdown clears its records. The engine destroys overlays;
    -- do not call native controls or restart effects while contexts are exiting.
end)
