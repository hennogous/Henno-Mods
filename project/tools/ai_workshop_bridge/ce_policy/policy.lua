-- Literal Lua port of adjacency_policy/policy.py v2. The native incentive is a
-- research priority, not an economic conversion. This file makes no game calls.
CSC_AI_AdjacencyPolicy = {}
local P = CSC_AI_AdjacencyPolicy
P.Profile = 'csc-adjacency-policy-v2'
P.Threshold, P.DeltaQ8 = 4, 1048576
P.PenaltyPerPointQ8, P.MaxPenaltyQ8, P.Capacity = 65536, 262144, 4096

local function finite(x)
    local t = type(x)
    return (t == 'number' or t == 'integer') and x == x and x > -math.huge and x < math.huge
end
local function key(r) return r.player..':'..r.city..':'..r.district..':'..r.plot end
local function cityBefore(a,b)
    return a.player < b.player or a.player == b.player and a.city < b.city
end
local function pairBefore(a,b)
    if a.player ~= b.player then return a.player < b.player end
    if a.city ~= b.city then return a.city < b.city end
    if a.district ~= b.district then return a.district < b.district end
    return a.plot < b.plot
end
local function better(a,b)
    if a.total ~= b.total then return a.total > b.total end
    if a.quarter ~= b.quarter then return a.quarter < b.quarter end
    return a.plot < b.plot
end
function P.Penalty(total)
    return total < P.Threshold and -math.min(P.MaxPenaltyQ8,math.ceil((P.Threshold-total)*P.PenaltyPerPointQ8)) or 0
end
function P.Shortlist(snapshot)
    assert(snapshot.turn <= 100,'Authorized endpoint is turn100')
    local allowed,seen,best,qualified,weak = {},{},{},{},{}
    for _,pid in ipairs(snapshot.originalAI) do allowed[pid] = true end
    for _,pid in ipairs(snapshot.currentHumans) do assert(not allowed[pid],'Human in policy scope') end
    for _,r in ipairs(snapshot.candidates) do
        local k = key(r)
        assert(not seen[k],'Duplicate candidate'); seen[k] = true
        assert(allowed[r.player] and r.legal == true,'Candidate outside scope')
        assert(finite(r.production) and finite(r.gold) and finite(r.total)
            and math.abs(r.total-r.production-r.gold) <= 1e-7,'Invalid adjacency total')
        if r.total < P.Threshold then weak[#weak+1] = r
        elseif not r.materialOnSite then
            qualified[#qualified+1] = r
            local c = r.player..':'..r.city
            if not best[c] or better(r,best[c]) then best[c] = r end
        end
    end
    local selected,entries,sortedWeak = {},{},{}
    for _,r in pairs(best) do selected[#selected+1] = r end
    table.sort(selected,cityBefore)
    for _,r in ipairs(selected) do
        entries[#entries+1] = {player=r.player,city=r.city,district=r.district,plot=r.plot,delta=P.DeltaQ8}
    end
    for _,r in ipairs(weak) do sortedWeak[#sortedWeak+1] = r end
    table.sort(sortedWeak,pairBefore)
    for _,r in ipairs(sortedWeak) do
        entries[#entries+1] = {player=r.player,city=r.city,district=r.district,plot=r.plot,delta=P.Penalty(r.total)}
    end
    assert(#entries <= P.Capacity,'Native policy table capacity exceeded')
    return {threshold=P.Threshold,qualified=qualified,selected=selected,penalized=weak,entries=entries,
        penalty_per_missing_point_Q8=P.PenaltyPerPointQ8,maximum_penalty_Q8=P.MaxPenaltyQ8,
        incentive_meaning='Signed district proposal priorities; not a yield or profit estimate; weak sites remain selectable'}
end
