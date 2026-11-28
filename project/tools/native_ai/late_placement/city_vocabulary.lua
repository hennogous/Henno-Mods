-- Stock-only city guidance: map a supplied footprint to native adjacency
-- effects that distinguish it from competing plots. Lua chooses the flags.
-- Civ reads their private yield at its next district comparison.
pairPolicy.vocabulary=true
local function family(key)
    return key:match('^[^_]+')
end

local function patternFor(rows,keys,target,positive,floor,hits)
    local wanted=rows[target]
    local gain=6*hits-(floor and wanted.g.neighbors or 0)
    if gain<6 or gain>18 then return end
    local scores,negative={},{}
    local used,families,missingFamilies={},{},0
    for _,k in ipairs(positive) do
        used[k]=true
        local f=family(k)
        if k~='RIVER' and not families[f] then families[f]=true;missingFamilies=missingFamilies+1 end
    end
    for i,s in ipairs(rows) do
        local counts=s.g.clues
        -- An unseen hex could have both a feature and an improvement, but
        -- cannot have two different terrains. River access is known on the
        -- candidate itself; it never contributes an unknown neighbor.
        local total=s.g.unknown*missingFamilies
        for _,k in ipairs(positive) do total=total+(counts[k] or 0) end
        scores[i]=6*total-(floor and s.g.neighbors or 0)
    end
    -- Add deductions only when they remove a specific rival's excess.
    -- The number of active flags follows the layout. Stop once all weak
    -- plots are safe and supplied rivals are below the intended site's gain.
    while true do
        local bad,margin,rival=0,100,-1
        for i,s in ipairs(rows) do
            if i~=target then
                if not s.supplied then bad=math.max(bad,scores[i]) end
                local lead=scores[target]-scores[i]
                if lead<margin then margin,rival=lead,s.g.index end
            end
        end
        if bad==0 and margin>0 then
            return {gain=scores[target],margin=margin,negative=negative,rival=rival}
        end
        local choice,most=nil,0
        for _,k in ipairs(keys) do
            -- Preserve the promised target gain. A deduction on a known
            -- neighbor is safe under fog: unknown negatives only help.
            if not used[k] and not wanted.g.clues[k] then
                local benefit=0
                for i,s in ipairs(rows) do
                    local n=s.g.clues[k]
                    if n and i~=target then
                        local limit=s.supplied and scores[target]-1 or 0
                        benefit=benefit+math.min(6*n,math.max(0,scores[i]-limit))
                    end
                end
                if benefit>most then choice,most=k,benefit end
            end
        end
        if not choice then
            if bad==0 and margin==0 then return {gain=scores[target],margin=margin,negative=negative,rival=rival} end
            return
        end
        used[choice]=true
        negative[#negative+1]=choice
        for i,s in ipairs(rows) do scores[i]=scores[i]-6*(s.g.clues[choice] or 0) end
    end
end

local function findCue(sites,profile)
    local rows,targets,seen,keys={},{},{},{}
    local function row(g,supplied)
        rows[#rows+1]={g=g,supplied=supplied}
        for k in pairs(g.clues) do seen[k]=true end
    end
    for _,s in ipairs(sites) do
        row(s.geometry,s.baseCount>0)
        if s.baseCount>0 then
            targets[#targets+1]={index=#rows,value=rank(s,landscape[profile.district.Index] or {})}
        end
    end
    for _,s in ipairs(sites.frontierAll or {}) do row(s.geometry,s.supplied) end
    if #targets==0 then return {floor=true},0 end
    for k in pairs(seen) do keys[#keys+1]=k end
    table.sort(keys)
    table.sort(targets,function(a,b)
        if a.value~=b.value then return a.value>b.value end
        return a.index<b.index
    end)
    local best
    for _,t in ipairs(targets) do
        if best and t.value<best.rank then break end
        local g=rows[t.index].g
        local candidates,positive={},{}
        for _,k in ipairs(keys) do if g.clues[k] then candidates[#candidates+1]=k end end
        -- Enumerate smaller combinations first. Four positive contributions
        -- already yield +18 even with the six-hex floor. More positive terms
        -- exceed the bid band; the number of useful deductions remains open.
        local function enumerate(start,remaining,hits)
            if remaining>0 then
                for j=start,#candidates-remaining+1 do
                    local k=candidates[j]
                    local nextHits=hits+g.clues[k]
                    if nextHits+remaining-1<=4 then
                        positive[#positive+1]=k
                        enumerate(j+1,remaining-1,nextHits)
                        positive[#positive]=nil
                    end
                end
            else
                for _,floor in ipairs({false,true}) do
                    local p=patternFor(rows,keys,t.index,positive,floor,hits)
                    if p then
                        -- Prefer isolating the site, then reaching +12. Beyond
                        -- that use fewer flags and the smaller sufficient lift.
                        local n=#positive+#p.negative+(floor and 1 or 0)
                        local quality=(p.margin>0 and 10000 or 0)+100*math.min(12,p.gain)-4*n-p.gain
                        if not best or quality>best.quality then
                            local rules={}
                            for _,k in ipairs(positive) do rules[#rules+1]='P_'..k end
                            for _,k in ipairs(p.negative) do rules[#rules+1]='N_'..k end
                            best={floor=floor,rules=rules,target=g.index,gain=p.gain,margin=p.margin,rival=p.rival,
                                  rank=t.value,quality=quality}
                        end
                    end
                end
            end
        end
        for width=1,math.min(4,#candidates) do
            enumerate(1,width,0)
            if best and best.margin>0 and best.gain>=12 and #best.rules<=width then break end
        end
    end
    return best or {floor=false},#targets
end

function pairPolicy.choose(sites,city,player,profile,turn)
    local cue,good=findCue(sites,profile)
    local district=profile.district.DistrictType
    print('CSC_FLOOR_REVIEW',turn,player,city:GetID(),district,#sites,good,cue.floor,cue.target or -1,
          cue.rules and cue.rules[1] or '-')
    if sites.frontierWeak then
        print('CSC_FRONTIER_REVIEW',turn,player,city:GetID(),district,#sites.frontierWeak,0,cue.target or -1)
    end
    if cue.target then
        print('CSC_VOCAB_SITE',turn,player,city:GetID(),city:GetName(),district,cue.target,
              cue.gain,cue.margin,cue.floor,table.concat(cue.rules,','),cue.rival)
    end
    return cue
end

local allTerrains={}
for terrain in GameInfo.Terrains() do allTerrains[#allTerrains+1]=terrain.TerrainType end
table.sort(allTerrains)
local function effectiveRules(cue)
    if not cue then return {} end
    if not cue.floor then return cue.rules or {} end
    -- Native readback showed that retiring a signed terrain effect while an
    -- independent -1 effect on the same terrain was active changed the floor.
    -- Express their sum as ONE record per terrain. F=-1, U=+5, D=-7.
    local terrainSigns,result={},{}
    for _,rule in ipairs(cue.rules or {}) do
        local sign,terrain=rule:match('^([PN])_(TERRAIN_.+)$')
        if sign then terrainSigns[terrain]=sign=='P' and 'U_' or 'D_'
        else result[#result+1]=rule end
    end
    for _,terrain in ipairs(allTerrains) do
        result[#result+1]=(terrainSigns[terrain] or 'F_')..terrain
    end
    return result
end
local activeByPlot, catalogueByQuarter={},{}
local function activeRules(center,key)
    local plot=center:GetIndex()
    activeByPlot[plot]=activeByPlot[plot] or {}
    local slot=activeByPlot[plot]
    if slot[key] then return slot end
    slot[key]={}
    if not center:GetProperty(key..'_ACTIVE') then return slot end
    -- Plot properties reliably round-trip integers. Rebuild the narrow live
    -- list once after reload from the numeric flags the engine itself reads.
    -- The generated modifier catalogue is shared across cities of this type.
    if not catalogueByQuarter[key] then
        local prefix=key..'__'
        local catalogue={}
        for mod in GameInfo.Modifiers() do
            if mod.ModifierId:sub(1,#prefix)==prefix then
                catalogue[#catalogue+1]=mod.ModifierId:sub(#prefix+1)
            end
        end
        table.sort(catalogue)
        catalogueByQuarter[key]=catalogue
    end
    for _,rule in ipairs(catalogueByQuarter[key]) do
        if center:GetProperty(key..'__'..rule)==1 then table.insert(slot[key],rule) end
    end
    return slot
end
function pairPolicy.update(city,center,player,profile,cue,turn,ownerKey)
    local key='CSC_AI_VOC_'..profile.district.DistrictType
    -- The saved list lets capture, foundation, reload and fallback withdraw
    -- exactly the flags this city owns without walking the global catalogue.
    local nextRules=effectiveRules(cue)
    local slot=activeRules(center,key)
    local current=slot[key]
    -- The stock UI observer reads these two plot IDs and the review turn.
    -- Neither property participates in the AI decision.
    if cue and cue.target then
        center:SetProperty(key..'_TARGET',cue.target)
        center:SetProperty(key..'_RIVAL',cue.rival)
        center:SetProperty(key..'_REVIEW',turn)
    elseif #current>0 then
        center:SetProperty(key..'_TARGET',nil)
        center:SetProperty(key..'_RIVAL',nil)
        center:SetProperty(key..'_REVIEW',nil)
    end
    if #current==#nextRules and table.concat(current,',')==table.concat(nextRules,',') then return end
    local keep={}
    for _,rule in ipairs(nextRules) do keep[rule]=true end
    for _,rule in ipairs(current) do
        if not keep[rule] then center:SetProperty(key..'__'..rule,0) end
    end
    for _,rule in ipairs(nextRules) do
        local id=key..'__'..rule
        if city:GetProperty(id..'_BOUND')~=1 then
            city:AttachModifierByID(id)
            city:SetProperty(id..'_BOUND',1)
        end
        center:SetProperty(id,1)
        center:SetProperty(ownerKey,player)
    end
    slot[key]=nextRules
    center:SetProperty(key..'_ACTIVE',#nextRules>0 and 1 or nil)
end
