-- CSC_Q_TAILORS_MC_MODE
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	INDUSTRIES & CORPORATIONS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO ImprovementModifiers
        (   ImprovementType,             ModifierId   )
VALUES  (   'IMPROVEMENT_INDUSTRY',      'MOD_CSC_TAILORS_BASE_INDUSTRY_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_CORPORATION',   'MOD_CSC_TAILORS_BASE_CORPORATION_ATTACH_QUARTER'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_PROD'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_PROD'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                               ModifierType,                                         OwnerRequirementSetId,                SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_BASE_INDUSTRY_ATTACH_QUARTER',           'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_TAILORS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_BASE_INDUSTRY_CULTURE_TO_WORKSHOP',      'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                 NULL   ),
        (   'MOD_CSC_TAILORS_BASE_CORPORATION_ATTACH_QUARTER',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'REQSET_CSC_TAILORS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_BASE_CORPORATION_CULTURE_TO_WORKSHOP',   'MODIFIER_BUILDING_YIELD_CHANGE',                     NULL,                                 NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_PROD',      'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_PROD',     'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_IND',                        'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                                 NULL   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_CORP',                       'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                                 NULL   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                               Name,             Value   )
VALUES  (   'MOD_CSC_TAILORS_BASE_INDUSTRY_ATTACH_QUARTER',           'ModifierId',     'MOD_CSC_TAILORS_BASE_INDUSTRY_CULTURE_TO_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_BASE_INDUSTRY_CULTURE_TO_WORKSHOP',      'BuildingType',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_BASE_INDUSTRY_CULTURE_TO_WORKSHOP',      'YieldType',      'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_BASE_INDUSTRY_CULTURE_TO_WORKSHOP',      'Amount',         2   ),
        (   'MOD_CSC_TAILORS_BASE_CORPORATION_ATTACH_QUARTER',        'ModifierId',     'MOD_CSC_TAILORS_BASE_CORPORATION_CULTURE_TO_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_BASE_CORPORATION_CULTURE_TO_WORKSHOP',   'BuildingType',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_BASE_CORPORATION_CULTURE_TO_WORKSHOP',   'YieldType',      'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_BASE_CORPORATION_CULTURE_TO_WORKSHOP',   'Amount',         3   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_PROD',      'ModifierId',     'MOD_CSC_TAILORS_PROD_TO_ADJ_IND'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_IND',                        'YieldType',      'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_IND',                        'Amount',         2   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_PROD',     'ModifierId',     'MOD_CSC_TAILORS_PROD_TO_ADJ_CORP'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_CORP',                       'YieldType',      'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_CORP',                       'Amount',         3   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                              RequirementSetType   )
VALUES  (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE',    'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE',   'REQUIREMENTSET_TEST_ALL'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                              RequirementId   )
VALUES  (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_TAILORS_PLOT_HAS_INDUSTRY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_CORPORATION'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Requirements
        (   RequirementId,                            RequirementType,                               Inverse   )
VALUES  (   'REQ_CSC_TAILORS_PLOT_HAS_INDUSTRY',      'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_PLOT_HAS_CORPORATION',   'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES',   0   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,                            Name,                Value   )
VALUES  (   'REQ_CSC_TAILORS_PLOT_HAS_INDUSTRY',      'ImprovementType',   'IMPROVEMENT_INDUSTRY'   ),
        (   'REQ_CSC_TAILORS_PLOT_HAS_CORPORATION',   'ImprovementType',   'IMPROVEMENT_CORPORATION'   );
