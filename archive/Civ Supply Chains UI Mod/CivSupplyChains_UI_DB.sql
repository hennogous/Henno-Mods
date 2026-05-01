--==========================================================================================================================
-- Zegangani: 
--==========================================================================================================================
-------------------------------------			
-- Notifications
-------------------------------------
INSERT INTO Types
		(	Type,													Kind)
VALUES	(	'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',					'KIND_NOTIFICATION'),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',				'KIND_NOTIFICATION'),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',				'KIND_NOTIFICATION'),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',				'KIND_NOTIFICATION');

INSERT INTO Notifications
		(	NotificationType,										SeverityType,	ExpiresEndOfTurn,		AutoNotify)
VALUES	(	'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',					'HIGH',			0,						0),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',				'HIGH',			0,						0),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',				'HIGH',			0,						0),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',				'HIGH',			0,						0);
		
----------------------
-- Henno_ValidCityModifiers
----------------------

CREATE TABLE IF NOT EXISTS Henno_ValidCityModifiers(
		ModifierId TEXT PRIMARY KEY NOT NULL, 
		AttachedModifierId TEXT DEFAULT NULL,
		ArgumentAmount INTEGER DEFAULT 0,
		ModifierDesc TEXT DEFAULT NULL,
		ModifierNewDesc TEXT DEFAULT NULL,
		ModifierIncreasedDesc TEXT DEFAULT NULL,
		ModifierDecreasedDesc TEXT DEFAULT NULL,
		ModifierRemovedDesc TEXT DEFAULT NULL,
		ModifierIcon TEXT DEFAULT NULL,
		ModifierIconTarget TEXT DEFAULT NULL
);


INSERT INTO Henno_ValidCityModifiers
		(	ModifierId,													ModifierIcon,						ModifierIconTarget		)
VALUES	(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',			'ICON_EFFECT_CSC_BAKERS_STAGE_2',	'BUILDING_GRANARY'		),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',			'ICON_EFFECT_CSC_BAKERS_STAGE_2',	'BUILDING_GRANARY'		),
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',				'ICON_EFFECT_CSC_BAKERS_STAGE_3',	'BUILDING_MARKET'		),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',		'ICON_EFFECT_CSC_BAKERS_STAGE_4',	'BUILDING_ZOO'			),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',			'ICON_EFFECT_CSC_BAKERS_STAGE_4',	'BUILDING_FERRIS_WHEEL'	);

----------------------
-- CSC_SpecialistModifiers
----------------------

CREATE TABLE IF NOT EXISTS CSC_SpecialistModifiers(
		ModifierId TEXT PRIMARY KEY NOT NULL, 
		AttachedModifierId TEXT DEFAULT NULL,
		ModifierNewDesc TEXT DEFAULT NULL
);


INSERT INTO CSC_SpecialistModifiers
		(	ModifierId		)
VALUES	(	'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_ATTACH_COMHUB'		),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_ENTER'		),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_WATER'		);