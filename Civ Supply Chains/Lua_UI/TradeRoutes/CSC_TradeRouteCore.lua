-- Shared route arithmetic. Gameplay UI supplies observed endpoints/routes,
-- previews supply one candidate, and the AI supplies explicit before/after
-- facts. This kernel reads no game objects, writes no properties and invents
-- neither routes nor workers. Native SQL is the payout authority; its validated
-- read-model supplies every actual bit, including optional Gold companions.
CSC_TradeRouteCore={}
local R=CSC_TradeRouteCore

local function finite(v)return(type(v)=='number'or type(v)=='integer')and v==v and math.abs(v)<math.huge end
function R.CityKey(player,city)
    if not finite(player)or not finite(city)or player<0 or city<0 or player%1~=0 or city%1~=0 then return nil end
    return string.format('%.0f:%.0f',player,city)
end

function R.ReadDefinitions(info)
    for _,name in ipairs({'CSC_TradeRouteChannels','CSC_TradeRouteChannelFacts','CSC_TradeRouteSupplyRequirements',
        'CSC_TradeRoutePayoutBindings','CSC_TradeRoutePayouts'})do
        if not info[name]then return nil,'Route definition table unavailable: '..name end
    end
    local result={channels={},byId={}}
    for row in info.CSC_TradeRouteChannels()do
        local channel={id=row.ChannelId,quarter=row.QuarterKey,producer=row.ProducerBuildingType,
            requireProducer=row.RequireProducerBuilding==1 or row.RequireProducerBuilding==true,
            importField=row.ImportField,exportField=row.ExportField,
            importProperty=row.ImportProperty,exportProperty=row.ExportProperty,requirements={},legs={},payouts={}}
        result.channels[#result.channels+1]=channel;result.byId[channel.id]=channel
    end
    if #result.channels==0 then return nil,'No route channels'end
    table.sort(result.channels,function(a,b)return a.id<b.id end)
    for row in info.CSC_TradeRouteChannelFacts()do
        local channel=result.byId[row.ChannelId]
        if not channel then return nil,'Unknown route facts'end
        channel.supplyProperty=row.SupplyProperty;channel.district=row.OriginDistrictType;channel.stage=row.ProducerStage
    end
    for row in info.CSC_TradeRouteSupplyRequirements()do
        local channel=result.byId[row.ChannelId]
        if not channel then return nil,'Unknown route supply requirement'end
        channel.requirements[#channel.requirements+1]={tag=row.MaterialClass,count=row.MinimumCount}
    end
    for row in info.CSC_TradeRoutePayoutBindings()do
        local channel=result.byId[row.ChannelId]
        if not channel or channel.legs[row.LegKey]then return nil,'Invalid route payout binding'end
        channel.legs[row.LegKey]={recipient=row.Recipient,bits={}}
    end
    for row in info.CSC_TradeRoutePayouts()do
        local channel=result.byId[row.ChannelId]
        local leg=channel and channel.legs[row.LegKey]
        if not leg or leg.bits[row.Bit]or not finite(row.Amount)or not row.YieldType
            or leg.recipient~=row.Recipient then return nil,'Invalid native route payout row'end
        local payout={leg=row.LegKey,recipient=row.Recipient,bit=row.Bit,yield=row.YieldType,
            amount=row.Amount,building=row.BuildingType}
        leg.bits[row.Bit]=payout;channel.payouts[#channel.payouts+1]=payout
    end
    for _,channel in ipairs(result.channels)do
        if not channel.supplyProperty or not channel.district or not channel.stage or #channel.requirements==0 then
            return nil,'Incomplete route channel: '..channel.id
        end
        local count=0
        for _,leg in pairs(channel.legs)do
            count=count+1
            for _,bit in ipairs({1,2,4,8,16})do if not leg.bits[bit]then return nil,'Missing native route bit: '..channel.id end end
        end
        if count==0 or #channel.payouts~=5*count then return nil,'Incomplete native route payouts: '..channel.id end
        table.sort(channel.payouts,function(a,b)return a.leg<b.leg or a.leg==b.leg and a.bit<b.bit end)
    end
    return result
end

function R.Eligible(channel,origin,destination)
    if not origin or not destination or(origin.quarters or{})[channel.district]then return false end
    local supplied=tonumber((destination.properties or{})[channel.supplyProperty])or 0
    return supplied>0 and(not channel.requireProducer or(destination.buildings or{})[channel.producer]==true)
end

function R.FamilyStates(definitions,origin,destination,quarter)
    local states={}
    for _,channel in ipairs(definitions.channels)do if channel.quarter==quarter then
        states[channel.stage]=R.Eligible(channel,origin,destination)or states[channel.stage]
    end end
    return states[3]==true,states[4]==true
end

-- Protocol fields are generated from the same channel relationships. The one
-- historical Quarter flag remains for existing SQL/save consumers. Sorting is
-- the deterministic mutation/publication order shared by UI and gameplay.
function R.Fields(definitions)
    local result={{'HasBakersQuarter','CSC_HAS_BAKERS_QUARTER'}}
    for _,channel in ipairs(definitions.channels)do
        result[#result+1]={channel.importField,channel.importProperty,true}
        result[#result+1]={channel.exportField,channel.exportProperty,true}
    end
    return result
end

function R.Accumulate(routes,cities,definitions)
    local counts={}
    for key,city in pairs(cities)do
        if key~=R.CityKey(city.player,city.city)then return nil,'Route endpoint identity mismatch'end
        counts[key]={player=city.player,city=city.city,channels={}}
        for _,channel in ipairs(definitions.channels)do counts[key].channels[channel.id]={ORIGIN=0,DESTINATION=0}end
    end
    for _,route in ipairs(routes)do
        local origin,destination=cities[route.origin],cities[route.destination]
        -- The game can expose an obsolete route while its endpoint is removed.
        -- The scanner has always skipped such routes; keep that native UI rule.
        if origin and destination then
            for _,channel in ipairs(definitions.channels)do if R.Eligible(channel,origin,destination)then
                local o=counts[route.origin].channels[channel.id]
                local d=counts[route.destination].channels[channel.id]
                o.ORIGIN=o.ORIGIN+1;d.DESTINATION=d.DESTINATION+1
            end end
        end
    end
    return counts
end

-- Counts remain complete integers. Evaluate their actual five bits instead of
-- clamping31 or multiplying by a copied unit rate:32 wraps to0 in current SQL.
-- Destination building yields require an intact receiving building even when
-- a Bakers supplied-property observation alone permits the origin's imports.
function R.EvaluateBits(channel,count,recipient,city)
    if not finite(count)or count<0 or count%1~=0 then return nil,'Invalid route count'end
    local amounts={}
    for _,payout in ipairs(channel.payouts)do
        if payout.recipient==recipient and math.floor(count/payout.bit)%2==1
            and(not payout.building or city and(city.buildings or{})[payout.building])then
            amounts[payout.yield]=(amounts[payout.yield]or 0)+payout.amount
        end
    end
    return amounts
end

-- UI displays this one route's nominal transaction (bit1), separately from AI
-- comparisons of complete city totals. Do not label it an aggregate/marginal.
function R.Nominal(definitions,origin,destination,recipient)
    local amounts={}
    for _,channel in ipairs(definitions.channels)do if R.Eligible(channel,origin,destination)then
        local city=recipient=='ORIGIN'and origin or destination
        for yield,amount in pairs(R.EvaluateBits(channel,1,recipient,city))do amounts[yield]=(amounts[yield]or 0)+amount end
    end end
    return amounts
end

function R.Economy(counts,cities,definitions,player)
    local streams={}
    for key,state in pairs(counts)do if state.player==player then
        for _,channel in ipairs(definitions.channels)do
            local values=state.channels[channel.id]
            for _,recipient in ipairs({'ORIGIN','DESTINATION'})do
                local amounts,error=R.EvaluateBits(channel,values[recipient],recipient,cities[key])
                if not amounts then return nil,error end
                for yield,amount in pairs(amounts)do if amount~=0 then
                    streams[#streams+1]={id='route:'..key..':'..channel.id..':'..recipient..':'..yield,
                        player=state.player,city=state.city,yield=yield,amount=amount}
                end end
            end
        end
    end end
    table.sort(streams,function(a,b)return a.id<b.id end)
    return streams
end

-- Native38f720: speed-adjust the base duration and current global-era change
-- separately, flooring each, then impose at least one turn after operation
-- start. This is current-policy earliest eligibility, not actual route expiry:
-- CheckComplete66bf70 also waits for the trader's return to its origin.
function R.MinimumEnd(start,base,multiplier,eraChange)
    local values={start,base,multiplier,eraChange}
    for i=1,4 do
        local v=values[i]
        if not finite(v)or v%1~=0 then return nil,'Native route duration input unavailable'end
    end
    if start<0 or base<0 or multiplier<=0 then return nil,'Invalid native route duration input'end
    return start+math.max(1,math.floor(base*multiplier/100)+math.floor(eraChange*multiplier/100))
end

-- Plain-record route counterfactual over explicitly observed valuation windows.
-- Callers supply future producer/supply/Quarter changes from the central plan.
-- The kernel neither constructs a route nor assumes renewal. Unknown remaining
-- lifetime supports the current observation only (one turn), not fifty turns
-- of invented trade. Segments merge across irrelevant events, preserving equal
-- before/after pricing and avoiding extra native quote work.
function R.Forecast(world,definitions,player,horizon)
    if not finite(horizon)or horizon<=0 then return nil,'Finite route horizon required'end
    if type(world.cities)~='table'or type(world.routes)~='table'then return nil,'Route observations unavailable'end
    if #world.routes>(world.maxRoutes or 4096)then return nil,'Route forecast budget exceeded'end
    local cities,events,times={}, {},{[0]=true,[horizon]=true}
    for key,source in pairs(world.cities)do
        local city={player=source.player,city=source.city}
        for _,field in ipairs({'quarters','buildings','properties'})do
            city[field]={};for k,v in pairs(source[field]or{})do city[field][k]=v end
        end
        cities[key]=city
    end
    for _,change in ipairs(world.changes or{})do
        if not finite(change.ready)or change.ready<0 or not cities[change.city]
            or(change.field~='quarters'and change.field~='buildings'and change.field~='properties')then
            return nil,'Invalid route counterfactual event'
        end
        if change.ready<horizon then
            local bucket=events[change.ready]or{};events[change.ready]=bucket;times[change.ready]=true
            local key=change.city..':'..change.field..':'..change.key
            if bucket[key]and bucket[key].value~=change.value then return nil,'Conflicting route counterfactual events'end
            bucket[key]=change
        end
    end
    for _,route in ipairs(world.routes)do
        local through=route.observedThrough or 1
        if not finite(through)or through<0 then return nil,'Invalid route observation window'end
        if through<horizon then times[through]=true end
    end
    local ordered={};for t in pairs(times)do ordered[#ordered+1]=t end;table.sort(ordered)
    if #ordered>(world.maxEvents or 128)then return nil,'Route event budget exceeded'end
    local result,last={},{}
    for i=1,#ordered-1 do
        local ready,finish=ordered[i],ordered[i+1]
        for _,change in pairs(events[ready]or{})do cities[change.city][change.field][change.key]=change.value end
        local active={}
        for _,route in ipairs(world.routes)do if(route.observedThrough or 1)>ready then active[#active+1]=route end end
        local counts,error=R.Accumulate(active,cities,definitions);if not counts then return nil,error end
        local streams,message=R.Economy(counts,cities,definitions,player);if not streams then return nil,message end
        for _,stream in ipairs(streams)do
            local previous=last[stream.id]
            if previous and previous.finish==ready and previous.amount==stream.amount then previous.finish=finish
            else
                local baseId=stream.id;stream.id=baseId..'@'..ready
                stream.ready=ready;stream.finish=finish
                result[#result+1]=stream;last[baseId]=stream
            end
        end
    end
    table.sort(result,function(a,b)return a.id<b.id end)
    return result
end
