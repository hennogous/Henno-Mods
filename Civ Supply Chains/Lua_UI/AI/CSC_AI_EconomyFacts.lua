-- Live-to-model boundary. Build one player/publication snapshot of definitions,
-- research costs, cities and completed district footprints. The economic model
-- consumes plain records; decision adapters never reinterpret these facts.
-- Static catalogues persist for the session. Ownership, production, research,
-- completion, supply and quotes never persist past this snapshot.
-- The customer-first reader reverses the generated gameplay partner graph and
-- exposes concrete customer/Quarter/material footprints to the policy adapter.
CSC_AI_EconomyFacts={}
local F=CSC_AI_EconomyFacts
local INF=math.huge
local catalogue
local customerQuarterMap
local districtParents
local routeCatalogue

function F.DistrictFamily(index)
    -- Definition-only lookup, shared by existing-footprint and customer-first
    -- readers. Resolve unique districts from the loaded replacement table;
    -- ownership/completion always comes from this publication's live inventory.
    local definition=GameInfo.Districts[index]
    if not definition then return nil end
    if not districtParents then
        districtParents={}
        if GameInfo.DistrictReplaces then for row in GameInfo.DistrictReplaces()do
            districtParents[row.CivUniqueDistrictType]=row.ReplacesDistrictType
        end end
    end
    return districtParents[definition.DistrictType]or definition.DistrictType
end

function F.CustomerQuarterMap()
    -- Reverse the GENERATED native partner graph, not a second authored list.
    -- CSC_AI_Connectors.sql unions gameplay transactions, sales/provider tags
    -- and unique replacements. Its AdjacentDistrict identifies the supplier
    -- Quarter; the standard district name identifies its Base/Spec class tags.
    -- Cache definitions only for this game session. No graph/capability means
    -- no speculative guidance; the ordinary native placement remains intact.
    if customerQuarterMap then return customerQuarterMap end
    if not GameInfo.District_Adjacencies or not GameInfo.Adjacency_YieldChanges
        or not GameInfo.Districts then return {} end
    local result,seen={},{}
    for link in GameInfo.District_Adjacencies()do
        local rule=GameInfo.Adjacency_YieldChanges[link.YieldChangeId]
        local customer=GameInfo.Districts[link.DistrictType]
        local quarter=rule and GameInfo.Districts[rule.AdjacentDistrict]
        local key=quarter and quarter.DistrictType:match('^DISTRICT_CSC_(.+)_QUARTER$')
        if key and customer and customer.DistrictType~='DISTRICT_CITY_CENTER'
            and customer.DistrictType~='DISTRICT_WONDER'
            and rule.YieldType=='YIELD_CSC_AI_PLACEMENT' and rule.YieldChange>0 then
            local identity=customer.Index..':'..quarter.Index
            if not seen[identity]then
                seen[identity]=true
                local row=result[customer.Index]or{definition=customer,quarters={}}
                result[customer.Index]=row
                row.quarters[#row.quarters+1]={key=key,district=quarter,
                    base='CLASS_CSC_'..key..'_BASE',specialty='CLASS_CSC_'..key..'_SPEC'}
            end
        end
    end
    for _,row in pairs(result)do table.sort(row.quarters,function(a,b)return a.district.Index<b.district.Index end)end
    customerQuarterMap=result;return result
end
local function numeric(value)return type(value)=='number'or type(value)=='integer'end
local function finite(value)return numeric(value)and value==value and value>=0 and value<INF end
local function number(object,name,...)
    if not object or type(object[name])~='function'then return nil end
    local ok,value=pcall(object[name],object,...)
    if ok and finite(value)then return value end
end
local function flag(v)return v==true or v==1 end
local function growthSurplus(city)
    if type(city.GetGrowth)~='function'then return nil end
    local growth=city:GetGrowth()
    if not growth or type(growth.GetFoodSurplus)~='function'then return nil end
    local ok,value=pcall(growth.GetFoodSurplus,growth)
    -- Starvation is a known zero positive-growth opportunity, not missing
    -- data. Keep signed surplus separate from nonnegative costs/IDs above.
    if ok and numeric(value)and value==value and value>-INF and value<INF then return math.max(0,value)end
end

