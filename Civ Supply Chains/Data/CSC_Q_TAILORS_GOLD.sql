-- Fixed building exchanges are generated from this Quarter's TRANSACTIONS companions.
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
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Building-owned Gold goes to improved materials and upstream producers as the
-- reciprocal return. Reuse core adjacency/material gates so Gold qualifies at
-- the same sites as the non-Gold half of the exchange.
INSERT INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_GOLD'   )

        ;

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
        (   ModifierId,                                            ModifierType,                                         OwnerRequirementSetId,   SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_GOLD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',                    'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                    NULL   ),

        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',                  'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                    'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   );

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

-- Payout arguments generated by CSC_BuildingTransactionProcessor.sql.

-- Keep floating-point division: integer division would erase the fractional
-- rate before the engine multiplies it by the receiving city's population.
-- Payout arguments generated by CSC_BuildingTransactionProcessor.sql.

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

-- Payout arguments generated by CSC_BuildingTransactionProcessor.sql.

-- Payout arguments generated by CSC_BuildingTransactionProcessor.sql.

-- Payout arguments generated by CSC_BuildingTransactionProcessor.sql.

-- Specialty producers receive the same bilateral return as Base producers.
INSERT INTO BuildingModifiers
        (   BuildingType,                           ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_GOLD'   );
INSERT INTO Modifiers
        (   ModifierId,                                                 ModifierType,                                         SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_GOLD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC'   );
