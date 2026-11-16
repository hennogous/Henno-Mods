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
    SpatialRule TEXT NOT NULL CHECK (SpatialRule IN ('ADJACENT_OWNED', 'SAME_CITY')),
    QuantityKind TEXT NOT NULL CHECK (QuantityKind IN ('FIXED', 'PARTNER_POPULATION', 'PARTNER_POPULATION_STEPS')),
    QuantityAmount REAL NOT NULL CHECK (QuantityAmount > 0),
    PopulationStep INTEGER,
    PartnerDistrictMustFunction INTEGER NOT NULL DEFAULT 0 CHECK (PartnerDistrictMustFunction IN (0, 1)),
    SellerPopulationProperty TEXT,
    CHECK ((QuantityKind = 'PARTNER_POPULATION_STEPS' AND PopulationStep > 0)
        OR (QuantityKind <> 'PARTNER_POPULATION_STEPS' AND PopulationStep IS NULL)),
    CHECK (QuantityKind = 'FIXED' OR SpatialRule = 'ADJACENT_OWNED'),
    CHECK (QuantityKind <> 'FIXED' OR QuantityAmount = CAST(QuantityAmount AS INTEGER)),
    CHECK (QuantityKind <> 'FIXED' OR PartnerDistrictMustFunction = 0),
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

-- Fixed exchanges use native building owners, rather than city property bits.
-- OwnerSide identifies the object carrying BuildingModifiers; Recipient in the
-- yield leg identifies who receives the income. These differ on return legs.
-- Local effects are city-scoped in the engine. SAME_CITY deliberately preserves
-- that behavior rather than inventing an extra same-plot/Quarter requirement.
--
-- Requirement IDs preserve shared native identities. The fixed processor derives
-- their district/building arguments from the opposite endpoint and regenerates
-- the narrow adjacency template. BuildingRequirementId is optional because the
-- existing outward customer payment explicitly checks the functioning customer,
-- while reverse payments rely on the target-building leaf. No Service gate is
-- implied by either pattern. Shared leaf IDs must have identical payout terms.
CREATE TABLE IF NOT EXISTS CSC_BuildingTransactionFixedBindings
    (
    TransactionId TEXT NOT NULL,
    LegKey TEXT NOT NULL,
    OwnerSide TEXT NOT NULL CHECK (OwnerSide IN ('SOURCE', 'PARTNER')),
    RootModifierId TEXT NOT NULL,
    ChildModifierId TEXT NOT NULL,
    SubjectRequirementSetId TEXT,
    AdjacencyRequirementId TEXT,
    DistrictRequirementId TEXT,
    BuildingRequirementId TEXT,
    PRIMARY KEY (TransactionId, LegKey),
    FOREIGN KEY (TransactionId, LegKey) REFERENCES CSC_BuildingTransactionYields (TransactionId, LegKey),
    CHECK ((RootModifierId = ChildModifierId AND SubjectRequirementSetId IS NULL
            AND AdjacencyRequirementId IS NULL AND DistrictRequirementId IS NULL AND BuildingRequirementId IS NULL)
        OR (RootModifierId <> ChildModifierId AND SubjectRequirementSetId IS NOT NULL
            AND AdjacencyRequirementId IS NOT NULL AND DistrictRequirementId IS NOT NULL))
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

-- Material exchanges are directional native relationships. An input selects
-- registered improvement hosts; a return selects the player's adjacent tagged
-- improvements, including hosts without an input root. Valid-resource mappings
-- register additional hosts and legal Builder possibilities, not a runtime gate
-- on every return. Industry/Corporation inputs are full amounts; their returns
-- add incremental legs to the ordinary return. Do not use a universal multiplier.
CREATE TABLE IF NOT EXISTS CSC_MaterialTransactions (
    TransactionId TEXT PRIMARY KEY NOT NULL,
    QuarterKey TEXT NOT NULL,
    ProducerBuildingType TEXT NOT NULL,
    MaterialClass TEXT NOT NULL,
    UNIQUE (ProducerBuildingType, MaterialClass)
);

CREATE TABLE IF NOT EXISTS CSC_MaterialTransactionYields (
    TransactionId TEXT NOT NULL REFERENCES CSC_MaterialTransactions (TransactionId),
    LegKey TEXT NOT NULL,
    Recipient TEXT NOT NULL CHECK (Recipient IN ('PRODUCER', 'IMPROVEMENT')),
    YieldType TEXT NOT NULL,
    Amount REAL NOT NULL CHECK (Amount > 0 AND Amount = CAST(Amount AS INTEGER)),
    ImprovementScope TEXT NOT NULL CHECK (ImprovementScope IN ('REGISTERED_INPUT', 'ANY_PLAYER_IMPROVEMENT', 'EXACT_IMPROVEMENT')),
    ImprovementType TEXT,
    PRIMARY KEY (TransactionId, LegKey),
    CHECK ((ImprovementScope = 'EXACT_IMPROVEMENT') = (ImprovementType IS NOT NULL)),
    CHECK (ImprovementScope <> 'REGISTERED_INPUT' OR Recipient = 'PRODUCER'),
    CHECK (ImprovementScope <> 'ANY_PLAYER_IMPROVEMENT' OR Recipient = 'IMPROVEMENT')
);

-- Native IDs retain compatibility with existing attachments and save state.
-- Core/compatibility SQL still registers native owners early; this projection
-- owns their links, payout arguments and gate arguments before game creation.
-- Stable parent rows are updated in place: REPLACE can cascade-delete Services.
CREATE TABLE IF NOT EXISTS CSC_MaterialTransactionBindings (
    TransactionId TEXT NOT NULL,
    LegKey TEXT NOT NULL,
    RootModifierId TEXT NOT NULL,
    ChildModifierId TEXT NOT NULL,
    OwnerRequirementSetId TEXT,
    SubjectRequirementSetId TEXT NOT NULL,
    PRIMARY KEY (TransactionId, LegKey),
    FOREIGN KEY (TransactionId, LegKey) REFERENCES CSC_MaterialTransactionYields (TransactionId, LegKey)
);

-- Role determines argument values from the transaction/leg, rather than copying
-- material or Quarter names into a second economic definition. Adjacency itself
-- takes no argument. Shared requirement IDs must resolve to identical templates.
CREATE TABLE IF NOT EXISTS CSC_MaterialTransactionGateBindings (
    TransactionId TEXT NOT NULL,
    LegKey TEXT NOT NULL,
    RequirementSetId TEXT NOT NULL,
    RequirementId TEXT NOT NULL,
    GateRole TEXT NOT NULL CHECK (GateRole IN ('MATERIAL_TAG', 'QUARTER_TYPE', 'ADJACENCY', 'IMPROVEMENT_TYPE')),
    PRIMARY KEY (TransactionId, LegKey, RequirementSetId, RequirementId),
    FOREIGN KEY (TransactionId, LegKey) REFERENCES CSC_MaterialTransactionBindings (TransactionId, LegKey)
);
