-- CSC_Q_TAILORS
-- Author: Henno
-- DateCreated: 2025-06-20 13:17:53
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	TYPES */
--===========================================================================================================================================================================--

INSERT OR IGNORE INTO Types

		(	Type,																Kind					)
VALUES	( 	'DISTRICT_CSC_TAILORS_QUARTER',                              		'KIND_DISTRICT'         );



--===========================================================================================================================================================================--
/*	RESOURCES AND ADJACENCY TAGS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

		(   Tag,										Vocabulary			)
VALUES	(	'CLASS_CSC_TAILORS_BASE',					'RESOURCE_CLASS'	),
		(	'CLASS_CSC_TAILORS_SPEC',					'RESOURCE_CLASS'	),
		(	'CLASS_CSC_TAILORS_HARBOR_TO_QUARTER_GOLD',	'DISTRICT_CLASS'	),
		(	'CLASS_CSC_TAILORS_SALES',					'DISTRICT_CLASS'	),
		(	'CLASS_CSC_TAILORS_SALES_PRODUCTION',		'DISTRICT_CLASS'	),
		(	'CLASS_CSC_TAILORS_SALES_CULTURE',			'DISTRICT_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO TypeTags

		(	Type,										Tag											)
VALUES
--	Tailors' Quarter base materials. Animal resources live in CSC_A_RESOURCES and related ModSupport_A files.
		(	'RESOURCE_COTTON',							'CLASS_CSC_TAILORS_BASE'					),

--	Tailors' Quarter specialty materials. Silk is animal-gated in CSC_A_RESOURCES.
		(	'RESOURCE_DYES',							'CLASS_CSC_TAILORS_SPEC'					),
		(	'RESOURCE_SILVER',							'CLASS_CSC_TAILORS_SPEC'					),

--	Tailors' Quarter customer/sales districts.
		(	'DISTRICT_HARBOR',							'CLASS_CSC_TAILORS_HARBOR_TO_QUARTER_GOLD'	),
		(	'DISTRICT_HARBOR',							'CLASS_CSC_TAILORS_SALES_PRODUCTION'		),
		(	'DISTRICT_COMMERCIAL_HUB',					'CLASS_CSC_TAILORS_SALES'					),
		(	'DISTRICT_COMMERCIAL_HUB',					'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_HOLY_SITE',						'CLASS_CSC_TAILORS_SALES'					),
		(	'DISTRICT_HOLY_SITE',						'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_THEATER',							'CLASS_CSC_TAILORS_SALES'					),
		(	'DISTRICT_THEATER',							'CLASS_CSC_TAILORS_SALES_CULTURE'			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterMaterialAdjacencyConfig
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO CSC_QuarterMaterialAdjacencyConfig
		(
		QuarterKey,
		SourceTag,
		SourceFilter,
		YieldType,
		YieldChange,
		AdjacencyType
		)
VALUES
--	Broad Tailors material classes use MAB typetag matching so optional resource mappings inherit automatically.
		(	'TAILORS',		'CLASS_CSC_TAILORS_BASE',		'',		'YIELD_PRODUCTION',		1,		'FROM_RINGS_TYPETAG_RESOURCE'	),
		(	'TAILORS',		'CLASS_CSC_TAILORS_SPEC',		'',		'YIELD_PRODUCTION',		1,		'FROM_RINGS_TYPETAG_RESOURCE'	);



--===============================================================================================================================================================================--
/*	TAILORS' QUARTER */
--===============================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Districts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Districts

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
		/*  DistrictType, */						'DISTRICT_CSC_TAILORS_QUARTER',
		/*  Name, */								'LOC_DISTRICT_CSC_TAILORS_QUARTER_NAME',
		/*  Description, */							'LOC_DISTRICT_CSC_TAILORS_QUARTER_DESCRIPTION',
		/*  PrereqTech, */							NULL,
		/*  PrereqCivic, */							'CIVIC_CRAFTSMANSHIP',
		/*  Cost, */								60,
		/*  CostProgressionModel, */    			'COST_PROGRESSION_PREVIOUS_COPIES',
		/*  CostProgressionParam1, */				10,
		/*  MilitaryDomain, */						'NO_DOMAIN',
		/*  RequiresPlacement, */					1,
		/*  Coast, */								0,
		/*  RequiresPopulation, */	    			0,
		/*  Aqueduct, */							0,
		/*  InternalOnly, */						0,
		/*  NoAdjacentCity, */						0,
		/*  PlunderType, */							'PLUNDER_CULTURE',
		/*  PlunderAmount, */						50,
		/*  Appeal, */								1,
		/*  OnePerCity, */							1,
		/*  CaptureRemovesBuildings, */	   			0,
		/*  CaptureRemovesCityDefenses, */			0,
		/*  Maintenance, */							1,
		/*  CityStrengthModifier */					2,
		/*  AdvisorType */							'ADVISOR_GENERIC'
													);
