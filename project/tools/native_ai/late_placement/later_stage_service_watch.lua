-- Diagnostic-only UI observer. Count a physical Service link only when the
-- live wrapper has its specific recipient and the corresponding native leaf
-- is active for that recipient. A hidden grant or a city property can persist
-- during a lapse and is insufficient here. Neither this watcher nor its
-- single-snapshot mode changes a modifier, research topic or production order.
include('CSC_AI_EconomyFacts')
local catalogue = CSC_AI_EconomyFacts.ServiceCatalogue()
local effects = assert(GameEffects, 'Service observer requires UI GameEffects')
local players = CSC_MILESTONE_SERVICE_PLAYERS
local roots, leaves = {}, {}
local count = 0
for _, records in pairs(catalogue.byProducer) do
    for _, record in ipairs(records) do
        if record.service then
            roots[record.root] = record
            leaves[record.leaf] = true
            count = count + 1
        end
    end
end
assert(count > 0, 'No Service benefit attachments in the gameplay catalogue')
local topics, unlocked = {tech = {}, civic = {}}, {}
if players then
    local function producerTopic(kind, key)
        if key then topics[kind][key] = true end
    end
    for _, rule in pairs(roots) do
        for key in pairs(rule.owner.techs) do producerTopic('tech', key) end
        for key in pairs(rule.owner.civics) do producerTopic('civic', key) end
    end
    for flow in GameInfo.CSC_QuarterFlowBuildings() do
        local building = GameInfo.Buildings[flow.BuildingType]
        if building and flow.Stage >= 3 then
            producerTopic('tech', building.PrereqTech)
            producerTopic('civic', building.PrereqCivic)
        end
    end
end

local function readDistrict(object)
    local fields = {}
    for name, value in (effects.GetObjectString(object) or ''):gmatch('(%w+):%s*(-?%d+)') do
        fields[name] = tonumber(value)
    end
    if fields.Owner and fields.District then return fields.Owner, fields.District end
end

local function sampleTopics(turn, initial)
    -- Take ownership at install as the baseline. A topic already owned on
    -- the checkpoint cannot be credited as an unlock on the first replay turn.
    local tag = initial and 'CSC_MILESTONE_TOPIC_OWNED' or 'CSC_MILESTONE_UNLOCK'
    for player in pairs(players or {}) do
        local polity = Players[player]
        if polity and polity:IsAlive() then
            local techs, civics = polity:GetTechs(), polity:GetCulture()
            for kind, keys in pairs(topics) do
                local definitions = kind == 'tech' and GameInfo.Technologies or GameInfo.Civics
                for key in pairs(keys) do
                    local definition = definitions[key]
                    local stamp = player .. ':' .. kind .. ':' .. key
                    if definition and not unlocked[stamp] then
                        local owned = kind == 'tech' and techs:HasTech(definition.Index)
                            or kind == 'civic' and civics:HasCivic(definition.Index)
                        if owned then
                            unlocked[stamp] = true
                            print(table.concat({tag, turn, player, kind, key}, '\t'))
                        end
                    end
                end
            end
        end
    end
end

local function snapshot(turn)
    local attachments, activeLeaves = {}, {}
    for _, id in pairs(assert(effects.GetModifiers())) do
        local definition = effects.GetModifierDefinition(id)
        local name = definition and definition.Id
        if name and (roots[name] or leaves[name]) and effects.GetModifierActive(id)
            and effects.GetModifierSubjectCount(id) > 0 then
            local owner = effects.GetModifierOwner(id)
            local subjects = effects.GetModifierSubjects(id) or {}
            if owner and roots[name] then
                local rule = roots[name]
                for _, subject in pairs(subjects) do
                    local key = rule.leaf .. ':' .. subject
                    local group = attachments[key] or {}
                    group[#group + 1] = {rule = rule, owner = owner, subject = subject}
                    attachments[key] = group
                end
            end
            if owner and leaves[name] then
                local subjectCount = effects.GetModifierSubjectCount(id)
                for _, subject in pairs(subjects) do
                    if subject == owner and subjectCount == 1 then
                        local key = name .. ':' .. owner
                        activeLeaves[key] = (activeLeaves[key] or 0) + 1
                    end
                end
            end
        end
    end
    local observed, links, unreadable = {}, 0, 0
    for key, group in pairs(attachments) do
        local copies = activeLeaves[key] or 0
        -- Two producers can supply the same recipient. Resolve their links
        -- only if each attachment has its own active copy of the benefit.
        if copies > 0 and copies ~= #group then unreadable = unreadable + 1
        elseif copies > 0 then
            for _, link in ipairs(group) do
                local rule = link.rule
                local owner, producer = readDistrict(link.owner)
                local receiver, customer = readDistrict(link.subject)
                if owner and receiver and owner == receiver then
                    local key = table.concat({owner, rule.service, producer, customer}, ':')
                    if (not players or players[owner]) and not observed[key] then
                        observed[key] = true
                        links = links + 1
                        print(table.concat({'CSC_MILESTONE_SERVICE_LINK', turn, owner, rule.quarter,
                            rule.stage, rule.service, producer, customer}, '\t'))
                    end
                else unreadable = unreadable + 1 end
            end
        end
    end
    print(table.concat({'CSC_MILESTONE_SERVICE_END', turn, links, unreadable}, '\t'))
    sampleTopics(turn, false)
end

sampleTopics(Game.GetCurrentGameTurn(), true)
if CSC_MILESTONE_SERVICE_EVERY_TURN then
    assert(not CSC_MILESTONE_SERVICE_WATCH_INSTALLED, 'Service observer already installed')
    local lastTurn, fault
    Events.TurnBegin.Add(function()
        local turn = Game.GetCurrentGameTurn()
        -- A matched full-game observer follows the original AI seats even
        -- on the fifth turn when autoplay hands control back to the harness.
        if fault or turn == lastTurn then return end
        if not CSC_MILESTONE_INCLUDE_HANDOFFS and not AutoplayManager.IsActive() then return end
        lastTurn = turn
        local ok, reason = pcall(snapshot, turn)
        if not ok then
            fault = true
            print('CSC_MILESTONE_SERVICE_FAULT', turn, reason)
        end
    end)
    CSC_MILESTONE_SERVICE_WATCH_INSTALLED = true
    print('CSC_MILESTONE_SERVICE_INSTALLED', count, #catalogue.omissions)
else snapshot(Game.GetCurrentGameTurn()) end
