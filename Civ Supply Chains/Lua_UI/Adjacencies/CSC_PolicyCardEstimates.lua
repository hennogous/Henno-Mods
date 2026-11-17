-- Optional BRS/EPC display adapter: live Quarter sites -> hypothetical policy
-- returns -> the public RMA API used when policy cards and reports are drawn.
-- This owns a separate UI context. Never replace RealModifierAnalysis: its Lua
-- is paired with BRS's XML, not imported for include(), and replacing it can
-- remove the very initialization/functions that EPC needs to draw its cards.
-- Original BRS initialization, refresh listeners and unrelated forecasts remain
-- in BRS's own context. No gameplay amounts or GovernmentScreen controls change.
include('Civ6Common');
include('CSC_AdjacencyCore');
local A = CSC_Adjacency;
A.Initialize();

local decodeModifier, calculateModifierEffect, yieldTableGetInfo;
-- RMA uses extended yield keys alongside the six engine yields. Reproduce only
-- its public numeric table shape; the native analyser still decodes all ordinary
-- modifiers. Keep zero entries so its formatter accepts a CSC-only return.
local function YieldTableNew()
    local result = {TOURISM=0, AMENITY=0, HOUSING=0, LOYALTY=0};
    for key in pairs(YieldTypes) do result[key] = 0; end
    return result;
end
local function YieldTableSetYield(impact, kind, amount)
    impact[string.gsub(kind,'^YIELD_','')] = amount;
end
local attachments, policies = {}, {};
-- Installed RMA 7.0 orders yield IDs with ipairs, which can omit Food at ID 0.
-- Probe its formatter numerically so corrected versions are never duplicated.
local omitsFood = false;
local function FormatImpact(impact)
    local text = yieldTableGetInfo(impact);
    if omitsFood and impact.FOOD and impact.FOOD ~= 0 then
        text = GetYieldString('YIELD_FOOD',impact.FOOD) .. (text ~= '' and ' ' .. text or '');
    end
    return text;
end
local calculationCache = nil;
local registered = {};
for link in GameInfo.PolicyModifiers() do registered[link.PolicyType .. ':' .. link.ModifierId] = true; end
for _,rule in ipairs(A.Rules) do
    if rule.ModifierOwner == 'PolicyModifiers' and rule.ProvideType == 'SelfBonus'
        and rule.AdjacencyType == 'FROM_RINGS_CAO_DISTRICT' then
        -- These wrappers encode ONE return in ten property bits. Forecast the
        -- whole return on the first registered wrapper, zero on the rest. Never
        -- sum the ten literal bit weights or require a card to be active first.
        -- Match exact registered IDs, leaving all other mod/vanilla effects alone.
        local first = true;
        for _,bit in ipairs(A.Bits) do
            local id = 'ATTACH_MOD_CSC_ADJ_' .. rule.ID .. '_' .. bit;
            if registered[rule.WhoIsTheOwner .. ':' .. id] then
                attachments[id] = {Rule=rule, First=first};
                policies[rule.WhoIsTheOwner] = true;
                first = false;
            end
        end
    end
end

local function Forecast(rule, playerID, cityID)
    local player = Players[playerID];
    if not player then return 0; end
    -- Hypothetical card impact must work for unslotted and already slotted cards.
    -- Bypass ONLY the active-card gate; shared eligibility and source counting
    -- retain ownership, rings, yield rounding/caps and unique-district matching.
    local hypothetical = {};
    for key,value in pairs(rule) do hypothetical[key] = value; end
    hypothetical.ModifierOwner = 'DistrictModifiers';
    local total = 0;
    for _,city in player:GetCities():Members() do
        if cityID == nil or city:GetID() == cityID then
            local districts = city:GetDistricts();
            for index=0,districts:GetNumDistricts()-1 do
                local district = districts:GetDistrictByIndex(index);
                local definition = GameInfo.Districts[district:GetType()];
                if definition and definition.DistrictType == rule.DistrictType
                    and district:IsComplete() and not districts:IsPillaged(district:GetType())
                    and A.Eligible(hypothetical,city,playerID) then
                    local plot = Map.GetPlot(district:GetX(),district:GetY());
                    if plot then total = total + A.Amount(rule,A.Count(rule,plot,city,playerID)); end
                end
            end
        end
    end
    return total;
end

function DecodeModifier(modifierID, playerID, cityID, mainSubjects, mainSubjectType)
    local entry = attachments[modifierID];
    if not entry then return decodeModifier(modifierID,playerID,cityID,mainSubjects,mainSubjectType); end
    local impact = YieldTableNew();
    if entry.First then
        playerID = playerID == nil and Game.GetLocalPlayer() or playerID;
        local key = entry.Rule.ID .. ':' .. tostring(playerID) .. ':' .. tostring(cityID);
        local amount = calculationCache and calculationCache[key];
        if amount == nil then
            amount = Forecast(entry.Rule,playerID,cityID);
            if calculationCache then calculationCache[key] = amount; end
        end
        -- This is the additional yield granted by this card, not the doubled
        -- district total. RMA adds it to its independently estimated vanilla bonus.
        YieldTableSetYield(impact,entry.Rule.YieldType,amount);
    end
    -- End the attach chain here: RMA must not evaluate the live property bits
    -- again. Preserve its seven-value DecodeModifier contract and metadata.
    local modifier = {ModifierId=modifierID, SubjectReqSetId=nil};
    return modifierID .. '[NEWLINE]' .. FormatImpact(impact), impact, nil, false, modifier, {}, 'District';
