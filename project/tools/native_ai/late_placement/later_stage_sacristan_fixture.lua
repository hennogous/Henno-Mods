-- Isolate Divine Right beside a working Base supplier and Holy Site. The
-- turn-55 fixture precedes the natural research choice. The turn-100 fixture
-- resets an earlier unlock for a controlled diagnostic. Both copies receive
-- the same missing buildings. Native AI owns selection and completion.
local pid, cityId, quarterPlot, templePlot = 5, 131073, 2038, 1965
local player = assert(Players[pid])
local city = assert(CityManager.GetCity(pid, cityId))
local quarter, venue = assert(Map.GetPlotByIndex(quarterPlot)), assert(Map.GetPlotByIndex(templePlot))
local customer = assert(Cities.GetPlotPurchaseCity(venue))
local civic = assert(GameInfo.Civics.CIVIC_DIVINE_RIGHT)
local culture = player:GetCulture()
local owned = culture:HasCivic(civic.Index)
local temple = assert(GameInfo.Buildings.BUILDING_TEMPLE)
local tailor = assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TAILOR)
local workshop = assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP)
local natural = naturalSacristan ~= nil
if mode == 'before' or mode == 'progress' then
    -- Progress is exposed by the UI reader. Gameplay owns the civic mutation
    -- below and has no progress getter in this binary.
    local progress = culture:GetCulturalProgress(civic.Index)
    local current = culture:GetProgressingCivic()
    if natural then
        assert(not owned and current ~= civic.Index, 'The natural civic needs a pending research decision')
    elseif mode == 'progress' then
        assert(progress == 0, 'Civic progress reset was not observed')
    end
    local marker = mode == 'before' and 'BEFORE' or 'PROGRESS'
    print('CSC_MILESTONE_SACRISTAN_' .. marker, Game.GetCurrentGameTurn(), pid, civic.Index, tostring(owned),
        progress, current)
    return
end
local function active(owner, definition, location)
    local buildings = owner:GetBuildings()
    return buildings:HasBuilding(definition.Index) and not buildings:IsPillaged(definition.Index)
        and buildings:GetBuildingLocation(definition.Index) == location
end
local function customerWorks()
    if active(customer, temple, templePlot) then return true end
    for row in GameInfo.BuildingReplaces() do
        if row.ReplacesBuildingType == temple.BuildingType
            and active(customer, assert(GameInfo.Buildings[row.CivUniqueBuildingType]), templePlot) then return true end
    end
    return false
end
if mode == 'setup' then
    assert(Game.GetCurrentGameTurn() == fixtureTurn and not player:IsHuman())
    assert(customer:GetOwner() == pid
        and Map.GetPlotDistance(quarter:GetX(), quarter:GetY(), venue:GetX(), venue:GetY()) == 1)
    local district = assert(city:GetDistricts():GetDistrict(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index))
    assert(district:IsComplete() and not district:IsPillaged()
        and district:GetX() == quarter:GetX() and district:GetY() == quarter:GetY())
    local holy = assert(customer:GetDistricts():GetDistrict(GameInfo.Districts.DISTRICT_HOLY_SITE.Index))
    assert(holy:IsComplete() and not holy:IsPillaged()
        and holy:GetX() == venue:GetX() and holy:GetY() == venue:GetY())
    local profile
    for _, candidate in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles()) do
        if candidate.key == 'TAILORS' then profile = candidate; break end
    end
    local supplied = false
    for _, item in ipairs(CSC_AI_QuarterPlacement.ReadSuppliers(player, quarter, assert(profile)).base) do
        supplied = supplied or item.working
    end
    assert(supplied, 'No working Base supplier in the archived Tailors chain')
    if natural then
        assert(not owned, 'Divine Right was already owned in the natural fixture')
        if not customerWorks() then
            assert(not customer:GetBuildings():HasBuilding(temple.Index), 'Fixture only adds a missing Temple')
            customer:GetBuildQueue():CreateBuilding(temple.Index, templePlot)
        end
    else
        -- Clearing ownership skips the completion broadcast. The Tailor
        -- must be absent so its attachment is created against reset facts.
        assert(not city:GetBuildings():HasBuilding(tailor.Index), 'The fixture needs the archived missing Tailor')
        assert(type(culture.SetCivic) == 'function' and type(culture.SetCulturalProgress) == 'function',
            'Gameplay civic setters are unavailable')
        culture:SetCivic(civic.Index, false)
        culture:SetCulturalProgress(civic.Index, 0)
        assert(not culture:HasCivic(civic.Index), 'The controlled civic ownership reset was not observed')
    end
    assert(customerWorks(), 'Fixture Temple unavailable')
    for _, building in ipairs({workshop, tailor}) do
        if not active(city, building, quarterPlot) then
            assert(not city:GetBuildings():HasBuilding(building.Index), 'Producer already exists but is damaged')
            city:GetBuildQueue():CreateBuilding(building.Index, quarterPlot)
        end
        assert(active(city, building, quarterPlot), 'Producer preparation failed')
    end
    if natural then
        -- Leave normal research and all other CSC credits present in both
        -- arms. Remove only the real Service adapter's added credit for this
        -- player and civic from the control packet.
        local adapter = assert(CSC_AI_EconomyAdapters)
        local offerServices = assert(adapter.ServiceResearch)
        local key = 'civic:' .. civic.Index
        adapter.ServiceResearch = function(snapshot, research)
            if snapshot.id ~= pid then return offerServices(snapshot, research) end
            local existing = research[key]
            local preserved
            if existing then
                preserved = {}
                for field, value in pairs(existing) do preserved[field] = value end
            end
            offerServices(snapshot, research)
            local quote = research[key]
            if quote and quote.serviceQ8 then
                print('CSC_MILESTONE_SACRISTAN_BID', Game.GetCurrentGameTurn(), pid, civic.Index,
                    quote.serviceQ8, quote.serviceChains, tostring(naturalSacristan))
                if not naturalSacristan then research[key] = preserved end
            end
        end
    end
    print('CSC_MILESTONE_SACRISTAN_SETUP', pid, cityId, quarterPlot, templePlot, civic.Index, tostring(owned))
    -- The UI Service watcher reports native district IDs. Record the
    -- physical plot mapping before play so its recipient can be joined.
    print('CSC_MILESTONE_SACRISTAN_DISTRICTS', district:GetID(), holy:GetID(), customer:GetID())
else
    assert(mode == 'outcome')
    print('CSC_MILESTONE_SACRISTAN_OUTCOME', Game.GetCurrentGameTurn(), pid, cityId, tostring(owned),
        tostring(active(city, tailor, quarterPlot)), tostring(customerWorks()),
        city:GetProperty('CSC_TAILORS_STAGE_3_EFFECT_FAITH') or 0)
end
