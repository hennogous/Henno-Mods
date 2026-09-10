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

		(	Tag,										Vocabulary			)
VALUES	(	'CLASS_CSC_BAKERS_GOODS_PROVIDER',			'DISTRICT_CLASS'	),
        (   'CLASS_CSC_TAILORS_GOODS_PROVIDER',          'DISTRICT_CLASS'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  CL Rural Communities provide goods/production to Bakers' Quarters.
INSERT OR IGNORE INTO TypeTags

		(	Type,								Tag											) VALUES
		(	'DISTRICT_RURALCOMMUNITYA',			'CLASS_CSC_BAKERS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_FRONTIER_TOWN',		'CLASS_CSC_BAKERS_GOODS_PROVIDER'			),
		(	'DISTRICT_RURALCOMMUNITYB',			'CLASS_CSC_BAKERS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_TROYU',				'CLASS_CSC_BAKERS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_TSIKHE',			'CLASS_CSC_BAKERS_GOODS_PROVIDER'			),
		(	'DISTRICT_RURALCOMMUNITYC',			'CLASS_CSC_BAKERS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_GYOSON',			'CLASS_CSC_BAKERS_GOODS_PROVIDER'			);

--  CL Rural Communities provide workforce/Production to Tailors' Quarters.
INSERT OR IGNORE INTO TypeTags

		(	Type,								Tag										) VALUES
		(	'DISTRICT_RURALCOMMUNITYA',			'CLASS_CSC_TAILORS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_FRONTIER_TOWN',		'CLASS_CSC_TAILORS_GOODS_PROVIDER'			),
		(	'DISTRICT_RURALCOMMUNITYB',			'CLASS_CSC_TAILORS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_TROYU',				'CLASS_CSC_TAILORS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_TSIKHE',				'CLASS_CSC_TAILORS_GOODS_PROVIDER'			),
		(	'DISTRICT_RURALCOMMUNITYC',			'CLASS_CSC_TAILORS_GOODS_PROVIDER'			),
		(	'DISTRICT_COREX_GYOSON',			'CLASS_CSC_TAILORS_GOODS_PROVIDER'			);

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

--  Tailors returns Culture to Rural Communities and Urban Boroughs. Urban Boroughs also purchase Tailors goods.
INSERT OR IGNORE INTO TypeTags

		(	Type,								Tag										) VALUES
		(	'DISTRICT_RURALCOMMUNITYA',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_FRONTIER_TOWN',		'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_RURALCOMMUNITYB',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_TROYU',				'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_TSIKHE',				'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_RURALCOMMUNITYC',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_GYOSON',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREEXPANSIONA',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREEXPANSIONA',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_XIAN',				'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREX_XIAN',				'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_UPAPITHA',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREX_UPAPITHA',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_VENICE_01',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREX_VENICE_01',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREEXPANSIONB',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREEXPANSIONB',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_VENICE_02',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREX_VENICE_02',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_FUERTE',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREX_FUERTE',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREEXPANSIONC',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREEXPANSIONC',			'CLASS_CSC_TAILORS_SALES_CULTURE'			),
		(	'DISTRICT_COREX_ELYSEE',			'CLASS_CSC_TAILORS_SALES'			),
		(	'DISTRICT_COREX_ELYSEE',			'CLASS_CSC_TAILORS_SALES_CULTURE'			);
