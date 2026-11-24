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
print('CSC_CUSTOMER_LAND_WATCH_INSTALLED',Game.GetCurrentGameTurn())
