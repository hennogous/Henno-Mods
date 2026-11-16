-- Observed routes -> shared channel eligibility -> synchronized city counters.
-- UI reads actual routes and publishes complete snapshots through the existing
-- EXECUTE_SCRIPT receiver. Only that receiver changes gameplay properties.
-- The same immutable observations are exposed read-only to the central AI model;
-- its counterfactuals never become routes or property writes here.
include("CSC_TradeRouteCore")
include("CSC_TradeRouteFacts")
local R=CSC_TradeRouteCore
local definitions,problem=R.ReadDefinitions(GameInfo)
if not definitions then print('CSC_ROUTE_CAPABILITY_UNAVAILABLE '..tostring(problem));return end
local reader=CSC_TradeRouteFacts.New(GameInfo,definitions)
local fields=R.Fields(definitions)
local m_HasPendingRequests=false
local m_RefreshRequested=false
local observed
local factsDirty=true

local function snapshot()
    if not observed or factsDirty or observed.turn~=Game.GetCurrentGameTurn()then
        local value,error=reader.Snapshot(PlayerManager.GetAlive(),Game.GetCurrentGameTurn())
        if not value then print('CSC_ROUTE_FACTS_UNAVAILABLE '..tostring(error));return nil end
        value.version=1;observed=value;factsDirty=false
    end
    return observed
end
ExposedMembers=ExposedMembers or{}
ExposedMembers.CSC_TradeRoutes={GetFacts=snapshot}

-- Compatibility exports used by existing route UI. Their family/stage mapping
-- is read from gameplay definitions, including the original Bakers/Tailors
-- supplied-property versus intact-producer distinction.
function CSC_GetBakersTradeRouteState(origin,destination)
    return R.FamilyStates(definitions,reader.City(origin),reader.City(destination),'BAKERS')
end
function CSC_GetTailorsTradeRouteState(origin,destination)
    return R.FamilyStates(definitions,reader.City(origin),reader.City(destination),'TAILORS')
end

local function authority()
    local id=Game.GetLocalPlayer()
    if id==nil or id<0 then return nil end
    if GameConfiguration.IsNetworkMultiplayer()and Network.GetGameHostPlayerID()~=id then return nil end
    return id
end
local function matches(state)
    local plot=Map.GetPlot(state.CityX,state.CityY)
    if not plot then return false end
    for _,field in ipairs(fields)do
        local value=state[field[1]]
        if(plot:GetProperty(field[2])or 0)~=value then return false end
        if field[3]then
            for _,bit in ipairs({1,2,4,8,16})do
                if(plot:GetProperty(field[2]..'_BIT_'..bit)or 0)~=math.floor(value/bit)%2 then return false end
            end
        end
    end
    return true
end

function CSC_RefreshBakersTradeRouteProperties()
    local sender=authority();m_HasPendingRequests=false
    if sender==nil then return end
    -- A refresh observes again after property/building/route events. All AI
    -- readers in that publication can reuse this one bounded route/city scan.
    observed=nil
    local facts=snapshot();if not facts then return end
    local counts,error=R.Accumulate(facts.routes,facts.cities,definitions)
    if not counts then print('CSC_ROUTE_COUNTS_UNAVAILABLE '..tostring(error));return end
    local keys={};for key in pairs(facts.cities)do keys[#keys+1]=key end
    table.sort(keys,function(a,b)
        local x,y=facts.cities[a],facts.cities[b]
        return x.player<y.player or x.player==y.player and x.city<y.city
    end)
    for _,key in ipairs(keys)do
        local city=facts.cities[key]
        local state={Version=2,Turn=facts.turn,CityPlayerID=city.player,CityID=city.city,
            Revision=city.revision,CityX=city.x,CityY=city.y,HasBakersQuarter=0,
            OnStart='CSC_SetBakersTradeRouteProperties'}
        for _,channel in ipairs(definitions.channels)do
            local count=counts[key].channels[channel.id]
            state[channel.importField]=count.ORIGIN;state[channel.exportField]=count.DESTINATION
            if channel.quarter=='BAKERS'and city.quarters[channel.district]then state.HasBakersQuarter=1 end
        end
        if not matches(state)then
            UI.RequestPlayerOperation(sender,PlayerOperations.EXECUTE_SCRIPT,state)
            m_HasPendingRequests=true
        end
    end
end

local function CSC_OnBakersRouteRefreshEvent()
	-- Coalesce property/building events until the next UI update. A snapshot
	-- must not be assembled midway through a gameplay modifier/property batch.
	m_RefreshRequested = true;
    factsDirty=true;
end

-- Route changes are the important trigger, but several city/building/district events
-- can change eligibility: a Bakery becomes supplied, a Cafe is built, a Quarter is
-- pillaged, or a city changes owner. These events all use the same full refresh.
Events.PlayerTurnActivated.Add(CSC_OnBakersRouteRefreshEvent);

if Events.TradeRouteActivityChanged ~= nil then
	Events.TradeRouteActivityChanged.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityProductionCompleted ~= nil then
	Events.CityProductionCompleted.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityProductionUpdated ~= nil then
	Events.CityProductionUpdated.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.BuildingAddedToMap ~= nil then
	Events.BuildingAddedToMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.BuildingChanged ~= nil then
	Events.BuildingChanged.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.BuildingRemovedFromMap ~= nil then
	Events.BuildingRemovedFromMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.DistrictAddedToMap ~= nil then
	Events.DistrictAddedToMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.DistrictRemovedFromMap ~= nil then
	Events.DistrictRemovedFromMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.DistrictPillaged ~= nil then
	Events.DistrictPillaged.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityTransfered ~= nil then
	Events.CityTransfered.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityAddedToMap ~= nil then
	Events.CityAddedToMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityRemovedFromMap ~= nil then
	Events.CityRemovedFromMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.LoadGameViewStateDone ~= nil then
	Events.LoadGameViewStateDone.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.LoadScreenClose ~= nil then
	Events.LoadScreenClose.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.MultiplayerHostMigrated ~= nil then
	Events.MultiplayerHostMigrated.Add(CSC_OnBakersRouteRefreshEvent);
end
for _, name in ipairs({"CityPropertyChanged", "ResearchCompleted", "CivicCompleted"}) do
	if Events[name] then Events[name].Add(CSC_OnBakersRouteRefreshEvent); end
end

-- Loading only asks the authority to send network operations; it never invokes
-- a gameplay function locally. Delayed/rejected snapshots are retried from fresh
-- state until properties agree, including when a route changed while in flight.
local retryElapsed = 0;
-- Empty AddUserInterfaces contexts start hidden. Hidden contexts do not receive
-- SetUpdate callbacks, so queued route changes would never reach gameplay.
-- There are no visual controls here; showing the context only enables its update.
ContextPtr:SetHide(false);
ContextPtr:SetUpdate(function(delta)
	if m_RefreshRequested then
		m_RefreshRequested = false;
		retryElapsed = 0;
		CSC_RefreshBakersTradeRouteProperties();
		return;
	end
	if not m_HasPendingRequests then retryElapsed = 0; return; end
	retryElapsed = retryElapsed + delta;
	if retryElapsed >= 1 then
		retryElapsed = 0;
		CSC_RefreshBakersTradeRouteProperties();
	end
end);

--=================================================================================================================
--=================================================================================================================
