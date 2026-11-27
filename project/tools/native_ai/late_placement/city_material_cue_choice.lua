-- Probe-only policy. Compare the owned legal Quarter sites of one city.
-- For each terrain actually carrying local Base, find the smallest neighbor
-- count that excludes every site without Base. The stock adjacency effect
-- pays one private yield per complete group of that many neighbors.
local function selectMaterialCue(sites, terrains)
    local best
    for _, terrain in ipairs(terrains) do
        local badSite, target, highestBad, highestTarget = nil, nil, -1, 0
        for _, site in ipairs(sites) do
            local count = site.count[terrain] or 0
            if not next(site.materialTerrain) and count > highestBad then
                badSite, highestBad = site, count
            end
            if site.materialTerrain[terrain] and count > highestTarget then
                target, highestTarget = site, count
            end
        end
        if badSite and target and highestTarget > highestBad then
            local cutoff = highestBad + 1
            local hits = 0
            for _, site in ipairs(sites) do
                if (site.count[terrain] or 0) >= cutoff then hits = hits + 1 end
            end
            -- Every hit touches real Base. Prefer the cue that gives Civ the
            -- most such options. Stable terrain and plot order resolve ties.
            if not best or hits > best.hits then
                best = {a=target, b=badSite, terrain=terrain, cutoff=cutoff, hits=hits, total=#sites}
            end
        end
    end
    return best
end
