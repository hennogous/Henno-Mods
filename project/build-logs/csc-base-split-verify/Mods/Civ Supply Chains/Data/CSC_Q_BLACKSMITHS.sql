-- CSC_BLACKSMITHS
-- Author: Henno
-- DateCreated: 2025-06-20 13:19:21
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	TYPES */
--===========================================================================================================================================================================--

INSERT INTO Types

		(	Type,																Kind					)
VALUES	( 	'DISTRICT_CSC_BLACKSMITHS_QUARTER',                                'KIND_DISTRICT'         );



--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

	(       Tag,                                    Vocabulary              )
VALUES	(	'CLASS_CSC_BLACKSMITHS_BASE',          'RESOURCE_CLASS'	        ),
        (	'CLASS_CSC_BLACKSMITHS_SPEC',          'RESOURCE_CLASS'	        );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Blacksmiths' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                           Tag			        )
SELECT	ResourceType,			        'CLASS_CSC_BLACKSMITHS_BASE'
FROM	Resources
WHERE	ResourceType 			        IN
    (	'RESOURCE_COPPER',
        'RESOURCE_IRON'                );

INSERT OR IGNORE INTO TypeTags

	(	Type,							Tag			        )
SELECT	TerrainType,					'CLASS_CSC_BLACKSMITHS_BASE'
FROM	Terrains
WHERE	Hills = 1;

-- Blacksmiths' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                           Tag			        )
SELECT	ResourceType,			        'CLASS_CSC_BLACKSMITHS_SPEC'
FROM    Resources
WHERE	ResourceType 			        IN
    (	'RESOURCE_ALUMINUM',
        'RESOURCE_SILVER'               );



--===============================================================================================================================================================================--
/*	BLACKSMITHS' QUARTER */
--===============================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Districts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO Districts

		(  	DistrictType,
			Name,
			Description,
			PrereqTech,
			PrereqCivic,
			Cost,
			CostProgressionModel,
			CostProgressionParam1,
			MilitaryDomain,
			RequiresPlacement,
			Coast,
			RequiresPopulation,
			Aqueduct,
			InternalOnly,
			NoAdjacentCity,
			PlunderType,
			PlunderAmount,
			Appeal,
			OnePerCity,
			CaptureRemovesBuildings,
			CaptureRemovesCityDefenses,
			Maintenance,
			CityStrengthModifier,
			AdvisorType                     		)
VALUES	(
		/*  DistrictType, */						'DISTRICT_CSC_BLACKSMITHS_QUARTER',
		/*  Name, */								'LOC_DISTRICT_CSC_BLACKSMITHS_QUARTER_NAME',
		/*  Description, */							'LOC_DISTRICT_CSC_BLACKSMITHS_QUARTER_DESCRIPTION',
		/*  PrereqTech, */							NULL,
		/*  PrereqCivic, */							'CIVIC_CRAFTSMANSHIP',
		/*  Cost, */								60,
		/*  CostProgressionModel, */    			'COST_PROGRESSION_PREVIOUS_COPIES',
		/*  CostProgressionParam1, */				100,
		/*  MilitaryDomain, */						'NO_DOMAIN',
		/*  RequiresPlacement, */					1,
		/*  Coast, */								0,
		/*  RequiresPopulation, */	    			0,
		/*  Aqueduct, */							0,
		/*  InternalOnly, */						0,
		/*  NoAdjacentCity, */						0,
		/*  PlunderType, */							'PLUNDER_GOLD',
		/*  PlunderAmount, */						50,
		/*  Appeal, */								1,
		/*  OnePerCity, */							1,
		/*  CaptureRemovesBuildings, */	   			0,
		/*  CaptureRemovesCityDefenses, */			0,
		/*  Maintenance, */							0,
		/*  CityStrengthModifier */					2,
		/*  AdvisorType */							'ADVISOR_GENERIC'
													);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Adjacency_YieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT INTO Adjacency_YieldChanges

		(	ID,											    Description,									    YieldType,				YieldChange,	AdjacentFeature,	AdjacentImprovement,	AdjacentDistrict,						AdjacentResourceClass,		PrereqTech			)
VALUES	(	'CSC_COMMERCIAL_HUB_GOLD_TO_BLACKSMITHS',		'LOC_CSC_COMMERCIAL_HUB_GOLD_TO_BLACKSMITHS',		'YIELD_GOLD',			1,				NULL,				NULL,					'DISTRICT_COMMERCIAL_HUB',				'NO_RESOURCECLASS',			NULL				),
		(	'CSC_BLACKSMITHS_PRODUCTION_TO_COMMERCIAL_HUB',	'LOC_CSC_BLACKSMITHS_PRODUCTION_TO_COMMERCIAL_HUB',	'YIELD_PRODUCTION',		1,				NULL,				NULL,					'DISTRICT_CSC_BLACKSMITHS_QUARTER',     'NO_RESOURCECLASS',			NULL				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	District_Adjacencies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT INTO District_Adjacencies

		(	DistrictType,						        YieldChangeId		)
VALUES	(	'DISTRICT_CSC_BLACKSMITHS_QUARTER',		    'CSC_COMMERCIAL_HUB_GOLD_TO_BLACKSMITHS'		    ),
		(	'DISTRICT_COMMERCIAL_HUB',			        'CSC_BLACKSMITHS_PRODUCTION_TO_COMMERCIAL_HUB'		);
