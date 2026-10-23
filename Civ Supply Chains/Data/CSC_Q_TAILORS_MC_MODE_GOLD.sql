-- CSC_Q_TAILORS_MC_MODE_GOLD
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

-- Tailors: M&C Gold companion
-- The Gold half of the producer-to-Industry/Corporation return. The ordinary
-- Gold layer already provides +1: these children add only +1 for Industry and
-- +2 for Corporation, yielding +2/+3 in total. M&C inputs paid to the producer
-- remain in the non-Gold M&C file.
--===========================================================================================================================================================================--
/*	INDUSTRIES & CORPORATIONS - GOLD MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- The producer owns the wrapper; its target is a matching adjacent M&C resource
-- improvement. The selected single-plot child delivers the marginal Gold amount.
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

-- Amounts are incremental Gold, not the final advertised total. Keep these
-- aligned with the non-Gold M&C increments and the ordinary material return.
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                             Name,           Value   )
VALUES  (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_GOLD',    'ModifierId',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND',                      'YieldType',    'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND',                      'Amount',       1   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_GOLD',   'ModifierId',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP',                     'YieldType',    'YIELD_GOLD'   ),
        (   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP',                     'Amount',       2   );

-- Additional +1 on top of the ordinary +1 return.
INSERT INTO BuildingModifiers
        (   BuildingType,                           ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IND_SPEC_GOLD'   );
INSERT INTO Modifiers
        (   ModifierId,                                                 ModifierType,                                         SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IND_SPEC_GOLD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_SPEC'   );
INSERT INTO ModifierArguments
        (   ModifierId,                                                 Name,           Value   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IND_SPEC_GOLD',   'ModifierId',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_IND'   );

-- Additional +2 on top of the ordinary +1 return.
INSERT INTO BuildingModifiers
        (   BuildingType,                           ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_CORP_SPEC_GOLD'   );
INSERT INTO Modifiers
        (   ModifierId,                                                  ModifierType,                                         SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_CORP_SPEC_GOLD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_SPEC'   );
INSERT INTO ModifierArguments
        (   ModifierId,                                                  Name,           Value   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_CORP_SPEC_GOLD',   'ModifierId',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP'   );
