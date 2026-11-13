-- Central CSC economic ledger. The facts adapter supplies physical footprints,
-- available investments and relative ready times; this module owns transaction
-- amounts, recipients, alternatives and marginal values. It never reads a game
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

-- Gameplay pays population returns using a Q8 per-receiving-citizen rate.
-- Round the combined target once, independently for each receiving city.
function M.PopulationPayout(target, population)
    if target<=0 or population<=0 then return 0 end
    return math.min(32767,math.ceil(target/population*256-1e-9))*population/256
end

local function ledger(site, second)
    local result={streams={},investments={},omissions={},byBuilding={},alternative=second and second.type,
        adjacency=(site.adjacency or 0)+(second and second.terrain or 0)}
    local seen,clocks,populationFlows,customerTimes={},{},{},{}
    local function emit(id,yield,amount,ready,city,building)
        if amount==0 or not present(ready) or ready>=site.horizon then return end
        assert(not seen[id],'Duplicate economic relationship: '..id)
        seen[id]=true
        result.streams[#result.streams+1]={id=id,yield=yield,amount=amount,ready=ready,
            city=city or site.city,building=building}
    end
    local function omit(id,reason)
        result.omissions[#result.omissions+1]={id=id,reason=reason}
    end
    local function invest(definition,prerequisite,recipient)
        if not definition then return INF end
        recipient=recipient or site.city
        local stamp=recipient..':'..definition.type
        if result.byBuilding[stamp]~=nil then return result.byBuilding[stamp]end
        local ready
        if definition.working then ready=0
        elseif definition.excluded then return INF
        elseif present(definition.unlock) and present(definition.turns) and present(prerequisite) then
            for _,required in ipairs(definition.prerequisites or {})do
                prerequisite=maximum(prerequisite,invest(required,prerequisite,recipient))
            end
            ready=maximum(definition.unlock,prerequisite,clocks[recipient]or 0)+definition.turns
            clocks[recipient]=ready
        else omit(definition.type,'Unknown unlock, construction or prerequisite timing');return INF end
        result.byBuilding[stamp]=ready
        if ready>0 then result.investments[#result.investments+1]={type=definition.type,
            ready=ready,cost=definition.cost or 0,city=recipient} end
        -- Production cost is represented by serial construction delay, matching
        -- the native income-stream convention. Do not also subtract the whole
        -- cost as an invented universal utility conversion. Upkeep is a real
        -- recurring cost and starts with the building, not at Quarter placement.
        if not definition.working then emit('upkeep:'..stamp,'YIELD_GOLD',
            -(definition.maintenance or 0),ready,recipient,definition.type) end
        return ready
    end
    local quarter=site.quarterReady
    if not present(quarter) then omit('quarter','Unknown Quarter readiness');return result end
    clocks[site.city]=quarter
    for _,flow in ipairs(site.direct or {})do
        emit('site:'..flow.id,flow.yield,flow.amount,quarter,flow.city)
    end
    if not site.existing then emit('quarter-upkeep','YIELD_GOLD',-(site.maintenance or 0),quarter)end
    if (site.purchaseGold or 0)>0 then
        emit('footprint-purchase','YIELD_GOLD',-site.purchaseGold,0,site.city)
        result.streams[#result.streams].fixed=true
    end
    local stages={}
    local function populationFlow(id,yield,target,ready,city,population,property)
        if not present(ready)or ready>=site.horizon or target<=0 then return end
        local key=city..':'..yield..':'..tostring(property or id)
        local list=populationFlows[key]or{};populationFlows[key]=list
        list[#list+1]={id=id,yield=yield,target=target,ready=ready,city=city,population=population}
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
            if customer.type then customerTimes[customer]=present(stages[stage])and invest(customer,0,customer.city)or INF
            elseif customer.city==site.city and not customer.working and present(customer.unlock)and present(customer.turns)then
                customerTimes[customer]=maximum(clocks[customer.city]or 0,customer.unlock,stages[stage])+customer.turns
                clocks[customer.city]=customerTimes[customer]
            else customerTimes[customer]=customer.ready or INF end
        end end
    end
    local ready2=stages[2]
    if second then emit('producer-terrain','YIELD_PRODUCTION',second.terrain or 0,ready2,site.city,second.type)end
    for _,supplier in ipairs(site.suppliers or {})do
        local stage=supplier.kind=='base' and 2 or 4
        local start=maximum(stages[stage],supplier.ready or INF)
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
    for _,stage in ipairs({3,4})do
        local definition
        if stage==3 then definition=site.third else definition=site.fourth end
        if definition then
            local start=maximum(ready2,stages[stage])
            -- The selected Stage2 alternative is the only local recipient.
            -- Never credit both mutually-exclusive Mills for one transaction.
            local rates=definition.rates or {production=1,gold=1,outward=1}
            emit('local-production:'..stage,'YIELD_PRODUCTION',rates.production,start,site.city,definition.type)
            emit('local-gold:'..stage,'YIELD_GOLD',rates.gold,start,site.city,definition.type)
            emit('local-return:'..stage,site.materialYield,rates.outward,start,site.city,definition.type)
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
            if stage==3 then
                quantity=(customer.population or 0)*(customer.rate or 0)
                -- Gameplay rounds the sum once per recipient/property, not
                -- once per edge. Emit changes in that aggregate at each ready
                -- time, so adding a second venue cannot round twice.
                populationFlow('sale-production','YIELD_PRODUCTION',quantity,start,site.city,site.population,customer.sellerProperty)
                populationFlow('sale-gold','YIELD_GOLD',quantity,start,site.city,site.population,customer.sellerProperty)
                populationFlow('sale-return',outward,quantity,start,customer.city,customer.population or 0,customer.customerProperty)
                sellerAmount,buyerAmount=0,0
            elseif stage==4 then
                quantity=math.floor((customer.population or 0)/5)
                sellerAmount,buyerAmount=quantity,quantity
            else
                local rates=customer.rates or {production=1,gold=1,outward=1}
                sellerAmount,buyerAmount=quantity,quantity
                emit('sale-production:'..customer.plot..':'..stage..':'..tostring(customer.building),'YIELD_PRODUCTION',rates.production*quantity,start,site.city)
                emit('sale-gold:'..customer.plot..':'..stage..':'..tostring(customer.building),'YIELD_GOLD',rates.gold*quantity,start,site.city)
                emit('sale-return:'..customer.plot..':'..stage..':'..tostring(customer.building),outward,rates.outward*quantity,start,customer.city)
                sellerAmount,buyerAmount=0,0
            end
            local key=customer.plot..':'..stage..':'..tostring(customer.building)
            emit('sale-production:'..key,'YIELD_PRODUCTION',sellerAmount,start,site.city)
            emit('sale-gold:'..key,'YIELD_GOLD',sellerAmount,start,site.city)
            emit('sale-return:'..key,outward,buyerAmount,start,customer.city)
            if customer.investment then result.investments[#result.investments+1]=customer.investment end
        end
    end
    for key,flows in pairs(populationFlows)do
        table.sort(flows,function(a,b)return a.ready<b.ready end)
        local target=(site.populationBaselines or{})[key]or 0
        local paid=M.PopulationPayout(target,flows[1].population)
        for i,flow in ipairs(flows)do
            target=target+flow.target
            if i==#flows or flows[i+1].ready~=flow.ready then
                local payout=M.PopulationPayout(target,flow.population)
                emit('population:'..key..':'..flow.ready,flow.yield,payout-paid,flow.ready,flow.city)
                paid=payout
            end
        end
    end
    -- Specialist slots and missing trade/Service valuation are not free income.
    -- Facts/adapter diagnostics expose these omissions; retain the separate
    -- Service-aware nomination policy until those economic channels are priced.
    for _,reason in ipairs(site.omissions or {})do omit('coverage',reason)end
    return result
end

function M.Price(result,price,horizon)
    local total=0
    for _,stream in ipairs(result.streams)do
        local value=price(stream, horizon)
        if not numeric(value) or value~=math.floor(value)then
            return nil,'Native price unavailable for '..stream.id
        end
        stream.valueQ8=value;total=total+value
    end
    return total
end

function M.Forecast(site,price,placementObjective)
    assert(present(site.horizon) and site.horizon>0,'Finite forecast horizon required')
    if not present(site.quarterReady)then return nil,'Quarter readiness unavailable'end
    local best
    local choices={false}
    for _,second in ipairs(site.seconds or {})do choices[#choices+1]=second end
    local function evaluate(plan,second)
        local result=ledger(plan,second or nil)
        local value,error=M.Price(result,price,site.horizon)
        if not value then return nil,error end
        result.valueQ8=value;return result
    end
    -- Optional later producers cannot make a good Stage2 investment worse.
    -- Four bounded stage plans include 2, 2+3, 2+4 and 2+3+4; already working
    -- buildings stay physical facts. Then greedily omit unprofitable missing
    -- customer buildings. This is bounded best-effort planning, not a claim to
    -- solve every ordering/subset of an empire's future production perfectly.
    for _,second in ipairs(choices)do for mask=0,3 do
        local plan={};for k,v in pairs(site)do plan[k]=v end
        if mask%2==0 and site.third and not site.third.working then plan.third=nil end
        if mask<2 and site.fourth and not site.fourth.working then plan.fourth=nil end
        plan.customers={};for _,customer in ipairs(site.customers or {})do plan.customers[#plan.customers+1]=customer end
        local result,error=evaluate(plan,second)
        if not result then return nil,error end
        for i=#plan.customers,1,-1 do
            if not plan.customers[i].working then
                local reduced={};for k,v in pairs(plan)do reduced[k]=v end
                reduced.customers={}
                for j,v in ipairs(plan.customers)do if j~=i then reduced.customers[#reduced.customers+1]=v end end
                local alternative,message=evaluate(reduced,second)
                if not alternative then return nil,message end
                if alternative.valueQ8>=result.valueQ8 then plan,result=reduced,alternative end
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
