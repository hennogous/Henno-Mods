-- ===========================================================================
-- Civ Supply Chains compatibility with Sukritact's Simple UI Adjustments
-- ===========================================================================

-- Explicit allowlist for moving CSC trade-route yield modifiers out of the
-- aggregate city-yield "from Modifiers" row. This table and its rows are UI
-- compatibility metadata and load only when Simple UI Adjustments is active.
-- Modifier names remain traceability metadata, never an inference rule.
CREATE TABLE IF NOT EXISTS CSC_TradeRouteYieldPresentation
    (
    EntryId         TEXT PRIMARY KEY NOT NULL,
    QuarterKey      TEXT NOT NULL,
    ModifierId      TEXT NOT NULL UNIQUE,
    PropertyName    TEXT NOT NULL UNIQUE,
    PropertyScope   TEXT NOT NULL,
    YieldType       TEXT NOT NULL,
    Amount          REAL NOT NULL,
    DisplayBucket   TEXT NOT NULL
    );

INSERT OR IGNORE INTO CSC_TradeRouteYieldPresentation
        (   EntryId,                                      QuarterKey,   ModifierId,                                         PropertyName,                                   PropertyScope,          YieldType,          Amount,   DisplayBucket   )
VALUES  (   'CSC_BAKERS_IMPORT_CONSUMER_FOOD',            'BAKERS',     'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD',             'CSC_BAKERS_IMPORT_CONSUMER_ROUTE',            'CITY_CENTER_PLOT',     'YIELD_FOOD',       1,        'OUTGOING_TRADE_ROUTES'   ),
        (   'CSC_BAKERS_IMPORT_SPECIALTY_FOOD',           'BAKERS',     'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD',            'CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',           'CITY_CENTER_PLOT',     'YIELD_FOOD',       1,        'OUTGOING_TRADE_ROUTES'   ),
        (   'CSC_TAILORS_IMPORT_CONSUMER_CULTURE',        'TAILORS',    'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',           'CSC_TAILORS_IMPORT_TAILOR_ROUTE',             'CITY_CENTER_PLOT',     'YIELD_CULTURE',    1,        'OUTGOING_TRADE_ROUTES'   );
