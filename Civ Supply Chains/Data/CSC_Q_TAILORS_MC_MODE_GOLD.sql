-- CSC_Q_TAILORS_MC_MODE_GOLD
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	INDUSTRIES & CORPORATIONS - GOLD MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_GOLD'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_GOLD'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                             ModifierType,                                         OwnerRequirementSetId,   SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_GOLD',    'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_GOLD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   NULL,                    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND',                      'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                    NULL   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP',                     'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',            NULL,                    NULL   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                             Name,           Value   )
VALUES  (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_GOLD',    'ModifierId',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND',                      'YieldType',    'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND',                      'Amount',       2   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_GOLD',   'ModifierId',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP',                     'YieldType',    'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP',                     'Amount',       3   );
