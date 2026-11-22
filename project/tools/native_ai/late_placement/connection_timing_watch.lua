-- DIAGNOSTIC ONLY. Measure parts of the running planner for one replay seat.
-- Delegate to every original function once. The only new native call is the
-- wall clock. Keep timing observations separate from offers and score receipts.
local player = assert(CSC_CONNECTION_TIMING_PLAYER)
local adapters = assert(CSC_AI_EconomyAdapters)
local clock = assert(CE_AIMonotonicSeconds)
local unpack = unpack or table.unpack
local function pack(...) return {n=select('#', ...), ...} end
local function micros(seconds) return math.floor(seconds * 1000000 + 0.5) end

local function measure(name, timeQuotes)
    local original = assert(adapters[name])
    adapters[name] = function(snapshot, ...)
        if snapshot.id ~= player then return original(snapshot, ...) end
        local quote = snapshot.CustomerNetValue
        local calls, quoteSeconds, longest = 0, 0, 0
        if timeQuotes and quote then
            snapshot.CustomerNetValue = function(...)
                local start = clock()
                local result = quote(...)
                local elapsed = clock() - start
                calls = calls + 1
                quoteSeconds = quoteSeconds + elapsed
                longest = math.max(longest, elapsed)
                return result
            end
        end
        local start = clock()
        local result = pack(pcall(original, snapshot, ...))
        local elapsed = clock() - start
        if timeQuotes and quote then snapshot.CustomerNetValue = quote end
        if not result[1] then error(result[2], 0) end
        print(string.format('CSC_CONNECTION_TIMING turn=%d player=%d phase=%s micros=%d quoteCalls=%d quoteMicros=%d quoteMaxMicros=%d',
            Game.GetCurrentGameTurn(), player, name, micros(elapsed), calls, micros(quoteSeconds), micros(longest)))
        return unpack(result, 2, result.n)
    end
end

-- Lower phases are included in QuarterBids elapsed time. Quote timing is
-- inclusive of the existing memo lookup so repeated cached reads stay visible.
measure('QuarterBids', false)
measure('CustomerEconomicOffers', false)
measure('AnchoredConnectionPlans', false)
measure('ApplyConnectionCosts', true)
print('CSC_CONNECTION_TIMING_READY=' .. player)
