-- Compare the owned legal Quarter sites of one city.
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
            local hits, bestLayout = 0, 0
            for _, site in ipairs(sites) do
                if (site.count[terrain] or 0) >= cutoff then
                    hits = hits + 1
                    -- At the same customer readiness, prefer a site that can
                    -- supply later stages too. Evaluate both on the same site.
                    local layout = 2 * (site.customerRank or 0) + (site.hasSpecialty and 1 or 0)
                    bestLayout = math.max(bestLayout,layout)
                end
            end
            -- Every hit touches real Base. Prefer the cue that gives Civ the
            -- best customer opportunity, followed by the most Base options.
            -- Stable terrain and plot order resolve remaining ties.
            if not best or bestLayout > best.layout or (bestLayout == best.layout and hits > best.hits) then
                best = {a=target, b=badSite, terrain=terrain, cutoff=cutoff, hits=hits, total=#sites,
                    layout=bestLayout, customerRank=math.floor(bestLayout/2)}
            end
        end
    end
    return best
end
