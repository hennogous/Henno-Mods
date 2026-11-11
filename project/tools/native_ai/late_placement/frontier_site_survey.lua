-- Diagnostic only, in CSC_AI_BakersGameplay at an inactive saved boundary.
-- Reuse CSC's loaded relationships and supplier suitability; enumerate frontier
-- geometry independently of the owned BUILD target list. No CE packet, request,
-- treasury, ownership, research, production or autoplay mutation occurs here.
local P, A = assert(CSC_AI_QuarterPlacement), assert(CSC_Adjacency)
A.Initialize()
local function call(object, method, ...)
    if not object or type(object[method]) ~= 'function' then return nil, 'missing method: ' .. method end
    local ok, value = pcall(object[method], object, ...)
    if ok then return value end
    return nil, tostring(value)
end
local function json(value)
    local kind = type(value)
    if kind == 'nil' then return 'null' end
    if kind == 'number' or kind == 'boolean' then return tostring(value) end
    if kind == 'string' then
        return '"' .. value:gsub('\\', '\\\\'):gsub('"', '\\"'):gsub('\n', '\\n'):gsub('\r', '\\r'):gsub('\t', '\\t') .. '"'
    end
    assert(kind == 'table')
    local count, array, fields = 0, true, {}
    for key in pairs(value) do count = count + 1; array = array and type(key) == 'number' end
    array = array and count == #value
    if array then
        for _, item in ipairs(value) do fields[#fields + 1] = json(item) end
        return '[' .. table.concat(fields, ',') .. ']'
    end
    local keys = {}; for key in pairs(value) do keys[#keys + 1] = key end
    table.sort(keys)
    for _, key in ipairs(keys) do fields[#fields + 1] = json(key) .. ':' .. json(value[key]) end
    return '{' .. table.concat(fields, ',') .. '}'
end
local function visible(pid, plot)
    return PlayersVisibility[pid]:IsRevealed(plot:GetX(), plot:GetY())
end
local function mappedHosts(profile)
    local types, definitions = {}, {}
    for row in GameInfo.Districts() do
        if profile.customers[row.Index] or A.HasTag('CLASS_CSC_' .. profile.key .. '_SALES', row.DistrictType)
            or A.HasTag('CLASS_CSC_' .. profile.key .. '_GOODS_PROVIDER', row.DistrictType) then
            types[row.Index] = true
            if row.DistrictType ~= 'DISTRICT_CITY_CENTER' then definitions[#definitions + 1] = row end
        end
    end
    table.sort(definitions, function(a,b) return a.Index < b.Index end)
    return types, definitions
end
local function unlocked(player, row)
    local tech = row.PrereqTech and GameInfo.Technologies[row.PrereqTech]
    local civic = row.PrereqCivic and GameInfo.Civics[row.PrereqCivic]
    return (not row.PrereqTech or tech and player:GetTechs():HasTech(tech.Index))
        and (not row.PrereqCivic or civic and player:GetCulture():HasCivic(civic.Index)) or false
end
local result = {turn=Game.GetCurrentGameTurn(), mutationCommands=0, players={}, sites={}, supplierLeads={}}
local width, height = Map.GetGridSize(); result.width, result.height = width, height
for pid=0,63 do
    local player = Players[pid]
    if player and player:IsAlive() and player:IsMajor() and not player:IsHuman() then
        local treasury = player:GetTreasury()
        local goldYield,yieldError=call(treasury,'GetGoldYield')
        local maintenance,maintenanceError=call(treasury,'GetTotalMaintenance')
        local economy = {player=pid, treasuryGold=treasury:GetGoldBalance(),
            goldYield=goldYield, maintenance=maintenance,
            goldYieldAvailable=type(goldYield)=='number', maintenanceAvailable=type(maintenance)=='number',
            goldYieldError=yieldError, maintenanceError=maintenanceError,
            frontierPairs=0, knownBasePairs=0, cities=0}
        result.players[#result.players + 1] = economy
        for _, city in player:GetCities():Members() do
            economy.cities = economy.cities + 1
            local center = assert(Map.GetPlot(city:GetX(),city:GetY()))
            for _, profile in ipairs(P.StageTwoProfiles()) do
                local hostTypes, hostDefinitions = mappedHosts(profile)
                if not city:GetDistricts():HasDistrict(profile.district.Index) then
                    for _, site in ipairs(A.PlotsInBand(center,1,3)) do
                        if site:GetOwner() == -1 and visible(pid,site) and site:GetDistrictType() == -1
                            and site:CanHaveDistrict(profile.district.Index,pid,city:GetID()) then
                            local border = false
                            for _, n in ipairs(Map.GetAdjacentPlots(site:GetX(),site:GetY())) do
                                border = border or n:GetOwner() == pid
                            end
                            if border then
                                economy.frontierPairs = economy.frontierPairs + 1
                                local supply = P.ReadSuppliers(player,site,profile)
                                -- Keep discovery bounded to known owned supply.
                                -- Fog and unowned materials are not promoted to
                                -- credible supply by this diagnostic.
                                if #supply.base > 0 then
                                    economy.knownBasePairs = economy.knownBasePairs + 1
                                    local quote,quoteError=call(call(city,'GetGold'),'GetPlotPurchaseCost',site:GetIndex())
                                    local row = {player=pid,city=city:GetID(),cityName=city:GetName(),
                                        profile=profile.key,district=profile.district.Index,plot=site:GetIndex(),
                                        supply=supply,riverEdges=site:GetRiverCrossingCount(),hosts={},futureHosts={},
                                        quote=quote,quoteAvailable=type(quote)=='number',quoteError=quoteError,
                                        producers={},unrevealedNeighbors=0}
                                    local r = GameInfo.Resources[site:GetResourceType()]
                                    row.visibleResource = r and A.ResourceVisible(pid,r.Index) and r.ResourceType or nil
                                    for _, producer in ipairs(profile.producers) do
                                        row.producers[#row.producers+1] = {building=producer.BuildingType,
                                            unlockKnown=unlocked(player,producer),tech=producer.PrereqTech,civic=producer.PrereqCivic}
                                    end
                                    for _, n in ipairs(Map.GetAdjacentPlots(site:GetX(),site:GetY())) do
                                        if not visible(pid,n) then row.unrevealedNeighbors=row.unrevealedNeighbors+1
                                        elseif n:GetOwner() == pid then
                                            if hostTypes[n:GetDistrictType()] then
                                                row.hosts[#row.hosts+1] = {plot=n:GetIndex(),district=n:GetDistrictType(),
                                                    stageTwo=profile.customers[n:GetDistrictType()]~=nil}
                                            elseif n:GetDistrictType() == -1 and n:GetResourceType() == -1 then
                                                local owner=Cities.GetPlotPurchaseCity(n)
                                                if owner and owner:GetOwner()==pid then
                                                    for _, host in ipairs(hostDefinitions) do
                                                        -- Potential geometry ignores current population and
                                                        -- research admission, matching long-term site planning.
                                                        if not owner:GetDistricts():HasDistrict(host.Index)
                                                            and n:CanHaveDistrict(host.Index,pid,owner:GetID()) then
                                                            row.futureHosts[#row.futureHosts+1]={plot=n:GetIndex(),
                                                                city=owner:GetID(),district=host.Index}
                                                        end
                                                    end
                                                end
                                            end
                                        end
                                    end
                                    result.sites[#result.sites+1]=row
                                    assert(#result.sites<=512,'Frontier discovery evidence bound')
                                end
                            end
                        end
                    end
                else
                    for i=0,city:GetDistricts():GetNumDistricts()-1 do
                        local district=city:GetDistricts():GetDistrictByIndex(i)
                        if district and district:GetType()==profile.district.Index then
                            for _, n in ipairs(Map.GetAdjacentPlots(district:GetX(),district:GetY())) do
                                local resource=GameInfo.Resources[n:GetResourceType()]
                                if n:GetOwner()==-1 and visible(pid,n) and resource
                                    and A.ResourceVisible(pid,resource.Index) and A.HasTag(profile.base,resource.ResourceType) then
                                    -- A lead is not a proven legal improvement or a purchase.
                                    result.supplierLeads[#result.supplierLeads+1]={player=pid,city=city:GetID(),
                                        quarterPlot=district:GetY()*width+district:GetX(),profile=profile.key,
                                        quarterComplete=district:IsComplete(),quarterPillaged=district:IsPillaged(),
                                        plot=n:GetIndex(),resource=resource.ResourceType,
                                        quote=call(call(city,'GetGold'),'GetPlotPurchaseCost',n:GetIndex())}
                                    assert(#result.supplierLeads<=512,'Supplier discovery evidence bound')
                                end
                            end
                        end
                    end
                end
            end
        end
        assert(treasury:GetGoldBalance()==economy.treasuryGold,'Survey mutated treasury')
    end
end
print('CSC_FRONTIER_SURVEY=' .. json(result))
