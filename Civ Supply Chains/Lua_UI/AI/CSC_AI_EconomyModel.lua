-- Central CSC economic ledger. The facts adapter supplies physical footprints,
-- available investments and relative ready times; this module owns transaction
-- application, recipients, alternatives and marginal values. It never reads a game
-- object, publishes a bid, grants anything or assumes an unbuilt district.
-- A pricing adapter converts recurring yields/amenities and admitted Service
-- effects to native Q8 utility. Quarter worlds opt into Service forecasting;
-- ordinary customer worlds retain their separate, Service-free comparison.
-- Keep that conversion outside the rules so district and building decisions
-- can consume the same ledger without maintaining separate CSC economies.
CSC_AI_EconomyModel = {}
local M = CSC_AI_EconomyModel
local INF = math.huge

local function maximum(...) return math.max(...) end
local function numeric(value)return type(value)=='number'or type(value)=='integer'end
local function present(value) return numeric(value) and value>=0 and value<INF end
local function ownerReady(definition,fallback)
    return definition and(definition.working or definition.intactOwner)and 0 or fallback
end

local function transactionCity(leg,site,customer)
    if leg.recipient=='SOURCE'then return site.city,site.population end
    return customer.city,customer.population
end

local function serviceRate(service)
    local yield,amount=service.kind,service.amount
    if yield=='YIELD_PERCENT'or yield=='NAVAL_PRODUCTION_PERCENT'then
        amount=(service.base or 0)*amount/100
        yield=yield=='YIELD_PERCENT'and service.yieldType or'YIELD_PRODUCTION'
    end
    return yield,amount
end

-- Gameplay pays population returns using a Q8 per-receiving-citizen rate.
-- Round the combined target once, independently for each receiving city.
function M.PopulationPayout(target, population)
    if target<=0 or population<=0 then return 0 end
    return math.min(32767,math.ceil(target/population*256-1e-9))*population/256
end

local function newLedger(site,second)
    return {result={streams={},investments={},omissions={},byBuilding={},futureDepths={},alternative=second and second.type,
        siteAdjustmentQ8=site.nativeSiteAdjustmentQ8 or 0,
        adjacency=(site.adjacency or 0)+(second and second.terrain or 0),quarterReadyByChain={},quarterStartByChain={}},
        seen={},clocks={},populationFlows={}}
end

