-- Lightweight trial in CSC's normal gameplay context. The two preceding Lua
-- modules read owned district sites and select one exact terrain cue per
-- Quarter. This adapter changes the stock city modifier's plot property.
-- Civ evaluates its private yield at the next ordinary district comparison.
local ordered = {}
for _, profile in pairs(profiles) do ordered[#ordered+1] = profile end
table.sort(ordered,function(a,b) return a.district.DistrictType < b.district.DistrictType end)
local reviewInterval = 12
local lastReview = 'CSC_AI_LOCAL_REVIEW_TURN'
local ownerKey = 'CSC_AI_LOCAL_CUE_OWNER'

local function singlePlayer()
    if GameConfiguration and type(GameConfiguration.IsAnyMultiplayer) == 'function' and type(GameConfiguration.IsHotseat) == 'function' then
        return GameConfiguration.IsAnyMultiplayer() == false and GameConfiguration.IsHotseat() == false
    end
    local ui = ExposedMembers and ExposedMembers.CSC_Adjacency
    return ui and type(ui.IsSinglePlayer) == 'function' and ui.IsSinglePlayer() == true
end

local function activeKey(profile)
    return 'CSC_AI_LOCAL_ACTIVE_' .. profile.district.DistrictType
end

local function update(city, center, player, profile, cue, turn)
    local district = profile.district.DistrictType
    local key = activeKey(profile)
    local previous = center:GetProperty(key)
    local rule = cue and ('CSC_AI_SITE_' .. district .. '__' .. cue.terrain .. '_' .. cue.cutoff)
    local bound = rule and ('CSC_AI_BOUND_' .. rule)
    if previous == rule and (not rule or city:GetProperty(bound) == 1) then return end
    if previous then center:SetProperty(previous,0) end
    center:SetProperty(key,nil)
    if rule then
        -- Attach once per city instance. Both the attachment marker and
        -- the center property survive a save/reload. Reusing a previous
        -- layout reopens the existing gate without stacking a second award.
        if city:GetProperty(bound) ~= 1 then
            city:AttachModifierByID(rule)
            city:SetProperty(bound,1)
        end
        center:SetProperty(ownerKey,player)
        center:SetProperty(rule,1)
        center:SetProperty(key,rule)
    end
    print('CSC_LOCAL_CUE_CHANGE',turn,player,city:GetID(),district,previous or '-',rule or '-',
        cue and cue.hits or 0,cue and cue.total or 0,cue and cue.customerRank or 0)
end

local function reviewPlayer(player, turn)
    local id = player:GetID()
    -- Record initial humans while the original seats are intact. Autoplay
    -- can subsequently report the observer seat as an AI. Unknown old
    -- saves keep the database guidance until seat identity is established.
    local seatKey = 'CSC_AI_OriginalHuman_' .. id
    local original = Game:GetProperty(seatKey)
    if original == nil and turn <= 1 then
        original = player:IsHuman() and 1 or 0
        Game:SetProperty(seatKey,original)
    end
    local eligible = original == 0 and not player:IsHuman()
    if player:GetProperty('CSC_AI_LOCAL_PASS_TURN') == turn then return end
    player:SetProperty('CSC_AI_LOCAL_PASS_TURN',turn)

    local chosen, chosenCenter, oldest
    for _, city in player:GetCities():Members() do
        local center = Map.GetPlot(city:GetX(),city:GetY())
        local previousOwner = center:GetProperty(ownerKey)
        if previousOwner ~= nil and (previousOwner ~= id or not eligible) then
            -- Plot properties remain after conquest. Withdraw the old plan
            -- before the new owner's normal decisions, including human seats.
            for _, profile in ipairs(ordered) do update(city,center,id,profile,nil,turn) end
            center:SetProperty(ownerKey,nil)
        end
        if eligible then
            local reviewed = city:GetProperty(lastReview) or -reviewInterval
            if turn-reviewed >= reviewInterval and
                    (not chosen or reviewed < oldest or (reviewed == oldest and center:GetIndex() < chosenCenter:GetIndex())) then
                chosen,chosenCenter,oldest = city,center,reviewed
            end
        end
    end
    if not chosen then return end
    -- At most one radius-three city scan per major AI per turn. Oldest
    -- review first prevents large empires starving their newer cities.
    local evaluated, matched = 0, 0
    for _, profile in ipairs(ordered) do
        local cue
        if not chosen:GetDistricts():HasDistrict(profile.district.Index) then
            local sites = ownedSites(chosen,id,profile)
            evaluated = evaluated + #sites
            cue = selectMaterialCue(sites,terrainKeys)
            if cue then matched = matched + 1 end
        end
        update(chosen,chosenCenter,id,profile,cue,turn)
    end
    chosen:SetProperty(lastReview,turn)
    print('CSC_LOCAL_CUE_REVIEW',turn,id,chosen:GetID(),evaluated,matched)
end

local disabled = false
local function advance()
    if disabled or not singlePlayer() then return end
    local turn = Game.GetCurrentGameTurn()
    local ok, message = pcall(function()
        for _, player in ipairs(PlayerManager.GetAliveMajors()) do reviewPlayer(player,turn) end
    end)
    if not ok then disabled = true; print('CSC_LOCAL_CUE_FAULT',turn,message) end
end
GameEvents.OnGameTurnStarted.Add(advance)
-- The normal game-load callback runs before the controller starts autoplay.
-- Capture the original seats here as well as at the first turn boundary.
advance()
print('CSC_LOCAL_CUE_INSTALLED',#ordered)
