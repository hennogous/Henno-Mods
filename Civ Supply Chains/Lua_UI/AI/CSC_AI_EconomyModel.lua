-- Central CSC economic ledger. The facts adapter supplies physical footprints,
-- available investments and relative ready times; this module owns transaction
-- application, recipients, alternatives and marginal values. It never reads a game
-- object, publishes a bid, grants anything or assumes an unbuilt district.
-- A pricing adapter converts recurring yields/amenities to native Q8 utility.
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

-- Gameplay pays population returns using a Q8 per-receiving-citizen rate.
-- Round the combined target once, independently for each receiving city.
function M.PopulationPayout(target, population)
    if target<=0 or population<=0 then return 0 end
    return math.min(32767,math.ceil(target/population*256-1e-9))*population/256
end

local function newLedger(site,second)
    return {result={streams={},investments={},omissions={},byBuilding={},futureDepths={},alternative=second and second.type,
        siteAdjustmentQ8=site.nativeSiteAdjustmentQ8 or 0,
        adjacency=(site.adjacency or 0)+(second and second.terrain or 0)},seen={},clocks={},populationFlows={}}
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
        if not stream.existingIncome and stream.amount>0 and stream.yield:find('YIELD_',1,true)==1
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
            ready=definition.hostReady
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
    local quarter=site.quarterReady
    if not present(quarter) then omit('quarter','Unknown Quarter readiness');return result end
    clocks[cityKey(site.city)]=maximum(clocks[cityKey(site.city)]or 0,quarter)
    -- A prospective customer district occupies its city's queue before its
    -- buildings. This plain-record reservation is shared by both sides of a
    -- marginal comparison; it does not reserve native production or delay an
    -- already working building. Separate cities can still invest in parallel.
    for city,ready in pairs(site.queueReady or{})do
        if present(ready)then clocks[cityKey(city)]=maximum(clocks[cityKey(city)]or 0,ready)end
    end
    for _,flow in ipairs(site.direct or {})do
        emit('site:'..flow.id,flow.yield,flow.amount,quarter,flow.city)
    end
    if not site.existing then emit('quarter-upkeep','YIELD_GOLD',-(site.maintenance or 0),quarter)end
    if (site.purchaseGold or 0)>0 then
        emit('footprint-purchase','YIELD_GOLD',-site.purchaseGold,0,site.city)
        result.streams[#result.streams].fixed=true
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
            if transaction then
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
                    local city=leg.recipient=='SOURCE'and site.city or customer.city
                    local population=leg.recipient=='SOURCE'and site.population or customer.population
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
    if site.service then
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
    -- Specialist slots, trade and later Services are not free assumed income.
    -- Facts/adapter diagnostics expose these omissions; retain the separate
    -- Service-aware nomination policy until those economic channels are priced.
    for _,reason in ipairs(site.omissions or {})do omit('coverage',reason)end
    -- Attribution is metadata for a decision adapter, never extra production.
    -- Existing investments, amenities, costs and immediate site yields receive
    -- no future-building depth premium. The adapter may map positive ordinary
    -- income of missing buildings to native-style effective building income.
    if shared then return result end
    context.populationBaselines=site.populationBaselines
    return finishLedger(context)
end

function M.Price(result,price,horizon)
    local total,bid=result.siteAdjustmentQ8 or 0,result.siteAdjustmentQ8 or 0
    for _,stream in ipairs(result.streams)do
        local value,weighted=price(stream, horizon)
        if not numeric(value) or value~=math.floor(value)then
            return nil,'Native price unavailable for '..stream.id
        end
        if weighted==nil then weighted=value end
        if not numeric(weighted)or weighted~=math.floor(weighted)then return nil,'Native bid price unavailable for '..stream.id end
        stream.valueQ8=value;stream.bidValueQ8=weighted;total=total+value;bid=bid+weighted
    end
    result.bidValueQ8=bid;result.forecastAdjustmentQ8=bid-total
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
-- production queue. This diagnostic entry evaluates them in one context; it
-- does not publish native packets. The facts adapter must include the complete
-- affected closure and every contributor to its population properties.
-- Minimal and all-enabled seeds let jointly profitable shared venues enter the
-- search even when each producer alone cannot cover their upkeep. Two sweeps
-- per seed bound the search. Exhausting the work
-- budget returns unavailable instead of presenting a partial world as complete.
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
    if #sites==0 then return nil,'No affected Quarter chains'end
    if #sites>(world.maxChains or 64)then return nil,'Affected chain budget exceeded'end
    table.sort(sites,function(a,b)return a.key<b.key end)
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
        if mask%2==0 and site.third and not site.third.working and not site.third.intactOwner then value.third=nil end
        if mask<2 and site.fourth and not site.fourth.working and not site.fourth.intactOwner then value.fourth=nil end
        value.customers={};for _,v in ipairs(site.customers or{})do value.customers[#value.customers+1]=v end
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
            if not seen[identity]then result[#result+1]=candidate;seen[identity]=true end
        end end
        return result
    end
    local alternatives,nodes,nodeKeys={},{},{}
    for i,site in ipairs(sites)do
        alternatives[i]=options(site)
        for _,customer in ipairs(site.customers or{})do
            if customer.type and not customer.working and not customer.intactOwner then
                local key=tostring(site.player or 0)..':'..customer.city..':'..customer.type
                if not nodeKeys[key]then nodes[#nodes+1]=key;nodeKeys[key]=true end
            end
        end
    end
    table.sort(nodes)
    local function evaluate(selected,disabled)
        evaluations=evaluations+1
        if evaluations>limit then return nil,'Joint evaluation budget exceeded'end
        local context=newLedger(sites[1],nil)
        context.joint=true;context.result.siteAdjustmentQ8=0;context.result.chainStages={}
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
        local value,error=M.Price(result,price,horizon)
        if not value then return nil,error end
        result.valueQ8=value;result.servicesExcluded=true;result.diagnosticOnly=true
        return result
    end
    local best
    for seed=1,2 do
        local selected,disabled={},{}
        for i,choices in ipairs(alternatives)do selected[i]=choices[seed==1 and 1 or #choices]end
        local current,message=evaluate(selected,disabled);if not current then return nil,message end
        for sweep=1,2 do
            for i,site in ipairs(sites)do
                local chosen=selected[i]
                for _,candidate in ipairs(alternatives[i])do
                    selected[i]=candidate
                    local result,error=evaluate(selected,disabled);if not result then return nil,error end
                    if result.valueQ8>current.valueQ8 then current,chosen=result,candidate end
                end
                selected[i]=chosen
            end
            -- Choose unique physical customer investments globally. A venue
            -- built for one Quarter automatically serves every eligible adjacent
            -- producer; deleting one chain's edge would invent a gameplay choice
            -- that does not exist. Relationship records therefore stay immutable.
            for _,key in ipairs(nodes)do
                local previous=disabled[key];disabled[key]=not previous or nil
                local result,error=evaluate(selected,disabled);if not result then return nil,error end
                if result.valueQ8>current.valueQ8 or result.valueQ8==current.valueQ8 and disabled[key]then
                    current=result
                else disabled[key]=previous end
            end
        end
        if not best or current.valueQ8>best.valueQ8 then best=current end
    end
    best.evaluations=evaluations;best.affectedChains=#sites
    return best
end

-- Both worlds are explicit plain facts. Only the after-world reserves the new
-- district's queue time, changes footprints and adds venues. The ordinary native
-- valuation and its overlap are reconciled by the later decision adapter.
function M.JointCustomerForecast(beforeWorld,afterWorld,price)
    if beforeWorld.horizon~=afterWorld.horizon then return nil,'Marginal horizons differ'end
    local before,message=M.JointForecast(beforeWorld,price);if not before then return nil,message end
    local after,error=M.JointForecast(afterWorld,price);if not after then return nil,error end
    return {before=before,after=after,valueQ8=after.valueQ8-before.valueQ8,
        bidValueQ8=after.bidValueQ8-before.bidValueQ8,servicesExcluded=true,diagnosticOnly=true}
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
