-- CSC_Q_TAILORS_MC_MODE
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

-- Tailors: Monopolies & Corporations layer
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
VALUES  (   'IMPROVEMENT_INDUSTRY',      'MOD_CSC_TAILORS_BASE_INDUSTRY_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_CORPORATION',   'MOD_CSC_TAILORS_BASE_CORPORATION_ATTACH_QUARTER'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Producer -> improvement adds a marginal return to the ordinary +1 already
-- attached in core: Industry adds 1 and Corporation adds 2, yielding totals
-- of 2 and 3. Adding the advertised total here would count that base +1 twice.


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Return sets require adjacency, the correct BASE/SPEC material tag, and the
-- exact Industry/Corporation improvement. An Industry on an unrelated luxury
-- does not qualify just because it is an Industry.


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ImprovementModifiers
        (   ImprovementType,          ModifierId   )
VALUES  (   'IMPROVEMENT_INDUSTRY',   'MOD_CSC_TAILORS_SPEC_INDUSTRY_ATTACH_QUARTER'   );

INSERT OR IGNORE INTO ImprovementModifiers
        (   ImprovementType,             ModifierId   )
VALUES  (   'IMPROVEMENT_CORPORATION',   'MOD_CSC_TAILORS_SPEC_CORPORATION_ATTACH_QUARTER'   );

-- Additional +1 on top of the ordinary +1 return.

-- Additional +2 on top of the ordinary +1 return.

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
        'INPUT_INDUSTRY',
        'PRODUCER',
        'YIELD_CULTURE',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'INPUT_CORPORATION',
        'PRODUCER',
        'YIELD_CULTURE',
        3,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'RETURN_PRODUCTION_CORPORATION',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'RETURN_PRODUCTION_INDUSTRY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'INPUT_INDUSTRY',
        'PRODUCER',
        'YIELD_CULTURE',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'INPUT_CORPORATION',
        'PRODUCER',
        'YIELD_CULTURE',
        3,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'RETURN_PRODUCTION_CORPORATION',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        2,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_CORPORATION'
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'RETURN_PRODUCTION_INDUSTRY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'EXACT_IMPROVEMENT',
        'IMPROVEMENT_INDUSTRY'
    );

INSERT INTO CSC_MaterialTransactionBindings
        (   TransactionId,                         LegKey,                            RootModifierId,                                              ChildModifierId,                                               OwnerRequirementSetId,                SubjectRequirementSetId   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_INDUSTRY',                  'MOD_CSC_TAILORS_BASE_INDUSTRY_ATTACH_QUARTER',              'MOD_CSC_TAILORS_BASE_INDUSTRY_CULTURE_TO_WORKSHOP',           'REQSET_CSC_TAILORS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_CORPORATION',               'MOD_CSC_TAILORS_BASE_CORPORATION_ATTACH_QUARTER',           'MOD_CSC_TAILORS_BASE_CORPORATION_CULTURE_TO_WORKSHOP',        'REQSET_CSC_TAILORS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_CORPORATION',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_CORP_BASE_PROD',        'MOD_CSC_TAILORS_PROD_TO_ADJ_CORP',                            NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IND_BASE_PROD',         'MOD_CSC_TAILORS_PROD_TO_ADJ_IND',                             NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_INDUSTRY',                  'MOD_CSC_TAILORS_SPEC_INDUSTRY_ATTACH_QUARTER',              'MOD_CSC_TAILORS_SPEC_INDUSTRY_CULTURE_TO_FASHION_HOUSE',      'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_CORPORATION',               'MOD_CSC_TAILORS_SPEC_CORPORATION_ATTACH_QUARTER',           'MOD_CSC_TAILORS_SPEC_CORPORATION_CULTURE_TO_FASHION_HOUSE',   'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_CORPORATION',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_CORP_SPEC_PROD',   'MOD_CSC_TAILORS_PROD_TO_ADJ_CORP',                            NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_SPEC'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_INDUSTRY',      'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IND_SPEC_PROD',    'MOD_CSC_TAILORS_PROD_TO_ADJ_IND',                             NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_SPEC'   );

INSERT INTO CSC_MaterialTransactionGateBindings
        (   TransactionId,                         LegKey,                            RequirementSetId,                              RequirementId,                              GateRole   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_INDUSTRY',                  'REQSET_CSC_TAILORS_PLOT_HAS_BASE',            'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_CORPORATION',               'REQSET_CSC_TAILORS_PLOT_HAS_BASE',            'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_CORPORATION',               'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_CORPORATION',               'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_CORPORATION',     'IMPROVEMENT_TYPE'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_TAILORS_PLOT_HAS_INDUSTRY',        'IMPROVEMENT_TYPE'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_BASE',    'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_INDUSTRY',                  'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',            'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_INDUSTRY',                  'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_CORPORATION',               'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',            'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_CORPORATION',               'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_CORPORATION',               'REQSET_CSC_ADJ_TAILORS_QUARTER',              'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_TAILORS_PLOT_HAS_CORPORATION',     'IMPROVEMENT_TYPE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_CORPORATION',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_CORP_SPEC',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_TAILORS_PLOT_HAS_INDUSTRY',        'IMPROVEMENT_TYPE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_INDUSTRY',      'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_IND_SPEC',    'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   );
