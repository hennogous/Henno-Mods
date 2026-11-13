-- Live-to-model boundary. Build one player/publication snapshot of definitions,
-- research costs, cities and completed district footprints. The economic model
-- consumes plain records; decision adapters never reinterpret these facts.
-- Static catalogues persist for the session. Ownership, production, research,
-- completion, supply and quotes never persist past this snapshot.
CSC_AI_EconomyFacts={}
local F=CSC_AI_EconomyFacts
local INF=math.huge
local catalogue
local function numeric(value)return type(value)=='number'or type(value)=='integer'end
local function finite(value)return numeric(value)and value==value and value>=0 and value<INF end
local function number(object,name,...)
    if not object or type(object[name])~='function'then return nil end
    local ok,value=pcall(object[name],object,...)
    if ok and finite(value)then return value end
end
local function flag(v)return v==true or v==1 end

local families={BAKERS={yield='YIELD_FOOD'},TAILORS={yield='YIELD_CULTURE'}}
-- This first ledger supports the current unit-transfer contracts. Check the
-- loaded leaf amounts instead of silently retaining a stale +1 after another
-- mod changes them. A different economy is unavailable, not worth zero. The
-- population branch below reads its actual fractional rate independently.
local unitContracts={
    BAKERS={'MOD_CSC_ALL_PROD_TO_PLOT','MOD_CSC_ALL_GOLD_TO_PLOT',
        'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WATER_MILL','MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY','MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL','MOD_CSC_BAKERS_GOLD_TO_WATER_MILL','MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY','MOD_CSC_BAKERS_FOOD_TO_CAFE'},
    TAILORS={'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP','MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE',
        'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE','MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',
        'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE','MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP','MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE','MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP','MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP'}}
