--===========================================================================================================================================================================--
/*	SPECIALTY PRODUCTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Civics
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_4_CIVIC}' || '{LOC_CSC_BAKERS_CAFE_DESCRIPTION_COMMISSION}' WHERE CivicType = 'CIVIC_URBANIZATION';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_ProductReference
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS CSC_ProductReference
    (
    Copy TEXT
    );

INSERT OR IGNORE INTO CSC_ProductReference
		(Copy)
VALUES	('0'), ('1'), ('2'), ('3'), ('4'), ('5'), ('6'), ('7'), ('8'), ('9');

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Types
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Types

		(	Type,																Kind					)
VALUES	(	'RESOURCE_CSC_BAKERS_SPECIALTY',									'KIND_RESOURCE'			),
		(	'PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',						'KIND_PROJECT'			);
		
---

INSERT OR IGNORE INTO Types

		(	Type,											Kind				)
SELECT		'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_' || Copy,		'KIND_GREATWORK'
FROM	CSC_ProductReference WHERE Copy > 0;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Resources
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Resources

		(	ResourceType,							ResourceClassType,			Happiness,	Frequency,	Name										)
VALUES	(	'RESOURCE_CSC_BAKERS_SPECIALTY',		'RESOURCECLASS_LUXURY',		4,			0,			'LOC_RESOURCE_CSC_BAKERS_SPECIALTY_NAME'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWorks
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO GreatWorks

	(	GreatWorkType,	GreatWorkObjectType,				Name	)
SELECT	Type,			'GREATWORKOBJECT_PRODUCT',		    'LOC_GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_X_NAME'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWorks_ImprovementType
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO GreatWorks_ImprovementType

		(	GreatWorkType,	ResourceType						)
SELECT	Type,				'RESOURCE_CSC_BAKERS_SPECIALTY'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWork_YieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO GreatWork_YieldChanges

		(	GreatWorkType,	YieldType,				YieldChange		)
SELECT	Type,				'YIELD_CULTURE',		'3'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWorkModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

/*
INSERT OR IGNORE INTO GreatWorkModifiers

		(GreatWorkType,	ModifierId								)
SELECT	Type,			'MOD_CSC_BAKERS_SPECIALTY_HOUSING'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

----

INSERT OR IGNORE INTO GreatWorkModifiers

		(GreatWorkType,	ModifierId								)
SELECT	Type,			'MOD_CSC_BAKERS_SPECIALTY_SLOT_ATTACH'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';
*/

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Projects
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Projects

		(	ProjectType,										PrereqDistrict,						RequiredBuilding,				PrereqTech,				PrereqCivic,				Cost,	AdvisorType,		Name,														ShortName,															Description		)
VALUES	(	'PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',		'DISTRICT_CSC_BAKERS_QUARTER',		'BUILDING_CSC_BAKERS_CAFE',		NULL,					'CIVIC_URBANIZATION',		500,	'ADVISOR_GENERIC',	'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_NAME',		'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_SHORT_NAME',		'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_DESCRIPTION'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ProjectCompletionModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ProjectCompletionModifiers

		(	ProjectType,										ModifierId																)
VALUES	(	'PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',		'MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY'					);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,													ModifierType											)
VALUES	(	'MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY',		'MODIFIER_PLAYER_GRANT_RANDOM_RESOURCE_PRODUCT'			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments

		(	ModifierId,													Name,				Value								)
VALUES	(	'MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY',		'ResourceType',		'RESOURCE_CSC_BAKERS_SPECIALTY'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_ProductReference
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

DROP TABLE CSC_ProductReference;

INSERT INTO CivilopediaPageExcludes
		(	SectionId,			PageId	) VALUES	
		(	'RESOURCES',		'RESOURCE_CSC_BAKERS_SPECIALTY');
