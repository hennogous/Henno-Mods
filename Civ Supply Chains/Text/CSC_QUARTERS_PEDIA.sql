-- CSC_QUARTERS_PEDIA
-- Generated from project\localization\CSC_QUARTERS_PEDIA.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

-- Raw SQL 1
INSERT OR REPLACE INTO CivilopediaPageGroups
		(SectionID,		PageGroupId,			SortIndex,	VisibleIfEmpty,	Tooltip,	Name)
VALUES	('CONCEPTS',	'CIV_SUPPLY_CHAINS',	4,			0,				'',			'LOC_PEDIA_CONCEPTS_PAGEGROUP_CSC_SUPPLY_CHAINS_NAME');

--------------------------------------------------------------
-- CivilopediaPages
--------------------------------------------------------------
-- Each overview layout uses the game's Simple renderer with native chapter headings.
INSERT OR REPLACE INTO CivilopediaPageLayouts (PageLayoutId, ScriptTemplate)
VALUES
    ('CSC_OVERVIEW_INTRODUCTION', 'Simple'),
    ('CSC_OVERVIEW_FRAMEWORK', 'Simple'),
    ('CSC_OVERVIEW_TRANSACTIONS', 'Simple'),
    ('CSC_OVERVIEW_MATERIALS', 'Simple'),
    ('CSC_OVERVIEW_QUARTERS', 'Simple'),
    ('CSC_OVERVIEW_INTERMEDIARY', 'Simple'),
    ('CSC_OVERVIEW_CONSUMER', 'Simple'),
    ('CSC_OVERVIEW_SPECIALTY', 'Simple'),
    ('CSC_OVERVIEW_SALES', 'Simple'),
    ('CSC_OVERVIEW_SERVICES', 'Simple');

INSERT OR REPLACE INTO CivilopediaPageLayoutChapters (PageLayoutId, ChapterId, SortIndex)
VALUES
    ('CSC_OVERVIEW_INTRODUCTION', 'CONTENT', 1),
    ('CSC_OVERVIEW_FRAMEWORK', 'CONTENT', 1),
    ('CSC_OVERVIEW_FRAMEWORK', 'STRATEGY', 2),
    ('CSC_OVERVIEW_TRANSACTIONS', 'CONTENT', 1),
    ('CSC_OVERVIEW_TRANSACTIONS', 'ACTORS', 2),
    ('CSC_OVERVIEW_TRANSACTIONS', 'YIELDS', 3),
    ('CSC_OVERVIEW_TRANSACTIONS', 'BALANCE', 4),
    ('CSC_OVERVIEW_MATERIALS', 'CONTENT', 1),
    ('CSC_OVERVIEW_MATERIALS', 'SUPPLIED', 2),
    ('CSC_OVERVIEW_MATERIALS', 'DEMAND', 3),
    ('CSC_OVERVIEW_MATERIALS', 'MONOPOLIES', 4),
    ('CSC_OVERVIEW_QUARTERS', 'CONTENT', 1),
    ('CSC_OVERVIEW_QUARTERS', 'YIELDS', 2),
    ('CSC_OVERVIEW_QUARTERS', 'PLACEMENT', 3),
    ('CSC_OVERVIEW_QUARTERS', 'ADJACENCIES', 4),
    ('CSC_OVERVIEW_QUARTERS', 'RELATIONSHIPS', 5),
    ('CSC_OVERVIEW_INTERMEDIARY', 'CONTENT', 1),
    ('CSC_OVERVIEW_INTERMEDIARY', 'INPUTS', 2),
    ('CSC_OVERVIEW_INTERMEDIARY', 'PROCESSING', 3),
    ('CSC_OVERVIEW_INTERMEDIARY', 'SALES', 4),
    ('CSC_OVERVIEW_CONSUMER', 'CONTENT', 1),
    ('CSC_OVERVIEW_CONSUMER', 'INPUTS', 2),
    ('CSC_OVERVIEW_CONSUMER', 'PROCESSING', 3),
    ('CSC_OVERVIEW_CONSUMER', 'SALES', 4),
    ('CSC_OVERVIEW_SPECIALTY', 'CONTENT', 1),
    ('CSC_OVERVIEW_SPECIALTY', 'INPUTS', 2),
    ('CSC_OVERVIEW_SPECIALTY', 'PROCESSING', 3),
    ('CSC_OVERVIEW_SPECIALTY', 'SALES', 4),
    ('CSC_OVERVIEW_SALES', 'CONTENT', 1),
    ('CSC_OVERVIEW_SALES', 'POPULATION', 2),
    ('CSC_OVERVIEW_SALES', 'CONSUMERTRADE', 3),
    ('CSC_OVERVIEW_SALES', 'SPECIALTYTRADE', 4),
    ('CSC_OVERVIEW_SERVICES', 'CONTENT', 1),
    ('CSC_OVERVIEW_SERVICES', 'EXAMPLES', 2),
    ('CSC_OVERVIEW_SERVICES', 'EFFECTS', 3),
    ('CSC_OVERVIEW_SERVICES', 'ART', 4);

