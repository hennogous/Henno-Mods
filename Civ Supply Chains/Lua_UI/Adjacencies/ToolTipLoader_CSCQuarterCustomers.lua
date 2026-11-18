-- Extend the district info tooltip's native adjacency list with Quarter sales returns.
local stockGetAdjacencyBonuses = ToolTipHelper.GetAdjacencyBonuses
local rules = GameInfo.CSC_AdjacencyRules
if not rules then
    return
end

local returnsByDistrict = {}
for rule in rules() do
    -- Policy-owned copies double the base return conditionally during play.
    if rule.ModifierOwner == "DistrictModifiers"
        and rule.ProvideType == "SelfBonus"
        and rule.AdjacencyType == "FROM_RINGS_CAO_DISTRICT"
        and rule.CustomAdjacentObject:match("^DISTRICT_CSC_%w+_QUARTER$")
        and rule.MinRings == 1 and (rule.MaxRings or rule.Rings) == 1
        and rule.YieldChange > 0 then
        local districtReturns = returnsByDistrict[rule.DistrictType]
        if not districtReturns then
            districtReturns = {}
            returnsByDistrict[rule.DistrictType] = districtReturns
        end
        table.insert(districtReturns, rule)
    end
end

for _, districtReturns in pairs(returnsByDistrict) do
    table.sort(districtReturns, function(a, b) return a.ID < b.ID end)
end

function ToolTipHelper.GetAdjacencyBonuses(t, field, key)
    local bonuses = stockGetAdjacencyBonuses(t, field, key)
    if field ~= "DistrictType" then
        return bonuses
    end

    -- Production passes a district hash, while CSC rules store district type names.
    local district = GameInfo.Districts[key]
    local districtReturns = district and returnsByDistrict[district.DistrictType]
    if districtReturns then
        for _, rule in ipairs(districtReturns) do
            local quarter = GameInfo.Districts[rule.CustomAdjacentObject]
            local yield = GameInfo.Yields[rule.YieldType]
            if quarter and yield then
                table.insert(bonuses, Locale.Lookup("LOC_TYPE_TRAIT_ADJACENT_BONUS",
                    rule.YieldChange, yield.IconString, yield.Name, 1, quarter.Name))
            end
        end
    end
    return bonuses
end
