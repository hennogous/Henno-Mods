-- Correct native policy badge totals, then add rules owned by CSC.
include('CSC_StockAdjacencyBonusSupport');
include('CSC_AdjacencyPresentation');
local A=CSC_Adjacency;
local stockYieldString=GetAdjacentYieldBonusString;
local stockBonuses=AddAdjacentPlotBonuses;
local stockIcon=GetAdjacentIconArtdefName;

local function IsBakersPlacement(districtType)
    if districtType ~= 'DISTRICT_CSC_BAKERS_QUARTER'
        or UI.GetInterfaceMode() ~= InterfaceModeTypes.DISTRICT_PLACEMENT then return false; end
    -- PlotInfo also collects every district for the general adjacency lens.
    local selected = GameInfo.Districts[UI.GetInterfaceModeParameter(CityOperationTypes.PARAM_DISTRICT_TYPE)];
    return selected and selected.DistrictType == districtType;
end

function GetAdjacentYieldBonusString(districtIndex,city,plot)
    local definition=GameInfo.Districts[districtIndex];
    if not definition or not A.ByDistrict[definition.DistrictType] then return stockYieldString(districtIndex,city,plot); end
    local _,customTooltip,totals=A.Preview(definition.DistrictType,plot,city);
    local baseYields={};
    for _,total in pairs(totals) do
        if total.Rule.ProvideType=='SelfBonus' then baseYields[total.Rule.YieldType]=total.Amount; end
    end
    -- Supply numeric additions before the shared formatter renders its icons.
    -- It adjusts native base adjacency for active policies BEFORE adding these
    -- CSC totals, which already include their separate policy-owned returns.
    local icons,tooltip,required=stockYieldString(districtIndex,city,plot,baseYields);
    local customIcons=A.TotalIcons(totals,true);
    if customIcons~='' then icons=(icons~='' and icons..'[NEWLINE]' or '')..customIcons; end
    if customTooltip~='' then tooltip=(tooltip~='' and tooltip..'[NEWLINE]' or '')..customTooltip; end
    if IsBakersPlacement(definition.DistrictType) then
        local potential, potentialTooltip = A.MillPlacementText(plot,city);
        if potential~='' then
            icons=potential..(icons~='' and '[NEWLINE]'..icons or '');
            tooltip=potentialTooltip..(tooltip~='' and '[NEWLINE]'..tooltip or '');
        end
    end
    return icons,tooltip,required;
end

-- The placement plot is needed for directional river tests. An eligible CSC
-- source's authored icon identifies the supply-chain role more precisely than
-- the native district/resource icon; native art is the fallback for other edges.
function GetAdjacentIconArtdefName(districtType,neighbor,city,direction,center,showMillPotential)
    if center then
        local icon=A.EdgeIcon(districtType,center,neighbor,city,direction,showMillPotential);
        if icon~='' then return icon; end
    end
    return stockIcon(districtType,neighbor,city,direction);
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
    if not A.ByDistrict[districtType] then return stockBonuses(center,districtType,city,current); end
    -- Do not call the native collector first: it calls the icon picker without
    -- the center and can reserve the same face with a generic icon. Select once,
    -- with the placement context, just as the fork's five-argument path did.
    local bonuses={};
    local showMillPotential = IsBakersPlacement(districtType);
    for direction,reverse in pairs(opposite) do
        local neighbor=Map.GetAdjacentPlot(center:GetX(),center:GetY(),direction);
        if neighbor then
            local icon=GetAdjacentIconArtdefName(districtType,neighbor,city,direction,center,showMillPotential);
            if icon and icon~='' then
                local view=bonuses[neighbor:GetIndex()] or GetViewPlotInfo(neighbor,current);
                local existing=nil;
                for index=#view.adjacent,1,-1 do
                    local edge=view.adjacent[index];
                    if edge.direction==reverse then
                        if existing then
                            -- Preserve an incoming marker while collapsing old
                            -- duplicate records for this same geometric face.
                            existing.inBonus=existing.inBonus or edge.inBonus;
                            table.remove(view.adjacent,index);
                        else existing=edge; end
                    end
                end
                if existing then
                    existing.iconArtdef=icon;
                    existing.outBonus=true;
                else
                    view.adjacent[#view.adjacent+1]={direction=reverse,iconArtdef=icon,inBonus=false,outBonus=true};
                end
                bonuses[neighbor:GetIndex()]=view;
            end
        end
    end
    return bonuses;
end
