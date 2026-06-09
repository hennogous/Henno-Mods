-- CSC_QUARTERS_PEDIA
-- Author: Shadow
-- DateCreated: 2025-09-13 19:38:40
--------------------------------------------------------------

--------------------------------------------------------------
-- CivilopediaPageGroups
--------------------------------------------------------------
INSERT OR REPLACE INTO CivilopediaPageGroups
		(SectionID,		PageGroupId,			SortIndex,	VisibleIfEmpty,	Tooltip,	Name)
VALUES	('CONCEPTS',	'CIV_SUPPLY_CHAINS',	4,			0,				'',			'LOC_PEDIA_CONCEPTS_PAGEGROUP_CSC_SUPPLY_CHAINS_NAME');

--------------------------------------------------------------
-- CivilopediaPages
--------------------------------------------------------------
INSERT OR REPLACE INTO CivilopediaPages
		(SectionId,		PageId,								PageGroupId,			SortIndex,	PageLayoutId,		Tooltip,	Name)
VALUES	('CONCEPTS',	'CSC_INTRODUCTION',				    'CIV_SUPPLY_CHAINS',	1,			'Simple',			'',			'LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_TITLE'),
		('CONCEPTS',	'CSC_MATERIALS',		            'CIV_SUPPLY_CHAINS',	2,			'Simple',           '',			'LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_CONTENT_TITLE'),
		('CONCEPTS',	'CSC_QUARTERS',		            	'CIV_SUPPLY_CHAINS',	3,			'Simple',           '',			'LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_CONTENT_TITLE'),
		('CONCEPTS',	'CSC_INTERMEDIARY',		            'CIV_SUPPLY_CHAINS',	4,			'Simple',           '',			'LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_CONTENT_TITLE'),
		('CONCEPTS',	'CSC_CONSUMER',		            	'CIV_SUPPLY_CHAINS',	5,			'Simple',           '',			'LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_CONTENT_TITLE'),
		('CONCEPTS',	'CSC_SPECIALTY',		            'CIV_SUPPLY_CHAINS',	6,			'Simple',           '',			'LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_CONTENT_TITLE'),
		('CONCEPTS',	'CSC_SALES',		            	'CIV_SUPPLY_CHAINS',	7,			'Simple',           '',			'LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_TITLE');

--------------------------------------------------------------
-- CivilopediaPageLayoutChapters
--------------------------------------------------------------
INSERT OR REPLACE INTO CivilopediaPageLayoutChapters
		(PageLayoutId,					ChapterId,			        SortIndex)	
VALUES	('District',					'CSCBASE',					7),
		('District',					'CSCSPEC',					8),
		('District',					'CSCHAIN',					9),
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