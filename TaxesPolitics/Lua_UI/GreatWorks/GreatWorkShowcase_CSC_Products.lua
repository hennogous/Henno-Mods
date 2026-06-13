-- ===========================================================================
-- Civ Supply Chains - Product Great Work Showcase support
--
-- Loaded through GreatWorkShowcase.lua wildcard include (GreatWorkShowcase_*).
-- Do not include GreatWorkShowcase here; this file wraps functions that already
-- exist in that context.
-- ===========================================================================

print("GreatWorkShowcase_CSC_Products: loaded");

local BASE_CSC_HandleCustomGreatWorkTypes = HandleCustomGreatWorkTypes;
local BASE_CSC_Initialize = Initialize;

local PADDING_BANNER:number = 120;
local SIZE_BANNER_MIN:number = 506;
local SIZE_GREAT_WORK_IMAGE:number = 256;

local m_ResourceTypeMap:table = {};

-- ===========================================================================
local function IsProductGreatWork(greatWorkInfo:table)
    return greatWorkInfo ~= nil and greatWorkInfo.GreatWorkObjectType == "GREATWORKOBJECT_PRODUCT";
end

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
        table.insert(candidates, "ICON_MONOPOLIES_AND_CORPS_RESOURCE_" .. suffix);
    end
    if resourceType ~= nil then
        table.insert(candidates, "ICON_" .. resourceType);
        table.insert(candidates, resourceType);
    end
    table.insert(candidates, "ICON_GREATWORKOBJECT_PRODUCT");

    for _, iconName in ipairs(candidates) do
        local textureOffsetX:number, textureOffsetY:number, textureSheet:string = IconManager:FindIconAtlas(iconName, SIZE_GREAT_WORK_IMAGE);
        if textureSheet ~= nil and textureSheet ~= "" then
            return iconName;
        end
    end

    return "ICON_GREATWORKOBJECT_PRODUCT";
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

-- ===========================================================================
function HandleCustomGreatWorkTypes(greatWorkType:string, greatWorkIndex:number)
    local greatWorkInfo:table = GameInfo.GreatWorks[greatWorkType];
    if not IsProductGreatWork(greatWorkInfo) then
        return BASE_CSC_HandleCustomGreatWorkTypes(greatWorkType, greatWorkIndex);
    end

    local resourceType:string = GetProductResourceType(greatWorkInfo.GreatWorkType);
    local icon:string = FindProductIconName(greatWorkInfo);

    Controls.GreatWorkImage:SetOffsetY(0);
    Controls.GreatWorkImage:SetIcon(icon, SIZE_GREAT_WORK_IMAGE);

    Controls.GreatWorkName:SetText(Locale.ToUpper(greatWorkInfo.Name));
    local nameSize:number = Controls.GreatWorkName:GetSizeX() + PADDING_BANNER;
    local bannerSize:number = math.max(nameSize, SIZE_BANNER_MIN);
    Controls.GreatWorkBanner:SetSizeX(bannerSize);
    Controls.GreatWorkBanner:SetHide(false);

    Controls.CreatedBy:SetText(Locale.Lookup("LOC_GREAT_WORKS_CREATED_BY", GetProductCreatorName(resourceType)));

    return true;
end

-- ===========================================================================
function Initialize()
    BASE_CSC_Initialize();

    m_ResourceTypeMap = {};
    for row in GameInfo.Resources() do
        m_ResourceTypeMap[row.Index] = row.ResourceType;
    end
end