-- Finalize only after every affected chain has contributed its unrounded
-- targets. A shared recipient/property must be rounded once at each completion
-- time. Contributor metadata retains who enabled the pool; the last flow never
-- acquires ownership of the whole pooled benefit or its building-depth premium.
local function finishLedger(context)
    local result=context.result
    for key,flows in pairs(context.populationFlows)do
        table.sort(flows,function(a,b)return a.ready<b.ready or a.ready==b.ready and a.id<b.id end)
        local target=context.populationBaselines and context.populationBaselines[key]or 0
        local paid=M.PopulationPayout(target,flows[1].population)
        local contributors={}
        for i,flow in ipairs(flows)do
            if not present(flow.population)or flow.population<=0
                or flow.population~=flows[1].population or flow.multiplier~=flows[1].multiplier then
                return nil,'Inconsistent shared population contract: '..key
            end
            target=target+flow.target
            contributors[#contributors+1]={id=flow.id,investmentKey=flow.investmentKey,target=flow.target}
            if i==#flows or flows[i+1].ready~=flow.ready then
                local payout=M.PopulationPayout(target,flow.population)
                local amount=(payout-paid)*flow.multiplier
                if amount~=0 then
                    local stream={id='population:'..key..':'..flow.ready,yield=flow.yield,amount=amount,
                        ready=flow.ready,city=flow.city,player=flow.player,contributors={}}
                    for _,v in ipairs(contributors)do stream.contributors[#stream.contributors+1]=v end
                    if not context.joint then
                        stream.building=flow.building;stream.investmentBuilding=flow.building
                        stream.investmentKey=flow.investmentKey
                    end
                    result.streams[#result.streams+1]=stream
                end
                paid=payout
            end
        end
    end
    for _,stream in ipairs(result.streams)do
        local depthKey=context.joint and stream.investmentKey or stream.building
        if not stream.service and not stream.existingIncome and stream.amount>0 and stream.yield:find('YIELD_',1,true)==1
            and depthKey and result.futureDepths[depthKey]~=nil then
            stream.forecastDepth=result.futureDepths[depthKey]
        end
    end
    return result
end

local function ledger(site, second, shared)
    local context=shared or newLedger(site,second)
    local result=context.result
    local seen,clocks,populationFlows,customerTimes=context.seen,context.clocks,context.populationFlows,{}
    local quarter=site.quarterReady
    local function cityKey(city)return context.joint and tostring(site.player or 0)..':'..city or tostring(city)end
    local function investmentKey(city,building)return cityKey(city)..':'..building end
    local function emit(id,yield,amount,ready,city,building,recipientBuilding,investmentCity)
        if amount==0 or not present(ready) or ready>=site.horizon then return end
        if context.joint and id:sub(1,7)~='upkeep:'then id=site.key..'/'..id end
        if seen[id]and context.joint then
            context.error='Duplicate economic relationship: '..id;return
        end
        assert(not seen[id],'Duplicate economic relationship: '..id)
        seen[id]=true
        result.streams[#result.streams+1]={id=id,yield=yield,amount=amount,ready=ready,
            city=city or site.city,player=site.player,building=building,investmentBuilding=building,
            investmentKey=building and investmentKey(investmentCity or site.city,building),recipientBuilding=recipientBuilding}
        return result.streams[#result.streams]
    end
    local function omit(id,reason)
        result.omissions[#result.omissions+1]={id=id,reason=reason}
    end
    local function invest(definition,prerequisite,recipient)
        if not definition then return INF end
        recipient=recipient or site.city
        local stamp=investmentKey(recipient,definition.type)
        if result.byBuilding[stamp]~=nil then return result.byBuilding[stamp]end
        if context.disabledBuildings and context.disabledBuildings[stamp]
            and not definition.working and not definition.intactOwner then return INF end
        local ready
        if definition.working then ready=0
        elseif definition.intactOwner and present(definition.hostReady)then
            -- Restoring the Quarter does not rebuild an intact producer or
            -- repay its upkeep. Existing stages also do not need their original
            -- construction prerequisites rebuilt before they can resume.
            ready=definition.hostQuarter==site.key and site.key~=nil and quarter or definition.hostReady
        elseif definition.excluded then return INF
        elseif present(definition.unlock) and present(definition.turns) and present(prerequisite) then
            for _,required in ipairs(definition.prerequisites or {})do
                prerequisite=maximum(prerequisite,invest(required,prerequisite,recipient))
            end
            if not present(prerequisite)then omit(definition.type,'Required investment unavailable');return INF end
            ready=maximum(definition.unlock,prerequisite,clocks[cityKey(recipient)]or 0)+definition.turns
            clocks[cityKey(recipient)]=ready
        else omit(definition.type,'Unknown unlock, construction or prerequisite timing');return INF end
        result.byBuilding[stamp]=ready
        if not definition.working and not definition.intactOwner then
            result.futureDepths[context.joint and stamp or definition.type]=definition.forecastDepth or 0
        end
        if ready>0 and not definition.intactOwner then result.investments[#result.investments+1]={type=definition.type,
            ready=ready,cost=definition.cost or 0,city=recipient,player=site.player,key=stamp} end
        -- Production cost is represented by serial construction delay, matching
        -- the native income-stream convention. Do not also subtract the whole
        -- cost as an invented universal utility conversion. Upkeep is a real
        -- recurring cost and starts with the building, not at Quarter placement.
        if not definition.working and not definition.intactOwner then emit('upkeep:'..stamp,'YIELD_GOLD',
            -(definition.maintenance or 0),ready,recipient,definition.type,nil,recipient) end
        return ready
    end
    if not present(quarter) then omit('quarter','Unknown Quarter readiness');return result end
    -- A prospective customer district occupies its city's queue before its
    -- buildings. This plain-record reservation is shared by both sides of a
    -- marginal comparison; it does not reserve native production or delay an
    -- already working building. Separate cities can still invest in parallel.
    for city,ready in pairs(site.queueReady or{})do
        if present(ready)then clocks[cityKey(city)]=maximum(clocks[cityKey(city)]or 0,ready)end
    end
    local quarterStart=0
    if site.quarterWork then
        -- Unfinished/repairing Quarters also consume the city's ONE queue.
        -- Absolute standalone ETAs cannot be combined with a customer-first
        -- reservation: that would build two districts concurrently. Schedule
        -- remaining root work here, then use this time for dependent hosts,
        -- adjacency receivers and route repair events throughout the ledger.
        local work=site.quarterWork
        if not present(work.unlock)or not present(work.turns)then
            context.error='Quarter construction work unavailable'
            if not shared then return nil,context.error end
            return result
        end
        quarterStart=maximum(clocks[cityKey(site.city)]or 0,work.unlock)
        quarter=quarterStart+work.turns
    end
    clocks[cityKey(site.city)]=maximum(clocks[cityKey(site.city)]or 0,quarter)
    if site.key then
        result.quarterReadyByChain[site.key]=quarter;result.quarterStartByChain[site.key]=quarterStart
    end
    for _,flow in ipairs(site.direct or {})do
        local ready=flow.ready==nil and quarter or flow.ready
        if flow.quarterStartKey then ready=maximum(ready,result.quarterStartByChain[flow.quarterStartKey]or INF)end
        local stream=emit('site:'..flow.id,flow.yield,flow.amount,ready,flow.city)
        -- The fallback loses worked yields when the footprint is built over.
        -- Pricing marks these alongside the native footprint adjustment so
        -- the placement adapter can preserve the charge through its cap.
        if stream and flow.id:sub(1,10)=='displaced:'then stream.footprint=true end
    end
    if not site.existing then emit('quarter-upkeep','YIELD_GOLD',-(site.maintenance or 0),quarter)end
    if (site.purchaseGold or 0)>0 then
        local invoice=emit('footprint-purchase','YIELD_GOLD',-site.purchaseGold,0,site.city)
        if invoice then invoice.fixed=true;invoice.footprint=true end
    end
    local stages={}
    local function populationFlow(id,yield,target,ready,city,population,property,building,multiplier)
        if not present(ready)or ready>=site.horizon or target<=0 then return end
        local key=cityKey(city)..':'..yield..':'..tostring(property or id)
        local list=populationFlows[key]or{};populationFlows[key]=list
        list[#list+1]={id=(context.joint and site.key..'/'or'')..id,yield=yield,target=target,ready=ready,
            city=city,player=site.player,population=population,building=building,multiplier=multiplier or 1,
            investmentKey=building and investmentKey(site.city,building)}
    end
    -- A city's single production queue is shared by producers, their missing
    -- prerequisite buildings and customers. Finish a stage's customer links
    -- before planning the next stage; separate cities can build in parallel.
    for stage=2,4 do
        local definition
        if stage==2 then definition=second elseif stage==3 then definition=site.third else definition=site.fourth end
        local prerequisite=stage==2 and quarter or stages[2]
        stages[stage]=invest(definition,prerequisite)
        for _,customer in ipairs(site.customers or {})do if customer.stage==stage and customer.complete==true then
            if customer.type then customerTimes[customer]=customer.working and 0
                or present(stages[stage])and invest(customer,0,customer.city)or INF
            elseif customer.city==site.city and not customer.working and present(customer.unlock)and present(customer.turns)then
                customerTimes[customer]=maximum(clocks[cityKey(customer.city)]or 0,customer.unlock,stages[stage])+customer.turns
                clocks[cityKey(customer.city)]=customerTimes[customer]
            else customerTimes[customer]=customer.ready or INF end
        end end
    end
    if context.joint then
        result.chainStages[site.key]={second=second and second.type,third=site.third and site.third.type,
            fourth=site.fourth and site.fourth.type,ready={[2]=stages[2],[3]=stages[3],[4]=stages[4]}}
    end
    -- Slots are capacity, not workers. Keep only observed assignments and the
    -- gameplay-owned ordinary citizen rates supplied by Facts. Existing rows
    -- are baseline income; an actually missing building can improve those same
    -- workers at its scheduled completion. No Service-building rate or assumed
    -- future assignment is introduced by this ledger.
    local specialists=site.specialists
    if specialists and(specialists.workers or 0)>0 then
        for yield,amount in pairs(specialists.base or{})do
            emit('specialist-base:'..yield,yield,amount*specialists.workers,0,specialists.city)
        end
        for stage=2,4 do
            local definition=stage==2 and second or stage==3 and site.third or stage==4 and site.fourth
            if definition and not(specialists.presentBuildings or{})[definition.type]then
                for yield,amount in pairs((specialists.buildings or{})[definition.type]or{})do
                    emit('specialist-building:'..definition.type..':'..yield,yield,amount*specialists.workers,
                        stages[stage],specialists.city,definition.type)
                end
            end
        end
    end
    local ready2=stages[2]
    if second then emit('producer-terrain','YIELD_PRODUCTION',second.terrain or 0,ready2,site.city,second.type)end
    for _,supplier in ipairs(site.suppliers or {})do
        local stage=supplier.kind=='base' and 2 or 4
        local start=maximum(stages[stage],supplier.ready or INF)
        local producer=stage==2 and second or site.fourth
        if supplier.transactions then
            -- Canonical directional legs already contain native host selection.
            -- An incoming attachment and an outgoing plot modifier can qualify
            -- independently. Industry/Corporation increments are summed, never
            -- inferred from the improvement's name or a universal multiplier.
            local transaction=producer and supplier.transactions[producer.type]
            if transaction then for _,leg in ipairs(transaction.legs)do
                -- A building-owned plot return can survive host-district damage
                -- while material input into that district stops. Facts may give
                -- an observed intact owner's readiness independently; a missing
                -- or pillaged producer still uses the scheduled stage/repair.
                local ready=maximum(leg.producerReady or stages[stage],leg.ready or INF)
                local identity='material:'..transaction.id..':'..supplier.plot..':'..leg.key
                if leg.recipient=='PRODUCER'then
                    emit(identity,leg.yield,leg.amount,ready,site.city,producer.type,producer.type)
                elseif supplier.worked and supplier.city then
                    local stream=emit(identity,leg.yield,leg.amount,ready,supplier.city,producer.type)
                    if stream then stream.existingIncome=leg.producerReady==0 end
                else omit(identity,'No observed working citizen/city; plot yield is not free city income')end
            end end
        else
        -- Legacy plain-record compatibility. Shipping facts always supply the
        -- canonical map, including an empty map when no native leg qualifies.
        local mult=supplier.multiplier or 1
        local supplyKey=supplier.kind..':'..supplier.plot
        local rates=supplier.rates or {input=1,production=1,gold=1}
        emit('material-input:'..supplyKey,site.materialYield,mult*rates.input,start,site.city,
            stage==2 and second and second.type or site.fourth and site.fourth.type)
        -- Improvement returns are tile yields: a supplied but unworked plot
        -- still feeds its producer, but earns no assumed worked-tile payout.
        if supplier.worked then
            emit('material-production:'..supplyKey,'YIELD_PRODUCTION',mult*rates.production,start,supplier.city)
            emit('material-gold:'..supplyKey,'YIELD_GOLD',mult*rates.gold,start,supplier.city)
        else omit('material-output:'..supplyKey,'No observed worker; no free future staffing')end
        end
    end
    for _,stage in ipairs({3,4})do
        local definition
        if stage==3 then definition=site.third else definition=site.fourth end
        if definition then
            local start=maximum(ready2,stages[stage])
            -- The selected Stage2 alternative is the only local recipient.
            -- Never credit both mutually-exclusive Mills for one transaction.
            if definition.localTransactions then
                local transaction=second and definition.localTransactions[second.type]
                if transaction then for _,leg in ipairs(transaction.legs)do
                    local recipient=leg.recipient=='SOURCE'and second.type or definition.type
                    -- Recipient is the actual upstream/downstream building.
                    -- Investment attribution remains the enabling later stage,
                    -- preserving the existing future-building utility convention.
                    -- SAME_CITY leaves are attached directly to buildings and
                    -- have no district-functioning filter. Intact existing
                    -- endpoints can exchange while their Quarter is damaged.
                    local flowReady=maximum(ownerReady(second,ready2),ownerReady(definition,stages[stage]))
                    emit('local:'..transaction.id..':'..leg.key,leg.yield,transaction.amount*leg.amount,
                        flowReady,site.city,definition.type,recipient)
                end end
            else
                -- Historical plain-record fixture/old-package compatibility.
                -- Current shipping facts always supply the canonical map, even
                -- when empty, so missing definitions never invent unit exchanges.
                local rates=definition.rates or {production=1,gold=1,outward=1}
                emit('local-production:'..stage,'YIELD_PRODUCTION',rates.production,start,site.city,definition.type)
                emit('local-gold:'..stage,'YIELD_GOLD',rates.gold,start,site.city,definition.type)
                emit('local-return:'..stage,site.materialYield,rates.outward,start,site.city,definition.type)
            end
            for _,beneficiary in ipairs(definition.amenityCities or {})do
                emit('amenity:'..stage..':'..beneficiary,'AMENITY',definition.amenityAmount or 0,stages[stage],beneficiary,definition.type)
                if context.joint and definition.working and (definition.amenityAmount or 0)~=0
                    and present(stages[stage])and stages[stage]<site.horizon then
                    -- These amenities already affect the native city baseline.
                    -- The joint quote pools all streams before pricing; retain
                    -- their current contribution so it is not granted again.
                    result.streams[#result.streams].amenityBaseline=definition.amenityAmount
                end
            end
        end
    end
    for _,customer in ipairs(site.customers or {})do
        local stage=customer.stage
        if customer.complete~=true then
            omit('customer:'..customer.plot..':'..stage,'Customer district is not complete')
        else
            local customerReady=customerTimes[customer] or INF
            local start=maximum(stages[stage] or INF,customerReady)
            local quantity=1
            local outward=customer.yield or site.materialYield
            local sellerAmount,buyerAmount
            local producer=stage==2 and second or stage==3 and site.third or site.fourth
            local transaction=customer.transaction
            if customer.transactions then transaction=producer and customer.transactions[producer.type]end
            if transaction and producer then
                -- Ordinary population exchanges share the actual gameplay
                -- header/legs. Round quantity by its property first; multiplying
                -- a target before Q8 rounding would change the native payout.
                local quantity=transaction.amount
                if transaction.kind=='PARTNER_POPULATION'then quantity=quantity*(customer.population or 0)end
                if transaction.kind=='PARTNER_POPULATION_STEPS'then
                    quantity=transaction.amount*math.floor((customer.population or 0)/transaction.step)
                end
                local producer=stage==2 and second or stage==3 and site.third or site.fourth
                local owner=producer and producer.type
                for _,leg in ipairs(transaction.legs)do
                    local city,population=transactionCity(leg,site,customer)
                    local identity='transaction:'..transaction.id..':'..customer.plot..':'..leg.key
                    if transaction.kind=='PARTNER_POPULATION'then
                        populationFlow(identity,leg.yield,quantity,start,city,population,leg.property,owner,leg.amount)
                    else
                        local recipient=leg.recipient=='SOURCE'and producer.type or customer.type
                        local flowReady=start
                        if transaction.kind=='FIXED'then
                            -- An intact modifier owner does not require its own
                            -- district restored. The opposite district remains
                            -- subject to the wrapper's functioning-type check.
                            -- Keep the two directions independent under damage.
                            flowReady=maximum(leg.ownerSide=='SOURCE'and ownerReady(producer,stages[stage])or stages[stage],
                                leg.ownerSide=='PARTNER'and ownerReady(customer,customerReady)or customerReady)
                        end
                        emit(identity,leg.yield,quantity*leg.amount,flowReady,city,owner,recipient)
                    end
                end
                sellerAmount,buyerAmount=0,0
            elseif customer.transactions then
                omit('customer-contract:'..customer.plot..':'..stage,'No transaction for the selected producer')
                sellerAmount,buyerAmount=0,0
            elseif stage==3 then
                quantity=(customer.population or 0)*(customer.rate or 0)
                -- Gameplay rounds the sum once per recipient/property, not
                -- once per edge. Emit changes in that aggregate at each ready
                -- time, so adding a second venue cannot round twice.
                local owner=site.third and site.third.type
                populationFlow('sale-production','YIELD_PRODUCTION',quantity,start,site.city,site.population,customer.sellerProperty,owner)
                populationFlow('sale-gold','YIELD_GOLD',quantity,start,site.city,site.population,customer.sellerProperty,owner)
                populationFlow('sale-return',outward,quantity,start,customer.city,customer.population or 0,customer.customerProperty,owner)
                sellerAmount,buyerAmount=0,0
            elseif stage==4 then
                quantity=math.floor((customer.population or 0)/5)
                sellerAmount,buyerAmount=quantity,quantity
            elseif not customer.transactions then
                local rates=customer.rates or {production=1,gold=1,outward=1}
                sellerAmount,buyerAmount=quantity,quantity
                local producer=stage==2 and second or stage==3 and site.third or site.fourth
                local owner=producer and producer.type
                emit('sale-production:'..customer.plot..':'..stage..':'..tostring(customer.building),'YIELD_PRODUCTION',rates.production*quantity,start,site.city,owner)
                emit('sale-gold:'..customer.plot..':'..stage..':'..tostring(customer.building),'YIELD_GOLD',rates.gold*quantity,start,site.city,owner)
                emit('sale-return:'..customer.plot..':'..stage..':'..tostring(customer.building),outward,rates.outward*quantity,start,customer.city,owner)
                sellerAmount,buyerAmount=0,0
            end
            local key=customer.plot..':'..stage..':'..tostring(customer.building)
            local producer=stage==2 and second or stage==3 and site.third or site.fourth
            local owner=producer and producer.type
            emit('sale-production:'..key,'YIELD_PRODUCTION',sellerAmount,start,site.city,owner)
            emit('sale-gold:'..key,'YIELD_GOLD',sellerAmount,start,site.city,owner)
            emit('sale-return:'..key,outward,buyerAmount,start,customer.city,owner)
            if customer.investment then result.investments[#result.investments+1]=customer.investment end
        end
    end
    -- Services are gated benefits, not extra unconditional Quarter yields.
    -- A complete existing customer footprint, scheduled buyer/producer, one
    -- credible Base supplier and civic ETA must all fit. Keep percentage units
    -- here; the decision adapter prices growth/naval capacity in yield utility.
    -- One recipient benefit is counted once even with duplicate mapping rows.
    if site.service and not context.joint then
        local supplierReady=INF
        for _,supplier in ipairs(site.suppliers or{})do if supplier.kind=='base'then
            supplierReady=math.min(supplierReady,supplier.ready or INF)
        end end
        local recipients={}
        for _,customer in ipairs(site.customers or{})do
            if customer.stage==2 and customer.complete and customer.serviceInputKnown~=false
                and not customer.serviceActive and not recipients[customer.city]then
                local ready=maximum(ready2,customerTimes[customer]or INF,supplierReady,site.service.unlock or INF)
                if present(ready)and ready<site.horizon then
                    emit('service:'..site.service.kind..':'..customer.city,site.service.kind,
                        site.service.amount,ready,customer.city)
                    if site.service.kind=='NAVAL_PRODUCTION_PERCENT'then
                        -- An observed ship queue is evidence for a short use,
                        -- not fifty turns of uninterrupted naval construction.
                        result.streams[#result.streams].finish=math.min(site.horizon,ready+10)
                    end
                    recipients[customer.city]=true
                end
            end
        end
    end
    if context.joint and context.includeServices then
        -- Each contribution belongs to one physical producer, attachment root
        -- and recipient PLOT. Same leaves can legitimately pay from different
        -- sources/stages; duplicated venue mappings cannot pay twice. Keep
        -- active benefits in both worlds so shared income cancels, and losing
        -- the actual last supplier removes the benefit in the after-world.
        for _,service in ipairs(site.services or{})do
            local producer=service.stage==2 and second or service.stage==3 and site.third or site.fourth
            local ready=maximum(stages[service.stage]or INF,customerTimes[service.customer]or INF,service.unlock or INF)
            for kind,count in pairs(service.materials or{})do
                local times={}
                for _,supplier in ipairs(site.suppliers or{})do if supplier.kind==kind then times[#times+1]=supplier.ready or INF end end
                table.sort(times);ready=maximum(ready,times[count]or INF)
            end
            if service.known and producer and producer.type==service.producer then
                local yield,amount=serviceRate(service)
                if ready<math.min(site.horizon,service.finish or site.horizon)then
                    local stream=emit('service:'..service.id,yield,amount,ready,service.city)
                    if stream then
                        stream.service=true;stream.pseudoYield=service.pseudoYield
                        stream.finish=service.finish;stream.recipientPlot=service.plot
                        stream.serviceRoot=service.root;stream.serviceLeaf=service.leaf
                        stream.serviceType=service.service
                        if yield=='HOUSING'then result.hasServiceHousing=true end
                    end
                end
            elseif not service.known then omit('service:'..service.id,'Service input or optional price capability unavailable')end
        end
    end
    -- Future staffing and unplanned routes do not earn income. Service-aware
    -- worlds price declared effects with supported gates and recipient facts.
    for _,reason in ipairs(site.omissions or {})do omit('coverage',reason)end
    -- Attribution is metadata for a decision adapter, never extra production.
    -- Existing investments, amenities, costs and immediate site yields receive
    -- no future-building depth premium. The adapter may map positive ordinary
    -- income of missing buildings to native-style effective building income.
    if shared then return result end
    context.populationBaselines=site.populationBaselines
    return finishLedger(context)
end

local function poolServiceHousing(result, housing, horizon)
    -- Housing affects growth at city thresholds, so stack all attachments
    -- before pricing. A flat value per Housing would reward cities with room
    -- to spare and double-count relief when two Innkeepers lift the same cap.
    -- With population and pre-growth Food held fixed, price the change in
    -- usable surplus as a native Food interval. The 2 Food cap bounds this
    -- approximation across long horizons without simulating population.
    if not housing or not result.hasServiceHousing and #housing.activeCities==0 then return end
    local retained,changes,ids={},{},{}
    for _,id in ipairs(housing.activeCities)do
        if housing.cities[id].left then changes[id]={};ids[#ids+1]=id end
    end
    for _,stream in ipairs(result.streams)do
        if stream.service and stream.yield=='HOUSING'then
            local city=housing.cities[stream.city]
            if city and city.left then
                local events=changes[stream.city]
                if not events then events={};changes[stream.city]=events;ids[#ids+1]=stream.city end
                local finish=math.min(horizon,stream.finish or horizon)
                events[stream.ready]=(events[stream.ready]or 0)+stream.amount
                events[finish]=(events[finish]or 0)-stream.amount
            end
        else retained[#retained+1]=stream end
    end
    local function multiplier(left)
        if left<housing.stop then return 0 end
        if left<=housing.quarter then return 0.25 end
        if left<=housing.half then return 0.5 end
        return 1
    end
    table.sort(ids)
    for _,id in ipairs(ids)do
        local city,events=housing.cities[id],changes[id]
        local times={0,horizon}
        for turn,change in pairs(events)do
            if turn>0 and turn<horizon and change~=0 then times[#times+1]=turn end
        end
        table.sort(times)
        local current=multiplier(city.left)
        local active=0
        for i=1,#times-1 do
            local ready,finish=times[i],times[i+1]
            active=active+(events[ready]or 0)
            local food=city.food*(multiplier(city.left-city.active+active)-current)
            local amount=math.max(-2,math.min(2,food))
            if amount~=0 then
                retained[#retained+1]={id='service:housing:'..id..':'..ready,
                    city=id,yield='YIELD_FOOD',amount=amount,ready=ready,finish=finish,service=true}
            end
        end
    end
    result.streams=retained
end

-- Price the live Services a single supplier job would restore. The existing
-- producer, recipient and unlock gates must already work. Count only observed
-- suppliers. This read model never assumes that another material job happens.
-- The same Service catalogue and yield conversion drive Quarter forecasts.
local function materialServiceState(site)
    local counts,seen,working={}, {}, {}
    for _,supplier in ipairs(site.suppliers or{})do
        local key=supplier.kind..':'..supplier.plot
        if supplier.ready==0 and not seen[key]then
            counts[supplier.kind]=(counts[supplier.kind]or 0)+1
            seen[key]=true
        end
    end
    for _,producer in ipairs(site.seconds or{})do if producer.working then working[producer.type]=true end end
    for _,producer in pairs({site.third,site.fourth})do if producer.working then working[producer.type]=true end end
    return counts,working
end

local function serviceAssetsReady(service,working,ready,horizon)
    return service.known and working[service.producer] and service.customer.complete and service.customer.working
        and ready<math.min(horizon,service.finish or horizon)
end

-- If two material classes went down together, neither repair can claim the
-- full Service cash flow on its own. Identify the required feasible repairs
-- for the priority floor without adding any speculative Service income.
function M.MaterialRestorationKinds(site,repairable,ready)
    local result={}
    if not site.services or #site.services==0 or not site.existing or site.quarterReady~=0 then return result end
    local counts,working=materialServiceState(site)
    for _,service in ipairs(site.services)do
        if service.unlock==0 and serviceAssetsReady(service,working,ready,site.horizon) then
            local feasible=true
            for kind,required in pairs(service.materials)do
                if (counts[kind]or 0)+(repairable[kind]or 0)<required then feasible=false;break end
            end
            if feasible then
                for kind,required in pairs(service.materials)do
                    if (counts[kind]or 0)<required then result[kind]=true end
                end
            end
        end
    end
    return result
end

function M.MaterialServiceStreams(site,kind,ready,housing)
    if not site.services or #site.services==0 or not site.existing or site.quarterReady~=0 or ready>=site.horizon then return {}end
    local counts,working=materialServiceState(site)
    local result={streams={}}
    for _,service in ipairs(site.services)do
        if service.unlock==0 and serviceAssetsReady(service,working,ready,site.horizon)
            and service.materials[kind]==(counts[kind]or 0)+1 then
            local enabled=true
            for other,count in pairs(service.materials)do
                if other~=kind and (counts[other]or 0)<count then enabled=false;break end
            end
            if enabled and (service.kind~='HOUSING'or housing) then
                local yield,amount=serviceRate(service)
                if amount~=0 then
                    result.streams[#result.streams+1]={id='service:'..service.id,city=service.city,yield=yield,amount=amount,
                        ready=ready,finish=service.finish,service=true,pseudoYield=service.pseudoYield}
                    if yield=='HOUSING'then result.hasServiceHousing=true end
                end
            end
        end
    end
    poolServiceHousing(result,housing,site.horizon)
    return result.streams
end

function M.ServiceResearchOffers(sites,housing,horizon,price)
    -- Credit the exact topic only for benefits it can activate by itself.
    -- Existing physical chains supply the gates and native research owns
    -- the cost, dependency tree and immediate step. Price benefits from ETA
    -- in the same Q8 as other research offers, with no building speculation.
    local topics={}
    for _,site in ipairs(sites)do
        if site.existing and site.quarterReady==0 and site.services and #site.services>0 then
            local counts,working=materialServiceState(site)
            for _,service in ipairs(site.services)do
                local topic,ready=service.researchTopic,service.unlock
                if topic and present(ready) and serviceAssetsReady(service,working,ready,horizon)then
                    local supplied=true
                    for kind,amount in pairs(service.materials)do
                        if (counts[kind]or 0)<amount then supplied=false;break end
                    end
                    local yield,amount=serviceRate(service)
                    if supplied and amount>0 and (yield~='HOUSING'or housing and housing.cities[service.city])then
                        local key=topic.kind..':'..topic.index
                        local offer=topics[key]
                        if not offer then
                            offer={kind=topic.kind,index=topic.index,streams={},omissions={},effects={},chains={}}
                            topics[key]=offer
                        end
                        -- Each attached effect can pay once per physical
                        -- source and recipient. Several effects on one Service
                        -- count as one chain for diagnostics, not several bids.
                        local id=site.key..':'..service.id
                        if not offer.effects[id]then
                            offer.effects[id]=true
                            offer.chains[site.key..':'..(service.service or service.stage)..':'..service.plot]=true
                            offer.streams[#offer.streams+1]={id=id,city=service.city,yield=yield,amount=amount,
                                ready=ready,finish=service.finish,service=true,pseudoYield=service.pseudoYield}
                            if yield=='HOUSING'then offer.hasServiceHousing=true end
                        end
                    end
                end
            end
        end
    end
    for key,offer in pairs(topics)do
        -- Apply a receiving city's growth threshold once to all Housing
        -- this topic would unlock. The baseline already has active effects.
        if offer.hasServiceHousing then poolServiceHousing(offer,housing,horizon)end
        local value=M.Price(offer,price,horizon)
        if value and value>0 then offer.value=value else topics[key]=nil end
    end
    return topics
end

-- Pool simultaneous amenity changes once per owner/city/interval. Native
-- AmenityValue is nonlinear at happiness thresholds; separate channel quotes
-- would count a threshold repeatedly. Every candidate uses the same actual
-- paid baseline, including ordinary amenities already present in its ledger.
-- The output amount is an offset from native CURRENT surplus, not a free
-- additional amenity. No building receives the pooled value/depth premium.
function M.PoolAmenities(result,baseline,horizon,coverage)
    local pools,retained={},{}
    local function pool(player,city)
        if not present(player)or player%1~=0 or not present(city)or city%1~=0 then
            return nil,'Explicit amenity recipient required'
        end
        local key=string.format('%.0f:%.0f',player,city)
        if not pools[key]then pools[key]={player=player,city=city,baseline=0,streams={},times={[0]=true,[horizon]=true}}end
        return pools[key],key
    end
    for key,amount in pairs(baseline or{})do
        local player,city=key:match('^(%d+):(%d+)$')
        local p,error=pool(tonumber(player),tonumber(city));if not p then return nil,error end
        if not numeric(amount)or amount~=amount or math.abs(amount)==INF then return nil,'Invalid paid amenity baseline'end
        p.baseline=amount
        p.routeBaseline=amount
        p.routeCoverage=coverage and coverage[key]or horizon
        if not present(p.routeCoverage)then return nil,'Invalid amenity route coverage'end
        if p.routeCoverage<horizon then p.times[p.routeCoverage]=true end
    end
    for _,stream in ipairs(result.streams)do
        if stream.yield~='AMENITY'then retained[#retained+1]=stream
        else
            local p,error=pool(stream.player,stream.city);if not p then return nil,error end
            local finish=math.min(horizon,stream.finish or horizon)
            if not present(stream.ready)or not present(finish)or not numeric(stream.amount)
                or stream.amount~=stream.amount or math.abs(stream.amount)==INF then return nil,'Invalid amenity interval'end
            p.baseline=p.baseline+(stream.amenityBaseline or 0)
            if stream.ready<finish then
                p.streams[#p.streams+1]=stream;p.times[stream.ready]=true;p.times[finish]=true
            end
        end
    end
    local keys={};for key in pairs(pools)do keys[#keys+1]=key end;table.sort(keys)
    for _,key in ipairs(keys)do
        local p=pools[key];local times={}
        for t in pairs(p.times)do times[#times+1]=t end;table.sort(times)
        if #times>128 then return nil,'Amenity event budget exceeded'end
        local previous
        for i=1,#times-1 do
            local ready,finish=times[i],times[i+1];local total,contributors=0,{}
            for _,s in ipairs(p.streams)do if s.ready<=ready and(s.finish or horizon)>ready then
                total=total+s.amount;contributors[#contributors+1]=s.id
            end end
            -- Beyond observed route coverage, keep its contribution neutral
            -- relative to CURRENT native happiness. This is an explicit quote
            -- assumption, not forecast income or proof of renewal. It allows
            -- ordinary future amenities to be quoted against today's baseline
            -- without inventing a trade loss or extra threshold crossing.
            if ready>=(p.routeCoverage or horizon)then total=total+(p.routeBaseline or 0)end
            local offset=total-p.baseline
            if offset~=0 then
                if previous and previous.finish==ready and previous.amount==offset then
                    previous.finish=finish
                    for _,id in ipairs(contributors)do previous.contributors[id]=true end
                else
                    previous={id='amenity-pool:'..key..'@'..ready,yield='AMENITY',player=p.player,city=p.city,
                        amount=offset,amenityBaseline=p.baseline,ready=ready,finish=finish,
                        counterfactualAmenity=true,contributors={}}
                    for _,id in ipairs(contributors)do previous.contributors[id]=true end
                    retained[#retained+1]=previous
                end
            end
        end
    end
    result.streams=retained
    return result
end

-- One network evaluation AFTER the shared ledger has scheduled every chosen
-- investment. Facts supplies observed endpoints, actual paid counts and plain
-- counterfactual events. A conditional event may name an investmentKey: an
-- omitted/unavailable producer cannot activate it, and its completion time is
-- shared with every other chain. This entry issues no routes, orders or bids.
local function cachedRoutes(R,trade,player,horizon,changes)
    local memo,observation=trade.memo,trade.observed
    if not memo then
        local routes,error=R.Forecast({cities=observation.cities,routes=observation.routes,changes=changes},trade.definitions,player,horizon)
        if not routes then return nil,error end
        local baseline,problem=R.PaidAmenities(observation.cities,trade.definitions,player)
        if not baseline then return nil,problem end
        local groups,coverage=R.Coverage(observation,trade.definitions,player,horizon)
        if not groups then return nil,coverage end
        return routes,baseline,coverage
    end
    if memo.observation then
        if memo.observation~=observation or memo.definitions~=trade.definitions or memo.player~=player or memo.horizon~=horizon then
            return nil,'Route memo observation scope differs'
        end
    else
        local baseline,problem=R.PaidAmenities(observation.cities,trade.definitions,player)
        if not baseline then return nil,problem end
        local groups,coverage=R.Coverage(observation,trade.definitions,player,horizon)
        if not groups then return nil,coverage end
        local activity=0
        for _,route in ipairs(observation.routes)do
            activity=math.max(activity,math.min(horizon,route.observedThrough or 1,route.removedAt or horizon))
        end
        memo.observation,memo.definitions,memo.player,memo.horizon=observation,trade.definitions,player,horizon
        memo.baseline,memo.coverage,memo.activity=baseline,coverage,activity
    end
    -- Validate/conflict-check BEFORE cache lookup or no-op removal. A malformed
    -- later event cannot hide behind an earlier successful forecast. Canonical
    -- order applies changes to projected state, preserving a later restoration.
    local events,seen={},{}
    local function text(value)local s=type(value)..':'..tostring(value);return #s..':'..s end
    for _,change in ipairs(changes)do
        if not present(change.ready)or not observation.cities[change.city]
            or(change.field~='quarters'and change.field~='buildings'and change.field~='properties')or change.key==nil then
            return nil,'Invalid route counterfactual event'
        end
        if change.ready<horizon then
            local identity=text(change.city)..text(change.field)..text(change.key)
            local key=text(change.ready)..identity
            if seen[key]and seen[key].value~=change.value then return nil,'Conflicting route counterfactual events'end
            if not seen[key]then
                local event={ready=change.ready,city=change.city,field=change.field,key=change.key,
                    value=change.value,identity=identity}
                seen[key]=event;events[#events+1]=event
            end
        end
    end
    table.sort(events,function(a,b)return a.ready<b.ready or a.ready==b.ready and a.identity<b.identity end)
    local states,normalized,parts={},{},{text(memo.activity)}
    for _,event in ipairs(events)do if event.ready<memo.activity then
        local state=states[event.identity]
        if not state then
            state={value=(observation.cities[event.city][event.field]or{})[event.key]};states[event.identity]=state
        end
        if state.value~=event.value then
            normalized[#normalized+1]=event
            parts[#parts+1]=text(event.ready)..event.identity..text(event.value)
            state.value=event.value
        end
    end end
    local key=table.concat(parts,'|');local routes=memo.entries[key]
    if routes then memo.hits=memo.hits+1
    else
        memo.misses=memo.misses+1
        if memo.activity==0 then routes={}
        else
            local error
            routes,error=R.Forecast({cities=observation.cities,routes=observation.routes,changes=normalized},
                trade.definitions,player,memo.activity)
            if not routes then return nil,error end
        end
        -- Publication-local bound; extra distinct timelines still calculate
        -- correctly, merely without retained reuse. No result survives a turn.
        if memo.count<128 then memo.entries[key]=routes;memo.count=memo.count+1 else memo.overflow=memo.overflow+1 end
    end
    return routes,memo.baseline,memo.coverage
end

function M.RouteLedger(result,trade,player,horizon)
    local R=CSC_TradeRouteCore
    if not R then return nil,'Shared route kernel unavailable'end
    if not present(player)or player%1~=0 then return nil,'Route evaluating player required'end
    local observation=trade.observed
    if not observation or not trade.definitions then return nil,'Complete route facts required'end
    local changes={}
    for _,change in ipairs(trade.changes or{})do changes[#changes+1]=change end
    for _,change in ipairs(trade.plannedChanges or{})do
        local ready=change.ready or 0
        if not present(ready)then return nil,'Route event readiness unavailable'end
        if change.investmentKey then
            local completion=result.byBuilding[change.investmentKey]
            ready=present(completion)and math.max(ready,completion)or INF
        end
        if change.quarterKey then ready=math.max(ready,(result.quarterReadyByChain or{})[change.quarterKey]or INF)end
        if change.quarterStartKey then ready=math.max(ready,(result.quarterStartByChain or{})[change.quarterStartKey]or INF)end
        if present(ready)and ready<horizon then
            changes[#changes+1]={ready=ready,city=change.city,field=change.field,key=change.key,value=change.value}
        end
    end
    local routes,baseline,coverage=cachedRoutes(R,trade,player,horizon,changes)
    if not routes then return nil,baseline end
    -- Pricing annotates streams. Borrow no cached output table into a trial;
    -- amenity pooling still runs against this trial's ordinary building flows.
    for _,stream in ipairs(routes)do
        local copy={};for k,v in pairs(stream)do copy[k]=v end
        result.streams[#result.streams+1]=copy
    end
    result.routeSegments=#routes
    return M.PoolAmenities(result,baseline,horizon,coverage)
end

function M.Price(result,price,horizon)
    local total,bid=result.siteAdjustmentQ8 or 0,result.siteAdjustmentQ8 or 0
    local footprint=bid
    for _,stream in ipairs(result.streams)do
        local value,weighted=price(stream, horizon)
        if stream.service and not numeric(value)then
            -- A newly optional native Service consumer can be unavailable on
            -- a particular definition/context. Preserve the qualified ordinary
            -- economy and expose the omission rather than disable all bids.
            result.omissions[#result.omissions+1]={id=stream.id,reason='Optional native Service quote unavailable'}
            value,weighted=0,0;stream.priceUnavailable=true
        end
        if not numeric(value) or value~=math.floor(value)then
            return nil,'Native price unavailable for '..stream.id
        end
        if weighted==nil then weighted=value end
        if not numeric(weighted)or weighted~=math.floor(weighted)then return nil,'Native bid price unavailable for '..stream.id end
        stream.valueQ8=value;stream.bidValueQ8=weighted;total=total+value;bid=bid+weighted
        if stream.footprint then footprint=footprint+weighted end
    end
    -- This signed Q8 subtotal is already in bidValueQ8. It lets the site
    -- adapter cap speculative income without erasing a real land cost.
    result.bidValueQ8=bid;result.forecastAdjustmentQ8=bid-total;result.footprintBidQ8=footprint
    return total
end

function M.Forecast(site,price,placementObjective)
    assert(present(site.horizon) and site.horizon>0,'Finite forecast horizon required')
    if not present(site.quarterReady)then return nil,'Quarter readiness unavailable'end
    local best
    local choices={};local physicalSecond=false
    for _,second in ipairs(site.seconds or{})do
        physicalSecond=physicalSecond or second.working==true or second.intactOwner==true
    end
    -- Already built, functioning producers are physical facts. A zero native
    -- yield weight must not let an absent-producer alternative erase their
    -- transactions (important for marginal/joint before/after comparisons).
    -- A city without a working producer can still defer every new investment.
    if not physicalSecond then choices[1]=false end
    for _,second in ipairs(site.seconds or {})do
        if not physicalSecond or second.working or second.intactOwner then choices[#choices+1]=second end
    end
    local function evaluate(plan,second)
        local result,problem=ledger(plan,second or nil)
        if not result then return nil,problem end
        local value,error=M.Price(result,price,site.horizon)
        if not value then return nil,error end
        result.valueQ8=value
        result.selectionQ8=placementObjective and placementObjective(result)or value
        return result
    end
    -- Optional later producers cannot make a good Stage2 investment worse.
    -- Four bounded stage plans include 2, 2+3, 2+4 and 2+3+4; already working
    -- buildings stay physical facts. Then greedily omit unprofitable missing
    -- customer buildings. This is bounded best-effort planning, not a claim to
    -- solve every ordering/subset of an empire's future production perfectly.
    for _,second in ipairs(choices)do for mask=0,3 do
        local plan={};for k,v in pairs(site)do plan[k]=v end
        if mask%2==0 and site.third and not site.third.working and not site.third.intactOwner then plan.third=nil end
        if mask<2 and site.fourth and not site.fourth.working and not site.fourth.intactOwner then plan.fourth=nil end
        plan.customers={};for _,customer in ipairs(site.customers or {})do plan.customers[#plan.customers+1]=customer end
        local result,error=evaluate(plan,second)
        if not result then return nil,error end
        for i=#plan.customers,1,-1 do
            if not plan.customers[i].working and not plan.customers[i].intactOwner then
                local reduced={};for k,v in pairs(plan)do reduced[k]=v end
                reduced.customers={}
                for j,v in ipairs(plan.customers)do if j~=i then reduced.customers[#reduced.customers+1]=v end end
                local alternative,message=evaluate(reduced,second)
                if not alternative then return nil,message end
                if alternative.selectionQ8>=result.selectionQ8 then plan,result=reduced,alternative end
            end
        end
        -- Placement must compare the final bid of each feasible producer plan.
        -- Selecting raw economics first can reject a profitable Wind +3 plan
        -- merely because earlier Water +2 pays slightly more. Other consumers
        -- (building marginals/supplier losses) retain the raw economic objective.
        -- This callback only ranks already priced plans; it adds no game reads
        -- or extra alternative enumeration to the bounded search above.
        result.selectionQ8=placementObjective and placementObjective(result)or result.valueQ8
        if not best or result.selectionQ8>best.selectionQ8 or result.selectionQ8==best.selectionQ8
            and (result.valueQ8>best.valueQ8 or result.valueQ8==best.valueQ8
            and tostring(result.alternative or '')<tostring(best.alternative or ''))then best=result end
    end end
    return best
end

-- A proposed customer can affect several Quarters and their city's shared
-- production queue. Live decision adapters evaluate them in this pure context;
-- packet publication is separate. The facts adapter must include the complete
-- affected closure and every contributor to its population properties.
-- Minimal and all-enabled seeds let jointly profitable shared venues enter the
-- search even when each producer alone cannot cover their upkeep. Two sweeps
-- per seed bound the search. Exhausting the work
-- budget returns unavailable instead of presenting a partial world as complete.
-- Values cover this counterfactual world and flow back to the decision adapter
-- for comparison with an alternative built from the same live snapshot.
function M.JointForecast(world,price)
    local sites,keys,definitions={},{},{}
    local horizon=world.horizon
    if not present(horizon)or horizon<=0 then return nil,'Finite joint horizon required'end
    for _,site in ipairs(world.sites or{})do
        if type(site.key)~='string'or keys[site.key]then return nil,'Missing or duplicate chain identity'end
        if not present(site.player)or site.player%1~=0 then return nil,'Explicit chain owner required'end
        if not present(site.city)or site.city%1~=0 then return nil,'Explicit chain city required'end
        if site.horizon~=horizon or not present(site.quarterReady)then return nil,'Inconsistent joint horizon/readiness'end
        keys[site.key]=true;sites[#sites+1]=site
    end
    if #sites==0 and not world.trade then return nil,'No affected Quarter chains'end
    if #sites>(world.maxChains or 64)then return nil,'Affected chain budget exceeded'end
    table.sort(sites,function(a,b)
        if (a.key==world.firstChainKey)~=(b.key==world.firstChainKey)then return a.key==world.firstChainKey end
        return a.key<b.key
    end)
    -- Repeated references describe one physical investment. Refuse conflicting
    -- state/cost/readiness copies rather than let chain traversal decide which
    -- Market is real. Relationship eligibility belongs on its own flow, not in
    -- contradictory versions of the shared building's construction facts.
    local function validate(site,city,definition,visiting)
        if not definition then return true end
        if type(definition.type)~='string'then return nil,'Investment type unavailable'end
        if not present(city)or city%1~=0 then return nil,'Investment city unavailable'end
        local stamp=site.player..':'..city..':'..definition.type
        if visiting[stamp]then return nil,'Cyclic shared investment prerequisites'end
        local fields={}
        for _,key in ipairs({'working','intactOwner','excluded'})do fields[#fields+1]=tostring(definition[key]==true)end
        for _,key in ipairs({'hostReady','unlock','turns','cost','maintenance','forecastDepth'})do
            local value=definition[key]
            if value==nil then value=(key=='cost'or key=='maintenance'or key=='forecastDepth')and 0 or INF end
            fields[#fields+1]=key..'='..tostring(value)
        end
        local required={}
        visiting[stamp]=true
        for _,v in ipairs(definition.prerequisites or{})do
            local ok,message=validate(site,city,v,visiting);if not ok then return nil,message end
            required[#required+1]=v.type
        end
        visiting[stamp]=nil;table.sort(required)
        fields[#fields+1]=table.concat(required,',')
        fields[#fields+1]='hostQuarter='..tostring(definition.hostQuarter or'')
        local signature=table.concat(fields,'|')
        if definitions[stamp]and definitions[stamp]~=signature then return nil,'Conflicting shared investment: '..stamp end
        definitions[stamp]=signature;return true
    end
    for _,site in ipairs(sites)do
        for _,v in ipairs(site.seconds or{})do local ok,e=validate(site,site.city,v,{});if not ok then return nil,e end end
        for _,v in pairs({third=site.third,fourth=site.fourth})do local ok,e=validate(site,site.city,v,{});if not ok then return nil,e end end
        for _,v in ipairs(site.customers or{})do if v.type then
            local ok,e=validate(site,v.city,v,{});if not ok then return nil,e end
        end end
    end
    local evaluations,limit=0,world.maxEvaluations or 512
    local function copy(source)
        local result={};for k,v in pairs(source)do result[k]=v end;return result
    end
    local function plan(site,second,mask)
        local value=copy(site);value.service=nil
        if not world.includeServices and not world.evaluationMemo then value.services=nil end
        if mask%2==0 and site.third and not site.third.working and not site.third.intactOwner then value.third=nil end
        if mask<2 and site.fourth and not site.fourth.working and not site.fourth.intactOwner then value.fourth=nil end
        -- Joint venue decisions live in disabledBuildings. Each alternative
        -- can share the immutable customer facts with the other plans.
        return {site=value,second=second or nil}
    end
    local function options(site)
        local seconds,physical={},false
        for _,v in ipairs(site.seconds or{})do physical=physical or v.working==true or v.intactOwner==true end
        if not physical then seconds[1]=false end
        for _,v in ipairs(site.seconds or{})do
            if not physical or v.working or v.intactOwner then seconds[#seconds+1]=v end
        end
        local result,seen={},{}
        for _,second in ipairs(seconds)do for mask=0,3 do
            local candidate=plan(site,second,mask)
            local identity=table.concat({second and second.type or'',candidate.site.third and candidate.site.third.type or'',
                candidate.site.fourth and candidate.site.fourth.type or''},'|')
            if not seen[identity]then
                candidate.option=#result+1
                result[#result+1]=candidate;seen[identity]=true
            end
        end end
        return result
    end
    local baseline=world.baselinePlan
    local affected={}
    if baseline then
        for key,value in pairs(world.affectedChains or{})do affected[key]=value end
        -- A shared physical customer must remain one decision. Expand only
        -- this investment connection; distant queue/route peers keep their
        -- choices but their readiness and effects are recomputed below.
        local customerPeers={}
        for _,site in ipairs(sites)do for _,v in ipairs(site.customers or{})do
            if v.type and not v.working and not v.intactOwner then
                local key=site.player..':'..v.city..':'..v.type
                customerPeers[key]=customerPeers[key]or{};customerPeers[key][#customerPeers[key]+1]=site.key
            end
        end end
        local changed=true
        while changed do
            changed=false
            for _,peers in pairs(customerPeers)do
                local touches=false;for _,key in ipairs(peers)do touches=touches or affected[key]end
                if touches then for _,key in ipairs(peers)do if not affected[key]then affected[key]=true;changed=true end end end
            end
        end
    end
    local alternatives,nodes,nodeKeys={},{},{}
    for i,site in ipairs(sites)do
        alternatives[i]=options(site)
        local frozen=baseline and baseline.chains[site.key]and not affected[site.key]
        if frozen then
            local selected
            local fixed=baseline.chains[site.key]
            for _,option in ipairs(alternatives[i])do
                if (option.second and option.second.type)==fixed.second
                    and(option.site.third and option.site.third.type)==fixed.third
                    and(option.site.fourth and option.site.fourth.type)==fixed.fourth then selected=option;break end
            end
            if not selected then return nil,'Baseline investment identity unavailable'end
            alternatives[i]={selected}
        end
        for _,customer in ipairs(site.customers or{})do
            if customer.type and not customer.working and not customer.intactOwner then
                local key=tostring(site.player or 0)..':'..customer.city..':'..customer.type
                if not frozen and not nodeKeys[key]then nodes[#nodes+1]=key;nodeKeys[key]=true end
            end
        end
    end
    table.sort(nodes)
    local function buildLedger(selected,disabled)
        local context=newLedger(sites[1]or{},nil)
        context.joint=true;context.includeServices=world.includeServices==true or world.evaluationMemo~=nil
        context.result.siteAdjustmentQ8=0;context.result.chainStages={}
        context.populationBaselines=world.populationBaselines or{}
        context.disabledBuildings=disabled
        for city,ready in pairs(world.queueReady or{})do
            if not present(ready)then return nil,'Unknown shared queue readiness'end
            context.clocks[city]=ready
        end
        for i,v in ipairs(selected)do
            context.result.siteAdjustmentQ8=context.result.siteAdjustmentQ8+(v.site.nativeSiteAdjustmentQ8 or 0)
            ledger(v.site,v.second,context)
            if context.error then return nil,context.error end
        end
        local result,problem=finishLedger(context)
        if not result then return nil,problem end
        for _,source in ipairs(world.extraStreams or{})do
            if not present(source.ready)or not present(source.player)or not present(source.city)
                or source.finish~=nil and not present(source.finish)
                or not numeric(source.amount)or source.amount~=source.amount or math.abs(source.amount)==INF then
                return nil,'Invalid joint externality stream'
            end
            -- Facts marks receiver/timing/component explicitly. Keep this
            -- separate from native ordinary site value for overlap attribution.
            local stream=copy(source)
            if stream.quarterKey then stream.ready=maximum(stream.ready,result.quarterReadyByChain[stream.quarterKey]or INF)end
            if stream.ready<math.min(horizon,stream.finish or horizon)then result.streams[#result.streams+1]=stream end
        end
        if world.trade then
            result,problem=M.RouteLedger(result,world.trade,world.player,horizon)
        else result,problem=M.PoolAmenities(result,{},horizon)end
        if not result then return nil,problem end
        if context.includeServices then poolServiceHousing(result,world.serviceHousing,horizon)end
        return result
    end
    local variable=#nodes>0
    for _,choices in ipairs(alternatives)do variable=variable or #choices>1 end
    local pricedStates,pricedCount={},0
    local function evaluate(selected,disabled,startingResult)
        evaluations=evaluations+1
        if evaluations>limit then return nil,'Joint evaluation budget exceeded'end
        if startingResult then return startingResult end
        -- The coordinates search revisits complete plans across seeds and
        -- sweeps. Within this one immutable world, the selected option per
        -- chain and the variable venue flags describe every changing input.
        -- Price and objective are pure for this call. Reusing a quote saves
        -- ledger construction and pricing, while still charging the same
        -- logical evaluation so the policy's budget and tie order stay fixed.
        local pricedKey
        if variable then
            local fields={}
            for i,choice in ipairs(selected)do fields[i]=choice.option end
            for i,node in ipairs(nodes)do fields[#selected+i]=disabled[node]and 1 or 0 end
            pricedKey=table.concat(fields,':')
            if pricedStates[pricedKey]then return pricedStates[pricedKey]end
        end
        -- Only an exact shared baseline gets this publication-local memo. Both
        -- pricing modes still run the full bounded plan search; cache identical
        -- UNPRICED ledgers, never a winning plan or a candidate world's answer.
        -- Keep at most16 states and copy priced stream headers so the ordinary
        -- consumer cannot mutate the Service consumer's cached contribution.
        local memo,key=world.evaluationMemo
        if memo then
            if memo.token~=world.ledgerMemoToken then return nil,'Baseline ledger memo identity differs'end
            local fields={}
            for _,v in ipairs(selected)do
                fields[#fields+1]=v.second and v.second.type or'~'
                fields[#fields+1]=v.site.third and v.site.third.type or'~'
                fields[#fields+1]=v.site.fourth and v.site.fourth.type or'~'
            end
            for _,node in ipairs(nodes)do if disabled[node]then fields[#fields+1]='disabled:'..node end end
            key=table.concat(fields,'|')
        end
        local full=memo and memo.entries[key]
        if full then memo.hits=memo.hits+1 else
            local problem;full,problem=buildLedger(selected,disabled)
            if not full then return nil,problem end
            if memo and memo.count<16 then memo.entries[key]=full;memo.count=memo.count+1 end
        end
        local result=full
        if memo then
            result=copy(full);result.streams={};result.omissions={}
            for _,s in ipairs(full.streams)do if world.includeServices or not s.service then result.streams[#result.streams+1]=copy(s)end end
            for _,o in ipairs(full.omissions)do
                if world.includeServices or o.id:sub(1,8)~='service:'then result.omissions[#result.omissions+1]=o end
            end
        end
        local value,error=M.Price(result,price,horizon)
        if not value then return nil,error end
        result.valueQ8=value;result.servicesExcluded=not world.includeServices;result.modelOnly=true
        result.serviceValueQ8=0;result.serviceStreams=0
        for _,s in ipairs(result.streams)do if s.service then
            result.serviceValueQ8=result.serviceValueQ8+s.valueQ8;result.serviceStreams=result.serviceStreams+1
        end end
        result.disabledBuildings={};for key,disabled in pairs(disabled)do if disabled then result.disabledBuildings[key]=true end end
        -- The placement adapter may rank producer alternatives by its final
        -- calibrated bid while retaining physical income/valueQ8 unchanged.
        -- This mirrors the single-site Forecast objective; other consumers
        -- continue to optimise raw economics with no policy callback.
        result.selectionQ8=world.objective and world.objective(result)or value
        -- Keep temporary retention bounded in mature empires. Cached results
        -- stay private during search. Only the winning one receives metadata.
        if pricedKey and pricedCount<16 then
            pricedStates[pricedKey]=result;pricedCount=pricedCount+1
        end
        return result
    end
    local best
    local function better(a,b)
        return a.selectionQ8>b.selectionQ8 or a.selectionQ8==b.selectionQ8 and a.valueQ8>b.valueQ8
    end
    for seed=1,variable and 2 or 1 do
        local selected,disabled={},{}
        if baseline then for key,value in pairs(baseline.disabledBuildings)do disabled[key]=value end end
        for _,key in ipairs(nodes)do disabled[key]=nil end
        for i,choices in ipairs(alternatives)do selected[i]=choices[seed==1 and 1 or #choices]end
        local current,message=evaluate(selected,disabled);if not current then return nil,message end
        for sweep=1,variable and 2 or 0 do
            for i=1,#sites do
                local chosen=selected[i]
                local startingChoice,startingResult=chosen,current
                if #alternatives[i]>1 then for _,candidate in ipairs(alternatives[i])do
                    selected[i]=candidate
                    local result,error=evaluate(selected,disabled,candidate==startingChoice and startingResult or nil)
                    if not result then return nil,error end
                    if better(result,current)then current,chosen=result,candidate end
                end end
                selected[i]=chosen
            end
            -- Choose unique physical customer investments globally. A venue
            -- built for one Quarter automatically serves every eligible adjacent
            -- producer; deleting one chain's edge would invent a gameplay choice
            -- that does not exist. Relationship records therefore stay immutable.
            for _,key in ipairs(nodes)do
                local previous=disabled[key];disabled[key]=not previous or nil
                local result,error=evaluate(selected,disabled);if not result then return nil,error end
                if better(result,current)or result.selectionQ8==current.selectionQ8 and result.valueQ8==current.valueQ8 and disabled[key]then
                    current=result
                else disabled[key]=previous end
            end
        end
        if not best or better(current,best)then best=current end
    end
    best.evaluations=evaluations;best.affectedChains=#sites
    -- Plain winning identities, never cached readiness or mutable search state.
    best.plan={chains=best.chainStages,disabledBuildings=best.disabledBuildings}
    return best
end

-- Both worlds are explicit plain facts. Only the after-world reserves the new
-- district's queue time, changes footprints and adds venues. The ordinary native
-- valuation and its overlap are reconciled by the later decision adapter.
function M.JointCustomerForecast(beforeWorld,afterWorld,price)
    if beforeWorld.horizon~=afterWorld.horizon then return nil,'Marginal horizons differ'end
    if beforeWorld.trade or afterWorld.trade then
        -- Both alternatives are counterfactuals of ONE immutable observation.
        -- Project changes through events, never by editing the acknowledged
        -- counters/endpoints in the after-world and erasing its native baseline.
        if not beforeWorld.trade or not afterWorld.trade
            or beforeWorld.trade.observed~=afterWorld.trade.observed
            or beforeWorld.trade.definitions~=afterWorld.trade.definitions
            or beforeWorld.player~=afterWorld.player then return nil,'Marginal trade observations differ'end
    end
    local before,message=M.JointForecast(beforeWorld,price);if not before then return nil,message end
    local localWorld={};for k,v in pairs(afterWorld)do localWorld[k]=v end
    if afterWorld.affectedChains then localWorld.baselinePlan=before.plan end
    local after,error=M.JointForecast(localWorld,price);if not after then return nil,error end
    return {before=before,after=after,valueQ8=after.valueQ8-before.valueQ8,
        bidValueQ8=after.bidValueQ8-before.bidValueQ8,servicesExcluded=true,modelOnly=true}
end

function M.Marginal(site,building,price)
    -- Actual building bidding is a different consumer from district placement.
    -- Both quotes use this same transaction ledger, so it cannot invent another
    -- set of supplier/customer amounts. Removing a prerequisite removes its
    -- dependent transactions through the readiness graph as well.
    local full,error=M.Forecast(site,price);if not full then return nil,error end
    local restricted={};for k,v in pairs(site)do restricted[k]=v end
    restricted.seconds={}
    for _,definition in ipairs(site.seconds or {})do
        if definition.type~=building then restricted.seconds[#restricted.seconds+1]=definition end
    end
    for _,field in ipairs({'third','fourth'})do
        if site[field] and site[field].type==building then restricted[field]=nil end
    end
    local without,message=M.Forecast(restricted,price);if not without then return nil,message end
    return full.valueQ8-without.valueQ8,full
end

function M.ProducerInvestment(site,options,price)
    -- Price one Stage 2 investment against leaving the Quarter without a
    -- producer. Water and Wind are alternatives for the same investment.
    -- Already operating customer buildings can trade as soon as the producer
    -- is ready. Later stages, Services and unbuilt customers have their own
    -- decisions and add no income to this bid.
    local stageTwo={}
    for key,value in pairs(site)do stageTwo[key]=value end
    stageTwo.third,stageTwo.fourth,stageTwo.service,stageTwo.services=nil,nil,nil,nil
    stageTwo.direct,stageTwo.customers={},{}
    for _,customer in ipairs(site.customers or{})do
        if customer.stage==2 and customer.working then
            stageTwo.customers[#stageTwo.customers+1]=customer
        end
    end
    local function value(option)
        local report=ledger(stageTwo,option)
        return report and M.Price(report,price,stageTwo.horizon)
    end
    local baseline=value(nil)
    if baseline==nil then return nil end
    local best,benefit,bestReady=nil,0,math.huge
    for _,option in ipairs(options)do
        local forecast=value(option)
        local delta=forecast and forecast-baseline
        local ready=option.unlock+option.turns
        if delta and (delta>benefit or delta==benefit and delta>0
            and (ready<bestReady or ready==bestReady and option.type<best.type))then
            best,benefit,bestReady=option,delta,ready
        end
    end
    return best,benefit
end

function M.StageTwoCustomerValue(site,customer,price)
    -- The native building candidate already has its own cost and intrinsic
    -- yields. Price only the fixed exchanges with an operating producer that
    -- the customer would activate. Its own completion time gates both legs.
    if customer.stage~=2 or not customer.complete or customer.working or customer.excluded
        or customer.unlock~=0 or customer.prerequisites or not present(customer.turns)
        or customer.turns>=site.horizon then return nil end
    local producer
    for _,option in ipairs(site.seconds or{})do
        if option.working then producer=option;break end
    end
    local transaction=producer and customer.transactions and customer.transactions[producer.type]
    if not transaction or transaction.kind~='FIXED' or transaction.spatial~='ADJACENT_OWNED'then return nil end

    local value=0
    for _,leg in ipairs(transaction.legs)do
        local priced=price({city=transactionCity(leg,site,customer),yield=leg.yield,
            amount=transaction.amount*leg.amount,ready=customer.turns},site.horizon)
        if not numeric(priced)then return nil end
        value=value+priced
    end
    return value
end

function M.StageBuildingInvestment(links,price)
    -- Evaluate exactly one later-stage building against the same physical
    -- world without it. Links share one city/type order and therefore one
    -- construction clock. Use the existing ledger for the population pools,
    -- step bands and directional payouts, with no speculative second order.
    local horizon=links[1].site.horizon
    local function quote(build)
        local context=newLedger({},nil)
        context.joint=true
        context.result.chainStages={}
        context.populationBaselines={}
        for _,link in ipairs(links)do
            local source=link.site
            local site={key=source.key,player=source.player,city=source.city,population=source.population,
                existing=true,quarterReady=0,horizon=horizon,materialYield=source.materialYield,
                suppliers=link.suppliers or{},customers={}}
            local second
            for _,definition in ipairs(source.seconds or{})do if definition.working then second=definition;break end end
            if source.third and source.third.working then site.third=source.third end
            if source.fourth and source.fourth.working then site.fourth=source.fourth end
            for _,customer in ipairs(source.customers)do
                if customer.working then site.customers[#site.customers+1]=customer end
            end
            if link.producer then
                -- Other sellers already feed working recipients. Preserve
                -- their raw targets so adding this producer rounds once.
                for key,value in pairs(source.populationBaselines or{})do
                    context.populationBaselines[source.player..':'..key]=value
                end
            end
            if build then
                -- Native building evaluation owns its ordinary upkeep and
                -- intrinsic Amenities. The add-on bid prices CSC's exchange.
                local function withoutNativeValue(building)
                    local target={}
                    for key,value in pairs(building)do target[key]=value end
                    target.maintenance=0;target.amenityAmount=0;target.forecastDepth=0
                    return target
                end
                if link.producer then site[link.producer]=withoutNativeValue(link.building)
                else for _,customer in ipairs(link.customers)do
                    site.customers[#site.customers+1]=withoutNativeValue(customer)
                end end
            end
            ledger(site,second,context)
            if context.error then return nil end
            if build and link.developmentCost then
                -- The separate supplier jobs spend Builder capacity. Their
                -- delays already gate material receipts, while their cost
                -- enters once here, independent of the building's own cost.
                context.result.streams[#context.result.streams+1]={id=source.key..':supplier-development',
                    city=source.city,yield='YIELD_PRODUCTION',amount=-link.developmentCost,ready=0,fixed=true}
            end
        end
        local result=finishLedger(context)
        return result and M.Price(result,price,horizon)
    end
    local before=quote(false)
    local after=quote(true)
    if before and after then return after-before end
end

function M.ExistingCustomerConnectionValue(site, customer, price)
    -- Estimate the ordinary value at risk if a new Quarter can no longer
    -- reach this particular existing venue. Use the same local ledger twice,
    -- including producer/building readiness and any investment still needed.
    -- Both arms omit Services. The regular Quarter bid still owns its joint
    -- valuation and the private native yield stays outside these quotes.
    local without, with = {}, {}
    for name, value in pairs(site) do without[name]=value;with[name]=value end
    without.service=nil;with.service=nil
    without.customers={}
    for _, venue in ipairs(site.customers or {}) do
        if venue~=customer then without.customers[#without.customers+1]=venue end
    end
    if customer.anchorReady then
        -- The partner district has a physical foundation and an estimated
        -- completion time. Admit it only inside the linked forecast. Its
        -- customer building, prerequisites and transaction keep that delay.
        with.customers={}
        for _,venue in ipairs(without.customers)do with.customers[#with.customers+1]=venue end
        local finished={};for key,value in pairs(customer)do finished[key]=value end
        finished.complete=true;with.customers[#with.customers+1]=finished
    end
    local baseline=M.Forecast(without,price)
    local linked=baseline and M.Forecast(with,price)
    return linked and linked.valueQ8-baseline.valueQ8
end

function M.CustomerBuildingForecast(site,projected,customerCity,districtReady,price)
    -- Building-transaction-only diagnostic, not a complete customer district
    -- value or a new customer policy. District adjacency/provider externalities
    -- and joint multi-Quarter aggregation need the decision-level ledger too.
    -- Price the same existing Quarter plan with/without this district's new
    -- customer venues. Both quotes exclude Services. Native district valuation
    -- keeps ordinary yields/upkeep/site costs; omit customer-building upkeep
    -- here to avoid charging it twice. Producer investment and actual ready
    -- times remain in the shared model. No fictitious native score is written.
    if not present(districtReady)then return nil,'Customer district readiness unavailable'end
    local function base()
        local copy={};for k,v in pairs(site)do copy[k]=v end
        copy.service=nil;copy.customers={};copy.queueReady={}
        for k,v in pairs(site.queueReady or{})do copy.queueReady[k]=v end
        copy.queueReady[customerCity]=maximum(copy.queueReady[customerCity]or 0,districtReady)
        for _,v in ipairs(site.customers or{})do copy.customers[#copy.customers+1]=v end
        return copy
    end
    local before=base();local after=base();local seen={}
    local function identity(v)return v.plot..':'..(v.transaction and v.transaction.id or v.stage..':'..tostring(v.building))end
    for _,v in ipairs(after.customers)do seen[identity(v)]=true end
    for _,source in ipairs(projected or{})do
        local key=identity(source)
        if source.projected==true and source.city==customerCity and not seen[key]then
            local function customerInvestment(value)
                local copy={};for k,v in pairs(value)do copy[k]=v end
                copy.maintenance=0;copy.prerequisites={}
                for _,required in ipairs(value.prerequisites or{})do
                    copy.prerequisites[#copy.prerequisites+1]=customerInvestment(required)
                end
                return copy
            end
            -- Shrine/Arena etc. are also already priced by the ordinary native
            -- customer forecast. Keep their construction/unlock timing, but do
            -- not charge their recurring upkeep a second time in this residual.
            local row=customerInvestment(source)
            -- Complete only inside this explicit hypothetical ledger. The live
            -- fact and input record remain incomplete and cannot be observed as
            -- constructed, accepted, or delivering a Service.
            row.complete=true;row.working=false;row.maintenance=0
            row.unlock=maximum(row.unlock or INF,districtReady)
            after.customers[#after.customers+1]=row;seen[key]=true
        end
    end
    local without,message=M.Forecast(before,price);if not without then return nil,message end
    local with,error=M.Forecast(after,price);if not with then return nil,error end
    return {valueQ8=with.valueQ8-without.valueQ8,
        bidValueQ8=with.bidValueQ8-without.bidValueQ8,with=with,without=without,
        servicesExcluded=true,customerOrdinaryUpkeepExcluded=true,buildingTransactionsOnly=true,districtReady=districtReady}
end
