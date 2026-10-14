local player=Players[0]; local city=nil;
for _,c in player:GetCities():Members() do
    if c:GetDistricts():HasDistrict(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index) then city=c; break; end
end
assert(city,'Missing fixture city');
for _,kind in ipairs({'DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER'}) do
    local district=city:GetDistricts():GetDistrict(GameInfo.Districts[kind].Index);
    local plot=Map.GetPlot(district:GetX(),district:GetY());
    local icons,description=GetAdjacentYieldBonusString(GameInfo.Districts[kind].Index,city,plot);
    local expectedIcons,expectedDescription=CSC_Adjacency.Preview(kind,plot,city);
    assert(expectedDescription~='' and description:find(expectedDescription,1,true),'Custom preview must be present');
    local tooltip=ToolTipHelper.GetToolTip(kind,0,city);
    assert(tooltip and not tooltip:find('Modular Adjacency Bonus:',1,true),'District tooltip must not append the redundant adjacency section');
    local bonuses=AddAdjacentPlotBonuses(plot,kind,city,{});
    for _,view in pairs(bonuses) do
        local faces={};
        for _,edge in ipairs(view.adjacent) do assert(not faces[edge.direction],'Duplicate edge art'); faces[edge.direction]=true; end
    end
    print('CSC_LIVE_UI',kind,icons,description);
end