local function definitions()
    if catalogue then return catalogue end
    local c={stages={},customers={},population={},replacements={},tech={},civic={},amounts={},prerequisites={},exclusives={}}
    for row in GameInfo.ModifierArguments()do
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
    for row in GameInfo.CSC_QuarterCustomerBuildings()do
        local p=c.customers[row.QuarterKey]or{};c.customers[row.QuarterKey]=p
        p[#p+1]=row
    end
    if GameInfo.CSC_Stage3CustomerTransactions then
        for row in GameInfo.CSC_Stage3CustomerTransactions()do
            c.population[row.SellerBuildingType..':'..row.CustomerBuildingType]=row
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
    for family,roots in pairs(unitContracts)do for _,root in ipairs(roots)do
        if c.amounts[root]~=1 then c.unsupported[family]='Unsupported loaded transaction amount: '..root end
    end end
    catalogue=c;return c
end

function F.New(player,placement,ui)
    local c=definitions();local pid=player:GetID()
    local snapshot={player=player,id=pid,cities={},districts={},supplies={},research={},sites={},quotes={}}
    local numericFacts,plotFacts={},{}
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
            else value=number(city:GetBuildQueue(),kind=='building'and'GetBuildingCost'or'GetDistrictCost',index)end
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
                if finite(value.workers)then facts.workers=value.workers end
                for yield,amount in pairs(value.yields or{})do
                    if numeric(amount)and amount==amount and math.abs(amount)<INF then facts.yields[yield]=amount end
                end
            end
            plotFacts[index]=facts
        end
        return plotFacts[index]
    end
    snapshot.PlotFacts=readPlot
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
    for _,city in player:GetCities():Members()do
        local row={object=city,id=city:GetID(),population=city:GetPopulation(),queue=city:GetBuildQueue(),
            buildings=city:GetBuildings(),production=cityNumber(city,'yield',GameInfo.Yields.YIELD_PRODUCTION.Index)}
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
    function snapshot.DirectAmounts(city,plot,profile,removed)
        local sums,percents={},{}
        local function project(p,rule)
            if p:GetIndex()==removed then return nil end
            if rule.AdjacencyType:find('DISTRICT',1,true)or rule.AdjacencyType:find('WONDER',1,true)then
                local district=snapshot.districts[p:GetIndex()]
                if not district or not district.complete then return nil end
            end
            return p
        end
        for _,rule in ipairs(CSC_Adjacency.ByDistrict[profile.district.DistrictType]or{})do
            if rule.ModifierOwner~='BuildingModifiers'and CSC_Adjacency.Eligible(rule,city,pid)then
                local amount=CSC_Adjacency.Amount(rule,CSC_Adjacency.Count(rule,plot,city,pid,project))
                if rule.ProvideType=='SelfBonus'then sums[rule.YieldType]=(sums[rule.YieldType]or 0)+amount
                elseif rule.ProvideType=='SelfMultiplier'then percents[rule.YieldType]=(percents[rule.YieldType]or 0)+amount end
            end
        end
        local raw={};for yield,amount in pairs(sums)do raw[yield]=amount;sums[yield]=amount*(1+(percents[yield]or 0)/100)end
        return sums,percents,raw
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
        local result={direct=direct,mills={},base=(direct.YIELD_PRODUCTION or 0)+(direct.YIELD_GOLD or 0)}
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
        local works=host and host.working and city.buildings:HasBuilding(definition.Index)and not city.buildings:IsPillaged(definition.Index)
            and city.buildings:GetBuildingLocation(definition.Index)==plot
        local cost=cityNumber(city.object,'building',definition.Index)
        local unlocked=math.max(research('tech',definition.PrereqTech),research('civic',definition.PrereqCivic))
        local b={type=definition.BuildingType,working=works,unlock=works and 0 or unlocked,cost=cost,
            turns=cost and city.production and city.production>0 and math.max(1,math.ceil(cost/city.production))or INF,
            maintenance=definition.Maintenance or 0}
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
    function snapshot.Site(cityObject,plot,profile)
        local key=cityObject:GetID()..':'..profile.key..':'..plot:GetIndex()
        if snapshot.sites[key]then return snapshot.sites[key]end
        local family=families[profile.key];if not family then return nil,'No economic family rules'end
        if c.unsupported[profile.key]then return nil,c.unsupported[profile.key]end
        local city=assert(snapshot.cities[cityObject:GetID()])
        local placed=snapshot.districts[plot:GetIndex()]
        local exists=placed and placed.type==profile.district.Index and placed.working
        local cost=cityNumber(cityObject,'district',profile.district.Index)
        local qUnlock=math.max(research('tech',profile.district.PrereqTech),research('civic',profile.district.PrereqCivic))
        local qReady=exists and 0 or cost and city.production and city.production>0
            and qUnlock+math.max(1,math.ceil(cost/city.production))or INF
        local site={city=city.id,population=city.population,horizon=50,quarterReady=qReady,adjacency=0,
            maintenance=profile.district.Maintenance or 0,existing=exists,materialYield=family.yield,
            direct={},suppliers={},customers={},seconds={},omissions={
                'Future specialist staffing, trade-route changes and Service premiums are not priced in this ordinary-transaction bid'}}
        -- Covering a worked tile removes its observed ordinary income. This
        -- is separate from protecting deposits that sustain another Quarter.
        -- Do not invent staffing for an unworked footprint or a harvest payout.
        local footprint=readPlot(plot)
        if footprint.workers==nil then return nil,'Footprint staffing unavailable'end
        if not exists and footprint.workers>0 then
            for yield in GameInfo.Yields()do
                if yield.YieldType~='YIELD_CSC_AI_PLACEMENT'then
                    local amount=footprint.yields[yield.YieldType]or number(plot,'GetYield',yield.Index)
                    if amount and amount>0 then site.direct[#site.direct+1]={id='displaced:'..yield.YieldType,yield=yield.YieldType,amount=-amount}end
                end
            end
        end
        local geometry=snapshot.Geometry(cityObject,plot,profile)
        for yield,amount in pairs(geometry.direct)do
            site.direct[#site.direct+1]={id=yield,yield=yield,amount=amount}
            if yield=='YIELD_PRODUCTION'or yield=='YIELD_GOLD'then site.adjacency=site.adjacency+amount end
        end
        local stages=c.stages[profile.key]or{}
        for stage=2,4 do
            for _,definition in ipairs(stages[stage]or{})do
                if allowed(definition)and not flag(definition.MustPurchase)then
                    local b=building(city,definition,plot:GetIndex())
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
                        amount=value*(1+(reciprocalPercent[yield]or 0)/100),city=buyer.id}
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
                    local stamp=near:GetIndex()..':'..mapping.ProducerStage
                    if matches and definition and allowed(definition)and not seen[stamp]then
                        local customer=futureCustomer(buyer,definition,near:GetIndex())
                        if not flag(definition.IsWonder)or customer.working then
                            customer.stage=mapping.ProducerStage;customer.complete=true
                            customer.yield=customer.stage==2 and(profile.key=='BAKERS'and'YIELD_FOOD'or'YIELD_PRODUCTION')or customer.stage==4 and'YIELD_CULTURE'or family.yield
                            local seller=(stages[3]or{})[1]
                            local transaction=seller and c.population[seller.BuildingType..':'..mapping.BuildingType]
                            customer.rate=transaction and transaction.EngineAmountPerPopulation
                            customer.sellerProperty=transaction and transaction.SellerReturnAmountProperty
                            customer.customerProperty=transaction and transaction.CustomerYieldAmountProperty
                            if customer.stage~=3 or customer.rate then site.customers[#site.customers+1]=customer;seen[stamp]=true end
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
    return snapshot
end
