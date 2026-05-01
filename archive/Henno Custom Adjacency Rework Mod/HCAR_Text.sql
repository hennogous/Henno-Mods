--==========================================================================================================================
-- Loclaization
--==========================================================================================================================
-- For the dynamic adjacency Strings:
-- {1_iBonus} (integer): is the Value of the Adjacency
-- {2_YieldIcon} (string): Icon of adjacency type (Yield/GPP/Other)
-- {3_AdjacentSubjectNum} (integer): Amount of Adjacency Sources (3 adjacent Hills/Resources...etc.)
-- {4_CAO} (string): Adjacency Object (like a terrain, resource...etc.)
-- {5_sAdjacency} (string): returns the adjacency type: local, adjacent or nearby.

-- We can use {X_Num : plural 1?string_1; other?string_2;} to dynamically change which string we want to use in a space based on the X argument's Value.
-- X can be any of the parameters above with an integer Value, so we can use it for {1_iBonus} and {3_AdjacentSubjectNum}
-- Example: {1_Num : plural 1?resource; other?resources;} -- If 1_Num (1_iBonus) returns 1 then we use the word 'resource', if not then we use 'resources' instead.
------------------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText	
		(Tag,											Language,			Text)
VALUES	('LOC_RUIVO_FROM_RINGS_TYPETAG_RESOURCE',		'en_US',			"{1_iBonus} {2_YieldIcon} from {3_AdjacentSubjectNum} {5_sAdjacency} {4_CAO} {3_Num : plural 1?resource; other?resources;}."),
		('LOC_RUIVO_FROM_RINGS_CAO_RESOURCE',			'en_US',			"{1_iBonus} {2_YieldIcon} from {3_AdjacentSubjectNum} {5_sAdjacency} {4_CAO} {3_Num : plural 1?resource; other?resources;}."),
		('LOC_RUIVO_FROM_RINGS_SPECIFIC_WONDER',		'en_US',			"{1_iBonus} {2_YieldIcon} from the {5_sAdjacency} {4_CAO} Wonder."),
		('LOC_RUIVO_FROM_RINGS_CAO_TERRAIN_SETS',		'en_US',			"{1_iBonus} {2_YieldIcon} from {3_AdjacentSubjectNum} {5_sAdjacency} {4_CAO} terrain."),
		('LOC_RUIVO_FROM_RINGS_CAO_TERRAIN',			'en_US',			"{1_iBonus} {2_YieldIcon} from {3_AdjacentSubjectNum} {5_sAdjacency} {4_CAO} terrain."),
		('LOC_RUIVO_FROM_RIVER_CROSSING',				'en_US',			'{1_iBonus} {2_YieldIcon} from {3_AdjacentSubjectNum} adjacent river segments.'	),
		
		('LOC_RUIVO_RING_0',							'en_US',			""),
		('LOC_RUIVO_RING_SPECIFIC',						'en_US',			" (in ring {1_MaxRings} only)"),
		('LOC_RUIVO_RING_MIN_MAX',						'en_US',			" (between a radius of {2_MinRings} and {1_MaxRings})"),
		('LOC_RUIVO_RING_MAX',							'en_US',			" (in a {1_MaxRings} tiles radius)"),
		
		('LOC_ZEGA_ADJACENCY_LOCAL',					'en_US',			"local"),
		('LOC_ZEGA_ADJACENCY_ADJACENT',					'en_US',			"adjacent"),
		('LOC_ZEGA_ADJACENCY_NEARBY',					'en_US',			"nearby"),
		
		('LOC_ZEGA_FROM_DISTRICT_ABILITY',				'en_US',			" (from district ability)");
		