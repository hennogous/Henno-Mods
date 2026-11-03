-- Current Service presentation shared by MCUIS and camera-facing lens pins.
-- Read active benefit wrappers, never persistent hidden Service grants or art
-- flags. SQL owns all eligibility; this module only counts their live subjects.
if CSC_ServicePresentation ~= nil then return end
CSC_ServicePresentation = {Anchors={}, Effects={}}
local P = CSC_ServicePresentation
if GameInfo.CSC_AbilityAttachModifiers then
    for row in GameInfo.CSC_AbilityAttachModifiers() do
        P.Anchors[row.ModifierId] = row
        if row.AbilityEffectModifierId then
            P.Effects[row.AbilityEffectModifierId] = row
        end
    end
end

function P.Collect(playerID, cityID)
    local cities = {}
    if playerID == -1 or GameEffects == nil then return cities end
    for _, modifier in pairs(GameEffects.GetModifiers() or {}) do
        local definition = GameEffects.GetModifierDefinition(modifier)
        local row = definition and P.Anchors[definition.Id]
        if row and GameEffects.GetModifierActive(modifier)
            and GameEffects.GetModifierSubjectCount(modifier) > 0 then
            for _, subject in pairs(GameEffects.GetModifierSubjects(modifier) or {}) do
                if Locale.Lookup(GameEffects.GetObjectType(subject) or "") == "District" then
                    local info = {}
                    for name, value in (GameEffects.GetObjectString(subject) or ""):gmatch("(%w+):%s*(-?%d+)") do
                        info[name] = tonumber(value)
                    end
                    if info.Owner == playerID and info.City and info.District
                        and (cityID == nil or cityID == info.City) then
                        -- Keep unresolved anchors observable for diagnostics,
                        -- but only resolved effects can produce icons/tooltips.
                        local effectID = row.AbilityEffectModifierId or row.ModifierId
                        cities[info.City] = cities[info.City] or {}
                        local city = cities[info.City]
                        city[effectID] = city[effectID] or {count=0, districts={}, row=row}
                        local effect = city[effectID]
                        effect.count = effect.count + 1
                        effect.districts[info.District] = true
                    end
                end
            end
        end
    end
    return cities
end

local function Signed(amount)
    return amount > 0 and "+" .. tostring(amount) or tostring(amount)
end

function P.Format(effectID, count, playerID)
    local row = P.Effects[effectID]
    if row == nil or count == nil or count <= 0 then return nil end
    -- Same localization parameters as MCUIS: total effect, signed stack count,
    -- numeric count for plurals and the existing supporting Supply Chain line.
    local tooltip = Locale.Lookup(row.AbilityDesc or "",
        Signed((tonumber(row.AbilityArgumentAmount) or 0) * count), Signed(count), count)
    local icon = row.AbilityIcon
    if icon == nil then
        local config = PlayerConfigurations and PlayerConfigurations[playerID]
        local civilization = config and config:GetCivilizationTypeName()
        icon = civilization and "ICON_" .. civilization or "ICON_BUILDING_MONUMENT"
    end
    return {tooltip=tooltip, icon=icon, target=row.AbilityIconTarget}
end
