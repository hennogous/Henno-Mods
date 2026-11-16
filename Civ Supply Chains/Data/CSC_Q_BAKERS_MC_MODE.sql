-- CSC_MC_MODE
-- Author: Henno
-- DateCreated: 2025-06-15 11:57:14
--------------------------------------------------------------

-- Bakers: Monopolies & Corporations layer
-- Loaded only with M&C. These rows augment ordinary material exchanges rather
-- than replacing core SQL. An Industry/Corporation still needs the matching
-- material, adjacency and ownership supplied by its selected collection.
-- Product commissioning/Great Works belong to Taxes & Politics, outside CSC.
--===========================================================================================================================================================================--
/*	INDUSTRIES & CORPORATIONS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

-- Improvement -> producer pays the full M&C input: Industry sends 2 and
-- Corporation sends 3 to the adjacent producer. These improvement types use
-- separate input attachments from ordinary Farms/Mines/Pastures.
INSERT INTO ImprovementModifiers
        (   ImprovementType,             ModifierId   )
VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

-- +2 Food to the Water Mill from a base materials Industry
        (   'IMPROVEMENT_INDUSTRY',      'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER'   ),

-- +2 Food to the Wind Mill from a base materials Industry
        (   'IMPROVEMENT_INDUSTRY',      'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND'   ),

-- +3 Food to the Water Mill from a base materials Corporation
        (   'IMPROVEMENT_CORPORATION',   'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER'   ),

-- +3 Food to the Wind Mill from a base materials Corporation
        (   'IMPROVEMENT_CORPORATION',   'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND'   ),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Food to the Cafe from a specialty materials Industry
        (   'IMPROVEMENT_INDUSTRY',      'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER'   ),

-- +3 Food to the Cafe from a specialty materials Corporation
        (   'IMPROVEMENT_CORPORATION',   'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Producer -> improvement adds a marginal return to the ordinary +1 already
-- attached in core: Industry adds 1 and Corporation adds 2, yielding totals
-- of 2 and 3. Adding the advertised total here would count that base +1 twice.
INSERT INTO BuildingModifiers
        (   BuildingType,                       ModifierId   )
VALUES

--	WIND / WATER MILL -------------------------------------------------------------------

-- +2 Production to adjacent base materials Industries
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD'   ),

-- +3 Production to adjacent base materials Corporations
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD'   ),

--	CAFE --------------------------------------------------------------------------

-- +2 Production to adjacent specialty materials Industries
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC_PROD'   ),

-- +3 Production to adjacent specialty materials Corporations
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC_PROD'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                                 ModifierType,                                         OwnerRequirementSetId,               SubjectRequirementSetId,                      SubjectStackLimit   )
VALUES

--	FLOUR MILL --------------------------------------------------------------------------

-- +2 Food to the Water Mill from a base materials Industry
        (   'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER',              NULL   ),
        (   'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WATER_MILL',      'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                NULL,                                         NULL   ),

-- +2 Food to the Wind Mill from a base materials Industry
        (   'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER',              NULL   ),
        (   'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WIND_MILL',       'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                NULL,                                         NULL   ),

-- +3 Food to the Water Mill from a base materials Corporation
        (   'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER',              NULL   ),
        (   'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WATER_MILL',   'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                NULL,                                         NULL   ),

-- +3 Food to the Wind Mill from a base materials Corporation
        (   'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER',              NULL   ),
        (   'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WIND_MILL',    'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                NULL,                                         NULL   ),

-- +2/+3 Production to adjacent base materials Industry/Corporation improvements
        (   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD',       'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    NULL   ),
        (   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD',      'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   NULL   ),
        (   'MOD_CSC_BAKERS_PROD_TO_ADJ_IND',                           'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                                NULL,                                         NULL   ),
        (   'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP',                          'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                                NULL,                                         NULL   ),

--  +2/+3 Production to adjacent specialty materials Industry/Corporation improvements
        (   'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC_PROD',             'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    NULL   ),
        (   'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC_PROD',            'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   NULL   ),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Food to the Cafe from a specialty materials Industry
        (   'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER',              'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_BAKERS_QUARTER',              NULL   ),
        (   'MOD_CSC_BAKERS_SPEC_INDUSTRY_FOOD_TO_ADJ_CAFE',            'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                NULL,                                         NULL   ),

-- +3 Food to the Cafe from a specialty materials Corporation
        (   'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER',           'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_BAKERS_QUARTER',              NULL   ),
        (   'MOD_CSC_BAKERS_SPEC_CORPORATION_FOOD_TO_ADJ_CAFE',         'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                NULL,                                         NULL   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		
-- 	FLOUR MILL --------------------------------------------------------------------------
-- +2 Food to the Water Mill from a base materials Industry
-- +2 Food to the Wind Mill from a base materials Industry
-- +3 Food to the Water Mill from a base materials Corporation
-- +3 Food to the Wind Mill from a base materials Corporation
-- +2 Production to adjacent base materials Industries
-- +3 Production to adjacent base materials Corporations
-- +2 Production to adjacent specialty materials Industries
-- +3 Production to adjacent specialty materials Corporations
-- 	CAFE --------------------------------------------------------------------------
-- +2 Food to the Cafe from a specialty materials Industry
-- +3 Food to the Cafe from a specialty materials Corporation

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                             RequirementSetType   )
VALUES

-- 	+2 Production to adjacent base materials Industries
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQUIREMENTSET_TEST_ALL'   ),

-- 	+3 Production to adjacent base materials Corporations
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQUIREMENTSET_TEST_ALL'   ),

-- 	+2 Production to adjacent specialty materials Industries
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    'REQUIREMENTSET_TEST_ALL'   ),

-- 	+3 Production to adjacent specialty materials Corporations
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   'REQUIREMENTSET_TEST_ALL'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Return sets require adjacency, the correct BASE/SPEC material tag, and the
-- exact Industry/Corporation improvement. An Industry on an unrelated luxury
-- does not qualify just because it is an Industry.
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                             RequirementId   )
VALUES

-- 	+2 Production to adjacent base materials Industries
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_PLOT_HAS_INDUSTRY'   ),

-- 	+3 Production to adjacent base materials Corporations
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_PLOT_HAS_CORPORATION'   ),

-- 	+2 Production to adjacent specialty materials Industries
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_PLOT_HAS_INDUSTRY'   ),

-- 	+3 Production to adjacent specialty materials Corporations
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_PLOT_HAS_CORPORATION'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Requirements
        (   RequirementId,                    RequirementType,                               Inverse   )
VALUES  (   'REQ_CSC_PLOT_HAS_INDUSTRY',      'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_PLOT_HAS_CORPORATION',   'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES',   0   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Specialty Products were moved to the Taxes And Politics project for later revisit.
-- Keep this file scoped to actual Monopolies & Corporations Industry/Corporation integration.

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
        'CSC_BAKERS_WATER_MILL_BASE',
        'INPUT_INDUSTRY',
        'PRODUCER',
        'YIELD_FOOD',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_BAKERS_WATER_MILL_BASE',
        'INPUT_CORPORATION',
        'PRODUCER',
        'YIELD_FOOD',
        3,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_BAKERS_WATER_MILL_BASE',
        'RETURN_PRODUCTION_CORPORATION',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_BAKERS_WATER_MILL_BASE',
        'RETURN_PRODUCTION_INDUSTRY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_BAKERS_WIND_MILL_BASE',
        'INPUT_INDUSTRY',
        'PRODUCER',
        'YIELD_FOOD',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_BAKERS_WIND_MILL_BASE',
        'INPUT_CORPORATION',
        'PRODUCER',
        'YIELD_FOOD',
        3,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_BAKERS_WIND_MILL_BASE',
        'RETURN_PRODUCTION_CORPORATION',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_BAKERS_WIND_MILL_BASE',
        'RETURN_PRODUCTION_INDUSTRY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_BAKERS_CAFE_SPEC',
        'INPUT_INDUSTRY',
        'PRODUCER',
        'YIELD_FOOD',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_BAKERS_CAFE_SPEC',
        'INPUT_CORPORATION',
        'PRODUCER',
        'YIELD_FOOD',
        3,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_BAKERS_CAFE_SPEC',
        'RETURN_PRODUCTION_CORPORATION',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_BAKERS_CAFE_SPEC',
        'RETURN_PRODUCTION_INDUSTRY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    );

INSERT INTO CSC_MaterialTransactionBindings
        (   TransactionId,                  LegKey,                            RootModifierId,                                           ChildModifierId,                                            OwnerRequirementSetId,               SubjectRequirementSetId   )
VALUES  (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_INDUSTRY',                  'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER',      'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WATER_MILL',      'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_CORPORATION',               'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER',   'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WATER_MILL',   'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_CORPORATION',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD',    'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP',                          NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD',     'MOD_CSC_BAKERS_PROD_TO_ADJ_IND',                           NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_INDUSTRY',                  'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND',       'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WIND_MILL',       'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_CORPORATION',               'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND',    'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WIND_MILL',    'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_CORPORATION',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD',    'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP',                          NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_INDUSTRY',      'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD',     'MOD_CSC_BAKERS_PROD_TO_ADJ_IND',                           NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_INDUSTRY',                  'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER',            'MOD_CSC_BAKERS_SPEC_INDUSTRY_FOOD_TO_ADJ_CAFE',            'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_CORPORATION',               'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER',         'MOD_CSC_BAKERS_SPEC_CORPORATION_FOOD_TO_ADJ_CAFE',         'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_CORPORATION',   'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC_PROD',          'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP',                          NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_INDUSTRY',      'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC_PROD',           'MOD_CSC_BAKERS_PROD_TO_ADJ_IND',                           NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC'   );

INSERT INTO CSC_MaterialTransactionGateBindings
        (   TransactionId,                  LegKey,                            RequirementSetId,                             RequirementId,                             GateRole   )
VALUES  (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_INDUSTRY',                  'REQSET_CSC_BAKERS_PLOT_HAS_BASE',            'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_CORPORATION',               'REQSET_CSC_BAKERS_PLOT_HAS_BASE',            'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_CORPORATION',               'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_CORPORATION',               'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_PLOT_HAS_CORPORATION',            'IMPROVEMENT_TYPE'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_PLOT_HAS_INDUSTRY',               'IMPROVEMENT_TYPE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_INDUSTRY',                  'REQSET_CSC_BAKERS_PLOT_HAS_BASE',            'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_CORPORATION',               'REQSET_CSC_BAKERS_PLOT_HAS_BASE',            'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_CORPORATION',               'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_CORPORATION',               'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_PLOT_HAS_CORPORATION',            'IMPROVEMENT_TYPE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_PLOT_HAS_INDUSTRY',               'IMPROVEMENT_TYPE'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_INDUSTRY',                  'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',            'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_CORPORATION',               'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',            'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_CORPORATION',               'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_CORPORATION',               'REQSET_CSC_ADJ_BAKERS_QUARTER',              'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_PLOT_HAS_CORPORATION',            'IMPROVEMENT_TYPE'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_PLOT_HAS_INDUSTRY',               'IMPROVEMENT_TYPE'   );
