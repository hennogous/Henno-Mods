-- Diagnostic only, installed in PlotInfo by the game controller. These are
-- the Firaxis purchase and treasury events used by StrategicView and the
-- diplomacy ribbon. Keep the events separate. The report matches the offer,
-- district tree, price, observed spend and eventual foundation on the plot.
assert(not CSC_CUSTOMER_LAND_WATCH, 'Duplicate customer land observer')
CSC_CUSTOMER_LAND_WATCH=true
local last,sequence={},{}
for _,player in ipairs(PlayerManager.GetAliveMajors()) do
    local id=player:GetID()
    last[id]=player:GetTreasury():GetGoldBalance()
    sequence[id]=0
end
local function event(id)
    sequence[id]=sequence[id]+1
    return Game.GetCurrentGameTurn(),id,sequence[id]
end
Events.TreasuryChanged.Add(function(id,yield,balance)
    if last[id]==nil then return end
    local previous=last[id]
    last[id]=balance
    -- Log gains as well. An intervening treasury event matters when matching
    -- a debit to a purchase. Balances are Gold as reported in UI, not Q8.
    if previous~=balance then
        local turn,player,ordinal=event(id)
        print('CSC_CUSTOMER_TREASURY',turn,player,ordinal,previous,balance)
    end
end)
Events.CityMadePurchase.Add(function(id,city,x,y,kind)
    if last[id]==nil or kind~=EventSubTypes.PLOT then return end
    local plot=Map.GetPlot(x,y)
    if plot then
        local turn,player,ordinal=event(id)
        print('CSC_CUSTOMER_PLOT_PURCHASE',turn,player,ordinal,city,plot:GetIndex(),x,y)
    end
end)
-- Short replays can nominate particular plots seen in a historical purchase
-- request. Sample those plots even before the planner offers to buy them. The
-- raw price and the unique-buyer price distinguish a costly site from one a
-- different city could buy. CanHaveDistrict checks fit on the map. The native
-- selection journal and purchase event establish the later decisions.
if landTargets and #landTargets>0 then
    local ui=assert(ExposedMembers.CSC_Adjacency)
    local function sample()
        local turn=Game.GetCurrentGameTurn()
        for _,target in ipairs(landTargets) do
            local pid,cityID,district,index=target[1],target[2],target[3],target[4]
            local plot=assert(Map.GetPlotByIndex(index))
            local city=CityManager.GetCity(pid,cityID)
            local known=PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY())
            if city and known then
                local owner=plot:GetOwner()
                local buyer=owner==pid and Cities.GetPlotPurchaseCity(plot)
                local raw,unique
                if owner==-1 then
                    raw=ui.GetRawPlotPurchaseQuote(pid,cityID,index)
                    unique=ui.GetPlotPurchaseQuote(pid,cityID,index)
                end
                print('CSC_CUSTOMER_LAND_TARGET',turn,pid,cityID,district,index,owner,
                    buyer and buyer:GetID() or -1,plot:GetDistrictType(),tostring(raw),tostring(unique),
                    tostring(plot:CanHaveDistrict(district,pid,cityID)),Players[pid]:GetTreasury():GetGoldBalance())
            else
                print('CSC_CUSTOMER_LAND_TARGET_UNAVAILABLE',turn,pid,cityID,district,index,
                    tostring(city~=nil),tostring(known))
            end
        end
    end
    local lastTurn
    local function observe()
        local turn=Game.GetCurrentGameTurn()
        if turn==lastTurn then return end
        lastTurn=turn
        local ok,reason=pcall(sample)
        if not ok then print('CSC_CUSTOMER_LAND_TARGET_FAULT',turn,reason) end
    end
    observe()
    Events.TurnBegin.Add(observe)
end
print('CSC_CUSTOMER_LAND_WATCH_INSTALLED',Game.GetCurrentGameTurn())
