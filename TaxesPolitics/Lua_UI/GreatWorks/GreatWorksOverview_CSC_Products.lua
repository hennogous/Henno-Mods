-- ===========================================================================
-- Civ Supply Chains - Product Great Works Overview support
--
-- Loaded through GreatWorksOverview.lua wildcard include (GreatWorksOverview_*).
-- Do not include GreatWorksOverview here; this file wraps functions that already
-- exist in that context.
--
-- CSC ships a lean Product substrate without requiring the Monopolies &
-- Corporations game mode. Firaxis Product UI handling is hard-coded to
-- GREATWORKOBJECT_PRODUCT / GREATWORKSLOT_PRODUCT, so CSC products use the
-- vanilla object/slot identity and this file provides the Product-aware display
-- support normally imported only by M&C.
-- ===========================================================================

print("GreatWorksOverview_CSC_Products: loaded");

g_DEFAULT_GREAT_WORKS_ICONS["GREATWORKSLOT_PRODUCT"] = "ICON_GREATWORKOBJECT_PRODUCT";

local SIZE_GREAT_WORK_ICON:number = 64;

local YIELD_FONT_ICONS:table = {
    YIELD_FOOD          = "[ICON_FoodLarge]",
    YIELD_PRODUCTION    = "[ICON_ProductionLarge]",
    YIELD_GOLD          = "[ICON_GoldLarge]",
    YIELD_SCIENCE       = "[ICON_ScienceLarge]",
    YIELD_CULTURE       = "[ICON_CultureLarge]",
    YIELD_FAITH         = "[ICON_FaithLarge]",
};

local m_ResourceTypeMap:table = {};

local BASE_CSC_GetGreatWorkIcon = GetGreatWorkIcon;
local BASE_CSC_GetGreatWorkTooltip = GetGreatWorkTooltip;
local BASE_CSC_Initialize = Initialize;

-- ===========================================================================
local function IsProductGreatWork(greatWorkInfo:table)
    return greatWorkInfo ~= nil and greatWorkInfo.GreatWorkObjectType == "GREATWORKOBJECT_PRODUCT";
end

-- Firaxis Product naming convention:
--   GREATWORK_PRODUCT_<RESOURCE_SUFFIX>_<N>
-- maps to:
--   RESOURCE_<RESOURCE_SUFFIX>
-- CSC intentionally follows it, e.g. GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_1
-- -> RESOURCE_CSC_BAKERS_SPECIALTY.
local function GetProductSuffix(greatWorkType:string)
    if greatWorkType == nil then
        return nil;
    end

    local suffix:string = greatWorkType:gsub("^GREATWORK_PRODUCT_", "");
    suffix = suffix:gsub("_%d+$", "");
    return suffix;
end

local function GetProductResourceType(greatWorkType:string)
    local suffix:string = GetProductSuffix(greatWorkType);
    if suffix == nil or suffix == "" then
        return nil;
    end
    return "RESOURCE_" .. suffix;
end

local function FindProductIconName(greatWorkInfo:table)
    local suffix:string = GetProductSuffix(greatWorkInfo.GreatWorkType);
    local resourceType:string = GetProductResourceType(greatWorkInfo.GreatWorkType);

    local candidates:table = {};
    if suffix ~= nil and suffix ~= "" then
        -- Firaxis M&C convention; CSC defines ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_* aliases.
        table.insert(candidates, "ICON_MONOPOLIES_AND_CORPS_RESOURCE_" .. suffix);
    end
    if resourceType ~= nil then
        table.insert(candidates, "ICON_" .. resourceType);
        table.insert(candidates, resourceType);
    end
    table.insert(candidates, "ICON_GREATWORKOBJECT_PRODUCT");

    for _, iconName in ipairs(candidates) do
        local textureOffsetX:number, textureOffsetY:number, textureSheet:string = IconManager:FindIconAtlas(iconName, SIZE_GREAT_WORK_ICON);
        if textureSheet ~= nil and textureSheet ~= "" then
            return iconName, textureOffsetX, textureOffsetY, textureSheet;
        end
    end

    return nil, nil, nil, nil;
end

