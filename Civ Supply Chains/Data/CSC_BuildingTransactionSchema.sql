-- Ordinary building economy: one gameplay-owned relationship and its payouts.
-- Quarter declarations supply terms; the late processor produces compatibility
-- read-models and native yield arguments. Gameplay and AI read the same terms.
-- Services and district adjacency remain in their own authoritative systems.
--
-- Population payout properties are aggregation identities, not extra income:
-- several legs may consume the same quantity (e.g. source Production and Gold).
-- The gameplay writer must accumulate that quantity once per relationship and
-- property, then round once per receiving city/property.
CREATE TABLE IF NOT EXISTS CSC_BuildingTransactions
    (
    TransactionId TEXT PRIMARY KEY NOT NULL,
    QuarterKey TEXT NOT NULL,
    SourceBuildingType TEXT NOT NULL,
    PartnerBuildingType TEXT NOT NULL,
    SpatialRule TEXT NOT NULL CHECK (SpatialRule = 'ADJACENT_OWNED'),
    QuantityKind TEXT NOT NULL CHECK (QuantityKind IN ('PARTNER_POPULATION', 'PARTNER_POPULATION_STEPS')),
    QuantityAmount REAL NOT NULL CHECK (QuantityAmount > 0),
    PopulationStep INTEGER,
    PartnerDistrictMustFunction INTEGER NOT NULL DEFAULT 0 CHECK (PartnerDistrictMustFunction IN (0, 1)),
    SellerPopulationProperty TEXT,
    CHECK ((QuantityKind = 'PARTNER_POPULATION_STEPS' AND PopulationStep > 0)
        OR (QuantityKind <> 'PARTNER_POPULATION_STEPS' AND PopulationStep IS NULL)),
    UNIQUE (SourceBuildingType, PartnerBuildingType, SpatialRule)
    );

CREATE TABLE IF NOT EXISTS CSC_BuildingTransactionYields
    (
    TransactionId TEXT NOT NULL REFERENCES CSC_BuildingTransactions (TransactionId),
    LegKey TEXT NOT NULL,
    Recipient TEXT NOT NULL CHECK (Recipient IN ('SOURCE', 'PARTNER')),
    YieldType TEXT NOT NULL,
    AmountPerUnit REAL NOT NULL CHECK (AmountPerUnit > 0 AND AmountPerUnit = CAST(AmountPerUnit AS INTEGER)),
    AmountProperty TEXT,
    PRIMARY KEY (TransactionId, LegKey)
    );

-- These are existing engine identities, not independent economic terms. Keep
-- the historical property/requirement/modifier names so saved state and native
-- attachments survive the migration. Shared prefixes must expand identically.
-- The population scanner owns object eligibility; existing SQL requirement
-- definitions test its property bits. The processor owns the payout arguments.
CREATE TABLE IF NOT EXISTS CSC_BuildingTransactionBindings
    (
    TransactionId TEXT NOT NULL,
    LegKey TEXT NOT NULL,
    ModifierPrefix TEXT NOT NULL,
    RequirementSetPrefix TEXT NOT NULL,
    BindingKind TEXT NOT NULL CHECK (BindingKind IN ('CITY_RATE_BITS', 'BUILDING_STACK_BITS')),
    PRIMARY KEY (TransactionId, LegKey),
    FOREIGN KEY (TransactionId, LegKey) REFERENCES CSC_BuildingTransactionYields (TransactionId, LegKey)
    );
