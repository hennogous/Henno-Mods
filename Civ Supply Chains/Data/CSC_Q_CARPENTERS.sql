-- CSC_CARPENTERS
-- Author: Henno
-- DateCreated: 2025-06-20 13:19:09
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	TYPES */
--===========================================================================================================================================================================--

INSERT INTO Types

		(	Type,																Kind					)
VALUES	( 	'DISTRICT_CSC_CARPENTERS_QUARTER',                                  'KIND_DISTRICT'         ),

		(	'BUILDING_CSC_CARPENTERS_JOINERY',									'KIND_BUILDING'			);



--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

	(       Tag,                                    Vocabulary                  )
VALUES	(	'CLASS_CSC_CARPENTERS_BASE',            'RESOURCE_CLASS'	        ),
        (	'CLASS_CSC_CARPENTERS_SPEC',            'RESOURCE_CLASS'	        );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Carpenters' Quarter base materials
INSERT OR IGNORE INTO TypeTags

	(	Type,							Tag			        )
SELECT	FeatureType,					'CLASS_CSC_CARPENTERS_BASE'
FROM	Features
WHERE	FeatureType 					IN
	(	'FEATURE_FOREST',
        'FEATURE_JUNGLE'                );

-- Carpenters' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                           Tag			        )
SELECT	ResourceType,			        'CLASS_CSC_CARPENTERS_SPEC'
FROM    Resources
WHERE	ResourceType 			        IN
    (	'RESOURCE_AMBER',
        'RESOURCE_DYES'                 );



--===============================================================================================================================================================================--
/*	CARPENTERS' QUARTER */
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
		/*  DistrictType, */						'DISTRICT_CSC_CARPENTERS_QUARTER',
		/*  Name, */								'LOC_DISTRICT_CSC_CARPENTERS_QUARTER_NAME',
		/*  Description, */							'LOC_DISTRICT_CSC_CARPENTERS_QUARTER_DESCRIPTION',
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
VALUES	(	'CSC_COMMERCIAL_HUB_GOLD_TO_CARPENTERS',		'LOC_CSC_COMMERCIAL_HUB_GOLD_TO_CARPENTERS',		'YIELD_GOLD',			1,				NULL,				NULL,					'DISTRICT_COMMERCIAL_HUB',				'NO_RESOURCECLASS',			NULL				),
		(	'CSC_CARPENTERS_PRODUCTION_TO_COMMERCIAL_HUB',	'LOC_CSC_CARPENTERS_PRODUCTION_TO_COMMERCIAL_HUB',	'YIELD_PRODUCTION',		1,				NULL,				NULL,					'DISTRICT_CSC_CARPENTERS_QUARTER',    	'NO_RESOURCECLASS',			NULL				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	District_Adjacencies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT INTO District_Adjacencies

		(	DistrictType,						        YieldChangeId		)
VALUES	(	'DISTRICT_CSC_CARPENTERS_QUARTER',		    'CSC_COMMERCIAL_HUB_GOLD_TO_CARPENTERS'		        ),
		(	'DISTRICT_COMMERCIAL_HUB',			        'CSC_CARPENTERS_PRODUCTION_TO_COMMERCIAL_HUB'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Boosts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

UPDATE Boosts SET TriggerDescription='LOC_BOOST_TRIGGER_CONSTRUCTION_CSC',	TriggerLongDescription='LOC_BOOST_TRIGGER_LONGDESC_CONSTRUCTION_CSC', BuildingType='BUILDING_CSC_CARPENTERS_JOINERY'	WHERE TechnologyType='TECH_CONSTRUCTION';



--===========================================================================================================================================================================--
/*	STAGES 2-4 - BUILDINGS */
--===========================================================================================================================================================================--

INSERT INTO Buildings

		(	BuildingType,
			Name,
			Description,
			PrereqTech,
			PrereqCivic,
			Cost,
			PrereqDistrict,
			PurchaseYield,
			Maintenance,
			CitizenSlots,
			AdvisorType				)
VALUES	(
		/*  BuildingType, */		'BUILDING_CSC_CARPENTERS_JOINERY',
		/*  Name, */				'LOC_BUILDING_CSC_CARPENTERS_JOINERY_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_CARPENTERS_JOINERY_DESCRIPTION',
		/*  PrereqTech, */			'TECH_BRONZE_WORKING',
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				80,
		/*  PrereqDistrict, */		'DISTRICT_CSC_CARPENTERS_QUARTER',
		/*  PurchaseYield, */		'YIELD_GOLD',
		/*  Maintenance, */			1,
		/*	CitizenSlots */			0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									);