-- Plot identity differs from costs/yields: native feature/resource/improvement
-- getters use -1 for absence. The nonnegative number() helper above would turn
-- an ordinary empty plot into unknown and disable its selected-site baseline.
-- Keep signed IDs explicit here; a missing/failed getter remains unknown.
function F.FootprintSignature(plot)
    local values={}
    for _,method in ipairs({'GetTerrainType','GetFeatureType','GetResourceType','GetImprovementType'})do
        if not plot or type(plot[method])~='function'then return '_'end
        local ok,value=pcall(plot[method],plot)
        if not ok or not numeric(value)or value~=value or value< -1
            or value>=INF or value~=math.floor(value)then return '_'end
        values[#values+1]=value
    end
    return table.concat(values,',')
end

local families={BAKERS={yield='YIELD_FOOD'},TAILORS={yield='YIELD_CULTURE'}}
local function definitions()
    if catalogue then return catalogue end
    local c={stages={},customers={},population={},transactions={},replacements={},tech={},civic={},amounts={},arguments={},prerequisites={},exclusives={}}
    c.materials={}
    c.citizenYields={};c.districtCitizenYields={}
    -- Ordinary specialist rates remain native gameplay definitions. Cache them
    -- once, then select only the Quarter's Stage2/3/4 producers at a live site;
    -- Service buildings cannot enter that subset. Intrinsic citizen Gold is
    -- independent of the optional transaction-Gold companion.
    for _,entry in ipairs({{GameInfo.Building_CitizenYieldChanges,c.citizenYields,'BuildingType'},
        {GameInfo.District_CitizenYieldChanges,c.districtCitizenYields,'DistrictType'}})do
        if entry[1]then for row in entry[1]()do
            local rates=entry[2][row[entry[3]]]or{};entry[2][row[entry[3]]]=rates
            rates[row.YieldType]=(rates[row.YieldType]or 0)+row.YieldChange
        end end
    end
    local fixedBindingRows,fixedLeaves={},{}
    if GameInfo.CSC_BuildingTransactionFixedBindings then for row in GameInfo.CSC_BuildingTransactionFixedBindings()do
        fixedBindingRows[#fixedBindingRows+1]=row;fixedLeaves[row.ChildModifierId]=true
    end end
    local materialBindings={}
    if GameInfo.CSC_MaterialTransactionBindings then for row in GameInfo.CSC_MaterialTransactionBindings()do
        materialBindings[row.TransactionId..':'..row.LegKey]=row
        fixedLeaves[row.ChildModifierId]=true
    end end
    for row in GameInfo.ModifierArguments()do
        -- Keep full arguments only for the small set of canonical fixed leaves.
        -- The loaded game can have tens of thousands of unrelated arguments;
        -- retaining their nested tables would add no placement information.
        if fixedLeaves[row.ModifierId]then
            c.arguments[row.ModifierId]=c.arguments[row.ModifierId]or{}
            c.arguments[row.ModifierId][row.Name]=row.Value
        end
        if row.Name=='Amount'then c.amounts[row.ModifierId]=tonumber(row.Value)end
    end
    for row in GameInfo.BuildingPrereqs()do
        c.prerequisites[row.Building]=c.prerequisites[row.Building]or{}
        table.insert(c.prerequisites[row.Building],row.PrereqBuilding)
    end
    for row in GameInfo.MutuallyExclusiveBuildings()do
        c.exclusives[row.Building]=c.exclusives[row.Building]or{}
        table.insert(c.exclusives[row.Building],row.MutuallyExclusiveBuilding)
    end
    for row in GameInfo.CSC_QuarterFlowBuildings()do
        local p=c.stages[row.QuarterKey]or{};c.stages[row.QuarterKey]=p
        p[row.Stage]=p[row.Stage]or{}
        p[row.Stage][#p[row.Stage]+1]=assert(GameInfo.Buildings[row.BuildingType])
    end
    if GameInfo.CSC_BuildingTransactions and GameInfo.CSC_BuildingTransactionYields then
        c.canonical=true
        local outputs,bindings={},{}
        for _,row in ipairs(fixedBindingRows)do
            bindings[row.TransactionId..':'..row.LegKey]=row
        end
        for row in GameInfo.CSC_BuildingTransactionYields()do
            outputs[row.TransactionId]=outputs[row.TransactionId]or{}
            local binding=bindings[row.TransactionId..':'..row.LegKey]
            outputs[row.TransactionId][#outputs[row.TransactionId]+1]={key=row.LegKey,
                recipient=row.Recipient,yield=row.YieldType,amount=row.AmountPerUnit,property=row.AmountProperty,
                ownerSide=binding and binding.OwnerSide,
                requiresOtherBuilding=binding and binding.BuildingRequirementId~=nil,
                nativeLeaf=binding and binding.ChildModifierId}
        end
        for row in GameInfo.CSC_BuildingTransactions()do
            -- Plain records cross into the pure ledger. Yield, quantity, payout
            -- property and functioning gates all come from the gameplay contract.
            c.transactions[row.SourceBuildingType..':'..row.PartnerBuildingType]={id=row.TransactionId,
                source=row.SourceBuildingType,partner=row.PartnerBuildingType,
                quarter=row.QuarterKey,spatial=row.SpatialRule,kind=row.QuantityKind,amount=row.QuantityAmount,step=row.PopulationStep,
                partnerDistrictMustFunction=flag(row.PartnerDistrictMustFunction),legs=outputs[row.TransactionId]or{}}
        end
    end
    if GameInfo.CSC_MaterialTransactions and GameInfo.CSC_MaterialTransactionYields then
        c.materialCanonical=true
        local outputs,hosts={},{}
        if GameInfo.CSC_MaterialTransactionInputHosts then for row in GameInfo.CSC_MaterialTransactionInputHosts()do
            local key=row.TransactionId..':'..row.LegKey
            hosts[key]=hosts[key]or{};hosts[key][row.ImprovementType]=true
        end end
        for row in GameInfo.CSC_MaterialTransactionYields()do
            local key=row.TransactionId..':'..row.LegKey
            local binding=materialBindings[key]
            outputs[row.TransactionId]=outputs[row.TransactionId]or{}
            table.insert(outputs[row.TransactionId],{key=row.LegKey,recipient=row.Recipient,
                yield=row.YieldType,amount=row.Amount,scope=row.ImprovementScope,improvement=row.ImprovementType,
                hosts=hosts[key]or{},nativeLeaf=binding and binding.ChildModifierId})
        end
        for row in GameInfo.CSC_MaterialTransactions()do
            c.materials[row.TransactionId]={id=row.TransactionId,quarter=row.QuarterKey,
                producer=row.ProducerBuildingType,tag=row.MaterialClass,legs=outputs[row.TransactionId]or{}}
        end
    end
    c.improvementJobs={}
    if GameInfo.Improvement_ValidResources then for row in GameInfo.Improvement_ValidResources()do
        local list=c.improvementJobs[row.ResourceType]or{};c.improvementJobs[row.ResourceType]=list
        local definition=GameInfo.Improvements[row.ImprovementType]
        if definition then list[#list+1]=definition end
    end end
    for _,list in pairs(c.improvementJobs)do table.sort(list,function(a,b)return a.Index<b.Index end)end
    local customerSeen={}
    local function customer(key,district,building,stage)
        local stamp=table.concat({key,district,building,stage},':')
        if customerSeen[stamp]then return end
        customerSeen[stamp]=true
        local p=c.customers[key]or{};c.customers[key]=p
        p[#p+1]={QuarterKey=key,DistrictType=district,BuildingType=building,ProducerStage=stage}
    end
    for row in GameInfo.CSC_QuarterCustomerBuildings()do
        customer(row.QuarterKey,row.DistrictType,row.BuildingType,row.ProducerStage)
    end
    if GameInfo.CSC_Stage3CustomerTransactions then
        for row in GameInfo.CSC_Stage3CustomerTransactions()do
            c.population[row.SellerBuildingType..':'..row.CustomerBuildingType]=row
            -- Stage3 was moved out of the Stage2/4 venue registry. Reading its
            -- amounts alone left Market/Temple absent from the actual customer
            -- list. Union both gameplay sources here, once, so every consumer
            -- sees the same venues and legacy overlapping rows cannot duplicate
            -- a sale. No AI-authored Quarter/customer interaction list is added.
            local key=row.SellerDistrictType and row.SellerDistrictType:match('^DISTRICT_CSC_(.+)_QUARTER$')
            if key then customer(key,row.CustomerDistrictType,row.CustomerBuildingType,3)end
        end
    end
    if GameInfo.CSC_QuarterWonderSales then
        -- These are ordinary Fashion House/customer exchanges, distinct from
        -- the Wonder's separately gated Service. Existing completed Wonders
        -- must enter the same ledger even while Service valuation is deferred.
        for row in GameInfo.CSC_QuarterWonderSales()do
            local definition=GameInfo.Buildings[row.BuildingType]
            if definition and definition.PrereqDistrict then
                customer(row.QuarterKey,definition.PrereqDistrict,row.BuildingType,row.ProducerStage)
            end
        end
    end
    for row in GameInfo.BuildingReplaces()do
        c.replacements[row.CivUniqueBuildingType]=row.ReplacesBuildingType
    end
    for row in GameInfo.TechnologyPrereqs()do
        c.tech[row.Technology]=c.tech[row.Technology]or{}
        table.insert(c.tech[row.Technology],row.PrereqTech)
    end
    for row in GameInfo.CivicPrereqs()do
        c.civic[row.Civic]=c.civic[row.Civic]or{}
        table.insert(c.civic[row.Civic],row.PrereqCivic)
    end
    c.unsupported={}
    if c.canonical and not c.materialCanonical then
        -- A partially loaded current package must not fall back to historical
        -- unit-rate assumptions. Old plain-record fixtures/packages without any
        -- canonical economy remain a separate compatibility path.
        for family in pairs(families)do c.unsupported[family]='Material catalogue unavailable'end
    end
    -- Fixed terms can differ from one. Validate the loaded native leaf against
    -- the canonical amount/type/yield, rather than keeping the old +1 assumption.
    -- This catches later compatibility edits after generation.
    for _,transaction in pairs(c.transactions)do if transaction.kind=='FIXED'then
        for _,leg in ipairs(transaction.legs)do
            local args=leg.nativeLeaf and c.arguments[leg.nativeLeaf]
            local target=leg.recipient=='SOURCE'and transaction.source or transaction.partner
            if not args or c.amounts[leg.nativeLeaf]~=transaction.amount*leg.amount
                or args.YieldType~=leg.yield or args.BuildingType~=target then
                c.unsupported[transaction.quarter]='Loaded fixed transaction differs: '..transaction.id..':'..leg.key
            end
        end
    end end
    for _,transaction in pairs(c.materials)do for _,leg in ipairs(transaction.legs)do
        local args=leg.nativeLeaf and c.arguments[leg.nativeLeaf]
        if not args or c.amounts[leg.nativeLeaf]~=leg.amount or args.YieldType~=leg.yield
            or leg.recipient=='PRODUCER'and args.BuildingType~=transaction.producer then
            c.unsupported[transaction.quarter]='Loaded material transaction differs: '..transaction.id..':'..leg.key
        end
    end end
    catalogue=c;return c
end

function F.CustomerDefinitions(key)
    -- Definition-only, read-only by contract; projections and actual footprints
    -- consume the same merged gameplay registry. Live state is never cached here.
    return definitions().customers[key]or{}
end

function F.SelectMaterialLegs(transaction,improvement,ready)
    -- Definition-only selection shared by the live reader and regressions.
    -- Registered native hosts decide inputs; the declared return selector
    -- decides outputs. A valid resource/improvement pair is not substituted for
    -- either test. Return a fresh record so per-publication readiness never
    -- mutates the session-static catalogue.
    local selected={id=transaction.id,legs={}}
    for _,leg in ipairs(transaction.legs)do
        local applies=improvement and(leg.recipient=='PRODUCER'and leg.hosts[improvement]
            or leg.recipient=='IMPROVEMENT'and(leg.scope=='ANY_PLAYER_IMPROVEMENT'
                or leg.improvement==improvement))
        if applies then selected.legs[#selected.legs+1]={key=leg.key,
            recipient=leg.recipient,yield=leg.yield,amount=leg.amount,ready=ready}end
    end
    return selected
end

function F.New(player,placement,ui,context)
    local c=definitions();local pid=player:GetID()
    local snapshot={player=player,id=pid,cities={},districts={},supplies={},research={},sites={},quotes={},
        nativeSiteStats={native=0,empty=0,unavailable=0}}
    local numericFacts,plotFacts={},{}
    local tradeFacts,tradeProblem,tradeRead
    function snapshot.TradeRoutes()
        -- One lazy observation per player/publication. UI owns route discovery;
        -- Gameplay refreshes endpoint properties/buildings and qualifies trader
        -- operations. Only static channel definitions persist across snapshots.
        -- No fresh/current observation means no complete trade counterfactual.
        if tradeRead then return tradeFacts,tradeProblem end
        tradeRead=true
        local R,A=CSC_TradeRouteCore,CSC_TradeRouteFacts
        local bridge=ExposedMembers and ExposedMembers.CSC_TradeRoutes
        if not R or not A or not bridge or type(bridge.GetFacts)~='function'then
            tradeProblem='Observed route bridge unavailable';return nil,tradeProblem
        end
        if not routeCatalogue then routeCatalogue,tradeProblem=R.ReadDefinitions(GameInfo)end
        if not routeCatalogue then return nil,tradeProblem end
        local ok,observed=pcall(bridge.GetFacts)
        local now=Game.GetCurrentGameTurn()
        if not ok or type(observed)~='table'or observed.version~=1
            or not finite(observed.turn)or observed.turn%1~=0 or observed.turn>now or now-observed.turn>1
            or type(observed.cities)~='table'or type(observed.routes)~='table'then
            tradeProblem='Current route observation unavailable';return nil,tradeProblem
        end
        -- Only routes touching this player can contribute its returns. Keep
        -- every such route (including duplicates/ineligible routes) and both
        -- endpoints, plus ALL own cities for acknowledged amenity baselines.
        -- Eligibility reads local endpoint state, not a recursive trade graph.
        local needed,scopedRoutes={},{}
        for key,city in pairs(observed.cities)do if city.player==pid then needed[key]=true end end
        for _,route in ipairs(observed.routes)do
            local origin,destination=observed.cities[route.origin],observed.cities[route.destination]
            if origin and origin.player==pid or destination and destination.player==pid then
                scopedRoutes[#scopedRoutes+1]=route;needed[route.origin]=true;needed[route.destination]=true
            end
        end
        local current={version=observed.version,turn=observed.turn,cities={},routes=scopedRoutes}
        local reader=A.New(GameInfo,routeCatalogue)
        for key,previous in pairs(observed.cities)do if needed[key]then
            local owner=Players[previous.player]
            local city=owner and owner:GetCities():FindID(previous.city)
            if city and city:GetOwner()==previous.player and city:GetID()==previous.city then
                local facts=reader.City(city)
                if key~=facts.key then tradeProblem='Route endpoint identity changed';return nil,tradeProblem end
                current.cities[key]=facts
            end
        end end
        local qualified=A.QualifyWindows(current,GameInfo,Game,GameConfiguration,Players,UnitOperationTypes)
        if qualified.durationStats.invalidObservation>0 then
            tradeProblem='Observed route operation changed';return nil,tradeProblem
        end
        tradeFacts={observed=qualified,definitions=routeCatalogue,changes={},plannedChanges={},
            memo={entries={},count=0,hits=0,misses=0,overflow=0}}
        return tradeFacts
    end
    snapshot.TradeCacheStats=function()
        local memo=tradeFacts and tradeFacts.memo
        return memo and{hits=memo.hits,misses=memo.misses,entries=memo.count,overflow=memo.overflow}or{}
    end
    local function cityNumber(city,kind,index)
        local key=city:GetID()..':'..kind..':'..index
        if numericFacts[key]~=nil then return numericFacts[key]or nil end
        local value
        if type(ui.GetEconomyCityNumber)=='function'then
            local ok,result=pcall(ui.GetEconomyCityNumber,pid,city:GetID(),kind,index)
            if ok and numeric(result)and result>=0 then value=result end
        end
        if value==nil then
            if kind=='yield'then value=number(city,'GetYield',index)
            elseif kind=='building'or kind=='district'then
                value=number(city:GetBuildQueue(),kind=='building'and'GetBuildingCost'or'GetDistrictCost',index)
            elseif kind=='buildingTurns'or kind=='districtTurns'then
                local definition=kind=='buildingTurns'and GameInfo.Buildings[index]or GameInfo.Districts[index]
                value=definition and number(city:GetBuildQueue(),'GetTurnsLeft',definition.BuildingType or definition.DistrictType)
            end
        end
        numericFacts[key]=value or false;return value
    end
    local function readPlot(plot)
        local index=plot:GetIndex()
        if not plotFacts[index]then
            local ok,value=false,nil
            if type(ui.GetEconomyPlotFacts)=='function'then ok,value=pcall(ui.GetEconomyPlotFacts,index)end
            -- A partial UI record must not erase an available Gameplay fact.
            local facts={workers=number(plot,'GetWorkerCount'),yields={}}
            if ok and type(value)=='table'then
                local gameplayWorkers=facts.workers
                local lag=finite(value.turn)and Game.GetCurrentGameTurn()-value.turn
                local currentObservation=lag and lag>=0 and lag<=1
                    and value.plotOwner==pid and plot:GetOwner()==pid
                if gameplayWorkers==nil and currentObservation and finite(value.workers)then facts.workers=value.workers end
                -- Publication can precede UI's turn transition. Accept its
                -- observed assignment through that one-turn phase only, with
                -- matching owner/worker facts. Older/future or conflicting
                -- observations do not earn assumed tile-return income.
                if currentObservation and value.workingPlayer==pid
                    and (gameplayWorkers==nil or value.workers==gameplayWorkers)
                    and finite(value.workingCity)then
                    facts.workingCity=value.workingCity;facts.workingObservationLag=lag
                end
                for yield,amount in pairs(value.yields or{})do
                    if numeric(amount)and amount==amount and math.abs(amount)<INF then facts.yields[yield]=amount end
                end
            end
            plotFacts[index]=facts
        end
        return plotFacts[index]
    end
    snapshot.PlotFacts=readPlot
    snapshot.FootprintSignature=F.FootprintSignature
    local tech,culture=player:GetTechs(),player:GetCulture()
    local function research(kind,key)
        if not key or key==''then return 0 end
        local memoKey=kind..':'..key
        if snapshot.research[memoKey]~=nil then return snapshot.research[memoKey]end
        local visiting,visited={},{}
        local function work(key)
        if visited[key]then return 0 end
        local definition=(kind=='tech'and GameInfo.Technologies or GameInfo.Civics)[key]
        if not definition then return INF end
        local object=kind=='tech'and tech or culture
        if kind=='tech'and object:HasTech(definition.Index)
            or kind=='civic'and object:HasCivic(definition.Index)then return 0 end
        if visiting[key]then return INF end;visiting[key]=true
        local cost=number(object,kind=='tech'and'GetResearchCost'or'GetCultureCost',definition.Index)
        local progress=number(object,kind=='tech'and'GetResearchProgress'or'GetCulturalProgress',definition.Index)
        local rate=number(object,kind=='tech'and'GetScienceYield'or'GetCultureYield')
        if type(ui.GetEconomyResearchNumbers)=='function'then
            local ok,value=pcall(ui.GetEconomyResearchNumbers,pid,kind,definition.Index)
            if ok and type(value)=='table'then
                if finite(value.cost)then cost=value.cost end
                if finite(value.progress)then progress=value.progress end
                if finite(value.rate)then rate=value.rate end
            end
        end
        local turns=cost and progress and rate and rate>0 and math.ceil(math.max(0,cost-progress)/rate)or INF
        -- Explicit current-rate estimate, not a promise that native research
        -- follows our path. Include prerequisite work; never grant an unlock.
        for _,prereq in ipairs(c[kind][key]or{})do turns=turns+work(prereq)end
        visiting[key]=nil;visited[key]=true;return turns
        end
        -- A shared prerequisite is paid once in this path's DAG, even if two
        -- branches require it. Cache the completed path, not subtree totals.
        local turns=work(key);snapshot.research[memoKey]=turns;return turns
    end
    snapshot.Research=research
    local traits={}
    local config=PlayerConfigurations[pid]
    if config then
        local civ,leader=config:GetCivilizationTypeName(),config:GetLeaderTypeName()
        for row in GameInfo.CivilizationTraits()do if row.CivilizationType==civ then traits[row.TraitType]=true end end
        local inherited={}
        while leader and not inherited[leader]do
            inherited[leader]=true
            for row in GameInfo.LeaderTraits()do if row.LeaderType==leader then traits[row.TraitType]=true end end
            local row=GameInfo.Leaders[leader];leader=row and row.InheritFrom
        end
    end
    local function allowed(definition)return not definition.TraitType or definition.TraitType==''or traits[definition.TraitType]end
    local replacements={}
    for unique,base in pairs(c.replacements)do
        local definition=GameInfo.Buildings[unique]
        if definition and allowed(definition)then replacements[base]=definition end
    end
    local function resolve(kind)return replacements[kind]or GameInfo.Buildings[kind]end
    local depths={}
    local function forecastDepth(definition,visiting)
        local kind=definition.BuildingType
        if depths[kind]~=nil then return depths[kind]end
        visiting=visiting or{}
        if visiting[kind]then return 0 end
        visiting[kind]=true
        local first
        for _,required in ipairs(c.prerequisites[kind]or{})do
            local candidate=resolve(required)
            -- Native's first-prerequisite depth is an investment heuristic.
            -- Availability markers are not economic investments: counting a
            -- River flag would favour Water over Wind for a fictional reason.
            if candidate and not flag(candidate.MustPurchase)and not flag(candidate.InternalOnly)
                and(not first or candidate.Index<first.Index)then first=candidate end
        end
        local depth=first and math.min(4,1+forecastDepth(first,visiting))or 0
        visiting[kind]=nil;depths[kind]=depth;return depth
    end
    for _,city in player:GetCities():Members()do
        local row={object=city,id=city:GetID(),population=city:GetPopulation(),queue=city:GetBuildQueue(),
            buildings=city:GetBuildings(),production=cityNumber(city,'yield',GameInfo.Yields.YIELD_PRODUCTION.Index),
            foodSurplus=growthSurplus(city),
            navalProduction=cityNumber(city,'navalProduction',0)}
        snapshot.cities[row.id]=row
        local ds=city:GetDistricts()
        row.populationDistricts=0
        for i=0,ds:GetNumDistricts()-1 do
            local d=ds:GetDistrictByIndex(i)
            if d then
                local plot=Map.GetPlot(d:GetX(),d:GetY())
                snapshot.districts[plot:GetIndex()]={city=row.id,complete=d:IsComplete(),
                    working=d:IsComplete()and not d:IsPillaged(),type=d:GetType()}
                local definition=GameInfo.Districts[d:GetType()]
                if not definition then row.capacityInventoryUnknown=true
                elseif flag(definition.RequiresPopulation)and not flag(definition.InternalOnly)then
                    -- Native admission counts unfinished/pillaged claims too.
                    -- Filtering this inventory to functioning districts would
                    -- incorrectly promise a slot already used by a foundation.
                    row.populationDistricts=row.populationDistricts+1
                end
            end
        end
    end
    function snapshot.DistrictCapacity(city)
        local facts=snapshot.cities[city:GetID()]
        if facts.capacity then return facts.capacity end
        -- One bounded UI crossing per city/publication, shared by all Quarters.
        -- A failed or stale read is unknown, never an invented free slot. The
        -- native city admission remains authoritative after this snapshot.
        local result={known=false,reason='unavailable'}
        local ok,value=false,nil
        if type(ui.GetDistrictCapacity)=='function'then
            ok,value=pcall(ui.GetDistrictCapacity,pid,city:GetID())
        end
        if ok and type(value)=='table'and finite(value.population)and finite(value.used)
            and finite(value.allowed)and value.used%1==0 and value.allowed%1==0 then
            result.population,result.used,result.allowed=value.population,value.used,value.allowed
            if not facts.capacityInventoryUnknown and value.population==facts.population
                and value.used==facts.populationDistricts then
                result.known=true
                result.reason=value.used<value.allowed and'ready'or'full'
            else result.reason='stale'end
        end
        facts.capacity=result;return result
    end
    function snapshot.Supply(plot,profile)
        local key=profile.key..':'..plot:GetIndex()
        if not snapshot.supplies[key]then snapshot.supplies[key]=placement.ReadSuppliers(player,plot,profile)end
        return snapshot.supplies[key]
    end
    function snapshot.TradeWorld(sites,footprint)
        -- Build plain route events from the SAME sites that the joint ledger
        -- will schedule. No amount/partner list lives here: native route supply
        -- predicates own the tags/counts, and the ledger owns investment times.
        -- A proposed customer may permanently displace one supplier footprint.
        -- District placement removes its improvement at foundation NOW, even
        -- though district/building completion occurs later. Future-dated
        -- destruction needs a separate before/after supply timeline; do not
        -- remove that supplier early by treating it as an immediate footprint.
        if footprint and (footprint.ready or 0)~=0 then return nil,'Only immediate district footprints are supported'end
        local base,problem=snapshot.TradeRoutes();if not base then return nil,problem end
        local R=CSC_TradeRouteCore
        local trade={observed=base.observed,definitions=base.definitions,changes={},plannedChanges={},memo=base.memo}
        local seen={}
        for _,site in ipairs(sites)do
            local cityKey=R.CityKey(site.player,site.city)
            local endpoint=base.observed.cities[cityKey]
            local plot=Map.GetPlotByIndex(site.plot)
            if not endpoint or not plot then return nil,'Quarter route endpoint unavailable'end
            local profile
            for _,candidate in ipairs(placement.StageTwoProfiles())do
                if candidate.key==site.quarterKey then profile=candidate;break end
            end
            if not profile then return nil,'Quarter route profile unavailable'end
            if seen[cityKey..':'..profile.key]then return nil,'Duplicate Quarter route site'end
            seen[cityKey..':'..profile.key]=true
            if site.routeFoundationReady~=nil then
                if not finite(site.routeFoundationReady)then return nil,'Quarter foundation timing unavailable'end
                trade.plannedChanges[#trade.plannedChanges+1]={ready=site.routeFoundationReady,city=cityKey,quarterStartKey=site.key,
                    field='quarters',key=profile.district.DistrictType,value=true}
            elseif site.existing and not endpoint.quarters[profile.district.DistrictType]and finite(site.quarterReady)then
                -- A repaired Quarter resumes its origin import-blocking flag.
                -- Existing unpillaged foundations already have that flag and
                -- must not wait for construction completion a second time.
                trade.plannedChanges[#trade.plannedChanges+1]={ready=0,city=cityKey,quarterKey=site.key,
                    field='quarters',key=profile.district.DistrictType,value=true}
            end
            local potential={}
            -- Reuse the central site's improvement ETAs, rather than introduce
            -- another Builder forecast or copied technology/repair allowance.
            -- Actual improved plots below remain independent of input-host and
            -- worker gates, as required by the route source's native selector.
            for _,supplier in ipairs(site.suppliers or{})do
                if finite(supplier.ready)then potential[supplier.plot]=math.min(potential[supplier.plot]or INF,supplier.ready)end
            end
            local suppliers={}
            for _,neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
                if neighbor:GetOwner()==pid and(not footprint or neighbor:GetIndex()~=footprint.removedPlot)then
                    local resource=GameInfo.Resources[neighbor:GetResourceType()]
                    if resource then
                        local improvement=GameInfo.Improvements[neighbor:GetImprovementType()]
                        local ready=improvement and not neighbor:IsImprovementPillaged()and 0 or potential[neighbor:GetIndex()]or INF
                        local tags={}
                        for _,channel in ipairs(base.definitions.channels)do if channel.quarter==profile.key then
                            for _,requirement in ipairs(channel.requirements)do
                                tags[requirement.tag]=CSC_Adjacency.HasTag(requirement.tag,resource.ResourceType)
                            end
                        end end
                        suppliers[#suppliers+1]={plot=neighbor:GetIndex(),ready=ready,tags=tags}
                    end
                end
            end
            for _,channel in ipairs(base.definitions.channels)do if channel.quarter==profile.key then
                local ready=R.SupplyReady(channel,suppliers)
                local presentProducer=endpoint.buildings[channel.producer]==true
                local investment=not presentProducer and cityKey..':'..channel.producer or nil
                -- Destruction is an explicit footprint event. Coverage expiry
                -- never enters this path. Other/future suppliers can restore
                -- the property later if their actual native counts suffice.
                if footprint and (endpoint.properties[channel.supplyProperty]or 0)>0
                    and ready>(footprint.ready or 0)then
                    trade.changes[#trade.changes+1]={ready=footprint.ready or 0,city=cityKey,
                        field='properties',key=channel.supplyProperty,value=0}
                end
                if finite(ready)then
                    trade.plannedChanges[#trade.plannedChanges+1]={ready=ready,city=cityKey,field='properties',
                        key=channel.supplyProperty,value=1,investmentKey=investment}
                end
                if not presentProducer then
                    trade.plannedChanges[#trade.plannedChanges+1]={city=cityKey,field='buildings',
                        key=channel.producer,value=true,investmentKey=investment}
                end
            end end
        end
        return trade
    end
    function snapshot.AdjacencyAmounts(city,plot,districtType,project)
        -- Match the gameplay writer: it gates the RECEIVING district's
        -- completion. Adjacent source types/tags include foundations and do
        -- not acquire an invented functioning/completion requirement here.
        local sums,percents={},{}
        for _,rule in ipairs(CSC_Adjacency.ByDistrict[districtType]or{})do
            if rule.ModifierOwner~='BuildingModifiers'and CSC_Adjacency.Eligible(rule,city,pid)then
                local amount=CSC_Adjacency.Amount(rule,CSC_Adjacency.Count(rule,plot,city,pid,project))
                if rule.ProvideType=='SelfBonus'then sums[rule.YieldType]=(sums[rule.YieldType]or 0)+amount
                elseif rule.ProvideType=='SelfMultiplier'then percents[rule.YieldType]=(percents[rule.YieldType]or 0)+amount end
            end
        end
        local raw={};for yield,amount in pairs(sums)do raw[yield]=amount;sums[yield]=amount*(1+(percents[yield]or 0)/100)end
        return sums,percents,raw
    end
    function snapshot.DirectAmounts(city,plot,profile,removed)
        return snapshot.AdjacencyAmounts(city,plot,profile.district.DistrictType,
            removed and function(p)if p:GetIndex()~=removed then return p end end or nil)
    end
    local geometry={}
    function snapshot.Geometry(city,plot,profile)
        -- Cheap admission uses the same loaded adjacency rules as the full
        -- ledger. Cache once per publication/site. Future customer districts
        -- earn nothing; a single possible local Mill is the explicit allowance.
        -- This upper bound lets weak sites defer before building full ledgers.
        local key=city:GetID()..':'..profile.key..':'..plot:GetIndex()
        if geometry[key]then return geometry[key]end
        local direct,percent,raw=snapshot.DirectAmounts(city,plot,profile)
        local result={direct=direct,mills={},quarterKey=profile.key,
            base=(direct.YIELD_PRODUCTION or 0)+(direct.YIELD_GOLD or 0)}
        -- Physical customer evidence for the adapter's narrow Tailors +1
        -- exception. A completed owned Harbor (including a unique replacement)
        -- can receive a Lighthouse later; a plan, foundation, CL provider or
        -- foreign Harbor cannot qualify. Pillage retains physical adjacency,
        -- while the ordinary ledger separately prices building/repair readiness.
        -- Use the shared inventory: no new CE/UI queries per candidate.
        if profile.key=='TAILORS'then
            for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
                local host=snapshot.districts[near:GetIndex()]
                if host and host.complete and F.DistrictFamily(host.type)=='DISTRICT_HARBOR'then
                    result.completedHarborPlot=math.min(result.completedHarborPlot or near:GetIndex(),near:GetIndex())
                end
            end
        end
        result.upper=result.base
        if profile.key=='BAKERS'then
            for _,kind in ipairs({'BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_BAKERS_WATER_MILL'})do
                if kind~='BUILDING_CSC_BAKERS_WATER_MILL'or plot:IsRiver()then
                    local extra,extraPercent=0,0
                    for _,rule in ipairs(CSC_Adjacency.ByDistrict[profile.district.DistrictType]or{})do
                        if rule.ModifierOwner=='BuildingModifiers'and rule.WhoIsTheOwner==kind and rule.YieldType=='YIELD_PRODUCTION'then
                            local amount=CSC_Adjacency.Amount(rule,CSC_Adjacency.Count(rule,plot,city,pid))
                            if rule.ProvideType=='SelfBonus'then extra=extra+amount
                            elseif rule.ProvideType=='SelfMultiplier'then extraPercent=extraPercent+amount end
                        end
                    end
                    -- Mills currently modify Production only. Apply the same
                    -- live percentage as direct adjacency, including policies;
                    -- the previous hard-coded terrain count omitted that step.
                    local delta=((raw.YIELD_PRODUCTION or 0)+extra)*(1+((percent.YIELD_PRODUCTION or 0)+extraPercent)/100)
                        -(direct.YIELD_PRODUCTION or 0)
                    result.mills[kind]=delta;result.upper=math.max(result.upper,result.base+delta)
                end
            end
        end
        geometry[key]=result;return result
    end
    local lostAdjacency={}
    function snapshot.SupplyAdjacencyLoss(chain,removed)
        local key=chain.city:GetID()..':'..chain.profile.key..':'..removed
        if lostAdjacency[key]then return lostAdjacency[key]end
        local full=snapshot.DirectAmounts(chain.city,chain.plot,chain.profile)
        local without=snapshot.DirectAmounts(chain.city,chain.plot,chain.profile,removed)
        local loss={}
        for yield,amount in pairs(full)do loss[yield]=amount-(without[yield]or 0)end
        lostAdjacency[key]=loss;return loss
    end
    local function building(city,definition,plot,visiting)
        local host=snapshot.districts[plot]
        local present=city.buildings:HasBuilding(definition.Index)and city.buildings:GetBuildingLocation(definition.Index)==plot
        local intact=present and not city.buildings:IsPillaged(definition.Index)
        local works=host and host.working and intact
        local cost=cityNumber(city.object,'building',definition.Index)
        local unlocked=math.max(research('tech',definition.PrereqTech),research('civic',definition.PrereqCivic))
        local b={type=definition.BuildingType,working=works,intactOwner=intact and host and host.complete or false,
            unlock=works and 0 or unlocked,cost=cost,
            turns=cityNumber(city.object,'buildingTurns',definition.Index)
                or(cost and city.production and city.production>0 and math.max(1,math.ceil(cost/city.production))or INF),
            maintenance=definition.Maintenance or 0,forecastDepth=forecastDepth(definition)}
        if works then return b end
        visiting=visiting or{}
        if visiting[definition.BuildingType]then b.excluded=true;return b end
        visiting[definition.BuildingType]=true
        b.excluded=not allowed(definition)or flag(definition.MustPurchase)or flag(definition.InternalOnly)
            or flag(definition.IsWonder)or flag(definition.EnabledByReligion)or flag(definition.RequiresReligion)
            or (definition.GovernmentTierRequirement or 0)>0
        for _,other in ipairs(c.exclusives[definition.BuildingType]or{})do
            local row=resolve(other)
            if row and city.buildings:HasBuilding(row.Index)then b.excluded=true end
        end
        -- BuildingPrereqs is OR, including the two alternative Mills. Existing
        -- producer prerequisites are sequenced by the model; missing ordinary
        -- prerequisites (e.g. Arena before Zoo) need their own queue investment.
        local alternatives=c.prerequisites[definition.BuildingType]or{}
        local best,found
        for _,kind in ipairs(alternatives)do
            local row=resolve(kind)
            if kind=='BUILDING_CSC_BAKERS_RIVER_ACCESS'and Map.GetPlotByIndex(plot):IsRiver()then found=true
            elseif row and row.PrereqDistrict==definition.PrereqDistrict and kind:find('BUILDING_CSC_',1,true)then
                found=true -- Explicit producer 2→3/4 edge is owned by the model.
            elseif row then
                local candidate=building(city,row,plot,visiting)
                if candidate.working then found=true
                elseif not candidate.excluded and(not best or candidate.unlock+candidate.turns<best.unlock+best.turns)then best=candidate end
            end
        end
        if #alternatives>0 and not found then
            if best then b.prerequisites={best}else b.excluded=true end
        end
        visiting[definition.BuildingType]=nil
        return b
    end
    local function futureCustomer(city,definition,plot)
        local b=building(city,definition,plot)
        b.ready=b.working and 0 or b.unlock+b.turns
        b.building=definition.BuildingType;b.city=city.id;b.plot=plot;b.population=city.population
        return b
    end
    local function customerRecord(profile,buyer,definition,plot,stage)
        local customer=futureCustomer(buyer,definition,plot)
        customer.stage=stage
        customer.serviceActive=profile.service and type(buyer.object.GetProperty)=='function'
            and(buyer.object:GetProperty(profile.service.property)or 0)>0 or false
        customer.serviceInputKnown=profile.key=='BAKERS'and buyer.foodSurplus~=nil
            or profile.key=='TAILORS'and buyer.navalProduction~=nil
        customer.yield=stage==2 and(profile.key=='BAKERS'and'YIELD_FOOD'or'YIELD_PRODUCTION')
            or stage==4 and'YIELD_CULTURE'or families[profile.key].yield
        local seller=((c.stages[profile.key]or{})[3]or{})[1]
        local transaction=seller and c.population[seller.BuildingType..':'..definition.BuildingType]
        -- Unique customers inherit the base transaction's rate/property contract.
        if not transaction and seller then
            transaction=c.population[seller.BuildingType..':'..(c.replacements[definition.BuildingType]or definition.BuildingType)]
        end
        customer.rate=transaction and transaction.EngineAmountPerPopulation
        customer.sellerProperty=transaction and transaction.SellerReturnAmountProperty
        customer.customerProperty=transaction and transaction.CustomerYieldAmountProperty
        customer.transactions=c.canonical and{}or nil
        local ordinary
        for _,source in ipairs((c.stages[profile.key]or{})[stage]or{})do
            local row=c.transactions[source.BuildingType..':'..(c.replacements[definition.BuildingType]or definition.BuildingType)]
            if row then customer.transactions[source.BuildingType]=row;ordinary=ordinary or row end
        end
        if ordinary then
            customer.transaction=ordinary
            for _,leg in ipairs(ordinary.legs)do if leg.recipient=='PARTNER'then customer.yield=leg.yield end end
            -- Preserve current gameplay: Stage3/Cafe accept a functioning
            -- customer building even if its host district is pillaged. Fashion
            -- district venues require both; no silent rule harmonization here.
            local host=snapshot.districts[plot]
            if host and not host.working then
                local functioning=buyer.buildings:HasBuilding(definition.Index)
                    and not buyer.buildings:IsPillaged(definition.Index)
                    and buyer.buildings:GetBuildingLocation(definition.Index)==plot
                if functioning and ordinary.kind~='FIXED'and not ordinary.partnerDistrictMustFunction then
                    customer.working=true;customer.unlock=0;customer.ready=0
                else
                    -- A missing building cannot be forecast ahead of an unknown
                    -- district repair. Later repair adapters can supply an ETA.
                    customer.excluded=true
                end
            end
        end
        if stage~=3 or customer.rate then return customer end
    end
    function snapshot.ProjectedCustomers(profile,cityID,districtIndex,plotIndex)
        -- Plain prospective records, NOT completed live districts. A diagnostic
        -- or future decision adapter must separately qualify the target, price
        -- district construction, and pass its ready time to the central model.
        -- The factory reuses actual building costs, prerequisites, replacements
        -- and population rates; it issues no order, bid or property write.
        local buyer=snapshot.cities[cityID];local result,seen={},{}
        if not buyer or not families[profile.key]then return result end
        for _,mapping in ipairs(c.customers[profile.key]or{})do
            local expected=GameInfo.Districts[mapping.DistrictType]
            local definition=resolve(mapping.BuildingType)
            if expected and F.DistrictFamily(expected.Index)==F.DistrictFamily(districtIndex)
                and definition and allowed(definition)and not flag(definition.IsWonder)then
                local stamp=definition.BuildingType..':'..mapping.ProducerStage
                local row=not seen[stamp]and customerRecord(profile,buyer,definition,plotIndex,mapping.ProducerStage)
                if row then
                    row.complete=false;row.projected=true;row.working=false
                    result[#result+1]=row;seen[stamp]=true
                end
            end
        end
        return result
    end
    -- Spatial potential is deliberately separate from transaction income.
    -- Read stock hypothetical adjacency for real customer footprints through
    -- the UI boundary (explicit AI/city/type), including loaded terrain rules.
    -- Each city/type map is scanned at most once per publication, at most the
    -- radius-three ring. Both Quarters share these caches. Never carry native
    -- adjacency, ownership, research or protected-plot facts into another turn.
    local customerMaps,customerAdjacency,customerTypes={},{},{}
    local spatialStats={maps=0,adjacencyReads=0,unavailable=0,laggedReads=0,options=0}
    snapshot.SpatialStats=function()return spatialStats end
    local function customerYield(city,plot,definition)
        local key=city:GetID()..':'..plot:GetIndex()..':'..definition.Index
        if customerAdjacency[key]~=nil then return customerAdjacency[key]or nil end
        local value
        if type(ui.GetDistrictAdjacency)=='function'then
            spatialStats.adjacencyReads=spatialStats.adjacencyReads+1
            local ok,record=pcall(ui.GetDistrictAdjacency,pid,city:GetID(),plot:GetIndex(),definition.Index)
            local lag=ok and type(record)=='table'and type(record.turn)=='number'
                and Game.GetCurrentGameTurn()-record.turn
            -- Core turn publication precedes UI's turn transition. The first
            -- spatial startup records Core45/UI44; requiring exact clock equality
            -- discarded every terrain read. Accept that bounded one-turn phase
            -- lag, while checking ownership, resources and geometry in Core.
            -- Terrain may reflect the preceding UI snapshot; current native
            -- eligibility still governs construction. Older/future clocks defer.
            if ok and type(record)=='table'and record.available and type(record.yields)=='table'
                and lag and lag>=0 and lag<=1 then
                if lag>0 then spatialStats.laggedReads=spatialStats.laggedReads+1 end
                -- Ordinary adjacency points are a terrain-quality measure,
                -- not native utility or forecast income. Private AI yields
                -- must never feed back into another planning preference.
                local sum=0
                for _,kind in ipairs({'YIELD_FOOD','YIELD_PRODUCTION','YIELD_GOLD',
                    'YIELD_SCIENCE','YIELD_CULTURE','YIELD_FAITH'})do
                    sum=sum+(record.yields[kind]or 0)
                end
                value=sum
            end
            if value==nil and spatialStats.unavailable==0 then
                print(string.format('CSC_AI_SPATIAL_INPUT turn=%d player=%d city=%d plot=%d district=%d ok=%s recordType=%s available=%s uiTurn=%s lag=%s',
                    Game.GetCurrentGameTurn(),pid,city:GetID(),plot:GetIndex(),definition.Index,
                    tostring(ok),type(record),tostring(type(record)=='table'and record.available),
                    tostring(type(record)=='table'and record.turn),tostring(lag)))
            end
        end
        if value==nil then spatialStats.unavailable=spatialStats.unavailable+1 end
        customerAdjacency[key]=value or false;return value
    end
    local function customerMap(city,definition,protectedPlots)
        local key=city:GetID()..':'..definition.Index
        if customerMaps[key]then return customerMaps[key]end
        spatialStats.maps=spatialStats.maps+1
        local result={plots={},best=0,free={}};customerMaps[key]=result
        local cityID=city:GetID()
        if customerTypes[cityID]==nil then
            customerTypes[cityID]=CSC_AI_FutureDistrictTypes and CSC_AI_FutureDistrictTypes(pid,city)or false
        end
        if not customerTypes[cityID]or not customerTypes[cityID][definition.Index]then return result end
        local center=Map.GetPlot(city:GetX(),city:GetY())
        for _,p in ipairs(CSC_Adjacency.PlotsInBand(center,1,3))do
            local owner=p:GetOwner()==pid and Cities.GetPlotPurchaseCity(p)
            if owner and owner:GetID()==cityID and p:GetDistrictType()==-1
                and p:GetResourceType()==-1 and not protectedPlots[p:GetIndex()]
                and PlayersVisibility[pid]:IsRevealed(p:GetX(),p:GetY())
                and p:CanHaveDistrict(definition.Index,pid,cityID)then
                local amount=customerYield(city,p,definition)
                result.plots[p:GetIndex()]={plot=p,adjacency=amount}
                if amount then result.best=math.max(result.best,amount)end
                if amount and not (snapshot.intentFootprints and snapshot.intentFootprints[p:GetIndex()])then
                    result.free[#result.free+1]={index=p:GetIndex(),adjacency=amount}
                end
            end
        end
        table.sort(result.free,function(a,b)
            if a.adjacency~=b.adjacency then return a.adjacency>b.adjacency end
            return a.index<b.index
        end)
        return result
    end
    function snapshot.CustomerOptions(city,plot,profile,protectedPlots)
        local options={}
        if not CSC_AI_SitingDistricts then return options end
        local permitted=CSC_AI_SitingDistricts(profile)
        for _,definition in ipairs(permitted.buildable)do
            -- No City Center or Wonder forecasts: settlement and Wonder
            -- placement remain separate decisions. Existing customer districts
            -- are already represented by the transaction ledger.
            if definition.DistrictType~='DISTRICT_CITY_CENTER'and definition.DistrictType~='DISTRICT_WONDER'then
                for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
                    local buyer=near:GetOwner()==pid and Cities.GetPlotPurchaseCity(near)
                    if buyer then
                        local map=customerMap(buyer,definition,protectedPlots)
                        local candidate=map.plots[near:GetIndex()]
                        if candidate and candidate.adjacency~=nil
                            and not (snapshot.intentFootprints and snapshot.intentFootprints[near:GetIndex()])then
                            -- A different native best site does not cancel an
                            -- older retained request. Do not promise its tile
                            -- as a customer footprint. Compare elsewhere cost
                            -- without counting this Quarter's own tile twice;
                            -- its separate displacement term remains below.
                            local best=map.free[1]
                            if best and best.index==plot:GetIndex()then best=map.free[2]end
                            local parent=definition.DistrictType
                            if GameInfo.DistrictReplaces then for row in GameInfo.DistrictReplaces()do
                                if row.CivUniqueDistrictType==parent then parent=row.ReplacesDistrictType;break end
                            end end
                            options[#options+1]={player=pid,city=buyer:GetID(),district=definition.Index,
                                family=parent,plot=near:GetIndex(),adjacency=candidate.adjacency,
                                bestAdjacency=best and best.adjacency or 0,
                                -- A Quarter can consume the city's best native
                                -- customer tile. Expose that opportunity cost;
                                -- the policy adapter decides its bounded weight.
                                displacedAdjacency=map.plots[plot:GetIndex()]
                                    and map.plots[plot:GetIndex()].adjacency or 0}
                        end
                    end
                end
            end
        end
        spatialStats.options=spatialStats.options+#options
        return options
    end

    function snapshot.CustomerFirstOptions(protectedPlots)
        -- Start at CURRENT native customer targets, then walk one hex to an
        -- empty Quarter footprint and one more to its tagged suppliers. Merely
        -- finding a matching resource within radius two is insufficient: all
        -- three distinct footprints must fit, including triangles where the
        -- customer also touches the material. Research/population may grow
        -- later; permanent actor exclusions and geometry must already allow
        -- the Quarter. This pass neither purchases land nor reserves a slot.
        -- Owned, revealed suppliers use the shared improvement-feasibility
        -- reader, including locked but geometrically possible improvements.
        -- Rebuild live facts each publication; cache each Quarter/site supply
        -- and each customer/site adjacency through the central snapshot.
        local options,potential={},{}
        local types=customerTypes -- share actor/type masks with forward layouts
        local work={targets=0,quarterChecks=0,supplyReads=0,options=0,unknown=0}
        snapshot.customerFirstWork=work
        local function futureTypes(city)
            local id=city:GetID()
            if types[id]==nil then types[id]=CSC_AI_FutureDistrictTypes
                and CSC_AI_FutureDistrictTypes(pid,city)or false end
            return types[id]
        end
        local function reserved(index)return snapshot.intentFootprints and snapshot.intentFootprints[index]end
        local function quarterAt(plot,profile)
            local key=plot:GetIndex()..':'..profile.district.Index
            if potential[key]~=nil then return potential[key]or nil end
            potential[key]=false;work.quarterChecks=work.quarterChecks+1
            local city=plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
            local allowed=city and futureTypes(city)
            if not city or not allowed or not allowed[profile.district.Index]
                or plot:GetDistrictType()~=-1 or plot:GetResourceType()~=-1
                or protectedPlots[plot:GetIndex()]or reserved(plot:GetIndex())
                or not PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY())
                or Map.GetPlotDistance(city:GetX(),city:GetY(),plot:GetX(),plot:GetY())>3
                or not plot:CanHaveDistrict(profile.district.Index,pid,city:GetID())then return nil end
            local supply=snapshot.Supply(plot,profile);work.supplyReads=work.supplyReads+1
            if not supply then return nil end
            local row={quarterCity=city:GetID(),quarterDistrict=profile.district.Index,quarterKey=profile.key,quarterPlot=plot:GetIndex(),
                basePlots={},specialtyPlots={}}
            -- A retained native district request may already be consuming a
            -- deposit; do not sell that doomed material as a future supplier.
            for _,material in ipairs(supply.base)do if not reserved(material.plot)then row.basePlots[#row.basePlots+1]=material.plot end end
            for _,material in ipairs(supply.specialty)do if not reserved(material.plot)then row.specialtyPlots[#row.specialtyPlots+1]=material.plot end end
            row.baseCount,row.specialtyCount=#row.basePlots,#row.specialtyPlots
            if row.baseCount==0 then return nil end
            table.sort(row.basePlots);table.sort(row.specialtyPlots)
            potential[key]=row;return row
        end
        local graph=F.CustomerQuarterMap()
        local districtIDs={};for id in pairs(graph)do districtIDs[#districtIDs+1]=id end;table.sort(districtIDs)
        local cityIDs={};for id in pairs(snapshot.cities)do cityIDs[#cityIDs+1]=id end;table.sort(cityIDs)
        if type(ui.GetLegalDistrictTargets)~='function'or not Map.GetPlotDistance then return options end
        for _,id in ipairs(cityIDs)do
            local city=snapshot.cities[id].object
            local allowed=futureTypes(city)
            for _,district in ipairs(districtIDs)do if allowed and allowed[district]then
                local mapping=graph[district];local definition=mapping.definition
                local ok,targets=pcall(ui.GetLegalDistrictTargets,pid,id,definition.Hash)
                if not ok or type(targets)~='table'then work.unknown=work.unknown+1
                else
                    local legal,prospects={},{}
                    for _,index in ipairs(targets)do
                        local plot=Map.GetPlotByIndex(index)
                        local owner=plot and plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
                        if owner and owner:GetID()==id and plot:GetDistrictType()==-1
                            and plot:GetResourceType()==-1 and not protectedPlots[index]and not reserved(index)
                            and PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY())then
                            legal[#legal+1]=plot;work.targets=work.targets+1
                            local adjacent=Map.GetAdjacentPlots(plot:GetX(),plot:GetY())
                            for _,profile in ipairs(mapping.quarters)do
                                local suppliedCities,unknownSupplier={},false
                                for _,near in ipairs(adjacent)do
                                    if near:GetOwner()==pid and near:GetDistrictType()==profile.district.Index then
                                        local supplier=Cities.GetPlotPurchaseCity(near)
                                        if supplier then suppliedCities[supplier:GetID()]=true else unknownSupplier=true end
                                    end
                                end
                                -- Existing-neighbour incentives already use native SQL.
                                -- Suppress only that supplier city/type; another
                                -- city's future Quarter is a separate real link.
                                if not unknownSupplier then for _,near in ipairs(adjacent)do
                                    local future=quarterAt(near,profile)
                                    if future and not suppliedCities[future.quarterCity]then prospects[#prospects+1]={plot=plot,future=future}end
                                end end
                            end
                        end
                    end
                    if #prospects>0 then
                        -- Read native ordinary adjacency only when a material-
                        -- backed layout exists. Unknown alternatives suppress
                        -- the speculative offer rather than invent a best site.
                        local best,known=-INF,true
                        for _,plot in ipairs(legal)do
                            local value=customerYield(city,plot,definition)
                            if value==nil then known=false else best=math.max(best,value)end
                        end
                        if known then for _,prospect in ipairs(prospects)do
                            local row={city=id,district=district,customerFamily=F.DistrictFamily(district),plot=prospect.plot:GetIndex(),
                                adjacency=customerYield(city,prospect.plot,definition),bestAdjacency=best}
                            for key,value in pairs(prospect.future)do row[key]=value end
                            options[#options+1]=row
                        end else work.unknown=work.unknown+1 end
                    end
                end
            end end
        end
        work.options=#options
        return options
    end

    function snapshot.Site(cityObject,plot,profile)
        local key=cityObject:GetID()..':'..profile.key..':'..plot:GetIndex()
        if snapshot.sites[key]then return snapshot.sites[key]end
        local family=families[profile.key];if not family then return nil,'No economic family rules'end
        if c.unsupported[profile.key]then return nil,c.unsupported[profile.key]end
        local city=assert(snapshot.cities[cityObject:GetID()])
        local placed=snapshot.districts[plot:GetIndex()]
        local exists=placed and placed.type==profile.district.Index and placed.complete
        local functioning=exists and placed.working
        local cost=cityNumber(cityObject,'district',profile.district.Index)
        local duration=cityNumber(cityObject,'districtTurns',profile.district.Index)
        local qUnlock=math.max(research('tech',profile.district.PrereqTech),research('civic',profile.district.PrereqCivic))
        local qReady=functioning and 0 or duration and qUnlock+math.max(1,duration)
            or cost and city.production and city.production>0 and qUnlock+math.max(1,math.ceil(cost/city.production))or INF
        local site={key=pid..':'..key,player=pid,city=city.id,plot=plot:GetIndex(),population=city.population,
            horizon=context and context.horizon or 50,quarterReady=qReady,adjacency=0,
            -- Founding can happen when the district unlocks, before its queue
            -- finishes construction. Legal admission is the decision adapter's
            -- responsibility; this timing never grants a district or unlock.
            routeFoundationReady=not placed and qUnlock or nil,
            quarterWork=not functioning and finite(qReady)and {unlock=qUnlock,turns=qReady-qUnlock}or nil,
            maintenance=profile.district.Maintenance or 0,existing=exists,materialYield=family.yield,
            direct={},suppliers={},customers={},seconds={},omissions={
                'Future worker assignments, trade routes, GPP and Stage3/4 Service premiums are not priced'}}
        if context and context.nativeSite and profile.service and profile.service.civic then
            local amount=profile.key=='BAKERS'and c.amounts.MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER
                or c.amounts.MOD_CSC_TAILORS_DOCKMASTER_EFFECT_ANCIENT_NAVAL_MELEE
            local last=GameInfo.Eras and GameInfo.Eras.ERA_RENAISSANCE
            if amount and(profile.key=='BAKERS'or last and player:GetEra()<=last.Index)then
                site.service={kind=profile.key=='BAKERS'and'GROWTH'or'NAVAL_PRODUCTION_PERCENT',amount=amount,
                    unlock=research('civic',profile.service.civic),property=profile.service.property}
            end
        end
        -- Covering a worked tile removes its observed ordinary income. This
        -- is separate from protecting deposits that sustain another Quarter.
        -- Do not invent staffing for an unworked footprint or a harvest payout.
        local footprint=readPlot(plot)
        if footprint.workers==nil then return nil,'Footprint staffing unavailable'end
        site.footprintWorkers=footprint.workers
        site.footprintSignature=snapshot.FootprintSignature(plot)
        if context and context.nativeSite and placed then
            -- Existing/pillaged Quarter footprints require no acquisition or
            -- improvement removal. Their repair/building values remain live
            -- consumers of the model, separate from new-site native quotes.
            site.nativeSiteAdjustmentQ8=0
        elseif context and context.nativeSite and not exists and qReady<site.horizon then
            -- Reuse native NetValue minus intrinsic district Value. This
            -- retains native land/harvest/improvement accounting without
            -- importing its Quarter yields or future-building aggregate.
            -- Cache lasts only this publication; a missing quote is unknown.
            local clearOwned=plot:GetOwner()==pid and site.footprintSignature:match('^%-?%d+,%-1,%-1,%-1$')
            local ok,raw
            if clearOwned then
                -- Proven NetValue branch identity: owned plot, no feature,
                -- resource, improvement or district => no site adjustment.
                -- Avoid two redundant native district evaluations per empty
                -- candidate. Frontier invoices and every nonempty site quote
                -- still run through the native evaluator.
                ok,raw=true,'{"adjustmentQ8":0,"includesPurchase":0}'
                snapshot.nativeSiteStats.empty=snapshot.nativeSiteStats.empty+1
            else
                snapshot.nativeSiteStats.native=snapshot.nativeSiteStats.native+1
                ok,raw=pcall(CE_AIDistrictSiteAdjustment,pid,city.id,profile.district.Index,
                    plot:GetX(),plot:GetY(),qReady,site.horizon,context.discountQ8)
            end
            local function field(name)return type(raw)=='string'and tonumber(raw:match('"'..name..'":(-?%d+)'))or nil end
            local value=ok and field('adjustmentQ8')
            if value==nil then snapshot.nativeSiteStats.unavailable=snapshot.nativeSiteStats.unavailable+1;return nil,'Native site accounting unavailable'end
            site.nativeSiteAdjustmentQ8=value;site.nativeSiteIncludesPurchase=field('includesPurchase')==1
            site.nativeSiteNetQ8=field('netQ8');site.nativeIntrinsicQ8=field('intrinsicQ8')
        elseif not exists and footprint.workers>0 and not(context and context.nativeSite)then
            for yield in GameInfo.Yields()do
                if yield.YieldType~='YIELD_CSC_AI_PLACEMENT'then
                    local amount=footprint.yields[yield.YieldType]or number(plot,'GetYield',yield.Index)
                    if amount and amount>0 then site.direct[#site.direct+1]={id='displaced:'..yield.YieldType,yield=yield.YieldType,amount=-amount}end
                end
            end
        end
        local geometry=snapshot.Geometry(cityObject,plot,profile)
        site.quarterKey=profile.key;site.completedHarborPlot=geometry.completedHarborPlot
        -- Before any producer building: use these facts to explain whether a
        -- paid footprint has immediate adjacency income once construction ends.
        -- Production is valuable utility but is not treasury income. Mill
        -- terrain and later transactions have their own delayed streams.
        site.startingAdjacency=geometry.base
        site.startingGold=geometry.direct.YIELD_GOLD or 0
        for yield,amount in pairs(geometry.direct)do
            site.direct[#site.direct+1]={id=yield,yield=yield,amount=amount}
            if yield=='YIELD_PRODUCTION'or yield=='YIELD_GOLD'then site.adjacency=site.adjacency+amount end
        end
        local stages=c.stages[profile.key]or{}
        local specialistCity=footprint.workingCity
        if not specialistCity and Cities.GetPlotWorkingCity then
            local ok,working=pcall(Cities.GetPlotWorkingCity,plot:GetIndex())
            if ok and working and working:GetOwner()==pid then specialistCity=working:GetID()end
        end
        local workers=exists and footprint.workers or 0
        if workers==0 or specialistCity and snapshot.cities[specialistCity]then
            site.specialists={workers=workers,city=specialistCity or city.id,base={},buildings={},presentBuildings={}}
            for yield,amount in pairs(c.districtCitizenYields[profile.district.DistrictType]or{})do
                site.specialists.base[yield]=amount
            end
            for stage=2,4 do for _,definition in ipairs(stages[stage]or{})do
                local kind=definition.BuildingType
                local rates=c.citizenYields[kind]or{}
                site.specialists.buildings[kind]=rates
                if city.buildings:HasBuilding(definition.Index)
                    and city.buildings:GetBuildingLocation(definition.Index)==plot:GetIndex()then
                    -- Native GetYield37ec60 sums citizen rows for every building
                    -- at the district location, including pillaged ones. Worker
                    -- capacity10fff0 separately excludes pillaged building slots.
                    -- Preserve that distinction; repairing a present building
                    -- does not create its citizen-yield increment a second time.
                    site.specialists.presentBuildings[kind]=true
                    for yield,amount in pairs(rates)do
                        site.specialists.base[yield]=(site.specialists.base[yield]or 0)+amount
                    end
                end
            end end
        else site.omissions[#site.omissions+1]='Specialist receiving city unavailable'end
        for stage=2,4 do
            for _,definition in ipairs(stages[stage]or{})do
                if allowed(definition)and not flag(definition.MustPurchase)then
                    local b=building(city,definition,plot:GetIndex())
                    -- An intact existing building needs its host restored, not
                    -- another copy constructed or another upkeep charge. Its
                    -- owner-side material returns can already be active at0.
                    b.hostReady=qReady
                    b.hostQuarter=site.key
                    if stage==2 then
                        local water=definition.BuildingType=='BUILDING_CSC_BAKERS_WATER_MILL'
                        if not water or plot:IsRiver()then
                            b.terrain=geometry.mills[definition.BuildingType]or 0
                            -- An already present alternative forbids switching
                            -- Mills merely because the other now quotes better.
                            local other=water and GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL or GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL
                            if profile.key~='BAKERS'or not other or not city.buildings:HasBuilding(other.Index)then site.seconds[#site.seconds+1]=b end
                        end
                    else
                        -- Local exchanges are keyed by the chosen upstream
                        -- alternative. A hypothetical city cannot credit both
                        -- Mills; the ledger chooses only that producer's terms.
                        b.localTransactions=c.canonical and{}or nil
                        for _,source in ipairs(stages[2]or{})do
                            local transaction=c.transactions[source.BuildingType..':'..definition.BuildingType]
                            if transaction and transaction.spatial=='SAME_CITY'then
                                b.localTransactions[source.BuildingType]=transaction
                            end
                        end
                        b.amenityAmount=definition.Entertainment or 0
                        b.amenityCities={city.id}
                        if (definition.RegionalRange or 0)>0 then
                            b.amenityCities={}
                            for id,recipient in pairs(snapshot.cities)do
                                local alreadyServed=false
                                for _,source in pairs(snapshot.cities)do
                                    if source.buildings:HasBuilding(definition.Index)and not source.buildings:IsPillaged(definition.Index)then
                                        local location=source.buildings:GetBuildingLocation(definition.Index)
                                        local district=snapshot.districts[location]
                                        local other=Map.GetPlotByIndex(location)
                                        if location~=plot:GetIndex()and district and district.working and other
                                            and Map.GetPlotDistance(other:GetX(),other:GetY(),recipient.object:GetX(),recipient.object:GetY())<=definition.RegionalRange then alreadyServed=true end
                                    end
                                end
                                if not alreadyServed and Map.GetPlotDistance(plot:GetX(),plot:GetY(),recipient.object:GetX(),recipient.object:GetY())<=definition.RegionalRange then b.amenityCities[#b.amenityCities+1]=id end
                            end
                        end
                        if stage==3 then site.third=b else site.fourth=b end
                    end
                end
            end
        end
        local supply=snapshot.Supply(plot,profile)
        site.baseCount=#supply.base;site.specialtyCount=#supply.specialty
        if c.materialCanonical then
            local potential={}
            for _,kind in ipairs({'base','specialty'})do for _,material in ipairs(supply[kind])do
                potential[kind..':'..material.plot]=material
            end end
            -- Inspect actual adjacent resources separately from Builder legality.
            -- Native registered inputs and improvement returns do not both test
            -- Improvement_ValidResources at runtime. A legacy/nonstandard host
            -- must not lose its real outgoing/incoming leg in this read-model.
            for _,p in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
                local resource=GameInfo.Resources[p:GetResourceType()]
                if resource and p:GetOwner()==pid and p:GetDistrictType()==-1
                    and PlayersVisibility[pid]:IsRevealed(p:GetX(),p:GetY())
                    and CSC_Adjacency.ResourceVisible(pid,p:GetResourceType())then
                    for _,kind in ipairs({'base','specialty'})do
                        local tag=kind=='base'and profile.base or profile.specialty
                        if CSC_Adjacency.HasTag(tag,resource.ResourceType)then
                            local structural=potential[kind..':'..p:GetIndex()]
                            local current=GameInfo.Improvements[p:GetImprovementType()]
                            local improvement=current and current.ImprovementType
                            local ready=current and not p:IsImprovementPillaged()and 0 or INF
                            if current and p:IsImprovementPillaged()and structural and structural.ready then ready=5 end
                            if not current and structural and structural.ready then
                                -- A future legal job earns only its declared,
                                -- registered legs. No guessed +1 input and no
                                -- automatic Industry/Corporation upgrade.
                                for _,candidate in ipairs(c.improvementJobs[resource.ResourceType]or{})do
                                    if candidate.ImprovementType~='IMPROVEMENT_INDUSTRY'
                                        and candidate.ImprovementType~='IMPROVEMENT_CORPORATION'
                                        and research('tech',candidate.PrereqTech)==0
                                        and research('civic',candidate.PrereqCivic)==0
                                        and ImprovementBuilder.CanHaveImprovement(p,candidate.Index,pid)then
                                        improvement=candidate.ImprovementType;ready=5;break
                                    end
                                end
                            end
                            local facts=readPlot(p);local workingCity=facts.workingCity
                            if workingCity==nil and Cities.GetPlotWorkingCity then
                                local ok,worker=pcall(Cities.GetPlotWorkingCity,p:GetIndex())
                                if ok and worker and worker:GetOwner()==pid then workingCity=worker:GetID()end
                            end
                            local record={kind=kind,plot=p:GetIndex(),city=workingCity,
                                worked=(facts.workers or 0)>0,ready=ready,transactions={}}
                            for _,transaction in pairs(c.materials)do
                                if transaction.quarter==profile.key and transaction.tag==tag then
                                    local selected=F.SelectMaterialLegs(transaction,improvement,ready)
                                    local definition=GameInfo.Buildings[transaction.producer]
                                    local intactOwner=definition and placed and placed.complete
                                        and city.buildings:HasBuilding(definition.Index)
                                        and not city.buildings:IsPillaged(definition.Index)
                                        and city.buildings:GetBuildingLocation(definition.Index)==plot:GetIndex()
                                    if intactOwner then for _,leg in ipairs(selected.legs)do
                                        -- Building-owned return modifiers remain
                                        -- live through district-only damage in
                                        -- the owned-land native fixture. Input
                                        -- receiving-building yields need the
                                        -- functioning host and keep stage timing.
                                        if leg.recipient=='IMPROVEMENT'then leg.producerReady=0 end
                                    end end
                                    record.transactions[transaction.producer]=selected
                                end
                            end
                            site.suppliers[#site.suppliers+1]=record
                        end
                    end
                end
            end
        else
        -- Legacy package/plain-record compatibility only. Current main CSC uses
        -- the directional catalogue above, including explicit empty leg maps.
        for _,kind in ipairs({'base','specialty'})do for _,material in ipairs(supply[kind])do
            local p=Map.GetPlotByIndex(material.plot);local owner=Cities.GetPlotPurchaseCity(p)
            local improvement=GameInfo.Improvements[p:GetImprovementType()]
            local multiplier=improvement and(improvement.ImprovementType=='IMPROVEMENT_CORPORATION'and 3
                or improvement.ImprovementType=='IMPROVEMENT_INDUSTRY'and 2)or 1
            -- Future Builder work has an explicit initial travel/job allowance;
            -- locked improvement ETA is unknown until its native job is viable.
            site.suppliers[#site.suppliers+1]={kind=kind,plot=material.plot,city=owner and owner:GetID()or city.id,
                ready=material.working and 0 or material.ready and 5 or INF,
                worked=(readPlot(p).workers or 0)>0,multiplier=multiplier}
        end end
        end
        for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
            local host=snapshot.districts[near:GetIndex()]
            if near:GetOwner()==pid and host and host.complete then
                local buyer=snapshot.cities[host.city]
                -- District return adjacency is a separate exchange from the
                -- later producer/customer-building transaction. Price it once.
                local reciprocal,reciprocalPercent={},{}
                for _,rule in ipairs(CSC_Adjacency.ByDistrict[GameInfo.Districts[host.type].DistrictType]or{})do
                    if rule.ProvideType=='SelfBonus'and rule.CustomAdjacentObject==profile.district.DistrictType
                        and rule.AdjacencyType=='FROM_RINGS_CAO_DISTRICT'and CSC_Adjacency.Eligible(rule,buyer.object,pid)then
                        reciprocal[rule.YieldType]=(reciprocal[rule.YieldType]or 0)+rule.YieldChange
                    elseif rule.ProvideType=='SelfMultiplier'and CSC_Adjacency.Eligible(rule,buyer.object,pid)then
                        reciprocalPercent[rule.YieldType]=(reciprocalPercent[rule.YieldType]or 0)
                            +CSC_Adjacency.Amount(rule,CSC_Adjacency.Count(rule,near,buyer.object,pid))
                    end
                end
                for yield,value in pairs(reciprocal)do
                    site.direct[#site.direct+1]={id='return:'..near:GetIndex()..':'..yield,yield=yield,
                        amount=value*(1+(reciprocalPercent[yield]or 0)/100),city=buyer.id,
                        -- The receiving customer already exists. A Quarter
                        -- foundation supplies this adjacency before its own
                        -- construction/producer investments finish.
                        ready=site.routeFoundationReady or 0}
                    if site.routeFoundationReady~=nil then site.direct[#site.direct].quarterStartKey=site.key end
                end
                local seen={}
                for _,mapping in ipairs(c.customers[profile.key]or{})do
                    local definition=resolve(mapping.BuildingType)
                    local expected=GameInfo.Districts[mapping.DistrictType]
                    local actual=GameInfo.Districts[host.type]
                    local matches=expected and(expected.Index==host.type)
                    if not matches and expected and GameInfo.DistrictReplaces then for r in GameInfo.DistrictReplaces()do
                        matches=matches or r.CivUniqueDistrictType==actual.DistrictType and r.ReplacesDistrictType==expected.DistrictType
                    end end
                    local stamp=near:GetIndex()..':'..mapping.ProducerStage..':'..mapping.BuildingType
                    if matches and definition and allowed(definition)and not seen[stamp]then
                        local customer=customerRecord(profile,buyer,definition,near:GetIndex(),mapping.ProducerStage)
                        if customer and(not flag(definition.IsWonder)or customer.working)then
                            customer.complete=true
                            site.customers[#site.customers+1]=customer;seen[stamp]=true
                        end
                    end
                end
            end
        end
        -- Other functioning sellers can already pay the same receiving-city
        -- property. Reconstruct their unrounded target from physical links;
        -- adding this candidate must price only the change after Q8 rounding.
        -- Rounded live property values cannot recover that raw target exactly.
        site.populationBaselines={}
        for _,customer in ipairs(site.customers)do if customer.stage==3 and customer.customerProperty then
            local venue=Map.GetPlotByIndex(customer.plot)
            local target=0
            for _,neighbor in ipairs(Map.GetAdjacentPlots(venue:GetX(),venue:GetY()))do
                local seller=snapshot.districts[neighbor:GetIndex()]
                local sellerCity=seller and snapshot.cities[seller.city]
                local definition=(stages[3]or{})[1]
                if seller and seller.working and seller.type==profile.district.Index
                    and neighbor:GetIndex()~=plot:GetIndex()and sellerCity and definition
                    and sellerCity.buildings:HasBuilding(definition.Index)
                    and not sellerCity.buildings:IsPillaged(definition.Index)
                    and sellerCity.buildings:GetBuildingLocation(definition.Index)==neighbor:GetIndex()then
                    target=target+customer.population*customer.rate
                end
            end
            site.populationBaselines[customer.city..':'..customer.yield..':'..customer.customerProperty]=target
        end end
        table.sort(site.customers,function(a,b)
            if a.stage~=b.stage then return a.stage<b.stage end
            if a.plot~=b.plot then return a.plot<b.plot end
            return a.building<b.building
        end)
        snapshot.sites[key]=site;return site
    end
    -- Existing chains and candidate sites share the same supply and district
    -- observations. Legacy/native protection adapters retain their policy bands.
    snapshot.chains=placement.ReadChains(player)
    for _,chain in ipairs(snapshot.chains)do
        chain.supply=snapshot.Supply(chain.plot,chain.profile)
        chain.economy=snapshot.Site(chain.city,chain.plot,chain.profile)
    end
    local customerWorlds={}
    function snapshot.CustomerCandidateSets(protectedPlots)
        -- Reverse gameplay partner edges from existing Quarters to legal owned
        -- customer footprints. Each city/type has an ordinary-adjacency reference
        -- and related alternatives. Policy chooses the bounded priced shortlist;
        -- this reader neither bids nor buys and retains no cross-turn targets.
        local groups={};local graph=F.CustomerQuarterMap()
        local auditTurn=Game.GetCurrentGameTurn()%25==0
        local query=snapshot.ui or ui
        if type(query.GetLegalDistrictTargets)~='function'then return {}end
        for _,chain in ipairs(snapshot.chains)do
            for district,mapping in pairs(graph)do
                local mapped=false
                for _,q in ipairs(mapping.quarters)do if q.key==chain.profile.key then mapped=true;break end end
                if mapped then for _,plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(),chain.plot:GetY()))do
                    local owner=plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
                    if owner and not protectedPlots[plot:GetIndex()]and plot:GetDistrictType()==-1 then
                        local key=owner:GetID()..':'..district
                        local group=groups[key]
                        if not group then
                            group={city=owner:GetID(),district=district,definition=mapping.definition,related={}}
                            groups[key]=group
                        end
                        local related=group.related[plot:GetIndex()]or{index=plot:GetIndex(),links=0}
                        related.links=related.links+1;group.related[plot:GetIndex()]=related
                    end
                end end
            end
        end
        local result={}
        for _,group in pairs(groups)do
            local city=snapshot.cities[group.city].object
            local unlocked=math.max(research('tech',group.definition.PrereqTech),research('civic',group.definition.PrereqCivic))==0
            if auditTurn then group.auditUnlocked=unlocked end
            if unlocked then
                local map=customerMap(city,group.definition,protectedPlots)
                local ok,targets=pcall(query.GetLegalDistrictTargets,pid,group.city,group.definition.Hash)
                if auditTurn then group.auditMap=map;group.auditTargetsAvailable=ok and type(targets)=='table' end
                if ok and type(targets)=='table'then
                    local admitted={};for _,index in ipairs(targets)do admitted[index]=true end
                    if auditTurn then group.auditAdmitted=admitted end
                    local choices={}
                    for _,row in ipairs(map.free)do if admitted[row.index]and not protectedPlots[row.index]then
                        local link=group.related[row.index]
                        choices[#choices+1]={plot=row.index,adjacency=row.adjacency,links=link and link.links or 0}
                    end end
                    -- customerMap sorts ordinary adjacency descending, then
                    -- plot index. This stable reference never reads our already
                    -- adjusted native score cache, avoiding feedback next turn.
                    if #choices>0 then
                        group.reference=choices[1];group.candidates={}
                        local related,other={},{}
                        for _,choice in ipairs(choices)do
                            local list=choice.links>0 and related or other;list[#list+1]=choice
                        end
                        table.sort(related,function(a,b)
                            if a.adjacency~=b.adjacency then return a.adjacency>b.adjacency end
                            if a.links~=b.links then return a.links>b.links end
                            return a.plot<b.plot
                        end)
                        -- Price both directions: a reference beside a Quarter
                        -- needs a negative comparison for its best unrelated
                        -- competitor. Alternate related/ordinary alternatives
                        -- so the small shortlist can improve either situation.
                        for i=1,math.max(#related,#other)do
                            if related[i]then group.candidates[#group.candidates+1]=related[i]end
                            if other[i]then group.candidates[#group.candidates+1]=other[i]end
                        end
                        if #related>0 then result[#result+1]=group end
                    end
                end
            end
        end
        if auditTurn then
            -- Passive coastal opportunity inventory: at most96 adjacent cells
            -- per player/25-turn census. Reuse maps/admission results computed
            -- above. Never ask for additional native legality/yield quotes or
            -- turn an unowned/locked footprint into an actionable bid.
            local harbors={DISTRICT_HARBOR=true}
            for row in GameInfo.DistrictReplaces()do
                if row.ReplacesDistrictType=='DISTRICT_HARBOR'then harbors[row.CivUniqueDistrictType]=true end
            end
            local records=0
            for _,chain in ipairs(snapshot.chains)do
                for district,mapping in pairs(graph)do
                    local mapped=false
                    for _,q in ipairs(mapping.quarters)do if q.key==chain.profile.key then mapped=true;break end end
                    if mapped and harbors[mapping.definition.DistrictType]then
                        for _,plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(),chain.plot:GetY()))do
                            if records<96 then
                                records=records+1
                                local owner=plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
                                local group=owner and groups[owner:GetID()..':'..district]
                                local row=group and group.auditMap and group.auditMap.plots[plot:GetIndex()]
                                local native=-1
                                if group and group.auditAdmitted then native=group.auditAdmitted[plot:GetIndex()]and 1 or 0 end
                                print(string.format('CSC_AI_CUSTOMER_OPPORTUNITY turn=%d player=%d quarter=%d quarterType=%s district=%d plot=%d owner=%d city=%d water=%s lake=%s occupied=%d resource=%d protected=%s unlocked=%s native=%d ordinaryAdjacency=%s reference=%d',
                                    Game.GetCurrentGameTurn(),pid,chain.plot:GetIndex(),chain.profile.key,district,plot:GetIndex(),
                                    plot:GetOwner(),owner and owner:GetID()or-1,tostring(plot:IsWater()),tostring(plot:IsLake()),
                                    plot:GetDistrictType(),plot:GetResourceType(),tostring(protectedPlots[plot:GetIndex()]~=nil),
                                    tostring(group and group.auditUnlocked),native,tostring(row and row.adjacency),
                                    group and group.reference and group.reference.plot or-1))
                            end
                        end
                    end
                end
            end
        end
        table.sort(result,function(a,b)if a.city~=b.city then return a.city<b.city end;return a.district<b.district end)
        return result
    end
    local currentWorld
    function snapshot.CurrentWorld()
        -- One immutable ordinary baseline per publication. Every marginal uses
        -- these exact sites and observed route counters; adapters may cache its
        -- priced plan for their snapshot's Price function, never across turns.
        if currentWorld then return currentWorld end
        if #snapshot.chains>64 then return nil,'Affected chain budget exceeded'end
        local world={player=pid,horizon=context and context.horizon or 50,
            sites={},populationBaselines={},extraStreams={}}
        for _,chain in ipairs(snapshot.chains)do
            if not chain.economy then return nil,'Existing Quarter economy unavailable'end
            world.sites[#world.sites+1]=chain.economy
        end
        local problem;world.trade,problem=snapshot.TradeWorld(world.sites)
        if not world.trade then return nil,problem end
        currentWorld=world;return world
    end
    local function investmentWorld(cityID,districtIndex,plotIndex,quarterSite)
        -- First correctness path: include ALL owned implemented chains. Queue
        -- sharing/population pools are not the only links: distant exporters
        -- can share a route counter or amenity recipient. A future component
        -- optimization must match this bounded full-world result. Never
        -- truncate its inventory or inherit single-site population baselines.
        local key=cityID..':'..districtIndex..':'..plotIndex..(quarterSite and ':quarter'or ':customer')
        if customerWorlds[key]then return customerWorlds[key][1],customerWorlds[key][2]end
        local buyer,definition,plot=snapshot.cities[cityID],GameInfo.Districts[districtIndex],Map.GetPlotByIndex(plotIndex)
        if not buyer or not definition or not plot or plot:GetOwner()~=pid and not(quarterSite and plot:GetOwner()==-1)then
            return nil,'Owned customer or owned/frontier Quarter footprint required'end
        local owner=Cities.GetPlotPurchaseCity(plot)
        if plot:GetOwner()==pid and(not owner or owner:GetOwner()~=pid or owner:GetID()~=cityID)then
            return nil,'Investment footprint belongs to another city'end
        if plot:GetDistrictType()~=-1 then return nil,'Customer footprint is occupied'end
        if definition.DistrictType=='DISTRICT_CITY_CENTER'or definition.DistrictType=='DISTRICT_WONDER'
            or not quarterSite and definition.DistrictType:match('^DISTRICT_CSC_.+_QUARTER$')then
            return nil,'Separate district investment adapter required'end
        local unlock=math.max(research('tech',definition.PrereqTech),research('civic',definition.PrereqCivic))
        if not quarterSite and unlock~=0 then return nil,'Customer district is not unlocked'end
        local duration=cityNumber(buyer.object,'districtTurns',districtIndex)
        local cost=cityNumber(buyer.object,'district',districtIndex)
        local ready=quarterSite and quarterSite.quarterReady or duration and math.max(1,duration)
            or cost and buyer.production and buyer.production>0 and math.max(1,math.ceil(cost/buyer.production))
        if not finite(ready)then return nil,'Customer construction timing unavailable'end
        local horizon=context and context.horizon or 50
        local function copy(source)local result={};for k,v in pairs(source)do result[k]=v end;return result end
        local before,baselineProblem=snapshot.CurrentWorld()
        if not before then return nil,baselineProblem end
        local after={player=pid,horizon=horizon,sites={},populationBaselines={},extraStreams={},
            baselineWorld=before,affectedChains={},
            -- A Quarter's own quarterWork is scheduled by the shared ledger.
            -- Customer districts need this root queue time before their venues.
            queueReady=not quarterSite and{[pid..':'..cityID]=ready}or nil}
        if #snapshot.chains>64 then return nil,'Affected chain budget exceeded'end
        -- Native PreCreateDistrict1029c0 rechecks zoning with/without resource
        -- removal. A visible deposit must be removed for an admitted fresh
        -- foundation. Hidden deposits may remain and are not counted by CSC's
        -- visible-resource adjacency matcher. Terrain/rivers remain unchanged.
        local resource=plot:GetResourceType()
        local resourceAfter=resource>=0 and CSC_Adjacency.ResourceVisible(pid,resource)and -1 or resource
        local projected=setmetatable({GetDistrictType=function()return districtIndex end,
            GetImprovementType=function()return -1 end,IsImprovementPillaged=function()return false end,
            GetResourceType=function()return resourceAfter end},{__index=function(_,name)
                local value=plot[name]
                if type(value)=='function'then return function(_,...)return value(plot,...)end end
                return value
            end})
        local function project(p)return p:GetIndex()==plotIndex and projected or p end
        local supported={FROM_RINGS_TYPETAG_RESOURCE=true,FROM_RINGS_TYPETAG_DISTRICT=true,
            FROM_RINGS_CAO_DISTRICT=true,FROM_RINGS_CAO_TERRAIN_SETS=true,FROM_RIVER_CROSSING=true}
        local function checkedAmounts(city,center,kind,projection)
            for _,rule in ipairs(CSC_Adjacency.ByDistrict[kind]or{})do
                if rule.ModifierOwner~='BuildingModifiers'and not supported[rule.AdjacencyType]then
                    return nil,'District projection source requires support: '..tostring(rule.AdjacencyType)
                end
            end
            return snapshot.AdjacencyAmounts(city,center,kind,projection)
        end
        for _,chain in ipairs(snapshot.chains)do
            local site=chain.economy
            if not site then return nil,'Existing Quarter economy unavailable'end
            local changed=copy(site);changed.service=nil;changed.suppliers={};changed.customers={}
            for _,supplier in ipairs(site.suppliers)do
                if supplier.plot~=plotIndex then changed.suppliers[#changed.suppliers+1]=supplier end
            end
            for _,customer in ipairs(site.customers)do changed.customers[#changed.customers+1]=customer end
            local adjacent=false
            for _,neighbor in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(),chain.plot:GetY()))do
                if neighbor:GetIndex()==plotIndex then adjacent=true;break end
            end
            if adjacent then
                after.affectedChains[site.key]=true
                for _,source in ipairs(snapshot.ProjectedCustomers(chain.profile,cityID,districtIndex,plotIndex))do
                    local venue=copy(source);venue.complete=true;venue.projected=true;venue.working=false;venue.intactOwner=false
                    venue.unlock=math.max(venue.unlock or INF,ready);venue.hostReady=ready
                    -- Keep ordinary upkeep/prerequisites in economic facts.
                    -- G4 reconciles native overlap; the older building-only
                    -- diagnostic's blanket expense removal is not used here.
                    changed.customers[#changed.customers+1]=venue
                end
            end
            after.sites[#after.sites+1]=changed
            if #changed.suppliers~=#site.suppliers then after.affectedChains[site.key]=true end
            local old,error=checkedAmounts(chain.city,chain.plot,chain.profile.district.DistrictType)
            if not old then return nil,error end
            local new,problem=checkedAmounts(chain.city,chain.plot,chain.profile.district.DistrictType,project)
            if not new then return nil,problem end
            local yields={};for yield in pairs(old)do yields[yield]=true end;for yield in pairs(new)do yields[yield]=true end
            for yield in pairs(yields)do
                local delta=(new[yield]or 0)-(old[yield]or 0)
                if delta~=0 then after.extraStreams[#after.extraStreams+1]={id='quarter-adjacency:'..site.key..':'..yield,
                    component='quarter-adjacency-externality',player=pid,city=site.city,yield=yield,amount=delta,
                    ready=0,quarterKey=site.key};after.affectedChains[site.key]=true end
            end
        end
        if quarterSite then
            local added=copy(quarterSite);added.service=nil
            after.sites[#after.sites+1]=added
            after.affectedChains[added.key]=true
            -- The question is the consequence of choosing this Quarter NOW.
            -- Schedule its root ahead of optional existing-chain investments;
            -- later shared work still queues normally and creates opportunity
            -- cost against the common baseline, without reserving native work.
            after.firstChainKey=added.key
        else
            local receiving,error=checkedAmounts(buyer.object,plot,definition.DistrictType,project)
            if not receiving then return nil,error end
            for yield,amount in pairs(receiving)do if amount~=0 then
                after.extraStreams[#after.extraStreams+1]={id='customer-adjacency:'..key..':'..yield,
                    component='customer-csc-adjacency',player=pid,city=cityID,yield=yield,amount=amount,ready=ready}
            end end
        end
        local problem
        after.trade,problem=snapshot.TradeWorld(after.sites,{removedPlot=plotIndex,ready=0})
        if not after.trade then return nil,problem end
        after.customer={city=cityID,district=districtIndex,plot=plotIndex,ready=ready,cost=cost}
        customerWorlds[key]={before,after}
        return before,after
    end
    function snapshot.CustomerWorld(cityID,districtIndex,plotIndex)
        return investmentWorld(cityID,districtIndex,plotIndex)
    end
    function snapshot.QuarterWorld(city,plot,profile,site)
        -- Candidate facts may contain a continuity-adjusted footprint invoice;
        -- keep that exact candidate as the new investment. The pair is not
        -- cached because the adapter can revise those same-footprint terms.
        local key=city:GetID()..':'..profile.district.Index..':'..plot:GetIndex()..':quarter'
        customerWorlds[key]=nil
        return investmentWorld(city:GetID(),profile.district.Index,plot:GetIndex(),site)
    end
    return snapshot
end
