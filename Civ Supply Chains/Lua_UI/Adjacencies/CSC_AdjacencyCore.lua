-- CSC adjacency evaluation shared by gameplay and placement UI.
-- Independently implemented from the behavior of Ruivo's Modular Adjacency
-- Bonuses and Henno's fork. Specific-Wonder behavior also informed by Zegangani.
-- No external MAB files, globals or events are required.
CSC_Adjacency = {};
local A = CSC_Adjacency;
A.Rules = {};
A.ByDistrict = {};
A.Tags = {};
A.Sources = {};
A.Bits = {1,2,4,8,16,32,64,128,256,512};
A.Limit = 1023;

local function flag(value) return value == true or value == 1; end
local function bool(value) return value and 1 or 0; end
local function call(object, method, ...)
    if object and object[method] then return object[method](object, ...); end
    return nil;
end
local function row(tableName, index)
    return GameInfo[tableName] and GameInfo[tableName][index];
end
local function typeOf(tableName, index, field)
    local definition = row(tableName, index);
    return definition and definition[field];
end
local function districtAt(plot)
    local player = Players[plot:GetOwner()];
    return player and player:GetDistricts():FindID(plot:GetDistrictID());
end
local function unitsAt(plot) return Units.GetUnitsInPlot(plot) or {}; end
local function size(items)
    local count = 0;
    for _ in pairs(items or {}) do count = count + 1; end
    return count;
end

function A.Truncate(number)
    return number < 0 and math.ceil(number) or math.floor(number);
end

function A.Bounds(rule)
    local first = tonumber(rule.MinRings) or 1;
    local last = tonumber(rule.MaxRings) or tonumber(rule.Rings) or 1;
    if last == 0 then return 0,0; end -- The explicit placement-tile case.
    return first, math.max(first,last);
end

