--==========================================================================================================================
-- Loclalization
--==========================================================================================================================
INSERT OR IGNORE  INTO LocalizedText	
		(Tag,																Language,		Text)
VALUES	('LOC_ZEGA_STACK_AMOUNT_DESC',										'en_US',		" (combined from {1_iStackAmount} {1_Num : plural 1?Source; other?Sources;})."),
		
		('LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_MESSAGE',			'en_US',		"Service Established"),
		('LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_SUMMARY',			'en_US',		'A supply chain ending in {1_CityName} has completed, establishing {2_Ability}. '),
		
		('LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_MESSAGE',	'en_US',		"Service Level Increased"),
		('LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_SUMMARY',	'en_US',		'A supply chain ending in {1_CityName} has been strengthened,[NEWLINE]expanding the local {2_Ability}. '),

		('LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_MESSAGE',	'en_US',		"Service Level Decreased"),
		('LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_SUMMARY',	'en_US',		'A supply chain ending in {1_CityName} has been disrupted,[NEWLINE]reducing the local {2_Ability}. '),

		('LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_MESSAGE',		'en_US',		"Service Closed"),
		('LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_SUMMARY',		'en_US',		'A supply chain ending in {1_CityName} has broken down,[NEWLINE]closing the local {2_Ability}. '),

--		('LOC_NOTIFICATION_HENNO_NEW_CITY_SPECIALIST_MESSAGE',				'en_US',		'New Specialist Slot'	),
--		('LOC_NOTIFICATION_HENNO_NEW_CITY_SPECIALIST_SUMMARY',				'en_US',		'With the appointment of a local {2_Specialist}, the City of {1_CityName} has now gained {3_SpecialistAmount} additional specialist {3_Num : plural 1?slot; other?slots;}.'),
		
		('LOC_NOTIFICATION_HENNO_NEW_CITY_ARISTOCRAT_MESSAGE',				'en_US',		'Aristocrat Established'	),
		('LOC_NOTIFICATION_HENNO_NEW_CITY_ARISTOCRAT_SUMMARY',				'en_US',		'The City of {1_CityName} now has a resident Aristocrat.'	),

		('LOC_HENNO_CITY_ABILITY_CHANGE_INCREASE',							'en_US',		"more"),
		('LOC_HENNO_CITY_ABILITY_CHANGE_DECREASE',							'en_US',		"fewer"),
		
		('LOC_ZEGA_STACK_AMOUNT_CHANGE_DESC',								'en_US',		" (from {1_iStackAmount} {2_ChangeType} {1_Num : plural 1?Source; other?Sources;})."),
		('LOC_HENNO_CITY_ABILITY_SOURCE_INCREASE',							'en_US',		"additional"),
		('LOC_HENNO_CITY_ABILITY_SOURCE_DECREASE',							'en_US',		"removed");
		