--==========================================================================================================================
-- Loclalization
--==========================================================================================================================
INSERT OR IGNORE  INTO LocalizedText	
		(Tag,																Language,		Text)
VALUES	('LOC_ZEGA_STACK_AMOUNT_DESC',										'en_US',		" (combined from {1_iStackAmount} {1_Num : plural 1?Source; other?Sources;})."),
		
		('LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_MESSAGE',			'en_US',		"Supply Chain Effect Unlocked"),
		('LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_SUMMARY',			'en_US',		'The City of {1_CityName} has gained {2_Ability}'),
		
		('LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_MESSAGE',	'en_US',		"Supply Chain Effect Increased"),
		('LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_SUMMARY',	'en_US',		'The City of {1_CityName} has gained a further {2_Ability}'),

		('LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_MESSAGE',	'en_US',		"Supply Chain Effect Decreased"),
		('LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_SUMMARY',	'en_US',		'The City of {1_CityName} has lost {2_Ability}'),

		('LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_MESSAGE',		'en_US',		"Supply Chain Effect Removed"),
		('LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_SUMMARY',		'en_US',		'The City of {1_CityName} has lost {2_Ability}'),
		
		('LOC_HENNO_CITY_ABILITY_CHANGE_INCREASE',							'en_US',		"more"),
		('LOC_HENNO_CITY_ABILITY_CHANGE_DECREASE',							'en_US',		"fewer"),
		
		('LOC_ZEGA_STACK_AMOUNT_CHANGE_DESC',								'en_US',		" (from {1_iStackAmount} {2_ChangeType} {1_Num : plural 1?Source; other?Sources;})."),
		('LOC_HENNO_CITY_ABILITY_SOURCE_INCREASE',							'en_US',		"additional"),
		('LOC_HENNO_CITY_ABILITY_SOURCE_DECREASE',							'en_US',		"removed");
		