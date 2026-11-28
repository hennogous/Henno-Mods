-- Lightweight Workshop trial. A negative native adjacency is enabled only
-- when a city has no visible or still-unexplored layout that could supply
-- the missing Quarter. Civ remains responsible for district and build choice.
local profiles, byTag = {}, {}
for row in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
    local tag = 'CLASS_CSC_' .. row.QuarterKey .. '_BASE'
    local district = GameInfo.Districts['DISTRICT_CSC_' .. row.QuarterKey .. '_QUARTER']
    if district and row.SourceTag == tag and row.SourceFilter == ''
            and row.AdjacencyType == 'FROM_RINGS_TYPETAG_RESOURCE' and not byTag[tag] then
        local profile = {district=district, gate='CSC_AI_NO_BASE_' .. district.DistrictType, base={}}
        byTag[tag] = profile
        profiles[#profiles+1] = profile
    end
end
for row in GameInfo.TypeTags() do
    local profile, resource = byTag[row.Tag], GameInfo.Resources[row.Type]
    if profile and resource then profile.base[resource.Index] = resource end
end
table.sort(profiles,function(a,b) return a.district.Index < b.district.Index end)

local function singlePlayer()
    if GameConfiguration and type(GameConfiguration.IsAnyMultiplayer) == 'function' and type(GameConfiguration.IsHotseat) == 'function' then
        return GameConfiguration.IsAnyMultiplayer()==false and GameConfiguration.IsHotseat()==false
    end
    local ui = ExposedMembers and ExposedMembers.CSC_Adjacency
    return ui and type(ui.IsSinglePlayer) == 'function' and ui.IsSinglePlayer() == true
end

local function revealedMaterial(player, resource)
    local tech = resource.PrereqTech and GameInfo.Technologies[resource.PrereqTech]
    local civic = resource.PrereqCivic and GameInfo.Civics[resource.PrereqCivic]
    return (not tech or player:GetTechs():HasTech(tech.Index))
       and (not civic or player:GetCulture():HasCivic(civic.Index))
end

local function futureSite(plot,player)
    -- A protected superset of sites: slots, unlocks, gold and removable
    -- features may change. Even a swappable tile in a sibling city can keep
    -- the plan alive. Persistent occupation, foreign land and impassable
    -- terrain cannot form the Quarter footprint in the current empire.
    local feature = GameInfo.Features[plot:GetFeatureType()]
    local resource = GameInfo.Resources[plot:GetResourceType()]
    return (plot:GetOwner() < 0 or plot:GetOwner() == player:GetID())
       and plot:GetDistrictType() < 0 and plot:GetWonderType() < 0
       and not plot:IsWater() and not plot:IsImpassable()
       and not (feature and (feature.NaturalWonder==true or feature.NaturalWonder==1))
       and not (resource and resource.ResourceClassType~='RESOURCECLASS_BONUS' and revealedMaterial(player,resource))
end

local function opportunities(city,player)
    local id,x,y = player:GetID(),city:GetX(),city:GetY()
    local vision = PlayersVisibility[id]
    local materials, unknown, neighbors = {},false,{}
    for dx=-3,3 do
        for dy=-3,3 do
            local site = Map.GetPlotXYWithRangeCheck(x,y,dx,dy,3)
            if site and (dx~=0 or dy~=0) then
                local sx,sy = site:GetX(),site:GetY()
                if not vision:IsRevealed(sx,sy) then
                    unknown = true
                elseif futureSite(site,player) then
                    for dir=0,5 do
                        local p = Map.GetAdjacentPlot(sx,sy,dir)
                        if p and not neighbors[p:GetIndex()] then
                            neighbors[p:GetIndex()] = true
                            if not vision:IsRevealed(p:GetX(),p:GetY()) then
                                unknown = true
                            elseif (p:GetOwner()<0 or p:GetOwner()==id) and p:GetDistrictType()<0 and p:GetWonderType()<0 then
                                materials[p:GetResourceType()] = true
                            end
                        end
                    end
                end
            end
        end
    end
    return materials, unknown
end

local function state(profile,materials,unknown,player)
    if not next(profile.base) then return 'unknown' end
    for index,resource in pairs(profile.base) do
        if not revealedMaterial(player,resource) then
            unknown = true
        elseif materials[index] then
            return 'base'
        end
    end
    return unknown and 'unknown' or 'absent'
end

local function update(city,center,profile,penalty)
    local key = profile.gate
    if penalty and city:GetProperty(key..'_BOUND')~=1 then
        -- The attachment and property persist in saves. One rule per terrain
        -- makes the penalty independent of which terrains surround the site.
        for terrain in GameInfo.Terrains() do city:AttachModifierByID(key..'__'..terrain.TerrainType) end
        city:SetProperty(key..'_BOUND',1)
    end
    if (center:GetProperty(key)==1)~=penalty then
        center:SetProperty(key,penalty and 1 or 0)
        return true
    end
end

local function review(player,turn)
    local id = player:GetID()
    local originalKey = 'CSC_AI_OriginalHuman_' .. id
    local human = Game:GetProperty(originalKey)
    if human==nil and turn<=1 then
        human = player:IsHuman() and 1 or 0
        Game:SetProperty(originalKey,human)
    end
    local eligible = human==0 and not player:IsHuman()
    local chosen,center,oldest
    for _,city in player:GetCities():Members() do
        local p = Map.GetPlot(city:GetX(),city:GetY())
        local owner = p:GetProperty('CSC_AI_NO_BASE_OWNER')
        if owner~=nil and (owner~=id or not eligible) then
            for _,profile in ipairs(profiles) do update(city,p,profile,false) end
            p:SetProperty('CSC_AI_NO_BASE_OWNER',nil)
        end
        local last = city:GetProperty('CSC_AI_NO_BASE_REVIEW') or -12
        if eligible and turn-last>=12 and (not oldest or last<oldest or (last==oldest and p:GetIndex()<center:GetIndex())) then
            chosen,center,oldest = city,p,last
        end
    end
    if not chosen then return end
    local materials,unknown
    for _,profile in ipairs(profiles) do
        local reason = 'built'
        if not chosen:GetDistricts():HasDistrict(profile.district.Index) then
            if not materials then materials,unknown=opportunities(chosen,player) end
            reason=state(profile,materials,unknown,player)
        end
        -- An observation-only run records the same classification at the
        -- same cadence with every native property gate left off.
        local changed=update(chosen,center,profile,reason=='absent' and CSC_NO_BASE_OBSERVE_ONLY~=true)
        chosen:SetProperty(profile.gate..'_REASON',reason)
        -- Trial evidence records an assessed opportunity even when no write
        -- was needed, so later foundations can be joined to the last review.
        print('CSC_NO_BASE_REVIEW',turn,id,chosen:GetID(),profile.district.Index,reason,changed and 1 or 0,chosen:GetName())
    end
    center:SetProperty('CSC_AI_NO_BASE_OWNER',id)
    chosen:SetProperty('CSC_AI_NO_BASE_REVIEW',turn)
end

local lastTurn
local function advance()
    if not singlePlayer() then return end
    local turn=Game.GetCurrentGameTurn()
    if lastTurn==turn then return end
    lastTurn=turn
    for _,player in ipairs(PlayerManager.GetAliveMajors()) do review(player,turn) end
end
GameEvents.OnGameTurnStarted.Add(advance)
if Events and Events.LoadScreenClose then Events.LoadScreenClose.Add(advance) end
advance()
print('CSC_NO_BASE_INSTALLED',#profiles)
