-- City-specific no-CE experiment. Legal owned footprints and visible Base
-- come from the shared geometry reader. Pick the smallest signed terrain
-- pattern that puts the target layout ahead of every material-free site.
-- Stock district and production comparisons still decide whether to build.
pairPolicy = {}
local landscape = {}
for rule in GameInfo.CSC_AdjacencyRules() do
    local district = GameInfo.Districts[rule.DistrictType]
    if district and rule.YieldType == 'YIELD_PRODUCTION' then
        local spec = landscape[district.Index] or {}
        landscape[district.Index] = spec
        if rule.AdjacencyType == 'FROM_RIVER_CROSSING' then spec.river = rule.YieldChange end
        if rule.CustomAdjacentObject == 'IsHills' and rule.Rings == 0 then spec.hills = rule.YieldChange end
    end
end

local function rank(site, spec)
    if not next(site.materialTerrain) then return 0 end
    -- Prefer existing customers and workable later stages. Among comparable
    -- sites, compare the better river or hill payout because Mills exclude
    -- each other. These scores only order valid supplier layouts locally.
    local terrainValue = math.max(math.floor((spec.river or 0)*site.plot:GetRiverCrossingCount()),
                                 site.plot:IsHills() and spec.hills or 0)
    return 1 + 32*site.customerRank + 8*(site.hasSpecialty and 1 or 0)
           + 4*math.min(site.baseCount-1,1) + math.min(3,terrainValue)
end

function pairPolicy.choose(sites, city, player, profile, turn)
    local ranks, keys, seen = {}, {}, {}
    local highest, bad = 0, 0
    for i,site in ipairs(sites) do
        ranks[i] = rank(site,landscape[profile.district.Index] or {})
        highest = math.max(highest,ranks[i])
        if ranks[i]==0 then bad=bad+1 end
        for terrain in pairs(site.count) do
            if not seen[terrain] then seen[terrain]=true; keys[#keys+1]=terrain end
        end
    end
    if highest==0 or bad==0 then
        print('CSC_PAIR_REVIEW',turn,player,city:GetID(),profile.district.DistrictType,#sites,bad,-1,-1,0)
        return
    end
    table.sort(keys)
    local terms={}
    for _,terrain in ipairs(keys) do
        local values,low,high={},6,0
        for i,site in ipairs(sites) do
            local count=site.count[terrain] or 0
            values[i]=count
            low,high=math.min(low,count),math.max(high,count)
        end
        -- Constant columns change the district bid everywhere in the city
        -- without helping the AI to distinguish sites. Leave them dormant.
        if low<high then
            for _,sign in ipairs({1,-1}) do
                terms[#terms+1]={terrain=terrain,sign=sign,values=values,
                    rule='CSC_AI_PAIR_'..profile.district.DistrictType..'__'..
                         (sign==1 and 'P_' or 'N_')..terrain}
            end
        end
    end
    local best
    local function consider(a,b)
        local goodScore,badScore,otherScore=-100,-100,-100
        local target,rival
        for i,site in ipairs(sites) do
            local v=a.sign*a.values[i]
            if b then v=v+b.sign*b.values[i] end
            if ranks[i]==0 and v>badScore then badScore,rival=v,site end
            if ranks[i]~=highest then otherScore=math.max(otherScore,v)
            elseif v>goodScore then goodScore,target=v,site end
        end
        local margin=goodScore-badScore
        if goodScore<otherScore or margin<=0 then return end
        -- Prefer a larger separation, then the lower boost to unsuitable
        -- sites. Stable terrain and plot order settle exact ties.
        if not best or margin>best.margin or (margin==best.margin and badScore<best.badScore) then
            best={a=a.rule,b=b and b.rule,margin=margin,badScore=badScore,goodScore=goodScore,
                  target=target.plot:GetIndex(),rival=rival.plot:GetIndex()}
        end
    end
    for _,a in ipairs(terms) do consider(a) end
    if not best then
        for i,a in ipairs(terms) do
            for j=i+1,#terms do
                if terms[j].terrain~=a.terrain then consider(a,terms[j]) end
            end
        end
    end
    print('CSC_PAIR_REVIEW',turn,player,city:GetID(),profile.district.DistrictType,#sites,bad,
          best and best.target or -1,best and best.rival or -1,best and best.margin or 0)
    return best
end

function pairPolicy.update(city,center,player,profile,cue,turn,ownerKey)
    local key='CSC_AI_PAIR_ACTIVE_'..profile.district.DistrictType
    local wanted={cue and cue.a,cue and cue.b}
    local old={center:GetProperty(key..1),center:GetProperty(key..2)}
    if old[1]==wanted[1] and old[2]==wanted[2] then return end
    for slot=1,2 do
        local id=old[slot]
        if id and id~=wanted[1] and id~=wanted[2] then center:SetProperty(id,0) end
    end
    for slot=1,2 do
        local id=wanted[slot]
        if id then
            if city:GetProperty(id..'_BOUND')~=1 then
                city:AttachModifierByID(id)
                city:SetProperty(id..'_BOUND',1)
            end
            center:SetProperty(id,1)
            center:SetProperty(ownerKey,player)
        end
        center:SetProperty(key..slot,id)
    end
    print('CSC_PAIR_SWITCH',turn,player,city:GetID(),profile.district.DistrictType,
          old[1] or '-',old[2] or '-',wanted[1] or '-',wanted[2] or '-')
end