end

function CalculateModifierEffect(object, objectType, playerID, cityID, influence)
    if object ~= 'Policy' or not policies[objectType] then
        return calculateModifierEffect(object,objectType,playerID,cityID,influence);
    end
    -- Forecasts live for one synchronous RMA request only. No stale empire or
    -- policy state survives a screen refresh, capture, pillage or adjacency edit.
    local previous = calculationCache;
    calculationCache = {};
    -- RMA's aggregator calls its context-local decoder rather than its exposed
    -- decoder. For affected policies, fold the public decoder results here using
    -- BRS 7.0's attachment/subject/filter rules. Ordinary roots still go through
    -- BRS unchanged; only exact CSC roots terminate at our hypothetical return.
    -- This avoids copying the analyser or replacing its initialization context.
    local yields, details, unknown = YieldTableNew(), {}, false;
    local filter = influence and 'PLAYER_HAS_' .. influence .. '_INFLUENCE' or nil;
    for link in GameInfo.PolicyModifiers() do
        if link.PolicyType == objectType then
            local text, impact, attached, rootUnknown, modifier, subjects, subjectType =
                DecodeModifier(link.ModifierId or link.ModifierID,playerID,cityID);
            if filter == nil or (modifier and modifier.SubjectReqSetId == filter) then
                table.insert(details,text);
                if attached then
                    table.insert(details,'Attached modifier');
                    if subjects ~= nil then
                        text, impact, attached, rootUnknown, modifier =
                            DecodeModifier(attached,playerID,cityID,subjects,subjectType);
                    else
                        text, impact, attached, rootUnknown, modifier = DecodeModifier(attached,playerID,cityID);
                    end
                    table.insert(details,text);
                    if subjects ~= nil and #subjects == 0 then
                        impact = nil;
                        table.insert(details,'Attached modifier has NO valid subjects');
                    end
                end
                if impact then
                    for kind, amount in pairs(impact) do yields[kind] = (yields[kind] or 0) + amount; end
                end
                unknown = unknown or rootUnknown;
                table.insert(details,'-------------------');
            end
        end
    end
    calculationCache = previous;
    if #details == 0 then table.insert(details,'No modifiers for this object.'); end
    local text = FormatImpact(yields);
    if text == '' then table.insert(details,'Yields not affected.'); end
    if unknown then table.insert(details,'[COLOR_Red]Unknown effect[ENDCOLOR] was not processed.'); end
    return text, yields, table.concat(details,'[NEWLINE]'), unknown;
end

local installed = false;
local reportedFailures = {};
local function SafeCalculateModifierEffect(object, objectType, playerID, cityID, influence)
    if object ~= 'Policy' or not policies[objectType] then
        return calculateModifierEffect(object,objectType,playerID,cityID,influence);
    end
    -- Optional display forecasts must not prevent policy selection. An API/data
    -- mismatch gets one diagnostic per policy, then BRS's original estimate.
    -- If that also fails, leave only this card's estimate blank. Preserve the
    -- public four-return shape and release request-local cache on every path.
    local previous = calculationCache;
    local ok, text, yields, tooltip, unknown = pcall(CalculateModifierEffect,
        object,objectType,playerID,cityID,influence);
    calculationCache = previous;
    if ok then return text, yields, tooltip, unknown; end
    if not reportedFailures[objectType] then
        reportedFailures[objectType] = true;
        print('CSC policy estimates: forecast failed for ' .. tostring(objectType) .. ': ' .. tostring(text));
    end
    ok, text, yields, tooltip, unknown = pcall(calculateModifierEffect,
        object,objectType,playerID,cityID,influence);
    if ok then return text, yields, tooltip, unknown; end
    return '', YieldTableNew(), 'Policy estimate unavailable; policy gameplay is unchanged.', true;
end
local function Install()
    if installed then return; end
    local rma = ExposedMembers.RMA;
    if not rma or type(rma.DecodeModifier) ~= 'function'
        or type(rma.CalculateModifierEffect) ~= 'function' or type(rma.YieldTableGetInfo) ~= 'function' then
        -- Keep BRS/EPC untouched if another version has not published its API.
        -- The load-complete event retries once after all UI contexts initialize;
        -- avoid a polling loop or per-turn work for this optional display feature.
        print('CSC policy estimates: waiting for original BRS analysis API');
        return;
    end
    decodeModifier, calculateModifierEffect, yieldTableGetInfo =
        rma.DecodeModifier, rma.CalculateModifierEffect, rma.YieldTableGetInfo;
    local foodProbe = YieldTableNew();
    YieldTableSetYield(foodProbe,'YIELD_FOOD',1);
    omitsFood = yieldTableGetInfo(foodProbe) == '';
    rma.DecodeModifier = DecodeModifier;
    rma.CalculateModifierEffect = SafeCalculateModifierEffect;
    installed = true;
    print('CSC policy estimates: attached to original BRS analysis API');
end
-- Context order is sufficient in the ordinary load; the event also handles BRS
-- initializing later. Both consumers keep the same RMA table identity, including
-- EPC's cached local reference. Duplicate events must never stack wrappers.
Events.LoadGameViewStateDone.Add(Install);
Install();
