-- Observed game-object boundary for the shared pure route kernel. UI gameplay
-- scanning, previews and the AI bridge use this reader. It never grants routes
-- or writes properties. A snapshot contains actual outgoing routes only; city
-- IDs are always qualified by owner, including foreign origins/destinations.
CSC_TradeRouteFacts={}
local A=CSC_TradeRouteFacts
local R=assert(CSC_TradeRouteCore)

-- Gameplay-only duration qualification. Outgoing UI records expose identities
-- and yields, not a timer. The existing unit-operation API supplies the native
-- start turn; current global-era/speed definitions supply earliest end eligibility.
-- Returning to origin and interruptions are additional conditions, so the window
-- is a conservative current-policy minimum, never a promised expiry or renewal.
function A.QualifyWindows(observed,info,game,configuration,players,operations)
    local now=game.GetCurrentGameTurn()
    -- A UI publication may precede Gameplay's turn transition by one turn.
    -- A trader can finish and receive another route in that gap: the newer
    -- operation must never lend its duration to the old observed endpoints.
    -- Older/future packets carry no usable observation of today's route.
    local observedTurn=observed.turn
    local observationCurrent=(type(observedTurn)=='number'or type(observedTurn)=='integer')
        and observedTurn==observedTurn and observedTurn%1==0 and observedTurn>=0
        and observedTurn<=now and now-observedTurn<=1
    local parametersOK,parameters=pcall(function()
        local base=info.GlobalParameters and info.GlobalParameters.TRADE_ROUTE_TURN_DURATION_BASE
        local speed=info.GameSpeeds and info.GameSpeeds[configuration.GetGameSpeedType()]
        local era=info.Eras and info.Eras[game.GetEras():GetCurrentEra()]
        if not era then return nil end
        local expansion=info.Eras_XP2 and info.Eras_XP2[era.EraType]
        if info.Eras_XP2 and not expansion then
            -- Relational GameInfo tables need not expose a string-key index.
            -- Join by EraType rather than assuming the two row indices agree.
            for row in info.Eras_XP2()do if row.EraType==era.EraType then expansion=row;break end end
        end
        return{base=base and tonumber(base.Value),multiplier=speed and tonumber(speed.CostMultiplier),
            era=era.EraType,adjustment=expansion and tonumber(expansion.TradeRouteMinimumEndTurnChange)or 0}
    end)
    local result={version=observed.version,turn=observed.turn,durationTurn=now,cities=observed.cities,routes={},
        durationStats={qualified=0,unknown=0,eligibleToFinish=0}}
    result.durationPolicy=parametersOK and parameters or nil
    local function hashEqual(a,b)
        return(type(a)=='number'or type(a)=='integer')and(type(b)=='number'or type(b)=='integer')
            and a%4294967296==b%4294967296
    end
    for _,route in ipairs(observed.routes)do
        local record={origin=route.origin,destination=route.destination,native=route.native,observedThrough=1}
        local ok,earliest,start=pcall(function()
            if not observationCurrent then return nil,'Route observation turn unavailable or stale'end
            local player=players[route.native.TraderUnitPlayer]
            local unit=player and player:GetUnits():FindID(route.native.TraderUnitID)
            if not unit or not unit.GetOperationType or not unit.GetOperationParameter then return nil,'Trader operation unavailable'end
            if not hashEqual(unit:GetOperationType(),operations.MAKE_TRADE_ROUTE)then return nil,'Trader operation changed'end
            local started=unit:GetOperationParameter(operations.PARAM_TURN)
            if(type(started)~='number'and type(started)~='integer')or started<0 or started%1~=0 or started>observedTurn then
                return nil,'Native operation start unavailable'
            end
            if not parametersOK or not parameters then return nil,'Native duration context unavailable'end
            local ending,problem=R.MinimumEnd(started,parameters.base,parameters.multiplier,parameters.adjustment)
            if not ending then return nil,problem end
            return ending,started
        end)
        if ok and earliest then
            record.nativeStartTurn=start;record.currentPolicyEarliestEnd=earliest
            record.observedThrough=math.max(1,earliest-now)
            result.durationStats.qualified=result.durationStats.qualified+1
            if earliest<=now then result.durationStats.eligibleToFinish=result.durationStats.eligibleToFinish+1 end
        else
            record.durationUnavailable=tostring(ok and start or earliest)
            result.durationStats.unknown=result.durationStats.unknown+1
        end
        result.routes[#result.routes+1]=record
    end
    return result
end

function A.New(info,definitions)
    local reader={}
    function reader.City(city)
        if not city then return nil end
        local result={player=city:GetOwner(),city=city:GetID(),x=city:GetX(),y=city:GetY(),
            revision=city:GetProperty('CSC_TRADE_ROUTE_REVISION')or 0,
            quarters={},properties={},buildings={},counts={}}
        result.key=assert(R.CityKey(result.player,result.city))
        local districts,buildings=city:GetDistricts(),city:GetBuildings()
        for _,channel in ipairs(definitions.channels)do
            local district=info.Districts[channel.district]
            -- Preserve the existing scanner's HasDistrict/IsPillaged rule.
            -- HasDistrict includes foundations (native715b0, default flagsfalse).
            -- Imports therefore stop at foundation, not construction completion.
            -- Do not silently add an IsComplete or destination-Quarter gate.
            if result.quarters[channel.district]==nil then
                result.quarters[channel.district]=district and districts and districts:HasDistrict(district.Index)
                    and(not districts.IsPillaged or not districts:IsPillaged(district.Index))or false
            end
            local producer=info.Buildings[channel.producer]
            result.buildings[channel.producer]=producer and buildings and buildings:HasBuilding(producer.Index)
                and(not buildings.IsPillaged or not buildings:IsPillaged(producer.Index))or false
            result.properties[channel.supplyProperty]=city:GetProperty(channel.supplyProperty)or 0
            result.counts[channel.importProperty]=city:GetProperty(channel.importProperty)or 0
            result.counts[channel.exportProperty]=city:GetProperty(channel.exportProperty)or 0
        end
        return result
    end
    function reader.Snapshot(players,turn)
        local result={turn=turn,cities={},routes={}}
        local ordered={};for _,player in ipairs(players)do ordered[#ordered+1]=player end
        table.sort(ordered,function(a,b)return a:GetID()<b:GetID()end)
        for _,player in ipairs(ordered)do
            local cities={}
            for _,city in player:GetCities():Members()do cities[#cities+1]=city end
            table.sort(cities,function(a,b)return a:GetID()<b:GetID()end)
            for _,city in ipairs(cities)do
                local facts=reader.City(city);result.cities[facts.key]=facts
                local trade=city:GetTrade()
                for _,route in ipairs(trade and trade:GetOutgoingRoutes()or{})do
                    local destination=R.CityKey(route.DestinationCityPlayer,route.DestinationCityID)
                    if destination then
                        local record={origin=facts.key,destination=destination,native={}}
                        -- Retain scalar observations for lifetime qualification;
                        -- cached BTS counters are not native route-duration data.
                        for k,v in pairs(route)do
                            if type(v)=='number'or type(v)=='integer'or type(v)=='string'or type(v)=='boolean'then record.native[k]=v end
                        end
                        result.routes[#result.routes+1]=record
                    end
                    if #result.routes>4096 then return nil,'Route snapshot budget exceeded'end
                end
            end
        end
        return result
    end
    return reader
end
