-- ModSupport_CL
-- Author: Shadow
-- DateCreated: 2025-08-09 09:41:06
--------------------------------------------------------------


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO ImprovementModifiers

        (	ImprovementType,				ModifierId												)	VALUES

-- 	CAFE --------------------------------------------------------------------------

--  +1 Production to the Cafe from improved specialty materials
        (	'IMP_CL_TRADING_POST',          'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'		);


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

		(	Tag,								Vocabulary			)
VALUES	(	'CLASS_CSC_BAKERS_INCOMING_GOODS',	'DISTRICT_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  CL Rural Communities provide incoming goods/production to Bakers' Quarters.
INSERT OR IGNORE INTO TypeTags

		(	Type,								Tag											) VALUES
		(	'DISTRICT_RURALCOMMUNITYA',			'CLASS_CSC_BAKERS_INCOMING_GOODS'			),
		(	'DISTRICT_COREX_FRONTIER_TOWN',		'CLASS_CSC_BAKERS_INCOMING_GOODS'			),
		(	'DISTRICT_RURALCOMMUNITYB',			'CLASS_CSC_BAKERS_INCOMING_GOODS'			),
		(	'DISTRICT_COREX_TROYU',				'CLASS_CSC_BAKERS_INCOMING_GOODS'			),
		(	'DISTRICT_COREX_TSIKHE',			'CLASS_CSC_BAKERS_INCOMING_GOODS'			),
		(	'DISTRICT_RURALCOMMUNITYC',			'CLASS_CSC_BAKERS_INCOMING_GOODS'			),
		(	'DISTRICT_COREX_GYOSON',			'CLASS_CSC_BAKERS_INCOMING_GOODS'			);

--  CL districts receive Bakers' Food return yields through the same Bakers sales-return tag used by core Bakers SQL.
INSERT OR IGNORE INTO TypeTags

		(	Type,								Tag							) VALUES
		(	'DISTRICT_RURALCOMMUNITYA',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_FRONTIER_TOWN',		'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_RURALCOMMUNITYB',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_TROYU',				'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_TSIKHE',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_RURALCOMMUNITYC',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_GYOSON',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREEXPANSIONA',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREEXPANSIONA',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_XIAN',				'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREX_XIAN',				'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_UPAPITHA',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREX_UPAPITHA',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_VENICE_01',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREX_VENICE_01',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREEXPANSIONB',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREEXPANSIONB',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_VENICE_02',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREX_VENICE_02',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_FUERTE',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREX_FUERTE',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREEXPANSIONC',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREEXPANSIONC',			'CLASS_CSC_BAKERS_SALES_FOOD'		),
		(	'DISTRICT_COREX_ELYSEE',			'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_COREX_ELYSEE',			'CLASS_CSC_BAKERS_SALES_FOOD'		);