local function GetProductCreatorName(resourceType:string)
    if resourceType == nil then
        return Locale.Lookup("LOC_GREATWORKOBJECT_PRODUCT");
    end

    if Game.GetEconomicManager ~= nil then
        local economicManager:table = Game.GetEconomicManager();
        if economicManager ~= nil and economicManager.GetCorporationName ~= nil then
            for resourceIndex, mappedResourceType in ipairs(m_ResourceTypeMap) do
                if mappedResourceType == resourceType then
                    local corporationName:string = economicManager:GetCorporationName(Game.GetLocalPlayer(), resourceIndex);
                    if corporationName ~= nil and corporationName ~= "" then
                        return corporationName;
                    end
                    break;
                end
            end
        end
    end

    local resourceName:string = Locale.Lookup("LOC_" .. resourceType .. "_NAME");
    local corporationTypeName:string = Locale.Lookup("LOC_IMPROVEMENT_CORPORATION_TYPE_NAME", resourceName);
    if corporationTypeName ~= nil and corporationTypeName ~= "LOC_IMPROVEMENT_CORPORATION_TYPE_NAME" then
        return corporationTypeName;
    end

    local corporationName:string = Locale.Lookup("LOC_IMPROVEMENT_CORPORATION_NAME", resourceName);
    if corporationName ~= nil and corporationName ~= "LOC_IMPROVEMENT_CORPORATION_NAME" then
        return corporationName;
    end

    return resourceName;
end

local function AppendProductEffectText(tooltip:string, resourceType:string)
    if resourceType == nil or GameInfo.ResourceIndustries == nil then
        return tooltip;
    end

    for row in GameInfo.ResourceIndustries() do
        if row.PrimaryKey == resourceType or row.ResourceType == resourceType then
            local effectTextKey:string = row.ResourceEffectText or row.ResourceEffectTExt;
            if effectTextKey ~= nil then
                return tooltip .. Locale.Lookup(effectTextKey);
            end
            break;
        end
    end

    return tooltip;
end

-- ===========================================================================
function GetGreatWorkIcon(greatWorkInfo:table)
    if IsProductGreatWork(greatWorkInfo) then
        local iconName:string, textureOffsetX:number, textureOffsetY:number, textureSheet:string = FindProductIconName(greatWorkInfo);
        if textureSheet == nil or textureSheet == "" then
            UI.DataError("CSC Product icon lookup failed in GetGreatWorkIcon for greatWork=" .. tostring(greatWorkInfo.GreatWorkType));
        end
        return textureOffsetX, textureOffsetY, textureSheet;
    end

    return BASE_CSC_GetGreatWorkIcon(greatWorkInfo);
end

-- ===========================================================================
function GetGreatWorkTooltip(pCityBldgs:table, greatWorkIndex:number, greatWorkType:number, pBuildingInfo:table)
    local greatWorkInfo:table = GameInfo.GreatWorks[greatWorkType];
    if not IsProductGreatWork(greatWorkInfo) then
        return BASE_CSC_GetGreatWorkTooltip(pCityBldgs, greatWorkIndex, greatWorkType, pBuildingInfo);
    end

    local resourceType:string = GetProductResourceType(greatWorkInfo.GreatWorkType);
    local creatorName:string = GetProductCreatorName(resourceType);

    local instanceInfo:table = Game.GetGreatWorkDataFromIndex(greatWorkIndex);
    local staticInfo:table = greatWorkInfo;
    if instanceInfo ~= nil and instanceInfo.GreatWorkType ~= nil and GameInfo.GreatWorks[instanceInfo.GreatWorkType] ~= nil then
        staticInfo = GameInfo.GreatWorks[instanceInfo.GreatWorkType];
    end

    local name:string = Locale.Lookup(staticInfo.Name);
    local turnCreated:number = 0;
    if instanceInfo ~= nil and instanceInfo.TurnCreated ~= nil then
        turnCreated = instanceInfo.TurnCreated;
    end
    local dateCreated:string = Calendar.MakeDateStr(turnCreated, GameConfiguration.GetCalendarType(), GameConfiguration.GetGameSpeedType(), false);

    local tourism:number = staticInfo.Tourism or 0;
    local yields:string = tostring(tourism) .. " [ICON_TourismLarge] " .. Locale.Lookup("LOC_PEDIA_CONCEPTS_PAGEGROUP_TOURISM_NAME");
    for row in GameInfo.GreatWork_YieldChanges() do
        if row.GreatWorkType == staticInfo.GreatWorkType then
            local yieldIcon:string = YIELD_FONT_ICONS[row.YieldType] or ("[ICON_" .. row.YieldType .. "]");
            yields = tostring(row.YieldChange) .. " " .. yieldIcon .. " " .. Locale.Lookup("LOC_" .. row.YieldType .. "_NAME") .. ", " .. yields;
            break;
        end
    end

    local typeName:string = Locale.Lookup("LOC_" .. staticInfo.GreatWorkObjectType);
    local tooltip:string = Locale.Lookup("LOC_GREAT_WORKS_TOOLTIP", name, typeName, creatorName, dateCreated, yields);

    return AppendProductEffectText(tooltip, resourceType);
end

-- ===========================================================================
function Initialize()
    BASE_CSC_Initialize();

    m_ResourceTypeMap = {};
    for row in GameInfo.Resources() do
        m_ResourceTypeMap[row.Index] = row.ResourceType;
    end
end
