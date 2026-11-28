-- Diagnostic replay only. Retain the legal alternatives seen at a real review
-- so alternative terrain weights can be compared without rerunning the AI.
-- Owned sites carry their gameplay-derived rank. Unrevealed frontier neighbors
-- are recorded as unknown so an offline test can bound their contribution.
local chooseWithFloor = pairPolicy.choose
function pairPolicy.choose(sites, city, player, profile, turn)
    local cue = chooseWithFloor(sites, city, player, profile, turn)
    local rows = {}
    local function record(plot, value, unknown, counts)
        local fields = {}
        for terrain, n in pairs(counts) do
            fields[#fields+1] = terrain:gsub('^TERRAIN_', '') .. '=' .. n
        end
        table.sort(fields)
        rows[#rows+1] = table.concat({plot, value, unknown, table.concat(fields, ',')}, ':')
    end
    for _, site in ipairs(sites) do
        record(site.plot:GetIndex(), rank(site, landscape[profile.district.Index] or {}), 0, site.count)
    end
    for _, rival in ipairs(sites.frontierWeak or {}) do
        record(-1, 0, rival.unknown, rival.count)
    end
    print('CSC_LAYOUT_GEOMETRY',turn,player,city:GetID(),profile.district.DistrictType,
          cue.target or -1,table.concat(rows,'|'))
    return cue
end
