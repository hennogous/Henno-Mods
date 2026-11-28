-- Stock-only trial. Each missing Quarter costs one private placement unit
-- per neighboring terrain hex. An owned Base can earn that back when a
-- terrain cue distinguishes its site from all currently legal weak sites.
-- Firaxis consumes these private yields in its ordinary district comparison.
local signedUpdate = pairPolicy.update
function pairPolicy.choose(sites, city, player, profile, turn)
    local cue = {floor=true}
    local good = 0
    for _, site in ipairs(sites) do
        if site.baseCount > 0 then good = good + 1 end
    end
    local frontier=sites.frontierWeak or {}
    local vetoes=0
    if reliefWeight > 0 and good > 0 then
        if good == #sites and #frontier==0 then
            cue.floor = false
        else
            local bestRank, bestDelta = -1, -1
            for _, key in ipairs(terrainKeys) do
                local safe, target, targetRank, delta = true, nil, -1, -1
                for _, site in ipairs(sites) do
                    local neighbors = 0
                    for _, n in pairs(site.count) do neighbors = neighbors + n end
                    local change = reliefWeight * (site.count[key] or 0) - neighbors
                    if site.baseCount == 0 and change >= 0 then safe = false; break end
                    local value = rank(site, landscape[profile.district.Index] or {})
                    if value > 0 and change >= 0 and
                            (value > targetRank or (value == targetRank and change > delta)) then
                        target, targetRank, delta = site.plot:GetIndex(), value, change
                    end
                end
                if safe and target then
                    for _, rival in ipairs(frontier) do
                        -- A hidden neighbor could also match the rewarded
                        -- terrain. Use its worst possible contribution without
                        -- reading through fog. The floor counts actual hexes.
                        local matches=(rival.count[key] or 0)+rival.unknown
                        if reliefWeight*matches>=rival.neighbors then
                            safe=false
                            vetoes=vetoes+1
                            break
                        end
                    end
                end
                -- Stable terrain/plot order breaks exact ties. Limit the
                -- award to one terrain signal even when several distinguish it.
                if safe and target and (targetRank > bestRank or
                        (targetRank == bestRank and delta > bestDelta)) then
                    bestRank, bestDelta = targetRank, delta
                    cue.a = 'CSC_AI_PAIR_'..profile.district.DistrictType..'__R_'..key
                    cue.target = target
                end
            end
        end
    end
    print('CSC_FLOOR_REVIEW',turn,player,city:GetID(),profile.district.DistrictType,
          #sites,good,cue.floor,cue.target or -1,cue.a or '-')
    if sites.frontierWeak then
        print('CSC_FRONTIER_REVIEW',turn,player,city:GetID(),profile.district.DistrictType,#frontier,vetoes,cue.target or -1)
    end
    return cue
end

function pairPolicy.update(city,center,player,profile,cue,turn,ownerKey)
    local gate = 'CSC_AI_NO_BASE_'..profile.district.DistrictType
    local wanted = cue and cue.floor or false
    if wanted and city:GetProperty(gate..'_BOUND') ~= 1 then
        for row in GameInfo.Terrains() do city:AttachModifierByID(gate..'__'..row.TerrainType) end
        city:SetProperty(gate..'_BOUND',1)
    end
    if wanted then center:SetProperty(ownerKey,player) end
    if (center:GetProperty(gate)==1) ~= wanted then center:SetProperty(gate,wanted and 1 or 0) end
    signedUpdate(city,center,player,profile,cue,turn,ownerKey)
end
