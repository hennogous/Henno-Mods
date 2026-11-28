-- Optional second pass for cities where one strong terrain cue is unsafe.
-- Civ sums two independent +3 private yields and the existing -1 per neighbor
-- floor. Reject any pattern that brings even one weak competitor back to zero.
-- The caller already gathered legal plots for this city and missing Quarter.
function pairPolicy.splitRelief(sites, profile)
    local keys, rivals, supplied = {}, {}, {}
    local seen = {}
    for _,site in ipairs(sites) do
        local n = 0
        for key,count in pairs(site.count) do
            seen[key] = true
            n = n + count
        end
        local s = {count=site.count, neighbors=n, unknown=0, plot=site.plot:GetIndex(),
                   rank=rank(site,landscape[profile.district.Index] or {})}
        local group = s.rank>0 and supplied or rivals
        group[#group+1] = s
    end
    for _,s in ipairs(sites.frontierWeak or {}) do rivals[#rivals+1]=s end
    for _,key in ipairs(terrainKeys) do
        if seen[key] then keys[#keys+1]=key end
    end
    local function delta(s,a,b)
        -- Each unknown hex can match at most one of the two terrain types.
        return 3*((s.count[a] or 0)+(s.count[b] or 0)+s.unknown)-s.neighbors
    end
    local best
    for i,a in ipairs(keys) do
        for j=i+1,#keys do
            local b = keys[j]
            local safe = true
            for _,rival in ipairs(rivals) do
                if delta(rival,a,b)>=0 then safe=false; break end
            end
            if safe then
                for _,site in ipairs(supplied) do
                    local change=delta(site,a,b)
                    if change>=0 and (not best or site.rank>best.rank or
                            (site.rank==best.rank and change>best.delta)) then
                        local prefix='CSC_AI_PAIR_'..profile.district.DistrictType..'__P_'
                        best={floor=true,a=prefix..a,b=prefix..b,target=site.plot,rank=site.rank,delta=change}
                    end
                end
            end
        end
    end
    if best then return best end

    -- When both weak and supplied sites share the rewarded terrain, try a
    -- second terrain as a deduction. Starting from ordinary values avoids a
    -- blanket six-point penalty. A legal weak footprint may tie its ordinary
    -- score, but it can never gain. Require a strictly positive supplied bid.
    -- Both signs use three private yield units per matching neighboring hex.
    for _,a in ipairs(keys) do
        for _,b in ipairs(keys) do
            if a~=b then
                local safe=true
                for _,s in ipairs(rivals) do
                    if (s.count[a] or 0)+s.unknown>(s.count[b] or 0) then safe=false; break end
                end
                if safe then
                    for _,s in ipairs(supplied) do
                        local change=3*((s.count[a] or 0)-(s.count[b] or 0))
                        if change>0 and (not best or s.rank>best.rank or
                                (s.rank==best.rank and change>best.delta)) then
                            local prefix='CSC_AI_PAIR_'..profile.district.DistrictType
                            best={floor=false,a=prefix..'__P_'..a,b=prefix..'__N_'..b,
                                  target=s.plot,rank=s.rank,delta=change}
                        end
                    end
                end
            end
        end
    end
    if best or not pairPolicy.thirdRelief then return best end
    -- A third cue can distinguish sites that share both of the simpler
    -- patterns. Compare only terrain types present on legal owned footprints.
    -- Test both signs of each contrast together, sharing the rival scan.
    -- Cold data stays in this review; no extra map reads or SQL rows are needed.
    local prefix='CSC_AI_PAIR_'..profile.district.DistrictType
    local function consider(a,b,c)
        local positive,negative=true,true
        for _,s in ipairs(rivals) do
            local v=(s.count[a] or 0)-(s.count[b] or 0)-(s.count[c] or 0)
            if v+s.unknown>0 then positive=false end
            if -v+s.unknown>0 then negative=false end
            if not positive and not negative then return end
        end
        for _,s in ipairs(supplied) do
            local v=(s.count[a] or 0)-(s.count[b] or 0)-(s.count[c] or 0)
            if (positive and v>0) or (negative and v<0) then
                local change=3*math.abs(v)
                if not best or s.rank>best.rank or (s.rank==best.rank and change>best.delta) then
                    local first=v>0 and '__P_' or '__N_'
                    local other=v>0 and '__N_' or '__P_'
                    best={floor=false,a=prefix..first..a,b=prefix..other..b,c=prefix..other..c,
                          target=s.plot,rank=s.rank,delta=change}
                end
            end
        end
    end
    for i=1,#keys-2 do
        for j=i+1,#keys-1 do
            for k=j+1,#keys do
                consider(keys[i],keys[j],keys[k])
                consider(keys[j],keys[i],keys[k])
                consider(keys[k],keys[i],keys[j])
            end
        end
    end
    return best
end
