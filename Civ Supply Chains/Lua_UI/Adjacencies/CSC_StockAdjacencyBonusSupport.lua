-- Firaxis UI support with optional numeric CSC additions in the yield formatter.
-- ===========================================================================
--	Functions related to finding the yield bonuses (district) plots are given
--	due to some attribute of an adjacent plot.
-- ==========================================================================
include( "Civ6Common" );		-- GetYieldString()
include( "MapEnums" );


-- Badge-only correction: the native adjacency query returns base adjacency,
-- while district yield output includes active policy percentages. Cache only
-- database definitions; query policy state on every redraw so swapping cards or
-- viewing another player's city cannot retain a previous player's multiplier.
-- Restrict discovery to direct player-district adjacency effects and simple
-- district-type gates used by vanilla. Unknown/conditional mod effects are left
-- to the engine instead of guessing at their activation. CSC flat policy returns
-- are added AFTER this percentage, since their evaluator already doubles them.
local m_AdjacencyPolicyBonuses = {};
do
    local function Arguments(tableName, idColumn)
        local result = {};
        for row in GameInfo[tableName]() do
            local id = row[idColumn];
            result[id] = result[id] or {};
            result[id][row.Name] = row.Value;
        end
        return result;
    end
    if GameInfo.PolicyModifiers and GameInfo.Modifiers and GameInfo.DynamicModifiers
        and GameInfo.ModifierArguments and GameInfo.RequirementSets
        and GameInfo.RequirementSetRequirements and GameInfo.Requirements
        and GameInfo.RequirementArguments then
        local arguments = Arguments('ModifierArguments', 'ModifierId');
        local requirementArguments = Arguments('RequirementArguments', 'RequirementId');
        local districtGates, members = {}, {};
        for member in GameInfo.RequirementSetRequirements() do
            local list = members[member.RequirementSetId] or {};
            list[#list + 1] = member.RequirementId;
            members[member.RequirementSetId] = list;
        end
        for set in GameInfo.RequirementSets() do
            local list = members[set.RequirementSetId] or {};
            local count, districtType = #list, nil;
            if count == 1 then
                local requirement = GameInfo.Requirements[list[1]];
                local args = requirementArguments[list[1]] or {};
                if requirement and requirement.RequirementType == 'REQUIREMENT_DISTRICT_TYPE_MATCHES'
                    and not (requirement.Inverse == true or requirement.Inverse == 1) then
                    districtType = args.DistrictType;
                end
            end
            -- A single type test has identical ALL/ANY semantics. Multi-test
            -- sets may include population, buildings or other unsupported gates.
            if count == 1 then districtGates[set.RequirementSetId] = districtType; end
        end
        local seen = {};
        for link in GameInfo.PolicyModifiers() do
            local modifier = GameInfo.Modifiers[link.ModifierId];
            local dynamic = modifier and GameInfo.DynamicModifiers[modifier.ModifierType];
            local args = arguments[link.ModifierId] or {};
            local policy = GameInfo.Policies[link.PolicyType];
            local districtType = modifier and districtGates[modifier.SubjectRequirementSetId];
            local identity = link.PolicyType .. ':' .. link.ModifierId;
            if policy and dynamic and dynamic.EffectType == 'EFFECT_ADJUST_DISTRICT_YIELD_MODIFIER'
                and dynamic.CollectionType == 'COLLECTION_PLAYER_DISTRICTS'
                and not modifier.OwnerRequirementSetId
                and (not modifier.SubjectRequirementSetId or districtType)
                and args.YieldType and tonumber(args.Amount) and not seen[identity] then
                seen[identity] = true;
                m_AdjacencyPolicyBonuses[#m_AdjacencyPolicyBonuses + 1] = {
                    PolicyIndex=policy.Index, DistrictType=districtType,
                    YieldType=args.YieldType, Amount=tonumber(args.Amount)
                };
            end
        end
    end
end

local function PolicyAdjustedAdjacency(amount, districtType, yieldType, playerID)
    local player = Players[playerID];
    local culture = player and player:GetCulture();
    if not culture then return amount; end
    local baseType = districtType;
    if GameInfo.DistrictReplaces then
        for replacement in GameInfo.DistrictReplaces() do
            if replacement.CivUniqueDistrictType == districtType then
                baseType = replacement.ReplacesDistrictType;
                break;
            end
        end
    end
    local percent = 0;
    for _,bonus in ipairs(m_AdjacencyPolicyBonuses) do
        if bonus.YieldType == yieldType
            and (not bonus.DistrictType or bonus.DistrictType == districtType or bonus.DistrictType == baseType)
            and culture:IsPolicyActive(bonus.PolicyIndex) then
            percent = percent + bonus.Amount;
        end
    end
    -- Policy adjacency percentages stack additively, not multiplicatively.
    return amount * (100 + percent) / 100;
end

-- ===========================================================================
--	CONSTANTS
-- ===========================================================================
local START_INDEX	:number = GameInfo.Yields["YIELD_FOOD"].Index;
local END_INDEX		:number = GameInfo.Yields["YIELD_FAITH"].Index;


local m_DistrictsWithAdjacencyBonuses	:table = {};
for row in GameInfo.District_Adjacencies() do
	local districtIndex = GameInfo.Districts[row.DistrictType].Index;
	if (districtIndex ~= nil) then
		m_DistrictsWithAdjacencyBonuses[districtIndex] = true;
	end
end

-- ===========================================================================
--	Obtain the artdef string name that shows an adjacency icon for a plot type.
--	RETURNS: Artdef string name for an icon to display between hexes
-- ===========================================================================
function GetAdjacentIconArtdefName( targetDistrictType:string, plot:table, pkCity:table, direction:number )

	local eDistrict = GameInfo.Districts[targetDistrictType].Index;
	local eType = -1;
	local iSubType = -1;
	eType, iSubType = plot:GetAdjacencyBonusType(Game.GetLocalPlayer(), pkCity:GetID(), eDistrict, direction);

	if eType == AdjacencyBonusTypes.NO_ADJACENCY then
		return "";
	elseif eType == AdjacencyBonusTypes.ADJACENCY_DISTRICT then
		return "Districts_Generic_District";
	elseif eType == AdjacencyBonusTypes.ADJACENCY_FEATURE then
		if iSubType == g_FEATURE_JUNGLE then
			return "Terrain_Jungle";
		elseif iSubType == g_FEATURE_FOREST then
			return "Terrain_Forest";
		elseif iSubType == g_FEATURE_GEOTHERMAL_FISSURE then
			return "Terrain_Generic_Resource";
		elseif iSubType == g_FEATURE_REEF then
			return "Terrain_Reef";
		end
	elseif eType == AdjacencyBonusTypes.ADJACENCY_IMPROVEMENT then
		if iSubType == 1 then
			return "Improvements_Farm";
		elseif iSubType == 2 then
			return "Improvement_Mine";
		elseif iSubType == 3 then
			return "Improvement_Quarry";
		end
	elseif eType == AdjacencyBonusTypes.ADJACENCY_NATURAL_WONDER then
		return "Wonders_Natural_Wonder";
	elseif eType == AdjacencyBonusTypes.ADJACENCY_RESOURCE then
		return "Terrain_Generic_Resource";
	elseif eType == AdjacencyBonusTypes.ADJACENCY_RESOURCE_CLASS then
		return "Terrain_Generic_Resource_Class";
	elseif eType == AdjacencyBonusTypes.ADJACENCY_RIVER then
		return "Terrain_River";
	elseif eType == AdjacencyBonusTypes.ADJACENCY_SEA_RESOURCE then
		return "Terrain_Sea";
	elseif eType == AdjacencyBonusTypes.ADJACENCY_TERRAIN then
		if iSubType == g_TERRAIN_TYPE_TUNDRA or iSubType == g_TERRAIN_TYPE_TUNDRA_HILLS then
			return "Terrain_Tundra";
		elseif iSubType == g_TERRAIN_TYPE_DESERT or iSubType == g_TERRAIN_TYPE_DESERT_HILLS then
			return "Terrain_Desert";
		elseif iSubType == g_TERRAIN_TYPE_COAST then -- TODO or TERRAIN_TYPE_OCEAN?
			return "Terrain_Coast";
		else -- TODO specify mountain and have an error asset if no match?
			return "Terrain_Mountain";
		end
	elseif eType == AdjacencyBonusTypes.ADJACENCY_WONDER then
		return "Generic_Wonder";
	end
	
	-- Default to generic icon
	return "Terrain_Generic_Resource";
end

-- ===========================================================================
--	Obtain a table of adjacency bonuses
-- ===========================================================================
function AddAdjacentPlotBonuses( kPlot:table, districtType:string, pSelectedCity:table, tCurrentBonuses:table )
	local adjacentPlotBonuses:table = {};
	local x		:number = kPlot:GetX();
	local y		:number = kPlot:GetY();

	for _,direction in pairs(DirectionTypes) do			
		if direction ~= DirectionTypes.NO_DIRECTION and direction ~= DirectionTypes.NUM_DIRECTION_TYPES then
			local adjacentPlot	:table= Map.GetAdjacentPlot( x, y, direction);
			if adjacentPlot ~= nil then
				local artdefIconName:string = GetAdjacentIconArtdefName( districtType, adjacentPlot, pSelectedCity, direction );
			
				if artdefIconName ~= nil and artdefIconName ~= "" then

		
					local districtViewInfo:table = GetViewPlotInfo( adjacentPlot, tCurrentBonuses );
					local oppositeDirection :number = -1;
					if direction == DirectionTypes.DIRECTION_NORTHEAST	then oppositeDirection = DirectionTypes.DIRECTION_SOUTHWEST; end
					if direction == DirectionTypes.DIRECTION_EAST		then oppositeDirection = DirectionTypes.DIRECTION_WEST; end
					if direction == DirectionTypes.DIRECTION_SOUTHEAST	then oppositeDirection = DirectionTypes.DIRECTION_NORTHWEST; end
					if direction == DirectionTypes.DIRECTION_SOUTHWEST	then oppositeDirection = DirectionTypes.DIRECTION_NORTHEAST; end
					if direction == DirectionTypes.DIRECTION_WEST		then oppositeDirection = DirectionTypes.DIRECTION_EAST; end
					if direction == DirectionTypes.DIRECTION_NORTHWEST	then oppositeDirection = DirectionTypes.DIRECTION_SOUTHEAST; end

					table.insert( districtViewInfo.adjacent, {
						direction	= oppositeDirection,
						iconArtdef	= artdefIconName,
						inBonus		= false,
						outBonus	= true					
						}
					);				

					adjacentPlotBonuses[adjacentPlot:GetIndex()] = districtViewInfo;
				end
			end		
		end
	end

	return adjacentPlotBonuses;
end

-- ===========================================================================
--	Adds a plot and all the adjacencent plots, unless already added.
--	ARGS:		kPlot,			gamecore plot object
--	ARGS:		kExistingTable,	table of existing plot into to check if we already have info about this plot
--	RETURNS:	A new/updated plotInfo table
-- ===========================================================================
function GetViewPlotInfo( kPlot:table, kExistingTable:table )
	local plotId	:number = kPlot:GetIndex();
	local plotInfo	:table = kExistingTable[plotId];
	if plotInfo == nil then 
		plotInfo = {
			index	= plotId, 
			x		= kPlot:GetX(), 
			y		= kPlot:GetY(),
			adjacent= {},				-- adjacent edge bonuses
			selectable = false,			-- change state with mouse over?
			purchasable = false
		}; 
	end
	--print( "   plot: " .. plotInfo.x .. "," .. plotInfo.y..": " .. tostring(plotInfo.iconArtdef) );
	return plotInfo;
end

-- ===========================================================================
--	RETURNS: true or false, indicating whether this placement option should be 
--	shown when the player can purchase the plot.
-- ===========================================================================
function IsShownIfPlotPurchaseable(eDistrict:number, pkCity:table, plot:table)
	local yieldBonus:string = GetAdjacentYieldBonusString(eDistrict, pkCity, plot);

	-- If we would get a bonus for placing here, then show it as an option
	if (yieldBonus ~= nil and yieldBonus ~= "") then
		return true;
	end

	-- If there are no adjacency bonuses for this district type (and so no bonuses to be had), then show it as an option
	if (m_DistrictsWithAdjacencyBonuses[eDistrict] == nil or m_DistrictsWithAdjacencyBonuses[eDistrict] == false) then
		return true;
	end

	return false;
end

-- ===========================================================================
--	RETURNS: "" if no bonus or...
--		1. Text with the bonuses for a district if added to the given plot,
--		2. parameter is a tooltip with detailed bonus informatin
--		3. NIL if can be used or a string explaining what needs to be done for plot to be usable.
-- ===========================================================================
-- Optional CSC additions are numeric base yields, evaluated by the shared core.
-- Omitting them preserves Firaxis' original callers and housing behavior.
function GetAdjacentYieldBonusString( eDistrict:number, pkCity:table, plot:table, additionalYields:table )

	local tooltipText	:string = "";
	local totalBonuses	:string = "";
	local requiredText	:string = "";
	local isFirstEntry	:boolean = true;	
	local iconString:string = "";
	local district = GameInfo.Districts[eDistrict];
	local isRepeatable = district.OnePerCity == false;
	local hasAdditionalYields = additionalYields ~= nil and next(additionalYields) ~= nil;
	
	-- Repeatable districts use the native Neighborhood tooltip path. Their CSC
	-- yields still need formatting even though this path skips native yield reads.
	if isRepeatable then

		tooltipText, requiredText = plot:GetAdjacencyBonusTooltip(Game.GetLocalPlayer(), pkCity:GetID(), eDistrict, 0);
	end

	if not isRepeatable or hasAdditionalYields then
		for iBonusYield = START_INDEX, END_INDEX do
			local iBonus:number = 0;
			if not isRepeatable then
				iBonus = plot:GetAdjacencyYield(Game.GetLocalPlayer(), pkCity:GetID(), eDistrict, iBonusYield);
			end
			if (iBonus > 0) then
				local yieldTooltip, yieldRequireText = plot:GetAdjacencyBonusTooltip(Game.GetLocalPlayer(), pkCity:GetID(), eDistrict, iBonusYield);
				if tooltipText == "" then
					tooltipText = yieldTooltip;
				else
					tooltipText = tooltipText .. "[NEWLINE]" .. yieldTooltip;
				end

				-- There is always only one requiredText so just replace it
				requiredText = yieldRequireText;

			end

			local yieldType:string = GameInfo.Yields[iBonusYield].YieldType;
			-- CSC supplies numeric additions here so cancellation and negative totals
			-- are resolved before the shared icon formatter renders the final amount.
			iBonus = PolicyAdjustedAdjacency(iBonus, district.DistrictType, yieldType, pkCity:GetOwner());
			iBonus = iBonus + (additionalYields and additionalYields[yieldType] or 0);
			if (iBonus > 0 or (additionalYields ~= nil and iBonus ~= 0)) then
				local yieldString:string = GetYieldString( yieldType, iBonus );
				if iconString == "" then
					iconString = yieldString;
				else
					iconString = iconString .. "[NEWLINE]" .. yieldString;
				end
			end
		end
			
	end
	if requiredText ~= nil and string.len(requiredText) < 1 then
		requiredText = nil;
	end

	-- Housing effects from districts (both one-per and normal)
	local iAppeal = plot:GetAppeal();
	local iBaseHousing = district.Housing;

	-- Default is Mbanza case (no appeal change)
	local iTotalHousing:number = iBaseHousing;

	for row in GameInfo.AppealHousingChanges() do
		if (row.DistrictType == district.DistrictType) then
			local iMinimumValue = row.MinimumValue;
			local iAppealChange = row.AppealChange;
			local szDescription = row.Description;
			if (iAppeal >= iMinimumValue) then
				iTotalHousing = iBaseHousing + iAppealChange;
				local housingTooltip = Locale.Lookup("LOC_DISTRICT_ZONE_NEIGHBORHOOD_TOOLTIP", iTotalHousing, szDescription);
				-- Keep the breakdown when the badge also shows native yields.
				-- Repeatable districts already use the native Housing tooltip path.
				if not isRepeatable and hasAdditionalYields and iconString ~= "" and tooltipText and tooltipText ~= "" then
					housingTooltip = housingTooltip .. "[NEWLINE]" .. tooltipText;
				end
				tooltipText = housingTooltip;
				break;
			end
		end
	end

	if iTotalHousing ~= 0 then
		-- Flat Housing (for example, a Rural Community) may have no native
		-- tooltip. Supply its amount before CSC appends any adjacency details.
		if not tooltipText or tooltipText == "" then
			tooltipText = Locale.Lookup("LOC_TYPE_TRAIT_HOUSING", iTotalHousing);
		end
		local housingString = "[ICON_Housing]+" .. tostring(iTotalHousing);
		-- Housing leads the badge. Keep yield rows when CSC contributed to it.
		if hasAdditionalYields and iconString ~= "" then
			housingString = housingString .. "[NEWLINE]" .. iconString;
		end
		iconString = housingString;
	end

	return iconString, tooltipText, requiredText;
end



-- ===========================================================================
--	Obtain all the owned (or could be owned) plots of a city.
--	ARGS: pCity, the city to obtain plots from
--	RETURNS: table of plot indices
-- ===========================================================================
function GetCityRelatedPlotIndexes( pCity:table )
	
	print("GetCityRelatedPlotIndexes() isn't updated with the latest purchaed plot if one was just purchased and this is being called on Event.CityMadePurchase !");
	local plots:table = Map.GetCityPlots():GetPurchasedPlots( pCity );

	-- Plots that arent't owned, but could be (and hence, could be a great spot for that district!)
	local tParameters :table = {};
	tParameters[CityCommandTypes.PARAM_PLOT_PURCHASE] = UI.GetInterfaceModeParameter(CityCommandTypes.PARAM_PLOT_PURCHASE);
	local tResults = CityManager.GetCommandTargets( pCity, CityCommandTypes.PURCHASE, tParameters );
	if (tResults[CityCommandResults.PLOTS] ~= nil and table.count(tResults[CityCommandResults.PLOTS]) ~= 0) then
		for _,plotId in pairs(tResults[CityCommandResults.PLOTS]) do
			table.insert(plots, plotId);
		end
	end

	return plots;
end

-- ===========================================================================
--	Same as above but specific to districts and works despite the cache not having an updated value.
-- ===========================================================================
function GetCityRelatedPlotIndexesDistrictsAlternative( pCity:table, districtHash:number )

	local district		:table = GameInfo.Districts[districtHash];
	local plots			:table = {};
	local tParameters	:table = {};

	tParameters[CityOperationTypes.PARAM_DISTRICT_TYPE] = districtHash;


	-- Available to place plots.
	local tResults :table = CityManager.GetOperationTargets( pCity, CityOperationTypes.BUILD, tParameters );
	if (tResults[CityOperationResults.PLOTS] ~= nil and table.count(tResults[CityOperationResults.PLOTS]) ~= 0) then			
		local kPlots:table = tResults[CityOperationResults.PLOTS];			
		for i, plotId in ipairs(kPlots) do
			table.insert(plots, plotId);
		end	
	end	

	--[[
	-- antonjs: Removing blocked plots from the UI display. Now that district placement can automatically remove features, resources, and improvements,
	-- as long as the player has the tech, there is not much need to show blocked plots and they end up being confusing.
	-- Plots that eventually can hold a district but are blocked by some required operation.
	if (tResults[CityOperationResults.BLOCKED_PLOTS] ~= nil and table.count(tResults[CityOperationResults.BLOCKED_PLOTS]) ~= 0) then			
		for _, plotId in ipairs(tResults[CityOperationResults.BLOCKED_PLOTS]) do
			table.insert(plots, plotId);		
		end
	end
	--]]

	-- Plots that arent't owned, but if they were, would give a bonus.
	tParameters = {};
	tParameters[CityCommandTypes.PARAM_PLOT_PURCHASE] = UI.GetInterfaceModeParameter(CityCommandTypes.PARAM_PLOT_PURCHASE);
	local tResults = CityManager.GetCommandTargets( pCity, CityCommandTypes.PURCHASE, tParameters );
	if (tResults[CityCommandResults.PLOTS] ~= nil and table.count(tResults[CityCommandResults.PLOTS]) ~= 0) then
		for _,plotId in pairs(tResults[CityCommandResults.PLOTS]) do
			
			local kPlot	:table = Map.GetPlotByIndex(plotId);	
			if kPlot:CanHaveDistrict(district.Index, pCity:GetOwner(), pCity:GetID()) then
				local isValid :boolean = IsShownIfPlotPurchaseable(district.Index, pCity, kPlot);
				if isValid then
					table.insert(plots, plotId);
				end
			end
			
		end
	end
	return plots;
end

-- ===========================================================================
--	Same as above but specific to wonders and works despite the cache not having an updated value.
-- ===========================================================================
function GetCityRelatedPlotIndexesWondersAlternative( pCity:table, buildingHash:number )

	local building		:table = GameInfo.Buildings[buildingHash];
	local plots			:table = {};
	local tParameters	:table = {};

	tParameters[CityOperationTypes.PARAM_BUILDING_TYPE] = buildingHash;


	-- Available to place plots.
	local tResults :table = CityManager.GetOperationTargets( pCity, CityOperationTypes.BUILD, tParameters );
	if (tResults[CityOperationResults.PLOTS] ~= nil and table.count(tResults[CityOperationResults.PLOTS]) ~= 0) then			
		local kPlots:table = tResults[CityOperationResults.PLOTS];			
		for i, plotId in ipairs(kPlots) do
			table.insert(plots, plotId);
		end	
	end	

	-- Plots that aren't owned, but if they were, would give a bonus.
	tParameters = {};
	tParameters[CityCommandTypes.PARAM_PLOT_PURCHASE] = UI.GetInterfaceModeParameter(CityCommandTypes.PARAM_PLOT_PURCHASE);
	local tResults = CityManager.GetCommandTargets( pCity, CityCommandTypes.PURCHASE, tParameters );
	if (tResults[CityCommandResults.PLOTS] ~= nil and table.count(tResults[CityCommandResults.PLOTS]) ~= 0) then
		for _,plotId in pairs(tResults[CityCommandResults.PLOTS]) do
			
			local kPlot	:table = Map.GetPlotByIndex(plotId);	
			if kPlot:CanHaveWonder(building.Index, pCity:GetOwner(), pCity:GetID()) then
				table.insert(plots, plotId);
			end
			
		end
	end
	return plots;
end
