-- CSC_MC_MODE
-- Author: Henno
-- DateCreated: 2025-08-09 16:51:27
--------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Types
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO Types

		(	Type,																Kind					)
VALUES	(	'BUILDING_CSC_ARISTOCRAT',											'KIND_BUILDING'			),
		(	'NOTIFICATION_CSC_NEW_ARISTOCRAT',									'KIND_NOTIFICATION'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO Buildings

		(	BuildingType,
			Name,
			Cost,
			PrereqDistrict,
			CitizenSlots,
			PurchaseYield,
			MustPurchase,
			Description			)
VALUES	(
		/*  BuildingType, */		'BUILDING_CSC_ARISTOCRAT',
		/*	Name  */				'Aristocrat',
		/*	Cost  */				0,
		/*  PrereqDistrict, */		'DISTRICT_CITY_CENTER',
		/*	CitizenSlots */			0,
		/*  PurchaseYield */		NULL,
		/*	MustPurchase */			1,
		/*  Description */			'LOC_BUILDING_CSC_ARISTOCRAT_DESCRIPTION'
									);

INSERT INTO Building_GreatWorks (
    BuildingType,
    GreatWorkSlotType,
    NumSlots   )
VALUES
(   'BUILDING_CSC_ARISTOCRAT',
    'GREATWORKSLOT_PRODUCT',
    3       );

INSERT INTO CivilopediaPageExcludes
		(	SectionId,			PageId	) VALUES	
		(	'BUILDINGS',		'BUILDING_CSC_ARISTOCRAT'				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TraitModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO TraitModifiers

		(	TraitType,								    ModifierId                              )	VALUES
		(	'TRAIT_LEADER_MAJOR_CIV', 				    'MOD_CSC_GRANT_ARISTOCRAT_ATTACH'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,									ModifierType,												SubjectRequirementSetId       	)
VALUES	(	'MOD_CSC_GRANT_ARISTOCRAT_ATTACH',          'MODIFIER_PLAYER_CITIES_ATTACH_MODIFIER',						NULL /*'REQSET_PLAYER_HAS_HUMANISM'*/	),
		(	'MOD_CSC_GRANT_ARISTOCRAT_GRANT',		    'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',		NULL /*'REQSET_PLAYER_HAS_HUMANISM'*/	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments

		(	ModifierId,									Name,				Value									)
VALUES	(	'MOD_CSC_GRANT_ARISTOCRAT_ATTACH',		    'ModifierId',		'MOD_CSC_GRANT_ARISTOCRAT_GRANT'		),
		(	'MOD_CSC_GRANT_ARISTOCRAT_GRANT',		    'BuildingType',		'BUILDING_CSC_ARISTOCRAT'		        );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO RequirementSets (
    RequirementSetId,
    RequirementSetType      )
VALUES
(   'REQSET_PLAYER_HAS_HUMANISM',
    'REQUIREMENTSET_TEST_ALL'   );

INSERT INTO RequirementSetRequirements  (
    RequirementSetId,
    RequirementId   )
VALUES
(   'REQSET_PLAYER_HAS_HUMANISM',
    'REQ_PLAYER_HAS_HUMANISM'   );

INSERT INTO Requirements    (
    RequirementId,
    RequirementType     )
VALUES
(   'REQ_PLAYER_HAS_HUMANISM',
    'REQUIREMENT_PLAYER_HAS_CIVIC' );

INSERT INTO RequirementArguments (
    RequirementId,
    Name,
    Value   )
VALUES
(   'REQ_PLAYER_HAS_HUMANISM',
	'CivicType',
    'CIVIC_HUMANISM'    );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Notifications
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO Notifications
		(	NotificationType,											SeverityType,	ExpiresEndOfTurn,		AutoNotify	)
VALUES	(	'NOTIFICATION_CSC_NEW_ARISTOCRAT',							'HIGH',			0,						0			);