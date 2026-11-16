-- Shared gameplay channel definitions -> nominal one-route UI amounts.
-- Formatting stays in BTS. Eligibility and actual native payout bits are shared
-- with the live scanner and AI; optional Gold is read from loaded bindings.
include("CSC_TradeRouteCore")
include("CSC_TradeRouteFacts")
local R=CSC_TradeRouteCore
local definitions,problem=R.ReadDefinitions(GameInfo)
if not definitions then print('CSC_ROUTE_PREVIEW_UNAVAILABLE '..tostring(problem));return end
local reader=CSC_TradeRouteFacts.New(GameInfo,definitions)
local function cities(route)
    if not route then return nil,nil end
    local origin=Players[route.OriginCityPlayer]
    local destination=Players[route.DestinationCityPlayer]
    return reader.City(origin and origin:GetCities():FindID(route.OriginCityID)),
        reader.City(destination and destination:GetCities():FindID(route.DestinationCityID))
end
function CSC_BTS_GetBakersTradeRouteState(route)
    local origin,destination=cities(route)
    return R.FamilyStates(definitions,origin,destination,'BAKERS')
end
function CSC_BTS_GetTailorsTradeRouteState(route)
    local origin,destination=cities(route)
    return R.FamilyStates(definitions,origin,destination,'TAILORS')
end
function CSC_BTS_GetQuarterImportAmenityAmount(route)
    local origin,destination=cities(route)
    return R.Nominal(definitions,origin,destination,'ORIGIN').AMENITY or 0
end

local function CSC_BTS_AppendTooltip(existingTooltip, newLine)
	if newLine == nil or newLine == "" then
		return existingTooltip or "";
	end

	if existingTooltip ~= nil and existingTooltip ~= "" then
		return existingTooltip .. "[NEWLINE]" .. newLine;
	end

	return newLine;
end

local function CSC_BTS_PrependTooltip(existingTooltip, newLine)
	if newLine == nil or newLine == "" then
		return existingTooltip or "";
	end

	if existingTooltip ~= nil and existingTooltip ~= "" then
		return newLine .. "[NEWLINE]" .. existingTooltip;
	end

	return newLine;
end

local function CSC_BTS_FormatSignedAmount(amount)
	if amount == nil then
		return "0";
	end

	local text=amount==math.floor(amount)and string.format('%.0f',amount)or tostring(amount);
	if amount > 0 then
		return "+" .. text;
	end

	return text;
end

local function CSC_BTS_FormatQuarterYieldTooltip(amount, iconString, yieldName, directionName)
	return CSC_BTS_FormatSignedAmount(amount) .. " " .. iconString .. " " .. Locale.Lookup(yieldName)
		.. " from Quarter " .. directionName .. ".";
end

local function CSC_BTS_FormatQuarterAmenityTooltip(amount)
	local amenityText = "Amenity";
	if amount ~= 1 then
		amenityText = "Amenities";
	end

	return CSC_BTS_FormatSignedAmount(amount) .. " [ICON_Amenities] " .. amenityText .. " from Quarter imports.";
end

local function CSC_BTS_GetLastPositiveYieldIndex(yieldValues)
	if yieldValues == nil then return FOOD_INDEX; end

	for yieldIndex = FAITH_INDEX, FOOD_INDEX, -1 do
		if (yieldValues[yieldIndex] or 0) > 0 then
			return yieldIndex;
		end
	end

	return FOOD_INDEX;
end

-- The array indices are BTS's six standard UI columns, not another list
-- of Quarter partners/rates. Nominal per-route display is separate from the
-- complete before/after counter arithmetic used by AI forecasts.
function CSC_BTS_ApplyBakersTradeRoutePreview(route,yields,tooltips,buildTooltip,target)
    if not yields then return end
    local origin,destination=cities(route)
    local recipient=target=='Origin'and'ORIGIN'or'DESTINATION'
    local amounts=R.Nominal(definitions,origin,destination,recipient)
    local columns={
        {FOOD_INDEX,'YIELD_FOOD','[ICON_Food]','LOC_YIELD_FOOD_NAME'},
        {PRODUCTION_INDEX,'YIELD_PRODUCTION','[ICON_Production]','LOC_YIELD_PRODUCTION_NAME'},
        {GOLD_INDEX,'YIELD_GOLD','[ICON_Gold]','LOC_YIELD_GOLD_NAME'},
        {SCIENCE_INDEX,'YIELD_SCIENCE','[ICON_Science]','LOC_YIELD_SCIENCE_NAME'},
        {CULTURE_INDEX,'YIELD_CULTURE','[ICON_Culture]','LOC_YIELD_CULTURE_NAME'},
        {FAITH_INDEX,'YIELD_FAITH','[ICON_Faith]','LOC_YIELD_FAITH_NAME'}}
    for _,column in ipairs(columns)do
        local amount=amounts[column[2]]or 0
        if amount~=0 then
            yields[column[1]]=(yields[column[1]]or 0)+amount
            if buildTooltip and tooltips then tooltips[column[1]]=CSC_BTS_PrependTooltip(tooltips[column[1]],
                CSC_BTS_FormatQuarterYieldTooltip(amount,column[3],column[4],recipient=='ORIGIN'and'imports'or'exports'))end
        end
    end
    if buildTooltip and tooltips and(amounts.AMENITY or 0)~=0 then
        local index=CSC_BTS_GetLastPositiveYieldIndex(yields)
        tooltips[index]=CSC_BTS_AppendTooltip(tooltips[index],CSC_BTS_FormatQuarterAmenityTooltip(amounts.AMENITY))
    end
end