INSERT OR REPLACE INTO CivilopediaPages
    (SectionId, PageId, PageGroupId, SortIndex, PageLayoutId, Tooltip, Name)
VALUES
    ('CONCEPTS', 'CSC_INTRODUCTION', 'CIV_SUPPLY_CHAINS', 1, 'CSC_OVERVIEW_INTRODUCTION', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_FRAMEWORK', 'CIV_SUPPLY_CHAINS', 2, 'CSC_OVERVIEW_FRAMEWORK', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_TRANSACTIONS', 'CIV_SUPPLY_CHAINS', 3, 'CSC_OVERVIEW_TRANSACTIONS', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_MATERIALS', 'CIV_SUPPLY_CHAINS', 4, 'CSC_OVERVIEW_MATERIALS', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_QUARTERS', 'CIV_SUPPLY_CHAINS', 5, 'CSC_OVERVIEW_QUARTERS', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_INTERMEDIARY', 'CIV_SUPPLY_CHAINS', 6, 'CSC_OVERVIEW_INTERMEDIARY', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_CONSUMER', 'CIV_SUPPLY_CHAINS', 7, 'CSC_OVERVIEW_CONSUMER', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_SPECIALTY', 'CIV_SUPPLY_CHAINS', 8, 'CSC_OVERVIEW_SPECIALTY', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_SALES', 'CIV_SUPPLY_CHAINS', 9, 'CSC_OVERVIEW_SALES', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_TITLE'),
    ('CONCEPTS', 'CSC_SERVICES', 'CIV_SUPPLY_CHAINS', 10, 'CSC_OVERVIEW_SERVICES', '', 'LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_CONTENT_TITLE');

--------------------------------------------------------------
-- CivilopediaPageLayoutChapters
--------------------------------------------------------------
INSERT OR REPLACE INTO CivilopediaPageLayoutChapters
		(PageLayoutId,					ChapterId,			        SortIndex)	
VALUES	('District',					'CSCBASE',					7),
		('District',					'CSCSPEC',					8),
		('District',					'CSCGOODS',					9),
		('District',					'CSCSALES',					10),
		('District',					'CSCHAIN',					11),
		('District',					'HISTORY',					12),
		('Building',					'CSCHAIN',					9),
		('Resource',					'CSCQUAR',					9),
		('Project',						'CSCSPEC',					9);

--------------------------------------------------------------
-- CivilopediaPageSearchTerms
--------------------------------------------------------------
INSERT OR IGNORE INTO CivilopediaPageSearchTerms (SectionId, PageId, Term)
SELECT DISTINCT
    'DISTRICTS',
    'DISTRICT_CSC_BAKERS_QUARTER',
    R.Name
FROM TypeTags AS T1
JOIN Resources AS R ON T1.Type = R.ResourceType
WHERE T1.Tag IN ('CLASS_CSC_BAKERS_BASE', 'CLASS_CSC_BAKERS_SPEC');


/*
INSERT OR IGNORE INTO CivilopediaPageSearchTerms
		(SectionId,			PageId,								Term)
VALUES	('DISTRICTS',		'DISTRICT_CSC_BAKERS_QUARTER',		'LOC_RESOURCE_WHEAT_NAME');
--------------------------------------------------------------

*/


/*
-- CivilopediaPageLayouts
--------------------------------------------------------------
INSERT OR REPLACE INTO CivilopediaPageLayouts
		(PageLayoutId,					ScriptTemplate)
VALUES	('CSC_Quarters',	            'Simple');
--------------------------------------------------------------


INSERT OR REPLACE INTO CivilopediaPageLayoutChapters
		(PageLayoutId,					ChapterId,			        SortIndex)	
VALUES	('CSC_Quarters',                'CSCBAKERSINTRO',           10);

INSERT OR REPLACE INTO CivilopediaPageLayoutChapters
		(PageLayoutId,					ChapterId,			        SortIndex)	
VALUES	('CSC_Quarters',                'CSCBAKERSBASE',            20);

INSERT OR REPLACE INTO CivilopediaPageLayoutChapters
		(PageLayoutId,					ChapterId,			        SortIndex)	
VALUES	('CSC_Quarters',                'CSCBAKERSSPEC',            30); */
