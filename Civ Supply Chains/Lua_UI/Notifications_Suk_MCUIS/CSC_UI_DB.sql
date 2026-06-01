--==========================================================================================================================
-- Zegangani: 
--==========================================================================================================================
-------------------------------------			
-- Notifications
-------------------------------------
INSERT INTO Types
		(	Type,														Kind)
VALUES	(	'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',						'KIND_NOTIFICATION'	),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',					'KIND_NOTIFICATION'	),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',					'KIND_NOTIFICATION'	),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',					'KIND_NOTIFICATION'	);

--		(	'NOTIFICATION_CSC_BAKERS_STAGE_3_SERVICE_GRANT',			'KIND_NOTIFICATION'	),
--		(	'NOTIFICATION_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',		'KIND_NOTIFICATION'	),
--		(	'NOTIFICATION_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',		'KIND_NOTIFICATION'	);

INSERT INTO Notifications
		(	NotificationType,											SeverityType,	ExpiresEndOfTurn,		AutoNotify	)
VALUES	(	'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',						'HIGH',			0,						0			),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',					'HIGH',			0,						0			),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',					'HIGH',			0,						0			),
		(	'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',					'HIGH',			0,						0			);

--		(	'NOTIFICATION_CSC_BAKERS_STAGE_3_SERVICE_GRANT',			'HIGH',			0,						0			),
--		(	'NOTIFICATION_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',		'HIGH',			0,						0			),
--		(	'NOTIFICATION_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',		'HIGH',			0,						0			);
		
----------------------
-- CSC_AbilityAttachModifiers
----------------------

CREATE TABLE IF NOT EXISTS CSC_AbilityAttachModifiers(
		ModifierId TEXT PRIMARY KEY NOT NULL, 
		AbilityEffectModifierId TEXT DEFAULT NULL,
		AbilityArgumentAmount INTEGER DEFAULT 0,
		AbilityDesc TEXT DEFAULT NULL,
		AbilityNewDesc TEXT DEFAULT NULL,
		AbilityIncreasedDesc TEXT DEFAULT NULL,
		AbilityDecreasedDesc TEXT DEFAULT NULL,
		AbilityRemovedDesc TEXT DEFAULT NULL,
		AbilityIcon TEXT DEFAULT NULL,
		AbilityIconTarget TEXT DEFAULT NULL
);


INSERT INTO CSC_AbilityAttachModifiers
		(	ModifierId,													AbilityIcon,										AbilityIconTarget							)
VALUES	(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',			'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE',			'BUILDING_CSC_BAKERS_STAGE_2_SERVICE'		),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',			'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE',			'BUILDING_CSC_BAKERS_STAGE_2_SERVICE'		),
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',				'ICON_BUILDING_CSC_BAKERS_STAGE_3_SERVICE',			'BUILDING_CSC_BAKERS_STAGE_3_SERVICE'		),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',		'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER'	),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',			'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER'	);

----------------------
-- CSC_SpecialistAttachModifiers
----------------------
/*
-- Specialist-slot grant notifications are currently folded into the main
-- Quarter effect notification text instead.
CREATE TABLE IF NOT EXISTS CSC_SpecialistAttachModifiers(
		ModifierId TEXT PRIMARY KEY NOT NULL, 
		SpecialistGrantModifierId TEXT DEFAULT NULL,
		SpecialistGrantDesc TEXT DEFAULT NULL
);
*/
/*
INSERT INTO CSC_SpecialistAttachModifiers
		(	ModifierId		)
VALUES	(	'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB'		),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER'		),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER'		); */
