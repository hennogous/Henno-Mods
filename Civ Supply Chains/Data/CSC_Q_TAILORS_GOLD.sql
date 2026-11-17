-- CSC_Q_TAILORS_GOLD
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

-- Tailors Gold companion
-- This adds Gold to the same Workshop/Tailor/Fashion House exchanges defined in core SQL.
-- Core owns buildings, supply checks, shared bits and Lua properties; this file
-- adds the Gold modifier layer for independent Taxes & Politics replacement.
-- It consumes existing demand rather than calculating a second set of customers.
--===========================================================================================================================================================================--
/*	GOLD MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Ordinary Gold exchange declarations
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- The declarations at the end of this file add Gold legs to core transactions.
-- CSC_Q_ALL_TransactionProcessor generates building/material attachments with
-- the same core gates. Property and route consumers below stay explicit.


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Stage 3 Gold reads the aggregate return-rate bits also used by Production.
-- One city-center consumer pays the summed customer demand once; the encoded
-- value is a 256-scaled per-population rate, not one Gold per active bit.
INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT INTO DistrictModifiers
        (   DistrictType,             ModifierId   )
VALUES  (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD'   );

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Wrappers select eligible receivers; child modifiers deliver Gold. Core
-- requirement sets preserve the same source, ownership and adjacency conditions
-- without maintaining another independently drifting eligibility definition.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                             ModifierType,                       OwnerRequirementSetId,   SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',   'MODIFIER_BUILDING_YIELD_CHANGE',   NULL,                    'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' || Bit,
	'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', NULL,
	'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit,
	'MODIFIER_BUILDING_YIELD_CHANGE', NULL,
	'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                             Name,             Value   )
VALUES  (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',   'BuildingType',   'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',   'YieldType',      'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',   'Amount',         1   );

-- Payout arguments generated by CSC_Q_ALL_TransactionProcessor.sql.

-- Keep floating-point division: integer division would erase the fractional
-- rate before the engine multiplies it by the receiving city's population.
-- Payout arguments generated by CSC_Q_ALL_TransactionProcessor.sql.

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit, 'BuildingType', 'BUILDING_CSC_TAILORS_TAILOR'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit, 'YieldType', 'YIELD_GOLD'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit, 'Amount', Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-- Fashion House and Tailor trade exports have independent route-count bits.
-- The fixed modifier covers bit 1; generated rows cover only larger bits so
-- that the first route's Gold cannot be paid twice.
INSERT INTO DistrictModifiers
        (   DistrictType,             ModifierId   )
VALUES  (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD'   );

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                    ModifierType,                       OwnerRequirementSetId,   SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD',   'MODIFIER_BUILDING_YIELD_CHANGE',   NULL,                    'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD_BIT_' || Bit,
	'MODIFIER_BUILDING_YIELD_CHANGE', NULL,
	'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                    Name,             Value   )
VALUES  (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD',   'BuildingType',   'BUILDING_CSC_TAILORS_FASHION_HOUSE'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD',   'YieldType',      'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD',   'Amount',         1   );

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD_BIT_' || Bit, 'BuildingType', 'BUILDING_CSC_TAILORS_FASHION_HOUSE'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD_BIT_' || Bit, 'YieldType', 'YIELD_GOLD'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD_BIT_' || Bit, 'Amount', Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-- Stage 4 Gold uses whole customer-population stacks, mirroring core Production.
-- The Stage 3 scaling divisor does not belong on these integer amounts.
INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_GOLD_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_GOLD_BIT_' || Bit, 'MODIFIER_BUILDING_YIELD_CHANGE', NULL, 'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

-- Payout arguments generated by CSC_Q_ALL_TransactionProcessor.sql.

-- Payout arguments generated by CSC_Q_ALL_TransactionProcessor.sql.

-- Payout arguments generated by CSC_Q_ALL_TransactionProcessor.sql.

-- Specialty producers receive the same bilateral return as Base producers.

-- ============================================================================
-- Ordinary transaction declarations
-- ============================================================================
-- Authored partners, quantities, yield legs and native identity bindings live
-- here. CSC_Q_ALL_TransactionProcessor.sql generates the bound gameplay rules.
-- Gold companions add legs to these identities. Route bindings below describe
-- the existing native route effects for the late shared reader. This file adds Gold legs only; it does not redefine source/partner relationships.

-- Gold is an additive companion to the ordinary transaction catalogue.
-- Register each source payout once. The scanner aggregates quantities by
-- property, so Production and Gold sharing that property cannot double sales.
INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,   LegKey,   Recipient,   YieldType,   AmountPerUnit,   AmountProperty   )
SELECT TransactionId, 'SOURCE_GOLD', Recipient, 'YIELD_GOLD', AmountPerUnit, AmountProperty
FROM CSC_BuildingTransactionYields
WHERE LegKey = 'SOURCE_PRODUCTION'
    AND TransactionId IN (SELECT TransactionId FROM CSC_BuildingTransactions WHERE QuarterKey = 'TAILORS');

INSERT INTO CSC_BuildingTransactionBindings
        (   TransactionId,   LegKey,   ModifierPrefix,   RequirementSetPrefix,   BindingKind   )
SELECT B.TransactionId, 'SOURCE_GOLD',
    CASE T.QuantityKind WHEN 'PARTNER_POPULATION' THEN 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' ELSE 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_GOLD_BIT_' END,
    B.RequirementSetPrefix, B.BindingKind
FROM CSC_BuildingTransactionBindings B
JOIN CSC_BuildingTransactions T ON T.TransactionId = B.TransactionId
WHERE T.QuarterKey = 'TAILORS' AND B.LegKey = 'SOURCE_PRODUCTION';

-- Fixed Gold legs are created by the shared SOURCE_GOLD projection above.
INSERT INTO CSC_BuildingTransactionFixedBindings
    (
        TransactionId,
        LegKey,
        OwnerSide,
        RootModifierId,
        ChildModifierId,
        SubjectRequirementSetId,
        AdjacencyRequirementId,
        DistrictRequirementId,
        BuildingRequirementId
    )
VALUES
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_GOLD',
        'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP',
        'REQSET_CSC_ADJ_TAILORS_QUARTER',
        'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    );

-- Canonical directional material exchanges.
-- Native aliases retain existing gates; declared legs own payout amounts.
INSERT INTO CSC_MaterialTransactionYields
    (
        TransactionId,
        LegKey,
        Recipient,
        YieldType,
        Amount,
        ImprovementScope,
        ImprovementType
    )
VALUES
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'RETURN_GOLD_ORDINARY',
        'IMPROVEMENT',
        'YIELD_GOLD',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'RETURN_GOLD_ORDINARY',
        'IMPROVEMENT',
        'YIELD_GOLD',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    );

INSERT INTO CSC_MaterialTransactionBindings
        (   TransactionId,                         LegKey,                   RootModifierId,                                             ChildModifierId,                      OwnerRequirementSetId,   SubjectRequirementSetId   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_GOLD_ORDINARY',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_GOLD',        'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',   NULL,                    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_GOLD_ORDINARY',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_GOLD',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',   NULL,                    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC'   );

INSERT INTO CSC_MaterialTransactionGateBindings
        (   TransactionId,                         LegKey,                   RequirementSetId,                         RequirementId,                              GateRole   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   );

-- Gold route legs exist only when this gameplay companion is loaded.

INSERT INTO CSC_TradeRoutePayoutBindings
        (   ChannelId,                 LegKey,          Recipient,       ModifierId   )
VALUES  (   'TAILORS_TAILOR',          'EXPORT_GOLD',   'DESTINATION',   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD'   ),
        (   'TAILORS_FASHION_HOUSE',   'EXPORT_GOLD',   'DESTINATION',   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_GOLD'   );
