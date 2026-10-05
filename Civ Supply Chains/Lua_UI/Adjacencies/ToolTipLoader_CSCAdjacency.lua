-- Firaxis discovers ToolTipLoader_* automatically. This adds descriptions
-- without replacing the game's tooltip helper or other kinds of tooltip.
-- The game's loading screen discovers these files too, before gameplay APIs
-- and the custom database exist. Each InGame context loads its own copy later.
if not DefenseTypes or not GameInfo.CSC_AdjacencyRules then return; end
include('CSC_AdjacencyPresentation');
local originalDistrictTooltip=ToolTipHelper.GetDistrictToolTip;
local function appendDescription(text,districtType)
    local description=CSC_Adjacency.RuleDescriptions(districtType);
    if description=='' then return text; end
    return text .. '[NEWLINE][NEWLINE]' .. Locale.Lookup('LOC_CSC_ADJ_HEADING') .. '[NEWLINE]' .. description;
end
ToolTipHelper.GetDistrictToolTip=function(districtType,...)
    local district=GameInfo.Districts[districtType];
    if district then districtType=district.DistrictType; end
    return appendDescription(originalDistrictTooltip(districtType,...),districtType);
end;
g_ToolTipGenerators.KIND_DISTRICT=ToolTipHelper.GetDistrictToolTip;
