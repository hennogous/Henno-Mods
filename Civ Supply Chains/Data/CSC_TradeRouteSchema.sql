-- Route relationships are gameplay definitions; native modifier arguments remain
-- the sole payout authority. The late processor exposes their actual five bit
-- rows and finite supply gates to gameplay UI, previews and the AI model.
-- No amount/yield is authored twice, and no native effect is rewritten here.
CREATE TABLE IF NOT EXISTS CSC_TradeRouteChannels
    (
    ChannelId TEXT PRIMARY KEY,
    QuarterKey TEXT NOT NULL,
    ProducerBuildingType TEXT NOT NULL,
    SupplyModifierId TEXT NOT NULL UNIQUE,
    RequireProducerBuilding INTEGER NOT NULL CHECK (RequireProducerBuilding IN (0, 1)),
    ImportField TEXT NOT NULL UNIQUE,
    ExportField TEXT NOT NULL UNIQUE,
    ImportProperty TEXT NOT NULL UNIQUE,
    ExportProperty TEXT NOT NULL UNIQUE
    );

CREATE TABLE IF NOT EXISTS CSC_TradeRoutePayoutBindings
    (
    ChannelId TEXT NOT NULL REFERENCES CSC_TradeRouteChannels (ChannelId),
    LegKey TEXT NOT NULL,
    Recipient TEXT NOT NULL CHECK (Recipient IN ('ORIGIN', 'DESTINATION')),
    ModifierId TEXT NOT NULL UNIQUE,
    PRIMARY KEY (ChannelId, LegKey)
    );

-- The remaining tables are generated read-models, not a second authored policy.
CREATE TABLE IF NOT EXISTS CSC_TradeRouteChannelFacts
    (
    ChannelId TEXT PRIMARY KEY REFERENCES CSC_TradeRouteChannels (ChannelId),
    SupplyProperty TEXT NOT NULL,
    OriginDistrictType TEXT NOT NULL,
    ProducerStage INTEGER NOT NULL
    );

CREATE TABLE IF NOT EXISTS CSC_TradeRouteSupplyRequirements
    (
    ChannelId TEXT NOT NULL REFERENCES CSC_TradeRouteChannels (ChannelId),
    RequirementId TEXT NOT NULL,
    MaterialClass TEXT NOT NULL,
    MinimumCount INTEGER NOT NULL CHECK (MinimumCount > 0),
    PRIMARY KEY (ChannelId, RequirementId)
    );

CREATE TABLE IF NOT EXISTS CSC_TradeRoutePayouts
    (
    ChannelId TEXT NOT NULL,
    LegKey TEXT NOT NULL,
    Recipient TEXT NOT NULL,
    Bit INTEGER NOT NULL CHECK (Bit IN (1, 2, 4, 8, 16)),
    ModifierId TEXT NOT NULL UNIQUE,
    YieldType TEXT NOT NULL,
    Amount REAL NOT NULL,
    BuildingType TEXT,
    PRIMARY KEY (ChannelId, LegKey, Bit),
    FOREIGN KEY (ChannelId, LegKey) REFERENCES CSC_TradeRoutePayoutBindings (ChannelId, LegKey)
    );
