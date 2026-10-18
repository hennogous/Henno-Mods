-- Hide CSC's private planning rows from UI enumeration only. Indexed lookup
-- remains intact; the native gameplay database and AI scoring are untouched.
-- This avoids copying Firaxis/RomanHoliday tooltip, report and Pedia files.
if UI == nil or CSC_AI_UIFilterInstalled then return end
-- Native GameInfo itself is read-only. A local-context facade shadows selected
-- enumerators while delegating every other lookup to that unchanged cache.
local nativeInfo = GameInfo
local overrides = {}
GameInfo = setmetatable({}, {__index=function(_, name)
    return overrides[name] or nativeInfo[name]
end})
local signal = 'YIELD_CSC_AI_PLACEMENT'
local function filter(name, keep)
    local original = nativeInfo[name]
    overrides[name] = setmetatable({}, {
        __index = function(_, key) return original[key] end,
        __call = function(_, ...)
            local nextRow, state, control = original(...)
            return function()
                local row = nextRow(state, control)
                control = row
                while row ~= nil and not keep(row) do
                    row = nextRow(state, control)
                    control = row
                end
                return row
            end
        end,
    })
end
filter('Yields', function(row) return row.YieldType ~= signal end)
filter('Adjacency_YieldChanges', function(row) return row.YieldType ~= signal end)
filter('District_Adjacencies', function(row)
    local adjacency = GameInfo.Adjacency_YieldChanges[row.YieldChangeId]
    return adjacency == nil or adjacency.YieldType ~= signal
end)
CSC_AI_UIFilterInstalled = true
