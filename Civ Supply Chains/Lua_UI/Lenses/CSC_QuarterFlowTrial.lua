-- Native fading conveyor waves for the existing working supply-chain links.
-- PressureOverlay supplies the shipped chevrons' quartic opacity envelope.
-- The retained chevron/trade comparisons use PathOverlay. Both are native
-- map overlays, without zero-height UI Lines or per-frame Lua animation.
-- Width/repeat/scroll/alpha are authored by build_chevron_art.py; the native
-- renderer animates them. No per-frame Lua timer or gameplay writes are needed.
local STYLES = {conveyor="ConveyorWaves", chevrons="Chevrons", trade="Trade"}
local OWNERS = {"Lens", "Placement"}
local owners, signatures, rebuildCounts = {}, {}, {}
-- The default now uses CSC's thick chevron texture. Keep the earlier native-art
-- styles available for comparison, with PressureOverlay as the old-art fallback.
local state = {Enabled=true, Ready=false, Style="conveyor"}
ExposedMembers.CSC_QuarterFlowTrial = state
local shuttingDown = false
local function Name(owner, style)
    return "CSC_Quarter" .. owner .. "_Flow" .. STYLES[style]
end

local function IsWave(style) return style == "conveyor" end

local function Reset(overlay, style)
    if IsWave(style) then overlay:ResetAllWaves() else overlay:ClearAllPaths() end
end

local function ConveyorWave(wave)
    -- The native wave shader multiplies the texture by this RGBA directly;
    -- BorderOverlay's Color_Alpha material field does not control its opacity.
    -- White conveyor trial: keep the native fade and 40% peak opacity, while
    -- leaving semantic yield colours on the original/comparison flow records.
    return {pos1=wave.pos1, pos2=wave.pos2, type=wave.type,
        speed=3, color=0x66ffffff}
end

local function Clear(owner, style)
    local name = Name(owner,style)
    local overlay = UILens.GetOverlay(name)
    if overlay and signatures[name] then Reset(overlay, style) end
    if overlay then overlay:SetVisible(false) end
    signatures[name] = nil
end

local function Rebuild()
    local count, missing = 0, {}
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
                    table.insert(missing,name)
                else
                    local parts = {}
                    for _, wave in ipairs(waves) do
                        table.insert(parts,wave.pos1..":"..wave.pos2..":"..tostring(wave.color))
                    end
                    local signature = table.concat(parts,"|")
                    if signatures[name] ~= signature then
                        rebuildCounts[name] = (rebuildCounts[name] or 0) + 1
                        print("CSC Flow Trial: rebuild layer="..name.." count="..rebuildCounts[name]
                            .." links="..#waves.." time="..string.format("%.3f",os.clock()))
                        Reset(overlay, style)
                        if IsWave(style) then
                            local fading = {}
                            for _, wave in ipairs(waves) do fading[#fading+1] = ConveyorWave(wave) end
                            overlay:CreateLinearWaves(fading)
                        else
                            for _, wave in ipairs(waves) do
                                overlay:CreatePathAlongSpline({wave.pos1,wave.pos2},wave.color)
                            end
                        end
                        signatures[name] = signature
                    end
                    overlay:SetVisible(true)
                    count = count + #waves
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
    print("CSC Flow Trial: v10 enabled="..tostring(state.Enabled).." style="..state.Style
        .." ready="..tostring(ready).." links="..count.." missing="..table.concat(missing,",")
        .." width=18 quadLength="..(state.Style=="conveyor" and "48 stride=8 glyphOffset=16" or "32")
        .." scroll="..(state.Style=="conveyor" and "0.10" or "0.13")
        .." alpha="..(state.Style=="conveyor" and "102" or "224")
        .." fade="..(state.Style=="conveyor" and "native-quartic" or "none")
        .." tint="..(state.Style=="conveyor" and "white" or "yield")
        .." shape="..(state.Style=="conveyor" and "thick-chevron nativeSpan=32" or "comparison"))
end

local function OnUpdate(owner,waves)
    if shuttingDown or (owner~="Lens" and owner~="Placement") then return end
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
    if type(style) ~= "string" or STYLES[style:lower()] == nil then
        print("CSC Flow Trial: choose style conveyor, chevrons or trade")
        return
    end
    state.Style = style:lower()
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
print("CSC Flow Trial: loaded v10 (white shadowed chevrons; 40% peak; native 32-unit band)")
