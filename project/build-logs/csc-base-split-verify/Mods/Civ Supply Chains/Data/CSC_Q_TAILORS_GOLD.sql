-- CSC_Q_TAILORS_GOLD
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	GOLD MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_GOLD'   ),
        (   'BUILDING_LIGHTHOUSE',                     'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_GOLD'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP'   );

INSERT OR IGNORE INTO BuildingModifiers
		( BuildingType, ModifierId )
SELECT CivUniqueBuildingType, 'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_GOLD'
FROM BuildingReplaces
WHERE ReplacesBuildingType = 'BUILDING_LIGHTHOUSE';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO DistrictModifiers
		( DistrictType, ModifierId )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT INTO DistrictModifiers
        (   DistrictType,             ModifierId   )
VALUES  (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD'   );

INSERT INTO DistrictModifiers
		( DistrictType, ModifierId )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                            ModifierType,                                         OwnerRequirementSetId,                         SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_GOLD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                                          'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',                    'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_GOLD',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      NULL,                                          'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP',         'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',             'MODIFIER_BUILDING_YIELD_CHANGE',                     'REQSET_CSC_TAILORS_CITY_HAS_TAILOR',          NULL   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',      'MODIFIER_BUILDING_YIELD_CHANGE',                     'REQSET_CSC_TAILORS_CITY_HAS_FASHION_HOUSE',   NULL   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',                  'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                          'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO Modifiers
		( ModifierId, ModifierType, OwnerRequirementSetId, SubjectRequirementSetId )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' || Bit,
	'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', NULL,
	'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO Modifiers
		( ModifierId, ModifierType, OwnerRequirementSetId, SubjectRequirementSetId )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit,
	'MODIFIER_BUILDING_YIELD_CHANGE', NULL,
	'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                            Name,             Value   )
VALUES  (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_GOLD',   'ModifierId',     'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',                    'YieldType',      'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',                    'Amount',         1   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_GOLD',      'ModifierId',     'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP',         'BuildingType',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP',         'YieldType',      'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP',         'Amount',         1   ),
        (   'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',             'BuildingType',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',             'YieldType',      'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',             'Amount',         1   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',      'BuildingType',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',      'YieldType',      'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',      'Amount',         1   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',                  'BuildingType',   'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',                  'YieldType',      'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD',                  'Amount',         1   );

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' || Bit, 'YieldType', 'YIELD_GOLD'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' || Bit, 'Amount', Bit / 10000.0
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit, 'BuildingType', 'BUILDING_CSC_TAILORS_TAILOR'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit, 'YieldType', 'YIELD_GOLD'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD_BIT_' || Bit, 'Amount', Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;
