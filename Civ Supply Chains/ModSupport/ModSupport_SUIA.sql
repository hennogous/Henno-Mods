-- CSC compatibility with Sukritact's Simple UI Adjustments. Reclassify only
-- actual origin-side route yield consumers from Modifiers to Outgoing Trade
-- Routes; this presentation metadata changes neither payouts nor city totals.
-- The late validated native read-model supplies partners, bits, yields and
-- amounts, so this UI integration owns no second transaction definition.
CREATE TABLE IF NOT EXISTS CSC_TradeRouteYieldPresentation
    (
    EntryId TEXT PRIMARY KEY NOT NULL,
    QuarterKey TEXT NOT NULL,
    ModifierId TEXT NOT NULL UNIQUE,
    PropertyName TEXT NOT NULL,
    PropertyScope TEXT NOT NULL,
    YieldType TEXT NOT NULL,
    Amount REAL NOT NULL,
    DisplayBucket TEXT NOT NULL
    );

INSERT OR IGNORE INTO CSC_TradeRouteYieldPresentation
    (
        EntryId,
        QuarterKey,
        ModifierId,
        PropertyName,
        PropertyScope,
        YieldType,
        Amount,
        DisplayBucket
    )
SELECT
        'CSC_ROUTE_' || P.ChannelId || '_' || P.LegKey || '_BIT_' || P.Bit,
        C.QuarterKey,
        P.ModifierId,
        C.ImportProperty || '_BIT_' || P.Bit,
        'CITY_CENTER_PLOT',
        P.YieldType,
        P.Amount,
        'OUTGOING_TRADE_ROUTES'
FROM CSC_TradeRoutePayouts P JOIN CSC_TradeRouteChannels C USING (ChannelId)
WHERE P.Recipient = 'ORIGIN' AND P.YieldType <> 'AMENITY';
