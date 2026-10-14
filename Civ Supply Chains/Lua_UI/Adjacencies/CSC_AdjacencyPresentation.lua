include('CSC_AdjacencyCore');
local A = CSC_Adjacency;
A.Initialize();

function A.Signed(value)
    return (value >= 0 and '+' or '') .. tostring(value);
end

function A.ValueIcon(rule, amount)
    if rule.ProvideType == 'SelfLoyalty' and amount < 0 then return '[ICON_PressureDown]'; end
    local provider = A.Providers[rule.ProvideType];
    local yield = GameInfo.Yields[rule.YieldType];
    if provider and provider.Icon then return '[' .. provider.Icon .. ']'; end
    return yield and yield.IconString or '';
end

function A.ValueString(rule, amount)
    local provider = A.Providers[rule.ProvideType];
    return A.ValueIcon(rule,amount) .. A.Signed(amount)
        .. ((provider and (provider.Percent == true or provider.Percent == 1)) and '%' or '');
end

function A.YieldName(rule)
    local kind=rule.ProvideType;
    if kind=='SelfExtractResource' then
        local resource=GameInfo.Resources[rule.YieldType];
        return resource and Locale.Lookup(resource.Name) or '';
    end
    if kind=='GreatPersonPoints' or kind=='GreatPersonMultiplier' then
        local person=GameInfo.GreatPersonClasses[rule.YieldType];
        local key='LOC_CSC_ADJ_YIELD_'..kind;
        local name=Locale.Lookup(key,person and Locale.Lookup(person.Name) or '');
        return name~=key and name or '';
    end
    if kind=='SelfBonus' or kind=='ProvideToADJ' or kind=='SelfMultiplier' then
        local yield=GameInfo.Yields[rule.YieldType];
        local name=yield and Locale.Lookup(yield.Name) or '';
        if kind=='SelfMultiplier' then
            local key='LOC_CSC_ADJ_YIELD_MULTIPLIER';
            local label=Locale.Lookup(key,name);
            return label~=key and label or name;
        end
        return name;
    end
    local key='LOC_CSC_ADJ_YIELD_'..kind;
    local name=Locale.Lookup(key);
    return name~=key and name or '';
end

function A.YieldText(rule,amount)
    return A.ValueIcon(rule,amount)..A.YieldName(rule);
end

function A.AmountText(rule,amount)
    local provider=A.Providers[rule.ProvideType];
    return A.Signed(amount)..((provider and (provider.Percent==true or provider.Percent==1)) and '%' or '');
end

function A.SourceName(rule,count)
    local key = rule.CustomAdjacentObject;
    local icon='';
    if (GameInfo.Resources and GameInfo.Resources[key]) or (GameInfo.Districts and GameInfo.Districts[key]) then
        icon='[ICON_'..key..']';
    end
    local object = A.Objects[key];
    if object and object.Name then return icon..Locale.Lookup(object.Name); end
    for _,tableName in ipairs({'Resources','ResourceClasses','Districts','Buildings','Improvements','Features','Terrains','Units','Routes'}) do
        local definitions = GameInfo[tableName];
        local definition = definitions and definitions[key];
        if definition and definition.Name then return icon..Locale.Lookup(definition.Name); end
    end
    local info = A.SourceInfo[rule.AdjacencyType];
    return info and Locale.Lookup(info.Name,count or 1) or Locale.Lookup('LOC_CSC_ADJ_SOURCE_GENERIC');
end

-- MAB's placement text keeps amount, localized yield, count, source and
-- distance separate. Preserve that contract using CSC-owned localization.
local namedSources={
    CAO_ROUTE='ROUTE',CAO_UNIT='UNIT',CAO_RESOURCE_CLASS='RESOURCE',
    TYPETAG_RESOURCE='RESOURCE',CAO_RESOURCE='RESOURCE',
    CAO_IMPROVEMENT='IMPROVEMENT',CAO_DISTRICT='DISTRICT',TYPETAG_DISTRICT='DISTRICT',
    CAO_FEATURE='FEATURE',CAO_TERRAIN='TERRAIN',CAO_TERRAIN_SETS='TERRAIN'
};
function A.PreviewLine(rule,amount,count)
    local first,last=A.Bounds(rule);
    local distance='LOC_CSC_ADJ_DISTANCE_NEARBY';
    if last==0 then distance='LOC_CSC_ADJ_DISTANCE_LOCAL';
    elseif first==1 and last==1 then distance='LOC_CSC_ADJ_DISTANCE_ADJACENT'; end
    local family=rule.AdjacencyType:gsub('^FROM_UI_RINGS_',''):gsub('^FROM_RINGS_','');
    local suffix=namedSources[family];
    local key=suffix and 'LOC_CSC_ADJ_PREVIEW_NAMED_'..suffix or 'LOC_CSC_ADJ_PREVIEW_LINE';
    if rule.AdjacencyType=='FROM_UNCONDITIONAL_BONUS' then key='LOC_CSC_ADJ_PREVIEW_FIXED'; end
    if rule.AdjacencyType=='FROM_RIVER_CROSSING' then distance='LOC_CSC_ADJ_DISTANCE_ADJACENT'; end
    -- Dedicated text is added when CSC first authors a rule using that family.
    local text=Locale.Lookup(key,A.AmountText(rule,amount),A.YieldText(rule,amount),count,A.SourceName(rule,count),Locale.Lookup(distance));
    if text==key then
        text=Locale.Lookup('LOC_CSC_ADJ_PREVIEW_LINE',A.AmountText(rule,amount),A.YieldText(rule,amount),count,A.SourceName(rule,count),Locale.Lookup(distance));
    end
    return text;
