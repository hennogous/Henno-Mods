-- UI readers share the gameplay evaluator so previews use the same eligibility,
-- visibility, rounding and amount limits. This file only builds display data.
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
    -- Name district sources in the badge tooltip without a second icon.
    if GameInfo.Resources and GameInfo.Resources[key] then
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
-- The badge and tooltip can render white with an inline alpha value. Use
-- the stock Gray color so forecast text visibly differs from active yields.
local millForecastColor = '[COLOR:Gray]';
local millForecastProduction = '[ICON_CSC_MILL_PRODUCTION]';

function A.PreviewLine(rule,amount,count,isForecast)
    -- The same Mill line is used for placement forecasts and active bonuses.
    if A.UnitSteps[rule.ID] then
        local key = rule.AdjacencyType == 'FROM_RIVER_CROSSING'
            and 'LOC_CSC_ADJ_MILL_RIVER' or 'LOC_CSC_ADJ_MILL_TERRAIN';
        local mill = GameInfo.Buildings[rule.WhoIsTheOwner];
        local yieldText = A.YieldText(rule,amount);
        if isForecast then
            -- The atlas supplies the icon's alpha. Dim the surrounding text separately.
            yieldText = '[ENDCOLOR]' .. millForecastProduction .. millForecastColor .. A.YieldName(rule);
        end
        local text = Locale.Lookup(key,A.AmountText(rule,amount),yieldText,
            count,A.SourceName(rule,count),Locale.Lookup(mill.Name));
        return isForecast and millForecastColor .. text .. '[ENDCOLOR]' or text;
    end
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