function A.PlotsInBand(center, first, last)
    -- Visit each plot once, even on wrapped maps where several paths reach it.
    -- The caller chooses whether the placement tile itself belongs to the band.
    if not center then return {}; end
    if last == 0 then return {center}; end
    local queue = {center};
    local seen = {[center:GetIndex()] = true};
    local result = {};
    local cursor = 1;
    if first == 0 then result[1] = center; end
    while cursor <= #queue do
        local current = queue[cursor];
        cursor = cursor + 1;
        for _,neighbor in ipairs(Map.GetAdjacentPlots(current:GetX(),current:GetY())) do
            local index = neighbor:GetIndex();
            if not seen[index] then
                seen[index] = true;
                local distance = Map.GetPlotDistance(center:GetX(),center:GetY(),neighbor:GetX(),neighbor:GetY());
                if distance >= first and distance <= last then result[#result+1] = neighbor; end
                if distance < last then queue[#queue+1] = neighbor; end
            end
        end
    end
    return result;
end

function A.ResourceVisible(playerID, resource)
    local definition = row('Resources',resource);
    local player = Players[playerID];
    if not definition or not player then return false; end
    -- Query discovery on every evaluation: do not cache a player's knowledge.
    if definition.PrereqTech then
        local tech = row('Technologies',definition.PrereqTech);
        if not tech or not player:GetTechs():HasTech(tech.Index) then return false; end
    elseif definition.PrereqCivic then
        local civic = row('Civics',definition.PrereqCivic);
        if not civic or not player:GetCulture():HasCivic(civic.Index) then return false; end
    end
    return true;
end

function A.HasTag(tag, objectType)
    return A.Tags[tag] and A.Tags[tag][objectType] == true;
end

local function trait(playerID, wanted)
    local configuration = PlayerConfigurations[playerID];
    if not configuration then return false; end
    local civilization = configuration:GetCivilizationTypeName();
    local leader = configuration:GetLeaderTypeName();
    for item in GameInfo.CivilizationTraits() do
        if item.CivilizationType == civilization and item.TraitType == wanted then return true; end
    end
    for item in GameInfo.LeaderTraits() do
        if item.LeaderType == leader and item.TraitType == wanted then return true; end
    end
    return false;
end

local function cityHasBuilding(city, buildingType)
    local building = row('Buildings',buildingType);
    return city and building and city:GetBuildings():HasBuilding(building.Index) or false;
end

function A.Eligible(rule, city, playerID)
    -- Check the source that owns the modifier before counting nearby objects.
    -- Collection scope decides whether a qualifying building must be in this
    -- city, anywhere in this player's empire, or in any living major's empire.
    local player = Players[playerID];
    if not player then return false; end
    if rule.Only == 'OnlyHuman' and not player:IsHuman() then return false; end
    if rule.Only == 'OnlyAI' and player:IsHuman() then return false; end
    if rule.TraitType and not flag(rule.DistrictModifiers) and not trait(playerID,rule.TraitType) then return false; end
    local owner = rule.ModifierOwner or 'DistrictModifiers';
    local key = rule.WhoIsTheOwner;
    if owner == 'DistrictModifiers' then return true; end
    if owner == 'TraitModifiers' then return trait(playerID,key); end
    if owner == 'BuildingModifiers' then
        if rule.CollectionType == 'COLLECTION_CITY_DISTRICTS' then return cityHasBuilding(city,key); end
        if rule.CollectionType == 'COLLECTION_ALL_DISTRICTS' then
            for _,other in ipairs(PlayerManager.GetAliveMajors()) do
                for _,otherCity in other:GetCities():Members() do
                    if cityHasBuilding(otherCity,key) then return true; end
                end
            end
            return false;
        end
        for _,otherCity in player:GetCities():Members() do
            if cityHasBuilding(otherCity,key) then return true; end
        end
        return false;
    end
    if owner == 'TechnologyModifiers' then
        local tech = row('Technologies',key);
        return tech and player:GetTechs():HasTech(tech.Index) or false;
    end
    if owner == 'CivicModifiers' then
        local civic = row('Civics',key);
        return civic and player:GetCulture():HasCivic(civic.Index) or false;
    end
    if owner == 'PolicyModifiers' then
        local policy = row('Policies',key);
        return policy and player:GetCulture():IsPolicyActive(policy.Index) or false;
    end
    if owner == 'GovernmentModifiers' then
        return typeOf('Governments',player:GetCulture():GetCurrentGovernment(),'GovernmentType') == key;
    end
    -- These sources are not used by CSC today. The engine modifiers supply their
    -- actual gates; their UI capability varies between the game's Lua contexts.
    if owner == 'GovernorPromotionModifiers' then
        local governors = player:GetGovernors();
        local assigned = call(governors,'GetAssignedGovernor',city);
        if rule.CollectionType == 'COLLECTION_CITY_DISTRICTS' then
            return assigned and call(assigned,'HasPromotion',DB.MakeHash(key)) or false;
        end
        if governors.GetGovernorList then
            local present,list = governors:GetGovernorList();
            if present then
                for _,governor in ipairs(list or {}) do
                    if governor:HasPromotion(DB.MakeHash(key)) then return true; end
                end
            end
            return false;
        end
        return true;
    end
    if owner == 'BeliefModifiers' then
        local religion = city and city:GetReligion();
        local religionID = religion and religion:GetMajorityReligion();
        local belief = row('Beliefs',key);
        local religions = Game.GetReligion():GetReligions();
        for _,entry in ipairs(religions or {}) do
            if entry.Religion == religionID then
                for _,beliefID in ipairs(entry.Beliefs or {}) do
                    if belief and beliefID == belief.Index then return true; end
                end
            end
        end
    end
    return false;
end

-- Source entries describe a per-plot quantity and whether the fork's MustOwn
-- option applied to that source. UI-only ring variants historically ignored it.
local function source(name, quantity, ownership)
    A.Sources[name] = {Quantity=quantity, Ownership=ownership ~= false};
end
local function ordinary(name, quantity)
    source('FROM_RINGS_' .. name,quantity);
    source('FROM_ADJACENT_' .. name,quantity,false);
end
local function matching(tableName, getter, field)
    return function(plot,key) return bool(typeOf(tableName,plot[getter](plot),field) == key); end;
end
ordinary('ROUTE',function(p) return p:GetRouteType()+1; end);
ordinary('WORKER',function(p) return p:GetWorkerCount(); end);
ordinary('UNIT',function(p) return p:GetUnitCount(); end);
ordinary('DISTRICT_AND_WONDER',function(p) return bool(p:GetDistrictType() >= 0); end);
ordinary('DISTRICT',function(p)
    local kind = typeOf('Districts',p:GetDistrictType(),'DistrictType');
    return bool(kind and kind ~= 'DISTRICT_WONDER');
end);
ordinary('LAKE',function(p) return bool(p:IsLake()); end);
ordinary('WATER_LEVEL',function(p) return p:IsFreshWater() and 3 or (p:IsCoastalLand() and 1 or 0); end);
ordinary('RESOURCE',function(p,_,context) return bool(A.ResourceVisible(context.PlayerID,p:GetResourceType())); end);
ordinary('WONDERS',function(p) return bool(p:GetWonderType() >= 0 and p:IsWonderComplete()); end);
source('FROM_RINGS_NATIONALPARK',function(p) return bool(p:IsNationalPark()); end);
source('FROM_RINGS_CAO_ROUTE',matching('Routes','GetRouteType','RouteType'));
source('FROM_RINGS_CAO_IMPROVEMENT',function(p,key)
    return bool(not p:IsImprovementPillaged() and typeOf('Improvements',p:GetImprovementType(),'ImprovementType') == key);
end);
source('FROM_RINGS_CAO_FEATURE',matching('Features','GetFeatureType','FeatureType'));
source('FROM_RINGS_CAO_TERRAIN',matching('Terrains','GetTerrainType','TerrainType'));
source('FROM_RINGS_CAO_DISTRICT',matching('Districts','GetDistrictType','DistrictType'));
source('FROM_RINGS_TYPETAG_DISTRICT',function(p,key)
    local tag = row('Tags',key);
    if not tag or tag.Vocabulary ~= 'DISTRICT_CLASS' then return 0; end
    return bool(A.HasTag(key,typeOf('Districts',p:GetDistrictType(),'DistrictType')));
end);
source('FROM_RINGS_TYPETAG_RESOURCE',function(p,key,context)
    local tag = row('Tags',key);
    if not tag or tag.Vocabulary ~= 'RESOURCE_CLASS' then return 0; end
    local resource = row('Resources',p:GetResourceType());
    return bool(resource and A.ResourceVisible(context.PlayerID,p:GetResourceType()) and A.HasTag(key,resource.ResourceType));
end);
source('FROM_RINGS_CAO_RESOURCE',function(p,key,context)
    return bool(A.ResourceVisible(context.PlayerID,p:GetResourceType()) and typeOf('Resources',p:GetResourceType(),'ResourceType') == key);
end);
source('FROM_RINGS_CAO_RESOURCE_CLASS',function(p,key,context)
    return bool(A.ResourceVisible(context.PlayerID,p:GetResourceType()) and typeOf('Resources',p:GetResourceType(),'ResourceClassType') == key);
end);
local terrainMethods = {
    IsMountain=true,IsHills=true,IsFlatlands=true,IsWater=true,IsShallowWater=true,
    IsLake=true,IsCanyon=true,IsCoastalLand=true,IsRiverCrossing=true,IsOpenGround=true,IsRoughGround=true
};
source('FROM_RINGS_CAO_TERRAIN_SETS',function(p,key) return bool(terrainMethods[key] and call(p,key)); end);
source('FROM_RINGS_CAO_UNIT',function(p,key)
    local count = 0;
    for _,unit in ipairs(unitsAt(p)) do
        if typeOf('Units',unit:GetType(),'UnitType') == key then count=count+1; end
    end
    return count;
end);
source('FROM_RINGS_SPECIFIC_WONDER',function(p,key,context)
    return bool(p:GetOwner() == context.PlayerID and p:IsWonderComplete()
        and typeOf('Buildings',p:GetWonderType(),'BuildingType') == key);
end);

local function property(hashed, district)
    return function(p,key)
        local object = district and districtAt(p) or p;
        if hashed then key = DB.MakeHash(key); end
        -- Native GetProperty can return no values for an absent key. Assign
        -- first so tonumber always receives one argument in either Lua context.
        local value = call(object,'GetProperty',key);
        return tonumber(value) or 0;
    end;
end
source('FROM_PLOT_PROPERTY',property(false,false),false);
source('FROM_PLOT_PROPERTY_HASHED',property(true,false),false);
source('FROM_DISTRICT_PROPERTY',property(false,true),false);
source('FROM_DISTRICT_PROPERTY_HASHED',property(true,true),false);
source('FROM_RINGS_PLOT_PROPERTY',property(false,false));
source('FROM_RINGS_PLOT_PROPERTY_HASHED',property(true,false));
source('FROM_RINGS_DISTRICT_PROPERTY',property(false,true),false);
source('FROM_RINGS_DISTRICT_PROPERTY_HASHED',property(true,true),false);

local function hitpoints(p,defense,measure)
    local district = districtAt(p);
    if not district then return 0; end
    local maximum = district:GetMaxDamage(defense);
    local damage = district:GetDamage(defense);
    if measure == 'MAX_HP' then return maximum; end
    if measure == 'DAMAGE' then return damage; end
    return maximum - damage;
end
for _,kind in ipairs({'DISTRICT','WALL'}) do
    for _,measure in ipairs({'MAX_HP','DAMAGE','REMAIN_HP'}) do
        local defense = kind == 'DISTRICT' and DefenseTypes.DISTRICT_GARRISON or DefenseTypes.DISTRICT_OUTER;
        source('FROM_RINGS_' .. kind .. '_' .. measure,function(p) return hitpoints(p,defense,measure); end);
    end
end
source('FROM_RINGS_DEFENSE_STRENGTH',function(p)
    return math.floor((call(districtAt(p),'GetDefenseStrength') or 0) + 0.5);
end);
source('FROM_RINGS_DISTRICTS_CAO_YIELD',function(p,key)
    local yield = row('Yields',key);
    return yield and (call(districtAt(p),'GetYield',yield.Index) or 0) or 0;
end);
source('FROM_UI_RINGS_UNIT_LEVELS',function(p)
    local count = 0;
    for _,unit in ipairs(unitsAt(p)) do
        local experience = unit:GetExperience();
        local level = call(experience,'GetLevel');
        -- GetLevel is UI-only. The bundled UI context exposes this read to
        -- gameplay; gameplay remains the sole writer of adjacency properties.
        local bridge = ExposedMembers and ExposedMembers.CSC_Adjacency;
        if level == nil and bridge and bridge.GetUnitLevel then
            level = bridge.GetUnitLevel(unit:GetOwner(),unit:GetID());
        end
        -- Before UI initialization there is no bridge yet. A later synchronized
        -- gameplay refresh can read it; local loading events do not write state.
        count=count+(level or 0);
    end
    return count;
end,false);
source('FROM_UI_RINGS_APPEAL',function(p) return p:GetAppeal(); end,false);
source('FROM_UI_RINGS_CAO_YIELD',function(p,key)
    local yield = row('Yields',key);
    return yield and p:GetYield(yield.Index) or 0;
end,false);
local function airSlots(p)
    local total = call(districtAt(p),'GetAirSlots') or 0;
    local improvement = row('Improvements',p:GetImprovementType());
    total = total + (improvement and improvement.AirSlots or 0);
    for _,unit in ipairs(unitsAt(p)) do total=total+(call(unit,'GetAirSlots') or 0); end
    return total;
end
local function airUnits(p)
    local total = size(call(p,'GetAirUnits'));
    local function count(object)
        if not object or not object.GetAirUnits then return 0; end
        local present,items = object:GetAirUnits();
        return present and size(items) or 0;
    end
    total = total + count(districtAt(p));
    for _,unit in ipairs(unitsAt(p)) do total = total + count(unit); end
    return total;
end
source('FROM_UI_RINGS_AIR_SLOTS',airSlots,false);
source('FROM_UI_RINGS_AIR_UNITS',airUnits,false);
source('FROM_UI_RINGS_SURPLUS_AIR_SLOTS',function(p) return airSlots(p)-airUnits(p); end,false);
source('FROM_RIVER_CROSSING',function(p) return p:GetRiverCrossingCount(); end,false);
source('FROM_UNCONDITIONAL_BONUS',function() return 1; end,false);

function A.Count(rule, center, city, playerID)
    -- Return source quantity, before YieldChange multiplication or bit encoding.
    -- A source may contribute a quantity (workers, property value), not just 0/1.
    local entry = A.Sources[rule.AdjacencyType];
    assert(entry,'CSC adjacency: unsupported source ' .. tostring(rule.AdjacencyType));
    if not center then return 0; end
    playerID = playerID or (city and city:GetOwner()) or center:GetOwner();
    local first,last = A.Bounds(rule);
    if rule.AdjacencyType:find('FROM_ADJACENT_',1,true) == 1 then first,last=1,1; end
    local plots;
    if rule.AdjacencyType:find('RINGS',1,true) then plots=A.PlotsInBand(center,first,last);
    elseif rule.AdjacencyType:find('FROM_ADJACENT_',1,true) == 1 then plots=A.PlotsInBand(center,1,1);
    else plots={center}; end
    local total = 0;
    local context = {PlayerID=playerID,City=city};
    for _,plot in ipairs(plots) do
        if not entry.Ownership or not flag(rule.MustOwn) or plot:GetOwner() == playerID then
            total=total+(entry.Quantity(plot,rule.CustomAdjacentObject,context) or 0);
        end
    end
    -- The historical exact-Wonder extension returns presence, not a tile count.
    if rule.AdjacencyType == 'FROM_RINGS_SPECIFIC_WONDER' then total=math.min(total,1); end
    return math.max(total,0);
end

function A.Amount(rule, count)
    -- SQL has a fixed ten-bit magnitude ladder. Keep the unclamped amount for
    -- diagnostics, but use the encoded amount in both gameplay and previews.
    local raw = A.Truncate(count * rule.YieldChange);
    return math.max(-A.Limit,math.min(A.Limit,raw)),raw;
end

function A.Write(plot, rule, count)
    -- These names are the contract with CSC_AdjacencyModifiers.sql. Bits carry
    -- magnitude; SQL gives each bit modifier the sign of the rule's YieldChange.
    local amount,raw = A.Amount(rule,count);
    local key = 'CSC_ADJ_' .. rule.ID;
    local function set(name,value)
        if plot:GetProperty(name) ~= value then plot:SetProperty(name,value); end
    end
    set(key .. '_TOTAL',count);
    set(key .. '_ACTUAL_AMOUNT',raw);
    set(key .. '_ENCODED_AMOUNT',amount);
    local magnitude = math.abs(amount);
    for _,bit in ipairs(A.Bits) do set(key .. '_' .. bit,math.floor(magnitude/bit)%2); end
end

function A.Initialize()
    -- Cache database definitions only. Player knowledge, policies and map state
    -- are evaluated live; sorting rules also fixes gameplay property-write order.
    A.Rules={}; A.ByDistrict={}; A.Tags={}; A.Objects={}; A.SourceInfo={}; A.Providers={};
    for item in GameInfo.TypeTags() do
        A.Tags[item.Tag] = A.Tags[item.Tag] or {};
        A.Tags[item.Tag][item.Type] = true;
    end
    for item in GameInfo.CSC_AdjacencyObjects() do A.Objects[item.CustomAdjacentObject]=item; end
    for item in GameInfo.CSC_AdjacencySources() do A.SourceInfo[item.AdjacencyType]=item; end
    for item in GameInfo.CSC_AdjacencyProviders() do A.Providers[item.ProvideType]=item; end
    for item in GameInfo.CSC_AdjacencyRules() do
        assert(A.Sources[item.AdjacencyType],'Unsupported CSC adjacency source: ' .. item.AdjacencyType);
        assert(A.Providers[item.ProvideType],'Unsupported CSC adjacency provider: ' .. item.ProvideType);
        A.Rules[#A.Rules+1]=item;
        A.ByDistrict[item.DistrictType] = A.ByDistrict[item.DistrictType] or {};
        table.insert(A.ByDistrict[item.DistrictType],item);
    end
    table.sort(A.Rules,function(a,b) return a.ID<b.ID; end);
    for _,rules in pairs(A.ByDistrict) do table.sort(rules,function(a,b) return a.ID<b.ID; end); end
end