end

function A.Preview(districtType, plot, city)
    local lines,totals = {},{};
    local playerID = city:GetOwner();
    for _,rule in ipairs(A.ByDistrict[districtType] or {}) do
        if A.Eligible(rule,city,playerID) then
            local count = A.Count(rule,plot,city,playerID);
            local amount = A.Amount(rule,count);
            if amount ~= 0 then
                local key = rule.ProvideType .. ':' .. rule.YieldType;
                totals[key] = totals[key] or {Rule=rule,Amount=0};
                totals[key].Amount=totals[key].Amount+amount;
                lines[#lines+1]=A.PreviewLine(rule,amount,count);
            end
        end
    end
    local keys,icons = {},{};
    for key in pairs(totals) do keys[#keys+1]=key; end
    table.sort(keys);
    for _,key in ipairs(keys) do
        local total=totals[key];
        if total.Amount ~= 0 then icons[#icons+1]=A.ValueString(total.Rule,total.Amount); end
    end
    return table.concat(icons,'[NEWLINE]'),table.concat(lines,'[NEWLINE]');
end

function A.RiverEdge(center, neighbor, direction)
    if not center or not neighbor then return false; end
    if direction == DirectionTypes.DIRECTION_EAST then return center:IsWOfRiver(); end
    if direction == DirectionTypes.DIRECTION_SOUTHEAST then return center:IsNWOfRiver(); end
    if direction == DirectionTypes.DIRECTION_SOUTHWEST then return center:IsNEOfRiver(); end
    if direction == DirectionTypes.DIRECTION_NORTHEAST then return neighbor:IsNEOfRiver(); end
    if direction == DirectionTypes.DIRECTION_WEST then return neighbor:IsWOfRiver(); end
    if direction == DirectionTypes.DIRECTION_NORTHWEST then return neighbor:IsNWOfRiver(); end
    return false;
end

-- Property and aggregate sources do not have a tile-edge representation.
local edgeSources = {
    FROM_RINGS_TYPETAG_RESOURCE=true,FROM_RINGS_CAO_RESOURCE=true,
    FROM_RINGS_CAO_RESOURCE_CLASS=true,FROM_RINGS_CAO_IMPROVEMENT=true,
    FROM_RINGS_CAO_FEATURE=true,FROM_RINGS_CAO_DISTRICT=true,
    FROM_RINGS_TYPETAG_DISTRICT=true,FROM_RINGS_CAO_TERRAIN=true,
    FROM_RINGS_CAO_TERRAIN_SETS=true,FROM_RINGS_RESOURCE=true,
    FROM_RINGS_LAKE=true,FROM_RINGS_WONDERS=true,FROM_RINGS_DISTRICT=true,
    FROM_RINGS_DISTRICT_AND_WONDER=true,FROM_ADJACENT_RESOURCE=true,
    FROM_ADJACENT_LAKE=true,FROM_ADJACENT_WONDERS=true,FROM_ADJACENT_DISTRICT=true,
    FROM_ADJACENT_DISTRICT_AND_WONDER=true,FROM_RINGS_SPECIFIC_WONDER=true
};

function A.EdgeIcon(districtType, center, neighbor, city, direction)
    for _,rule in ipairs(A.ByDistrict[districtType] or {}) do
        local first,last = A.Bounds(rule);
        if first <= 1 and last >= 1 and A.Eligible(rule,city,city:GetOwner())
            and (not (rule.MustOwn == true or rule.MustOwn == 1) or neighbor:GetOwner() == city:GetOwner()) then
            local match = false;
            if rule.AdjacencyType == 'FROM_RIVER_CROSSING' then
                match=A.RiverEdge(center,neighbor,direction);
            elseif edgeSources[rule.AdjacencyType] then
                match=A.Sources[rule.AdjacencyType].Quantity(neighbor,rule.CustomAdjacentObject,{PlayerID=city:GetOwner(),City=city}) > 0;
            end
            if match then
                local object=A.Objects[rule.CustomAdjacentObject];
                local info=A.SourceInfo[rule.AdjacencyType];
                local icon=object and object.ArtdefOverlayEntry;
                if not icon or icon == '' then icon=info and info.ArtdefOverlayEntry; end
                if icon and icon ~= '' then return icon; end
            end
        end
    end
    return '';
end