function A.TotalIcons(totals, skipBaseYields)
    local keys,icons = {},{};
    for key,total in pairs(totals) do
        if not skipBaseYields or total.Rule.ProvideType ~= 'SelfBonus' then keys[#keys+1]=key; end
    end
    table.sort(keys);
    for _,key in ipairs(keys) do
        local total=totals[key];
        if total.Amount ~= 0 then icons[#icons+1]=A.ValueString(total.Rule,total.Amount); end
    end
    return table.concat(icons,'[NEWLINE]');
end

function A.Preview(districtType, plot, city)
    -- Totals combine equal provider/yield pairs for the icons. Detail keys keep
    -- distinct sources/ring bands separate while merging their policy additions.
    local lines,totals,details,detailKeys = {},{},{},{};
    local playerID = city:GetOwner();
    for _,rule in ipairs(A.ByDistrict[districtType] or {}) do
        if A.Eligible(rule,city,playerID) then
            local count = A.Count(rule,plot,city,playerID);
            local amount = A.Amount(rule,count);
            if amount ~= 0 then
                local key = rule.ProvideType .. ':' .. rule.YieldType;
                totals[key] = totals[key] or {Rule=rule,Amount=0};
                totals[key].Amount=totals[key].Amount+amount;
                -- A policy adds to the same source sentence, rather than
                -- displaying an indistinguishable second +1 Quarter line.
                local first,last=A.Bounds(rule);
                local detailKey=table.concat({key,rule.AdjacencyType,rule.CustomAdjacentObject,first,last,count},':');
                if not details[detailKey] then
                    details[detailKey]={Rule=rule,Amount=0,Count=count};
                    detailKeys[#detailKeys+1]=detailKey;
                end
                details[detailKey].Amount=details[detailKey].Amount+amount;
            end
        end
    end
    local quarter = districtType:match('^DISTRICT_CSC_(%w+)_QUARTER$');
    local classPrefix = quarter and 'CLASS_CSC_' .. quarter;
    local terrainLines = {};
    local goodsLine, lastMaterialLine;
    for _,key in ipairs(detailKeys) do
        local detail=details[key];
        if detail.Amount ~= 0 then
            local rule = detail.Rule;
            local source = rule.CustomAdjacentObject;
            local line = A.PreviewLine(rule,detail.Amount,detail.Count);
            -- Put the Quarter's tile terrain bonuses before its supply sources.
            if quarter and (rule.AdjacencyType == 'FROM_RIVER_CROSSING'
                or (rule.AdjacencyType == 'FROM_RINGS_CAO_TERRAIN_SETS' and source == 'IsHills')) then
                terrainLines[#terrainLines+1] = line;
            else
                lines[#lines+1] = line;
                if classPrefix and source == classPrefix .. '_GOODS_PROVIDER' then
                    goodsLine = #lines;
                elseif classPrefix and (source == classPrefix .. '_BASE' or source == classPrefix .. '_SPEC') then
                    lastMaterialLine = #lines;
                end
            end
        end
    end
    -- Move the Quarter's goods-provider line after the last visible material.
    -- Other lines retain their order, including when no materials contribute.
    if goodsLine and lastMaterialLine and goodsLine < lastMaterialLine then
        local line = table.remove(lines, goodsLine);
        table.insert(lines, lastMaterialLine, line);
    end
    for _,line in ipairs(lines) do terrainLines[#terrainLines+1] = line; end
    return A.TotalIcons(totals),table.concat(terrainLines,'[NEWLINE]'),totals;
end

function A.RiverEdge(center, neighbor, direction)
    -- A river edge is stored on only one of its two hexes. The opposite three
    -- directions therefore query the neighbor's corresponding edge flag.
    if not center or not neighbor then return false; end
    if direction == DirectionTypes.DIRECTION_EAST then return center:IsWOfRiver(); end
    if direction == DirectionTypes.DIRECTION_SOUTHEAST then return center:IsNWOfRiver(); end
    if direction == DirectionTypes.DIRECTION_SOUTHWEST then return center:IsNEOfRiver(); end
    if direction == DirectionTypes.DIRECTION_NORTHEAST then return neighbor:IsNEOfRiver(); end
    if direction == DirectionTypes.DIRECTION_WEST then return neighbor:IsWOfRiver(); end
    if direction == DirectionTypes.DIRECTION_NORTHWEST then return neighbor:IsNWOfRiver(); end
    return false;
end

local millHillsIcons = {
    TERRAIN_GRASS_HILLS = '[ICON_CSC_MILL_GRASS_HILLS]',
    TERRAIN_PLAINS_HILLS = '[ICON_CSC_MILL_PLAINS_HILLS]',
    TERRAIN_DESERT_HILLS = '[ICON_CSC_MILL_DESERT_HILLS]',
    TERRAIN_TUNDRA_HILLS = '[ICON_CSC_MILL_TUNDRA_HILLS]',
    TERRAIN_SNOW_HILLS = '[ICON_CSC_MILL_SNOW_HILLS]'
};

function A.MillPlacementText(plot, city, playerID)
    local options, lines = {}, {};
    playerID = playerID or city:GetOwner();
    -- The two local unit-step rules describe alternative Mills. Read their
    -- terrain and amounts without the functioning-Mill gate used by A.Preview.
    -- Skip any already-active rule and keep these figures out of live totals.
    for _,rule in ipairs(A.ByDistrict.DISTRICT_CSC_BAKERS_QUARTER or {}) do
        if A.UnitSteps[rule.ID] and not A.Eligible(rule,city,playerID) then
            local count = A.Count(rule,plot,city,playerID);
            local amount = A.Amount(rule,count);
            if amount > 0 then
                local value = A.AmountText(rule,amount);
                local terrainIcon = '[ICON_CSC_MILL_RIVER]';
                if rule.AdjacencyType ~= 'FROM_RIVER_CROSSING' then
                    local terrain = GameInfo.Terrains[plot:GetTerrainType()];
                    terrainIcon = terrain and millHillsIcons[terrain.TerrainType] or millHillsIcons.TERRAIN_GRASS_HILLS;
                end
                -- Atlas glyphs have their own alpha. Color only the text
                -- so the inline icon renderer cannot dim the glyphs twice.
                options[#options+1] = millForecastProduction .. millForecastColor .. value
                    .. '[ENDCOLOR] ' .. terrainIcon;
                lines[#lines+1] = A.PreviewLine(rule,amount,count,true);
            end
        end
    end
    if #options == 0 then return '', ''; end
    return table.concat(options,'  ' .. millForecastColor .. '/[ENDCOLOR]  '), table.concat(lines,'[NEWLINE]');
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

function A.EdgeIcon(districtType, center, neighbor, city, direction, showMillPotential)
    local fallback='';
    for _,rule in ipairs(A.ByDistrict[districtType] or {}) do
        local first,last = A.Bounds(rule);
        -- In placement, preview every Water Mill river face on the candidate
        -- tile. The river belongs to the face even if the far bank is unowned.
        -- A.Preview still checks the functioning Mill for amounts and tooltips.
        local plannedRiver = showMillPotential and rule.ID == 'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER';
        if first <= 1 and last >= 1 and (plannedRiver or (A.Eligible(rule,city,city:GetOwner())
            and (not (rule.MustOwn == true or rule.MustOwn == 1) or neighbor:GetOwner() == city:GetOwner()))) then
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
                if icon and icon~='' then return icon; end
                -- A generic source (for example a river edge) must not hide a
                -- matching material/Sales object just because its rule sorts first.
                icon=info and info.ArtdefOverlayEntry;
                if fallback=='' and icon and icon~='' then fallback=icon; end
            end
        end
    end
    return fallback;
end
