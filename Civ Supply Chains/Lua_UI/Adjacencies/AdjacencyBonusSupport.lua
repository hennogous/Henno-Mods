-- Preserve Firaxis behavior, then add only rules owned by CSC.
include('CSC_StockAdjacencyBonusSupport');
include('CSC_AdjacencyPresentation');
local A=CSC_Adjacency;
local stockYieldString=GetAdjacentYieldBonusString;
local stockBonuses=AddAdjacentPlotBonuses;
local stockIcon=GetAdjacentIconArtdefName;

function GetAdjacentYieldBonusString(districtIndex,city,plot)
    local definition=GameInfo.Districts[districtIndex];
    if not definition or not A.ByDistrict[definition.DistrictType] then return stockYieldString(districtIndex,city,plot); end
    local _,customTooltip,totals=A.Preview(definition.DistrictType,plot,city);
    local baseYields={};
    for _,total in pairs(totals) do
        if total.Rule.ProvideType=='SelfBonus' then baseYields[total.Rule.YieldType]=total.Amount; end
    end
    -- Supply numeric additions before Firaxis formats its icons. Native policy
    -- multipliers are already included by GetAdjacencyYield; never apply them
    -- again to either the native total or the policy-owned CSC additions.
    local icons,tooltip,required=stockYieldString(districtIndex,city,plot,baseYields);
    local customIcons=A.TotalIcons(totals,true);
    if customIcons~='' then icons=(icons~='' and icons..'[NEWLINE]' or '')..customIcons; end
    if customTooltip~='' then tooltip=(tooltip~='' and tooltip..'[NEWLINE]' or '')..customTooltip; end
    return icons,tooltip,required;
end

-- Keep the optional center argument for direct callers as well as this wrapper.
function GetAdjacentIconArtdefName(districtType,neighbor,city,direction,center)
    local icon=stockIcon(districtType,neighbor,city,direction);
    if icon and icon~='' then return icon; end
    if not center then return ''; end
    return A.EdgeIcon(districtType,center,neighbor,city,direction);
end

local opposite = {
    -- Native overlay records belong to the neighbor, so its face points back
    -- toward the selected district rather than using the center's direction.
    [DirectionTypes.DIRECTION_NORTHEAST]=DirectionTypes.DIRECTION_SOUTHWEST,
    [DirectionTypes.DIRECTION_EAST]=DirectionTypes.DIRECTION_WEST,
    [DirectionTypes.DIRECTION_SOUTHEAST]=DirectionTypes.DIRECTION_NORTHWEST,
    [DirectionTypes.DIRECTION_SOUTHWEST]=DirectionTypes.DIRECTION_NORTHEAST,
    [DirectionTypes.DIRECTION_WEST]=DirectionTypes.DIRECTION_EAST,
    [DirectionTypes.DIRECTION_NORTHWEST]=DirectionTypes.DIRECTION_SOUTHEAST
};

function AddAdjacentPlotBonuses(center,districtType,city,current)
    local bonuses=stockBonuses(center,districtType,city,current);
    if not A.ByDistrict[districtType] then return bonuses; end
    for direction,reverse in pairs(opposite) do
        local neighbor=Map.GetAdjacentPlot(center:GetX(),center:GetY(),direction);
        if neighbor then
            local icon=A.EdgeIcon(districtType,center,neighbor,city,direction);
            if icon~='' then
                -- Native icons take priority; each face has only one art slot.
                local view=bonuses[neighbor:GetIndex()] or GetViewPlotInfo(neighbor,current);
                local occupied=false;
                for _,edge in ipairs(view.adjacent) do if edge.direction==reverse then occupied=true; break; end end
                if not occupied then
                    view.adjacent[#view.adjacent+1]={direction=reverse,iconArtdef=icon,inBonus=false,outBonus=true};
                end
                bonuses[neighbor:GetIndex()]=view;
            end
        end
    end
    return bonuses;
end
